"""Example: Lorimier Method - Swiss Government Bonds"""
import sys
sys.path.insert(0, '../src')
import numpy as np
from pytermstructure.methods import LorimierMethod

def main():
    print("\n" + "="*60)
    print("Example: Lorimier Method - Swiss Government Bonds")
    print("="*60)
    
    # Swiss market data (negative rates)
    maturities = np.array([2, 3, 4, 5, 7, 10, 20, 30])
    yields_pct = np.array([-0.79, -0.73, -0.65, -0.55, -0.33, -0.04, 0.54, 0.73])
    yields = yields_pct / 100.0
    
    # Fit with smoothing parameter
    lorimier = LorimierMethod(alpha=0.1, verbose=True)
    curve = lorimier.fit(yields, maturities)
    
    print(f"\nMarket Yields vs Discount Factors:")
    for T, y, P in zip(maturities, yields_pct, curve):
        print(f"  {T:2.0f}Y: Yield={y:6.2f}%  P(0,T)={P:.6f}")
    
    print("\n✓ Example completed!")

if __name__ == "__main__":
    main()
