"""Test Pseudoinverse Method"""
import sys
sys.path.insert(0, '../src')
import numpy as np
from pytermstructure.methods import PseudoinverseMethod

def test_pseudoinverse():
    C = np.eye(3)
    p = np.array([0.99, 0.98, 0.97])
    dates = np.array([1, 2, 3])
    
    pseudoinv = PseudoinverseMethod()
    curve = pseudoinv.fit(C, p, dates)
    
    assert curve is not None
    assert len(curve) == 3
    print("✓ Pseudoinverse test passed")

if __name__ == "__main__":
    test_pseudoinverse()
