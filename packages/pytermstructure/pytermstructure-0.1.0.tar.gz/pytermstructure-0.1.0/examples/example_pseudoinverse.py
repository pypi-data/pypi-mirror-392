"""Example: Pseudoinverse Method"""
import sys
sys.path.insert(0, '../src')
import numpy as np
from pytermstructure.methods import PseudoinverseMethod

def main():
    print("\n" + "="*60)
    print("Example: Pseudoinverse Method")
    print("="*60)
    
    # Simple cash flow matrix (3 instruments, 3 dates)
    C = np.array([
        [1.0, 0.0, 0.0],
        [0.5, 0.5, 0.0],
        [0.3, 0.3, 0.4]
    ])
    
    p = np.array([0.99, 1.98, 2.95])  # Market prices
    dates = np.array([0.5, 1.0, 2.0])  # Maturities
    
    # Fit
    pseudoinv = PseudoinverseMethod(verbose=True)
    curve = pseudoinv.fit(C, p, dates)
    
    print(f"\nDiscount Factors:")
    for T, P in zip(dates, curve):
        print(f"  P(0, {T:.2f}Y) = {P:.6f}")
    
    print("\n✓ Example completed!")

if __name__ == "__main__":
    main()
