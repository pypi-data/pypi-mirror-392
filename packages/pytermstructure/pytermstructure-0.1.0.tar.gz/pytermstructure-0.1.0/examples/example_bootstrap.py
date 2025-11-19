"""Example: Bootstrap Method"""
import sys
sys.path.insert(0, '../src')
from pytermstructure.core import MarketInstrument, InstrumentType
from pytermstructure.methods import BootstrapMethod

def main():
    print("\n" + "="*60)
    print("Example: Bootstrap Method - US Market")
    print("="*60)
    
    bootstrap = BootstrapMethod(verbose=True)
    
    # Add LIBOR rates
    bootstrap.add_instrument(MarketInstrument(InstrumentType.LIBOR, 0.25, 0.15))
    bootstrap.add_instrument(MarketInstrument(InstrumentType.LIBOR, 0.5, 0.20))
    
    # Add swap rates
    bootstrap.add_instrument(MarketInstrument(InstrumentType.SWAP, 2.0, 0.50))
    bootstrap.add_instrument(MarketInstrument(InstrumentType.SWAP, 5.0, 0.75))
    
    # Fit curve
    curve = bootstrap.fit()
    
    print(f"\nDiscount Factors:")
    for i, (T, P) in enumerate(zip(bootstrap.maturities, curve)):
        print(f"  P(0, {T:.2f}Y) = {P:.6f}")
    
    print("\n✓ Example completed successfully!")

if __name__ == "__main__":
    main()
