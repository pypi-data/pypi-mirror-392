"""
Horcrux - File encryption and splitting tool using Shamir's Secret Sharing.

This package allows you to split files into encrypted fragments (horcruxes)
using Shamir's Secret Sharing Scheme combined with AES-256-GCM encryption.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

from hrcx.api import split, bind

__all__ = ["split", "bind", "__version__"]
