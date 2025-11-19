Installation
============

Requirements
------------

PyTermStructure requires Python 3.8 or higher.

Dependencies
~~~~~~~~~~~~

* numpy >= 1.20.0
* scipy >= 1.7.0
* pandas >= 1.3.0
* openpyxl >= 3.0.0

Install from PyPI
-----------------

The easiest way to install PyTermStructure is via pip:

.. code-block:: bash

   pip install pytermstructure

Install from Source
-------------------

You can also install from the GitHub repository:

.. code-block:: bash

   git clone https://github.com/MarcoGigante/pytermstructure.git
   cd pytermstructure
   pip install -e .

Development Installation
------------------------

For development, install with optional dependencies:

.. code-block:: bash

   # Install with dev dependencies
   pip install pytermstructure[dev]

   # Or from source
   git clone https://github.com/MarcoGigante/pytermstructure.git
   cd pytermstructure
   pip install -e ".[dev]"

Optional Dependencies
---------------------

Documentation
~~~~~~~~~~~~~

.. code-block:: bash

   pip install pytermstructure[docs]

This installs Sphinx and related packages for building documentation.

Examples
~~~~~~~~

.. code-block:: bash

   pip install pytermstructure[examples]

This installs matplotlib and jupyter for running examples.

Verify Installation
-------------------

After installation, verify it works:

.. code-block:: python

   import pytermstructure as pts
   pts.version()
   pts.help()

You should see output like:

.. code-block:: text

   PyTermStructure version 1.0.0
   Author: Marco Gigante
   License: GPLv3
   URL: https://github.com/MarcoGigante/pytermstructure

Troubleshooting
---------------

Import Errors
~~~~~~~~~~~~~

If you get import errors, make sure all dependencies are installed:

.. code-block:: bash

   pip install numpy scipy pandas openpyxl

Windows Issues
~~~~~~~~~~~~~~

On Windows, you might need to install Visual C++ build tools for some dependencies.

Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

Mac Issues
~~~~~~~~~~

On Mac, you might need to install Xcode command line tools:

.. code-block:: bash

   xcode-select --install

Upgrade
-------

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade pytermstructure

Uninstall
---------

To uninstall:

.. code-block:: bash

   pip uninstall pytermstructure
