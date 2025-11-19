"""PyTermStructure - Helpers"""

import numpy as np
from scipy.interpolate import interp1d

def calculate_forward_rate(discount_factors, maturities, T1, T2):
    """Calculate forward rate between T1 and T2."""
    interp = interp1d(maturities, discount_factors, kind='linear')
    P1 = interp(T1)
    P2 = interp(T2)
    return (P1 / P2 - 1) / (T2 - T1)
