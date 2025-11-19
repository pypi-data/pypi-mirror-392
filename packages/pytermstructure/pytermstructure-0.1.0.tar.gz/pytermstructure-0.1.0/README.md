# PyTermStructure

**Educational Python library for interest rate term structure estimation**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Inspired by **Damir Filipović's "Interest Rate Models"**  
École Polytechnique Fédérale de Lausanne (EPFL)  
[Course Link](https://www.coursera.org/learn/interest-rate-models)

***

## Version 0.1.0

**NEW in v0.1.0**: Bootstrap accuracy improvements

- Exact calendar date support with ACT/360 day-count
- Automatic curve densification with interpolated swap rates
- Three-phase bootstrap algorithm
- **Accuracy**: <1 bps on benchmark data (improved from ~13 bps)

**Status**: Educational implementation suitable for learning and research.

**Recommendation**: Use for **educational purposes, research, and prototyping**. For production systems requiring high precision, consider [QuantLib](https://www.quantlib.org/) or [FinancePy](https://github.com/domokane/FinancePy).

***

## Quick Start

### Installation

```bash
pip install pytermstructure
```

### Your First Term Structure (NEW: with exact dates!)

```python
import pytermstructure as pts
from pytermstructure.core import MarketInstrument, InstrumentType
from datetime import datetime

# Create bootstrap with spot date
spot = datetime(2024, 1, 15)
bootstrap = pts.BootstrapMethod(verbose=True, spot_date=spot)

# Add LIBOR with exact date
bootstrap.add_instrument(MarketInstrument(
    instrument_type=InstrumentType.LIBOR,
    maturity=datetime(2024, 4, 15),  # 3 months
    quote=0.15,                       # 0.15%
    spot_date=spot
))

# Add swap with exact date
bootstrap.add_instrument(MarketInstrument(
    instrument_type=InstrumentType.SWAP,
    maturity=datetime(2026, 1, 15),  # 2 years
    quote=0.50,                       # 0.50%
    spot_date=spot
))

# Fit discount curve (automatic densification!)
discount_curve = bootstrap.fit()

# Get zero rates
zero_rates = bootstrap.get_zero_rates()
```

### Getting Help

```python
import pytermstructure as pts

# General help
pts.help()

# Method-specific help
pts.help("bootstrap")
pts.help("lorimier")
pts.help("accuracy")  # NEW!
```

***

## Features

### Methods Implemented

| Method | Type | Accuracy | Use Case |
|--------|------|----------|----------|
| **Bootstrap** | Exact | <1 bps | Educational, curve construction |
| **Pseudoinverse** | Exact | <1 bps | Smooth + exact pricing |
| **Lorimier** | Smooth | ±3 bps | Smooth forward curves |
| **PCA** | Analysis | N/A | Risk management |
| **Nelson-Siegel** | Parametric | N/A | Quick approximation |

### Educational Quality

- Built-in help system with comprehensive documentation
- Based on academic course materials (Filipović, EPFL)
- Full typing support with type hints
- Validated with academic benchmark data
- Free Software (GNU GPLv3 license)
- Professional structure ready for contributions

***

## Methods Overview

### 1. Bootstrap Method

Sequential construction from LIBOR → Futures → Swaps.

**NEW in v0.1.0**: Sub-basis-point accuracy with exact dates!

```python
from datetime import datetime

spot = datetime(2024, 10, 3)
bootstrap = pts.BootstrapMethod(verbose=True, spot_date=spot)

bootstrap.add_instrument(pts.MarketInstrument(
    pts.InstrumentType.LIBOR, 
    datetime(2025, 1, 3), 
    0.15,
    spot_date=spot
))

bootstrap.add_instrument(pts.MarketInstrument(
    pts.InstrumentType.SWAP, 
    datetime(2026, 10, 3), 
    0.50,
    spot_date=spot
))

discount_curve = bootstrap.fit()
```

**Accuracy**: <1 bps on benchmark data (v0.1.0)

***

### 2. Lorimier Method

Smoothing splines with parameter α for smooth forward curves.

```python
import numpy as np

# Swiss government bond yields
maturities = np.array([2, 3, 4, 5, 7, 10, 20, 30])
yields = np.array([-0.79, -0.73, -0.65, -0.55, 
                   -0.33, -0.04, 0.54, 0.73]) / 100

lorimier = pts.LorimierMethod(alpha=0.1)
discount_curve = lorimier.fit(yields, maturities)

# Interpolate at 6 years
y_6y = lorimier.get_yield_at(6.0)
```

**Accuracy**: ±3 bps on benchmark data

***

### 3. PCA Analysis

Principal component analysis of yield curve movements.

```python
pca = pts.PCAAnalysis()
eigenvalues, eigenvectors, explained_var = pca.fit(yield_changes)

print(f"Level:     {explained_var[0]:.1f}%")
print(f"Slope:     {explained_var[1]:.1f}%")
print(f"Curvature: {explained_var[2]:.1f}%")
```

***

## Installation

### From PyPI

```bash
pip install pytermstructure
```

### From Source

```bash
git clone https://github.com/MarcoGigante/pytermstructure.git
cd pytermstructure
pip install -e .
```

### Test Installation

```bash
python -c "import pytermstructure as pts; pts.version(); pts.help()"
```

Expected output:
```
PyTermStructure 0.1.0 loaded. For help: pts.help()
PyTermStructure 0.1.0
Author: Marco Gigante
License: GPLv3
```

***

## Running Examples

```bash
# Example 1: Bootstrap US market
python examples/example_bootstrap.py

# Example 2: Pseudoinverse
python examples/example_pseudoinverse.py

# Example 3: Lorimier Swiss bonds
python examples/example_lorimier.py

# Run all examples
python examples/practical_examples.py
```

***

## What's New in v0.1.0

### Bootstrap Enhancements

1. **Exact Date Support**  
   Use real calendar dates instead of year fractions

2. **Automatic Densification**  
   Automatically adds intermediate points with interpolated swap rates

3. **Three-Phase Algorithm**  
   - Phase 1: Bootstrap market instruments (LIBOR, Futures, Swaps ≤20Y)
   - Phase 2: Add intermediate dates (21-29Y) with interpolated rates
   - Phase 3: Calculate long swaps (30Y+) using densified curve

4. **ACT/360 Day-Count**  
   Exact day-count calculations for all periods

### Technical Improvements

- Added `python-dateutil` dependency for date handling
- Enhanced `MarketInstrument` with `maturity_date` support
- Implemented `_get_exact_swap_schedule()` for ACT/360
- Removed unused dependencies (pandas, openpyxl)

---

## Academic Reference

This library implements methods from:

**Filipović, D.** (2009). *Term-Structure Models: A Graduate Course*. Springer Finance.

**Online Course**: [Interest Rate Models](https://www.coursera.org/learn/interest-rate-models)  
École Polytechnique Fédérale de Lausanne (EPFL)

***

## License

GNU General Public License v3.0 or later.

This ensures PyTermStructure remains **free software** forever.

See [LICENSE](LICENSE) for details.

***

## Contributing

Contributions are welcome. Areas for improvement:

1. Enhanced numerical methods
2. Additional day-count conventions
3. Business day calendars
4. Curve analytics
5. Additional validation tests

Please ensure GPL-compatible contributions.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

***

## Author

**Marco Gigante**  
MSc in Quantitative Finance, University of Siena

Inspired by Prof. Damir Filipović's course at EPFL.

***

## Acknowledgments

- Prof. Damir Filipović (EPFL)
- École Polytechnique Fédérale de Lausanne
- NumPy, SciPy communities
- Free Software Foundation

---

## Support

- **Built-in Help**: `pts.help()`
- **Issues**: [GitHub Issues](https://github.com/MarcoGigante/pytermstructure/issues)
- **Documentation**: [pytermstructure.readthedocs.io](https://pytermstructure.readthedocs.io/)

***

## Changelog

### v0.1.0 (November 17, 2025)

- Bootstrap accuracy improvements (<1 bps on benchmark data)
- Exact calendar date support with ACT/360
- Automatic curve densification
- Three-phase bootstrap algorithm
- Enhanced documentation and help system

### v0.0.1 (Initial Release)

- Bootstrap, Lorimier, PCA, Nelson-Siegel methods
- Built-in help system
- Educational implementation

See [CHANGELOG.md](CHANGELOG.md) for complete history.)
