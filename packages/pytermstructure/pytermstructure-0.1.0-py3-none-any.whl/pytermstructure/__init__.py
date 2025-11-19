"""
PyTermStructure - Interest Rate Term Structure Estimation
Copyright (C) 2025 Marco Gigante
Licensed under GNU GPLv3
"""

__version__ = "0.0.1"
__author__ = "Marco Gigante"
__license__ = "GPL-3.0-or-later"

# Import core classes
from .core import TermStructureBase, MarketInstrument, InstrumentType

# Import methods
from .methods import (
    BootstrapMethod,
    PseudoinverseMethod,
    LorimierMethod,
    NelsonSiegelMethod
)

# Import analysis
from .analysis import PCAAnalysis

# Import help system
from .help_system import show_help

def help(topic=None):
    """Display help for PyTermStructure."""
    show_help(topic)

def version():
    """Display version information."""
    print(f"PyTermStructure {__version__}")

# Auto-display on import
print(f"PyTermStructure {__version__} loaded. For help: pts.help()")

__all__ = [
    "TermStructureBase",
    "MarketInstrument",
    "InstrumentType",
    "BootstrapMethod",
    "PseudoinverseMethod",
    "LorimierMethod",
    "NelsonSiegelMethod",
    "PCAAnalysis",
    "help",
    "version",
]