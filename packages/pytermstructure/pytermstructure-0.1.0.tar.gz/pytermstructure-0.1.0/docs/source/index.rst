PyTermStructure Documentation
==============================

**Educational Python library for interest rate term structure estimation**

Version 0.1.0

By **Marco Gigante** | Inspired by Damir Filipović's "Interest Rate Models" (EPFL)

.. note::
   Educational implementation suitable for learning and research.
   Bootstrap method achieves sub-basis-point accuracy on benchmark data.
   See :ref:`accuracy-section` for validation details.

.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0
   :alt: License: GPL v3

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.8+

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install pytermstructure

First Example
~~~~~~~~~~~~~

.. code-block:: python

   import pytermstructure as pts
   from pytermstructure.core import MarketInstrument, InstrumentType
   from datetime import datetime

   # Create bootstrap with spot date
   spot = datetime(2024, 1, 15)
   bootstrap = pts.BootstrapMethod(verbose=True, spot_date=spot)

   # Add LIBOR with exact date
   bootstrap.add_instrument(MarketInstrument(
       instrument_type=InstrumentType.LIBOR,
       maturity=datetime(2024, 4, 15),
       quote=0.15,
       spot_date=spot
   ))

   # Add swap with exact date
   bootstrap.add_instrument(MarketInstrument(
       instrument_type=InstrumentType.SWAP,
       maturity=datetime(2026, 1, 15),
       quote=0.50,
       spot_date=spot
   ))

   # Fit discount curve
   discount_curve = bootstrap.fit()
   zero_rates = bootstrap.get_zero_rates()

.. _accuracy-section:

Accuracy & Validation
---------------------

v0.1.0 Improvements
~~~~~~~~~~~~~~~~~~~

Version 0.1.0 brings significant accuracy improvements to the bootstrap method:

- Exact calendar date support with ACT/360 day-count convention
- Automatic curve densification with interpolated swap rates
- Three-phase bootstrap algorithm for long-term instruments
- Improved accuracy: from ~13 bps to <1 bps on benchmark data

Test Results
~~~~~~~~~~~~

Validation using academic benchmark data:

.. list-table::
   :header-rows: 1
   :widths: 20 20 15 15 15

   * - Method
     - Test Case
     - Result
     - Target
     - Deviation
   * - Bootstrap
     - 30Y forward rate
     - 2.56%
     - 2.56%
     - 0.00 bps
   * - Bootstrap
     - 30Y discount factor
     - 0.483144
     - 0.483194
     - 0.50 bps
   * - Lorimier
     - 6Y Swiss yield
     - -0.44%
     - -0.41%
     - 3.0 bps

Expected Tolerances
~~~~~~~~~~~~~~~~~~~

- **Bootstrap method**: typically <1 bps on benchmark data
- **Lorimier method**: typically ±3 bps on interpolated yields
- **Pseudoinverse**: uses bootstrap as baseline

**Recommendation**: Suitable for educational purposes and research. 
Always validate results against your specific dataset before use in applications.

What's New in v0.1.0
--------------------

Bootstrap Enhancements
~~~~~~~~~~~~~~~~~~~~~~

1. **Exact Date Support**
   
   You can now use real calendar dates instead of year fractions:
   
   .. code-block:: python
   
      from datetime import datetime
      
      maturity_date = datetime(2025, 12, 15)
      inst = MarketInstrument(
          InstrumentType.SWAP,
          maturity_date,
          2.50,
          spot_date=datetime(2024, 12, 15)
      )

2. **Automatic Densification**
   
   The bootstrap method automatically adds intermediate points:
   
   .. code-block:: python
   
      bootstrap.fit()  # Automatically densifies curve
      # Example: 17 market instruments → 38 curve points

3. **Three-Phase Algorithm**
   
   - Phase 1: Bootstrap LIBOR, Futures, and swaps up to 20Y
   - Phase 2: Add intermediate dates with interpolated swap rates
   - Phase 3: Calculate long swaps using densified curve

4. **ACT/360 Day-Count**
   
   Exact day-count calculations for all periods:
   
   .. code-block:: python
   
      days = (maturity_date - spot_date).days
      year_fraction = days / 360.0  # ACT/360

Methods
-------

Bootstrap Method
~~~~~~~~~~~~~~~~

Sequential construction from LIBOR to Futures to Swaps.

**Example**:

.. code-block:: python

   from pytermstructure import BootstrapMethod
   from pytermstructure.core import MarketInstrument, InstrumentType
   from datetime import datetime

   spot = datetime(2024, 10, 3)
   bootstrap = BootstrapMethod(verbose=True, spot_date=spot)
   
   # LIBOR 3M
   bootstrap.add_instrument(MarketInstrument(
       InstrumentType.LIBOR, 
       datetime(2025, 1, 3), 
       0.15,
       spot_date=spot
   ))
   
   # Swap 2Y
   bootstrap.add_instrument(MarketInstrument(
       InstrumentType.SWAP, 
       datetime(2026, 10, 3), 
       0.50,
       spot_date=spot
   ))
   
   curve = bootstrap.fit()

Lorimier Method
~~~~~~~~~~~~~~~

Smoothing splines for yield curve interpolation.

**Example**:

.. code-block:: python

   import numpy as np
   from pytermstructure import LorimierMethod

   # Swiss government bond yields
   maturities = np.array([2, 3, 4, 5, 7, 10, 20, 30])
   yields = np.array([-0.79, -0.73, -0.65, -0.55, 
                      -0.33, -0.04, 0.54, 0.73]) / 100

   lorimier = LorimierMethod(alpha=0.1, verbose=True)
   curve = lorimier.fit(yields, maturities)
   
   # Interpolate at 6 years
   y_6y = lorimier.get_yield_at(6.0)

PCA Analysis
~~~~~~~~~~~~

Principal component analysis of yield curve movements.

.. code-block:: python

   import numpy as np
   from pytermstructure import PCAAnalysis

   # Historical yield changes
   yield_changes = np.random.randn(100, 5) * 0.01

   pca = PCAAnalysis(verbose=True)
   eigenvalues, eigenvectors, explained_var = pca.fit(yield_changes)

Built-in Help System
--------------------

.. code-block:: python

   import pytermstructure as pts

   pts.help()                  # General help
   pts.help("bootstrap")       # Bootstrap method
   pts.help("lorimier")        # Lorimier method
   pts.help("quickstart")      # Quick start guide
   pts.help("accuracy")        # Accuracy information

Common Issues
-------------

Import Error
~~~~~~~~~~~~

If you get import errors:

.. code-block:: bash

   pip install -e .  # Development mode
   # or
   pip install pytermstructure  # From PyPI

Accuracy Concerns
~~~~~~~~~~~~~~~~~

Version 0.1.0 typically achieves <1 bps accuracy on benchmark data. 
If you observe larger deviations:

1. Check date format: use ``datetime`` objects
2. Verify spot date matches your data
3. Check instrument order (bootstrap processes sequentially)
4. Confirm day-count convention (ACT/360 assumed)

See :ref:`accuracy-section` for expected tolerances.

API Reference
-------------

Core Classes
~~~~~~~~~~~~

.. autoclass:: pytermstructure.core.MarketInstrument
   :members:

.. autoclass:: pytermstructure.core.InstrumentType
   :members:

.. autoclass:: pytermstructure.core.DayCountConvention
   :members:

Methods
~~~~~~~

.. autoclass:: pytermstructure.methods.BootstrapMethod
   :members:

.. autoclass:: pytermstructure.methods.LorimierMethod
   :members:

.. autoclass:: pytermstructure.methods.PCAAnalysis
   :members:

Academic Reference
------------------

This library implements methods from:

**Filipović, D.** (2009). *Term-Structure Models: A Graduate Course*. Springer Finance.

**Online Course**: `Interest Rate Models <https://www.coursera.org/learn/interest-rate-models>`_

École Polytechnique Fédérale de Lausanne (EPFL)

Contributing
------------

Contributions are welcome. Areas for improvement include:

1. Enhanced numerical methods
2. Additional day-count conventions
3. Business day calendars
4. Curve analytics
5. Additional validation tests

See `CONTRIBUTING.md <https://github.com/MarcoGigante/pytermstructure/blob/main/CONTRIBUTING.md>`_.

License
-------

GNU General Public License v3.0 or later.

See `LICENSE <https://github.com/MarcoGigante/pytermstructure/blob/main/LICENSE>`_ for details.

Links
-----

* **GitHub**: https://github.com/MarcoGigante/pytermstructure
* **PyPI**: https://pypi.org/project/pytermstructure/
* **Issues**: https://github.com/MarcoGigante/pytermstructure/issues

Acknowledgments
---------------

- Prof. Damir Filipović (EPFL)
- École Polytechnique Fédérale de Lausanne
- NumPy, SciPy communities

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   examples
   api

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
