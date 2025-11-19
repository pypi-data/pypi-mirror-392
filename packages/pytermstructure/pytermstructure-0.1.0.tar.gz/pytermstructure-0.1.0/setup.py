from setuptools import setup, find_packages

setup(
    name="pytermstructure",
    version="0.1.0",
    author="Marco Gigante",
    description="Educational Python library for interest rate term structure estimation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MarcoGigante/pytermstructure",
    project_urls={
        "Bug Tracker": "https://github.com/MarcoGigante/pytermstructure/issues",
        "Documentation": "https://pytermstructure.readthedocs.io",
        "Source Code": "https://github.com/MarcoGigante/pytermstructure",
        "Changelog": "https://github.com/MarcoGigante/pytermstructure/blob/main/CHANGELOG.md",
    },
    license="GPL-3.0-or-later",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="finance interest-rates term-structure yield-curve quantitative-finance bootstrap lorimier",
)
