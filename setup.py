"""Lightweight setup for rtopy package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from package
__version__ = "0.2.0"

# Read README for long description
here = Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else "Lightweight R-Python bridge"

setup(
    name="rtopy",
    version=__version__,
    author="T. Moudiki (forked and improved)",
    author_email="thierry.moudiki@gmail.com",
    description="Lightweight bridge for calling R functions from Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thierrymoudiki/rtopy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.7",
    install_requires=[
       "numpy>=1.19.0", "pandas>=1.1.0", "scikit-learn>=1.0.0", "scipy>=1.0.0"
    ],
    extras_require={
        "full": ["numpy>=1.19.0", "pandas>=1.1.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "pandas>=1.1.0",
            "numpy>=1.19.0",
        ],
    },
    keywords="r python bridge statistics data-science",
    project_urls={
        "Bug Reports": "https://github.com/thierrymoudiki/rtopy/issues",
        "Source": "https://github.com/thierrymoudiki/rtopy",
    },
)
