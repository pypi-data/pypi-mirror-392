"""PyTermStructure - Examples"""
import numpy as np
import sys
sys.path.insert(0, '../src')

def example_1_bootstrap():
    from pytermstructure.core import MarketInstrument, InstrumentType
    from pytermstructure.methods import BootstrapMethod
    
    print("\nExample 1: Bootstrap Method")
    print("="*50)
    
    bootstrap = BootstrapMethod(verbose=True)
    bootstrap.add_instrument(MarketInstrument(InstrumentType.LIBOR, 0.25, 0.15))
    bootstrap.add_instrument(MarketInstrument(InstrumentType.SWAP, 2.0, 0.50))
    
    curve = bootstrap.fit()
    print(f"Discount factors: {curve}")
    return curve

def run_all_examples():
    example_1_bootstrap()
    print("\nAll examples completed!")

if __name__ == "__main__":
    run_all_examples()
