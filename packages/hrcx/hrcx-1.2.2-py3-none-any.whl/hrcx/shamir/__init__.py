"""
Shamir's Secret Sharing implementation.

This module provides functions to split secrets into shares and reconstruct them.
"""

from hrcx.shamir.shamir import split, combine

__all__ = ["split", "combine"]
