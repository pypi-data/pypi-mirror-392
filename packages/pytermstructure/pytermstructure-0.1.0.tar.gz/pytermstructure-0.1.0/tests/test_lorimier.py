"""Test Lorimier Method"""
import sys
sys.path.insert(0, '../src')
import numpy as np
from pytermstructure.methods import LorimierMethod

def test_lorimier():
    maturities = np.array([1, 2, 3, 5])
    yields = np.array([0.01, 0.015, 0.02, 0.025])
    
    lorimier = LorimierMethod(alpha=0.1)
    curve = lorimier.fit(yields, maturities)
    
    assert curve is not None
    assert len(curve) == 4
    print("✓ Lorimier test passed")

if __name__ == "__main__":
    test_lorimier()
