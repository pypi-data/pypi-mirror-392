"""
Setup configuration for the Composite Indicator Builder package
Author: Dr. Merwan Roudane
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="indicator",
    version="1.0.0",
    author="Dr. Merwan Roudane",
    author_email="merwanroudane920@gmail.com",
    description="Professional tool for constructing composite indicators using various methodologies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/merwanroudane/indicators",
    project_urls={
        "Bug Tracker": "https://github.com/merwanroudane/indicators/issues",
        "Documentation": "https://github.com/merwanroudane/indicators#readme",
        "Source Code": "https://github.com/merwanroudane/indicators",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "customtkinter>=5.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "openpyxl>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "indicator=indicator.gui:main",
        ],
    },
    keywords=[
        "composite indicators",
        "OECD",
        "PCA",
        "entropy",
        "benefit of doubt",
        "DEA",
        "data analysis",
        "econometrics",
        "statistics",
        "research tools",
    ],
    include_package_data=True,
    zip_safe=False,
)
