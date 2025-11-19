"""Test Bootstrap"""
import sys
sys.path.insert(0, '../src')

def test_bootstrap():
    from pytermstructure.core import MarketInstrument, InstrumentType
    from pytermstructure.methods import BootstrapMethod
    
    bootstrap = BootstrapMethod()
    bootstrap.add_instrument(MarketInstrument(InstrumentType.LIBOR, 0.25, 0.15))
    curve = bootstrap.fit()
    assert curve is not None
    print("✓ Test passed")

if __name__ == "__main__":
    test_bootstrap()
