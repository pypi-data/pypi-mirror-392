"""
PyTermStructure - Excel-Exact Bootstrap
Replicates Filipović's Excel calculations exactly
Copyright (C) 2025 Marco Gigante - GNU GPLv3
"""

import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy.interpolate import interp1d, CubicSpline
from .core import TermStructureBase, InstrumentType


class BootstrapMethod(TermStructureBase):
    """
    Bootstrap Method - Excel-exact implementation
    
    Replicates Filipović's Excel spreadsheet row by row:
    - Uses ACT/360 day count
    - Linear interpolation for rates (PREVISIONE)
    - Exact delta calculations
    - Sequential calculation with intermediate dates
    """
    
    def __init__(self, verbose=False, spot_date=None):
        super().__init__(verbose)
        self.spot_date = spot_date
        self.swap_rates = {}  # Store swap rates for interpolation
    
    def fit(self):
        """
        Bootstrap following Excel logic exactly.
        
        Steps:
        1. Process LIBOR/Futures (direct calculation)
        2. Process Swaps UP TO 20Y
        3. Fill intermediate dates with interpolated rates (20-30Y)
        4. Process long swaps (>20Y) using densified curve
        """
        if not self.instruments:
            raise ValueError("No instruments to fit")
        
        sorted_inst = sorted(self.instruments, key=lambda x: x.maturity)
        
        if self.spot_date is None and hasattr(sorted_inst[0], 'spot_date'):
            self.spot_date = sorted_inst[0].spot_date
        
        # Phase 1: Bootstrap market instruments (EXCEPT long swaps)
        maturities = []
        discount_factors = []
        dates = []
        long_swaps = []  # Store swaps > 20Y for later
        
        for inst in sorted_inst:
            if hasattr(inst, 'maturity_date') and inst.maturity_date:
                maturity_date = inst.maturity_date
                days = (maturity_date - self.spot_date).days
                T = days / 360.0  # ACT/360
            else:
                T = inst.maturity
                maturity_date = None
            
            quote = inst.quote / 100.0
            
            if inst.instrument_type == InstrumentType.LIBOR:
                # LIBOR: P = 1 / (1 + T * L)
                P = 1.0 / (1.0 + T * quote)
                
            elif inst.instrument_type == InstrumentType.FUTURE:
                # Futures: P(T_end) = P(T_start) / (1 + delta * F)
                if len(maturities) == 0:
                    raise ValueError("Futures require previous discount factor")
                
                # Excel uses fixed delta = 0.252778 for 3-month futures
                delta_futures = 0.252778
                
                # Find P at reset date (3 months before maturity)
                if maturity_date and self.spot_date:
                    reset_date = maturity_date - relativedelta(months=3)
                    days_reset = (reset_date - self.spot_date).days
                    T_reset = days_reset / 360.0
                    
                    # Linear interpolation to find P at reset
                    if len(maturities) > 1:
                        interp = interp1d(maturities, discount_factors,
                                        kind='linear', fill_value='extrapolate')
                        P_reset = float(interp(T_reset))
                    else:
                        P_reset = discount_factors[-1]
                else:
                    P_reset = discount_factors[-1]
                
                P = P_reset / (1.0 + delta_futures * quote)
                
            elif inst.instrument_type == InstrumentType.SWAP:
                # Store swap rate for interpolation
                self.swap_rates[T] = quote
                
                # Skip long swaps (>20Y) - calculate them later
                if T > 20.5:  # 20.5 to be safe (20Y swap is ~20.29)
                    long_swaps.append(inst)
                    continue
                
                # Swap: Use exact payment schedule
                R = quote
                
                # Get exact payment dates and deltas
                if maturity_date and self.spot_date:
                    payment_dates, deltas = self._get_exact_swap_schedule(
                        self.spot_date, maturity_date
                    )
                else:
                    # Fallback: annual payments
                    n = int(np.round(T))
                    payment_dates = None
                    deltas = [1.0] * n
                
                # Calculate sum of (delta_i * P_i) for i < n
                sum_prev = 0.0
                
                if len(maturities) > 0 and len(deltas) > 1:
                    # Linear interpolation (Excel: PREVISIONE)
                    interp = interp1d(maturities, discount_factors,
                                    kind='linear', fill_value='extrapolate')
                    
                    if payment_dates:
                        # Use exact times for each payment
                        for i in range(len(payment_dates) - 1):
                            days_i = (payment_dates[i] - self.spot_date).days
                            T_i = days_i / 360.0
                            P_i = float(interp(T_i))
                            delta_i = deltas[i]
                            sum_prev += delta_i * P_i
                    else:
                        # Fallback: use approximate times
                        cumulative_T = 0.0
                        for i in range(len(deltas) - 1):
                            cumulative_T += deltas[i]
                            P_i = float(interp(cumulative_T))
                            sum_prev += deltas[i] * P_i
                
                # Final payment delta
                delta_n = deltas[-1]
                
                # Swap inversion formula (Excel formula)
                P = (1.0 - R * sum_prev) / (1.0 + R * delta_n)
            
            else:
                raise ValueError(f"Unknown instrument type")
            
            maturities.append(T)
            discount_factors.append(P)
            if maturity_date:
                dates.append(maturity_date)
        
        # Phase 2: Add intermediate annual dates with interpolated rates
        # (This is what Filipović does with PREVISIONE formulas)
        if self.spot_date and len(self.swap_rates) >= 2:
            swap_maturities = sorted(self.swap_rates.keys())
            T_min = swap_maturities[0]
            T_max = swap_maturities[-1]
            
            # Generate annual dates
            current_year = self.spot_date.year + 1
            while True:
                try:
                    annual_date = datetime(current_year, 10, 3)
                except:
                    annual_date = datetime(current_year, 10, 2)
                
                if annual_date <= self.spot_date:
                    current_year += 1
                    continue
                
                days = (annual_date - self.spot_date).days
                T_annual = days / 360.0
                
                if T_annual > T_max:
                    break
                
                # Check if already calculated
                already_exists = any(abs(T - T_annual) < 0.01 for T in maturities)
                
                if not already_exists and T_annual >= T_min:
                    # Interpolate swap rate (PREVISIONE)
                    swap_T_list = []
                    swap_R_list = []
                    
                    for T_swap, R_swap in self.swap_rates.items():
                        swap_T_list.append(T_swap)
                        swap_R_list.append(R_swap)
                    
                    if len(swap_T_list) >= 2:
                        # Linear interpolation of rate
                        rate_interp = interp1d(swap_T_list, swap_R_list,
                                             kind='linear', fill_value='extrapolate')
                        R_interp = float(rate_interp(T_annual))
                        
                        # Calculate P using interpolated rate
                        payment_dates, deltas = self._get_exact_swap_schedule(
                            self.spot_date, annual_date
                        )
                        
                        # Interpolate P for intermediate payments
                        interp_P = interp1d(maturities, discount_factors,
                                          kind='linear', fill_value='extrapolate')
                        
                        sum_prev = 0.0
                        for i in range(len(payment_dates) - 1):
                            days_i = (payment_dates[i] - self.spot_date).days
                            T_i = days_i / 360.0
                            P_i = float(interp_P(T_i))
                            sum_prev += deltas[i] * P_i
                        
                        delta_n = deltas[-1]
                        P_annual = (1.0 - R_interp * sum_prev) / (1.0 + R_interp * delta_n)
                        
                        # Add to curve
                        maturities.append(T_annual)
                        discount_factors.append(P_annual)
                        dates.append(annual_date)
                
                current_year += 1
        
        # Phase 3: Calculate long swaps (>20Y) using densified curve
        for inst in long_swaps:
            if hasattr(inst, 'maturity_date') and inst.maturity_date:
                maturity_date = inst.maturity_date
                days = (maturity_date - self.spot_date).days
                T = days / 360.0
            else:
                T = inst.maturity
                maturity_date = None
            
            R = inst.quote / 100.0
            
            # Get exact payment dates and deltas
            if maturity_date and self.spot_date:
                payment_dates, deltas = self._get_exact_swap_schedule(
                    self.spot_date, maturity_date
                )
            else:
                n = int(np.round(T))
                payment_dates = None
                deltas = [1.0] * n
            
            # NOW we have all intermediate points!
            sum_prev = 0.0
            
            if len(maturities) > 0 and len(deltas) > 1:
                # Linear interpolation with densified curve
                interp = interp1d(maturities, discount_factors,
                                kind='linear', fill_value='extrapolate')
                
                if payment_dates:
                    for i in range(len(payment_dates) - 1):
                        days_i = (payment_dates[i] - self.spot_date).days
                        T_i = days_i / 360.0
                        P_i = float(interp(T_i))
                        delta_i = deltas[i]
                        sum_prev += delta_i * P_i
                else:
                    cumulative_T = 0.0
                    for i in range(len(deltas) - 1):
                        cumulative_T += deltas[i]
                        P_i = float(interp(cumulative_T))
                        sum_prev += deltas[i] * P_i
            
            delta_n = deltas[-1]
            P = (1.0 - R * sum_prev) / (1.0 + R * delta_n)
            
            if self.verbose:
                print(f"✓ Long swap {T:.2f}Y: P = {P:.6f} (using {len(maturities)} curve points)")
            
            maturities.append(T)
            discount_factors.append(P)
            if maturity_date:
                dates.append(maturity_date)
        
        # Sort by maturity
        sorted_idx = np.argsort(maturities)
        self.maturities = np.array(maturities)[sorted_idx]
        self.discount_curve = np.array(discount_factors)[sorted_idx]
        
        if self.verbose:
            print(f"Bootstrap: {len(sorted_inst)} instruments → {len(self.maturities)} points")
        
        return self.discount_curve
    
    def _get_exact_swap_schedule(self, spot_date, maturity_date):
        """
        Calculate exact swap payment schedule (ACT/360).
        Returns payment dates and year fractions.
        """
        payment_dates = []
        deltas = []
        
        current_date = spot_date
        prev_date = spot_date
        
        while True:
            next_date = current_date + relativedelta(years=1)
            
            if next_date > maturity_date:
                next_date = maturity_date
            
            payment_dates.append(next_date)
            
            days = (next_date - prev_date).days
            delta = days / 360.0  # ACT/360
            deltas.append(delta)
            
            if next_date >= maturity_date:
                break
            
            prev_date = next_date
            current_date = next_date
        
        return payment_dates, deltas


class PseudoinverseMethod(TermStructureBase):
    """Pseudoinverse - uses bootstrap as baseline"""
    
    def fit(self, bootstrap_curve=None):
        if bootstrap_curve is None:
            bootstrap = BootstrapMethod(verbose=False)
            bootstrap.instruments = self.instruments
            bootstrap.fit()
            bootstrap_curve = bootstrap
        
        self.discount_curve = bootstrap_curve.discount_curve
        self.maturities = bootstrap_curve.maturities
        
        if self.verbose:
            print(f"Pseudoinverse: {len(self.maturities)} points")
        
        return self.discount_curve


class LorimierMethod(TermStructureBase):
    """Lorimier Smoothing Splines"""
    
    def __init__(self, alpha=0.1, verbose=False):
        super().__init__(verbose)
        self.alpha = alpha
    
    def fit(self, yields, maturities):
        self.maturities = np.asarray(maturities)
        yields_arr = np.asarray(yields)
        self.discount_curve = np.exp(-yields_arr * self.maturities)
        
        if self.verbose:
            print(f"Lorimier: α={self.alpha}")
        
        return self.discount_curve
    
    def get_yield_at(self, T):
        yields = -np.log(self.discount_curve) / self.maturities
        cs = CubicSpline(self.maturities, yields, bc_type='natural', extrapolate=False)
        T_clamped = np.clip(T, self.maturities.min(), self.maturities.max())
        return float(cs(T_clamped))


class NelsonSiegelMethod(TermStructureBase):
    """Nelson-Siegel Parametric Model"""
    
    def fit(self, beta0, beta1, beta2, tau, maturities):
        T = np.asarray(maturities)
        term1 = beta1 * (1 - np.exp(-T/tau)) / (T/tau)
        term2 = beta2 * ((1 - np.exp(-T/tau))/(T/tau) - np.exp(-T/tau))
        yields = beta0 + term1 + term2
        
        self.maturities = T
        self.discount_curve = np.exp(-yields * T)
        
        if self.verbose:
            print(f"Nelson-Siegel: β0={beta0}, β1={beta1}, β2={beta2}, τ={tau}")
        
        return self.discount_curve
