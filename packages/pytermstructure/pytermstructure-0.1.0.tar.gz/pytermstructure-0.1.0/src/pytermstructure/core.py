"""
PyTermStructure - Core Classes
Based on Damir Filipović Interest Rate Models (EPFL)
Copyright (C) 2025 Marco Gigante - GNU GPLv3
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Union
import numpy as np


class DayCountConvention(Enum):
    """
    Day-count conventions for interest rate calculations.
    
    References
    ----------
    Filipović Chapter 2.1: "Day-count convention is actual/360"
    """
    ACT_360 = "ACT/360"
    ACT_365 = "ACT/365"
    THIRTY_360 = "30/360"


def calc_year_fraction(start_date: datetime, 
                       end_date: datetime, 
                       convention: DayCountConvention = DayCountConvention.ACT_360) -> float:
    """
    Calculate year fraction using day-count convention.
    
    This implements the formula: delta = (t_i - t_0) / basis
    where basis is 360 for ACT/360, 365 for ACT/365, etc.
    
    Parameters
    ----------
    start_date : datetime
        Start date (spot date t_0)
    end_date : datetime
        End date (maturity date t_i)
    convention : DayCountConvention, optional
        Day-count convention (default: ACT/360 per Filipović)
    
    Returns
    -------
    float
        Year fraction (delta)
    
    Examples
    --------
    >>> from datetime import datetime
    >>> spot = datetime(2012, 3, 10)
    >>> maturity = datetime(2012, 4, 10)
    >>> delta = calc_year_fraction(spot, maturity)
    >>> print(f"{delta:.6f}")  # 31/360 = 0.086111
    
    >>> # 3-month LIBOR: 93 days
    >>> spot = datetime(2012, 10, 1)
    >>> mat = datetime(2013, 1, 2)
    >>> delta = calc_year_fraction(spot, mat)
    >>> print(f"{delta:.6f}")  # 93/360 = 0.258333
    
    Notes
    -----
    ACT/360 is standard for:
    - USD LIBOR
    - USD money market instruments
    - Most interest rate swaps
    
    References
    ----------
    Filipović (2009), Chapter 2.1, page 2-3
    """
    days = (end_date - start_date).days
    
    if convention == DayCountConvention.ACT_360:
        return days / 360.0
    
    elif convention == DayCountConvention.ACT_365:
        return days / 365.0
    
    elif convention == DayCountConvention.THIRTY_360:
        # 30/360 US (Bond Basis)
        y1, m1, d1 = start_date.year, start_date.month, start_date.day
        y2, m2, d2 = end_date.year, end_date.month, end_date.day
        
        # Adjust days per 30/360 convention
        if d1 == 31:
            d1 = 30
        if d2 == 31 and d1 >= 30:
            d2 = 30
        
        return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)) / 360.0
    
    else:
        raise ValueError(f"Unknown convention: {convention}")


class InstrumentType(Enum):
    """Market instrument types."""
    LIBOR = "LIBOR"
    FUTURE = "Future"
    SWAP = "Swap"
    BOND = "Bond"


class MarketInstrument:
    """
    Market instrument with support for dates or year fractions.
    
    Supports two modes:
    1. **Year fraction mode** (backward compatible)
    2. **Date mode** (recommended for accuracy)
    
    Parameters
    ----------
    instrument_type : InstrumentType
        Type of instrument (LIBOR, FUTURE, SWAP, BOND)
    maturity : float or datetime
        If float: year fraction from spot (e.g., 0.25 for 3M)
        If datetime: actual maturity date (preferred)
    quote : float
        Market quote in % (e.g., 0.15 for 0.15%)
    name : str, optional
        Instrument name/identifier
    spot_date : datetime, optional
        Spot date (required if maturity is datetime)
    convention : DayCountConvention, optional
        Day-count convention (default: ACT/360)
    
    Attributes
    ----------
    maturity : float
        Year fraction calculated using day-count convention
    maturity_date : datetime or None
        Original maturity date (if provided)
    spot_date : datetime or None
        Original spot date (if provided)
    
    Examples
    --------
    >>> # Method 1: Year fraction (old way, still works)
    >>> libor = MarketInstrument(InstrumentType.LIBOR, 0.25, 0.15)
    >>> print(f"Delta: {libor.maturity}")  # 0.25
    
    >>> # Method 2: Actual dates (new way, more accurate)
    >>> from datetime import datetime
    >>> spot = datetime(2012, 3, 10)
    >>> mat = datetime(2012, 4, 10)
    >>> libor = MarketInstrument(InstrumentType.LIBOR, mat, 0.15, 
    ...                           spot_date=spot)
    >>> print(f"Delta: {libor.maturity:.6f}")  # 0.086111 (31/360)
    
    Notes
    -----
    Using actual dates improves accuracy by ~5-10 basis points
    because it accounts for exact calendar days instead of 
    approximate year fractions.
    """
    
    def __init__(self, 
                 instrument_type: InstrumentType,
                 maturity: Union[float, datetime],
                 quote: float,
                 name: Optional[str] = None,
                 spot_date: Optional[datetime] = None,
                 convention: DayCountConvention = DayCountConvention.ACT_360):
        
        self.instrument_type = instrument_type
        self.quote = quote
        self.name = name
        self.convention = convention
        
        # Handle datetime or float
        if isinstance(maturity, datetime):
            # Date mode: calculate year fraction with day-count
            if spot_date is None:
                raise ValueError("spot_date required when maturity is datetime")
            
            self.maturity_date = maturity
            self.spot_date = spot_date
            # Calculate exact delta using ACT/360
            self.maturity = calc_year_fraction(spot_date, maturity, convention)
        
        else:
            # Float mode: use directly (backward compatible)
            self.maturity = float(maturity)
            self.maturity_date = None
            self.spot_date = spot_date
    
    def __repr__(self):
        """String representation."""
        if self.maturity_date:
            days = (self.maturity_date - self.spot_date).days
            name_str = f" '{self.name}'" if self.name else ""
            return (f"{self.instrument_type.value}{name_str}("
                   f"{self.maturity_date.strftime('%Y-%m-%d')}, "
                   f"{self.quote:.4f}%, "
                   f"{days}d, δ={self.maturity:.6f})")
        else:
            name_str = f" '{self.name}'" if self.name else ""
            return (f"{self.instrument_type.value}{name_str}("
                   f"{self.maturity:.4f}Y, "
                   f"{self.quote:.4f}%)")
    
    def __str__(self):
        """Human-readable string."""
        return self.__repr__()


class TermStructureBase:
    """
    Base class for term structure estimation methods.
    
    All estimation methods (Bootstrap, Pseudoinverse, Lorimier, etc.)
    inherit from this class.
    
    Attributes
    ----------
    instruments : list of MarketInstrument
        Collection of market instruments
    maturities : np.ndarray or None
        Array of maturity dates (after fit)
    discount_curve : np.ndarray or None
        Array of discount factors P(0,T) (after fit)
    verbose : bool
        Print progress messages
    
    Examples
    --------
    >>> class MyMethod(TermStructureBase):
    ...     def fit(self):
    ...         # Implementation here
    ...         pass
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.instruments = []
        self.discount_curve = None
        self.maturities = None
    
    def add_instrument(self, instrument: MarketInstrument):
        """
        Add market instrument to the collection.
        
        Parameters
        ----------
        instrument : MarketInstrument
            Instrument to add
        """
        self.instruments.append(instrument)
    
    def fit(self):
        """
        Fit discount curve to market instruments.
        
        Override in subclasses with specific implementation.
        
        Returns
        -------
        np.ndarray
            Discount factors P(0,T)
        """
        raise NotImplementedError("Subclasses must implement fit()")
    
    def get_zero_rates(self) -> np.ndarray:
        """
        Calculate zero rates from discount factors.
        
        Zero rate r(0,T) is defined by: P(0,T) = exp(-r(0,T) * T)
        
        Returns
        -------
        np.ndarray
            Zero rates r(0,T)
        
        Raises
        ------
        ValueError
            If fit() has not been called yet
        """
        if self.discount_curve is None:
            raise ValueError("Call fit() first")
        return -np.log(self.discount_curve) / self.maturities
    
    def get_forward_rates(self) -> np.ndarray:
        """
        Calculate instantaneous forward rates.
        
        Forward rate f(T1,T2) is defined by:
        f(T1,T2) = [log(P(0,T1)) - log(P(0,T2))] / (T2 - T1)
        
        Returns
        -------
        np.ndarray
            Forward rates f(Ti, Ti+1) for consecutive maturities
        
        Raises
        ------
        ValueError
            If fit() has not been called yet
        """
        if self.discount_curve is None:
            raise ValueError("Call fit() first")
        
        n = len(self.maturities)
        forward_rates = np.zeros(n - 1)
        
        for i in range(n - 1):
            T1 = self.maturities[i]
            T2 = self.maturities[i + 1]
            P1 = self.discount_curve[i]
            P2 = self.discount_curve[i + 1]
            
            # f(T1,T2) = log(P(T1)/P(T2)) / (T2-T1)
            forward_rates[i] = (np.log(P1 / P2)) / (T2 - T1)
        
        return forward_rates
    
    def get_discount_factor(self, T: float) -> float:
        """
        Get discount factor at maturity T using linear interpolation.
        
        Parameters
        ----------
        T : float
            Maturity in years
        
        Returns
        -------
        float
            Discount factor P(0,T)
        
        Raises
        ------
        ValueError
            If fit() has not been called yet
        """
        if self.discount_curve is None:
            raise ValueError("Call fit() first")
        
        # Linear interpolation
        return float(np.interp(T, self.maturities, self.discount_curve))
