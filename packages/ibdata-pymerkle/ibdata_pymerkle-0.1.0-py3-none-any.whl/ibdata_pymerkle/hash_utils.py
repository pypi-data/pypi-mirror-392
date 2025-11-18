"""
Hash utility functions and algorithm configuration.
"""

import hashlib
from enum import Enum
from pathlib import Path


class HashAlgorithm(Enum):
    """Supported hash algorithms."""

    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"
    MD5 = "md5"


class HashUtils:
    """Utility class for hash operations."""

    def __init__(self, algorithm: HashAlgorithm = HashAlgorithm.SHA256):
        """
        Initialize hash utilities with specified algorithm.

        Args:
            algorithm: Hash algorithm to use (default: SHA256)
        """
        self.algorithm = algorithm
        self._hash_func = getattr(hashlib, algorithm.value)

    def hash_file(self, file_path: Path, chunk_size: int = 8192) -> str:
        """
        Calculate hash of a file.

        Args:
            file_path: Path to the file
            chunk_size: Size of chunks to read (default: 8192 bytes)

        Returns:
            Hexadecimal hash string

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
        """
        hash_obj = self._hash_func()

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    hash_obj.update(chunk)
        except (FileNotFoundError, PermissionError) as e:
            raise e

        return str(hash_obj.hexdigest())

    def hash_string(self, data: str, encoding: str = "utf-8") -> str:
        """
        Calculate hash of a string.

        Args:
            data: String data to hash
            encoding: Text encoding to use (default: utf-8)

        Returns:
            Hexadecimal hash string
        """
        return str(self._hash_func(data.encode(encoding)).hexdigest())

    def hash_bytes(self, data: bytes) -> str:
        """
        Calculate hash of bytes.

        Args:
            data: Byte data to hash

        Returns:
            Hexadecimal hash string
        """
        return str(self._hash_func(data).hexdigest())

    def combine_hashes(self, *hashes) -> str:
        """
        Combine multiple hashes into a single hash.

        Args:
            *hashes: Hash strings to combine (can be individual args or a list)

        Returns:
            Combined hash string
        """
        # Handle both combine_hashes(list) and combine_hashes(hash1, hash2, hash3)
        if len(hashes) == 1 and isinstance(hashes[0], (list, tuple)):
            hash_list = list(hashes[0])
        else:
            hash_list = list(hashes)

        if not hash_list:
            return str(self._hash_func(b"").hexdigest())

        # Combine with separators for deterministic results
        combined = "".join(hash_list)
        return self.hash_string(combined)

    def hash_file_sparse(
        self,
        file_path: Path,
        chunk_size: int = 8192,
        threshold_size: int = 1024 * 1024 * 1024,
        sample_divisor: int = 10,
    ) -> str:
        """
        Calculate a sparse hash of a file.  This will determine if a file is
        NOT identical to another file, provided it is called with the same
        chunk  and divisor size, but cannot determine if the two files
        are, in fact, identical.  This allows for faster hashing of very
        large files by sampling chunks throughout the file rather than
        reading the entire file.  The threshold_size parameter determines the
        minimum file size to apply sparse hashing; files smaller than this
        size will be fully hashed.  The threshold_size should be larger than
        the chunk_size, and ideally very significantly larger.

        This means that if you call hash_file_sparse on two different
        files with the same chunk, threshold, and divisor size, and
        get different hashes, the files are definitely different.

        However, if you get the same hash, the files may or may not be
        identical, as this is a sampled approach.

        Args:
            file_path: Path to the file
            chunk_size: Size of chunks to read (default: 8192 bytes)
            threshold_size: Minimum file size to apply sparse hashing
            sample_divisor: Number of chunks to sample for sparse hashing

        Returns:
            Hexadecimal hash string

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file cannot be read
        """
        hash_obj = self._hash_func()

        try:
            total_size = file_path.stat().st_size
            if (
                chunk_size <= 0
                or sample_divisor <= 1
                or total_size <= threshold_size
                or total_size < chunk_size
                or total_size == 0
                or threshold_size <= chunk_size
            ):
                return self.hash_file(file_path, chunk_size)  # Fallback to full hash
            interval_size = total_size // (total_size // sample_divisor)
            seek = [i * interval_size for i in range(0, sample_divisor)]
            seek.append(
                max(total_size - chunk_size, 0)
            )  # Ensure we read the end of the file

            with open(file_path, "rb") as f:
                for position in seek:
                    f.seek(position)
                    chunk = f.read(chunk_size)
                    hash_obj.update(chunk)

        except (FileNotFoundError, PermissionError) as e:
            raise e

        return str(hash_obj.hexdigest() + "*")
