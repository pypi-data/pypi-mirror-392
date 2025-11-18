"""
Configurable SHA merkle tree generator for directory structures.

This package provides functionality to generate merkle trees for directory
structures, creating .merkle files in each subdirectory containing SHA sums
of files and subdirectories.
"""

__version__ = '0.1.0'
__author__ = "Mykel Alvis"
__email__ = "mykel.alvis@gmail.com"

from .config import MerkleConfig
from .hash_utils import HashAlgorithm
from .ibdata_constants import DEFAULT_MERKLE_FILENAME
from .merkle_tree import MerkleTree

__all__ = ["MerkleTree", "MerkleConfig", "HashAlgorithm", "DEFAULT_MERKLE_FILENAME"]
