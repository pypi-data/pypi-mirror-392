import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Set

from .hash_utils import HashAlgorithm
from .ibdata_constants import DEFAULT_MERKLE_FILENAME


@dataclass
class MerkleConfig:
    """Configuration for merkle tree generation."""

    # Hash algorithm to use
    algorithm: HashAlgorithm = HashAlgorithm.SHA256

    # Output file name for merkle files
    merkle_filename: str = DEFAULT_MERKLE_FILENAME

    # Whether to include hidden files (starting with .)
    include_hidden: bool = False

    # Whether to follow symbolic links
    follow_symlinks: bool = False

    # File patterns to exclude (glob patterns)
    exclude_patterns: Set[str] = field(default_factory=set)

    # File patterns to include (glob patterns, if specified only these will be included)
    include_patterns: Set[str] = field(default_factory=set)

    # Maximum file size to process (in bytes, None for no limit)
    max_file_size: Optional[int] = None

    # Whether to create merkle files in subdirectories
    create_subdirectory_merkles: bool = True

    # Whether to include file metadata (size, mtime) in hash calculation
    include_metadata: bool = False

    # Chunk size for reading files
    chunk_size: int = 8192

    # Packaging format: zip, tar, or tgz
    packaging: str = "zip"

    generate_sparse_merkle: bool = False

    sparse_merkle_threshold: int = 1024 * 1024 * 1024  # 1 Gb

    sparse_merkle_sample_divisor: int = 10  # Read 10 chunks of the overall file

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Validate packaging format
        valid_packaging_formats = {"zip", "tar", "tgz"}
        if self.packaging not in valid_packaging_formats:
            raise ValueError(
                f"packaging must be one of {valid_packaging_formats}, "
                f"got {self.packaging}"
            )

        # Validate chunk size
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        # Convert patterns to sets if they're not already
        if not isinstance(self.exclude_patterns, set):
            self.exclude_patterns = set(self.exclude_patterns)
        if not isinstance(self.include_patterns, set):
            self.include_patterns = set(self.include_patterns)

        # Compile all patterns to regex objects for consistent behavior
        self._exclude_regexes = []
        self._include_regexes = []

        # Debugging: Log patterns before compilation
        print("Exclude patterns before compilation:", self.exclude_patterns)
        print("Include patterns before compilation:", self.include_patterns)

        # Convert all glob patterns to regex
        for pattern in self.exclude_patterns:
            regex_pattern = self._glob_to_regex(pattern)
            self._exclude_regexes.append(re.compile(regex_pattern))

        for pattern in self.include_patterns:
            regex_pattern = self._glob_to_regex(pattern)
            self._include_regexes.append(re.compile(regex_pattern))

        # Log compiled regex patterns for debugging
        print(
            "Compiled exclude regex patterns:",
            [regex.pattern for regex in self._exclude_regexes],
        )
        print(
            "Compiled include regex patterns:",
            [regex.pattern for regex in self._include_regexes],
        )

    def _glob_to_regex(self, pattern: str) -> str:
        """Convert a glob pattern to a regex pattern."""
        # Simple conversion - for more complex patterns, could use fnmatch.translate
        return fnmatch.translate(pattern)

    def should_include_file(self, file_path: Path) -> bool:
        """
        Check if a file should be included in the merkle tree.

        Args:
            file_path: Path to the file

        Returns:
            True if file should be included, False otherwise
        """
        filename = file_path.name

        print(f"Checking file: {file_path}")
        print(f"Exclude patterns: {self.exclude_patterns}")
        print(f"Include patterns: {self.include_patterns}")

        # Always exclude the merkle file itself to avoid recursion
        if filename == self.merkle_filename:
            print("Excluded: merkle file itself.")
            return False

        # Check hidden files
        if not self.include_hidden and filename.startswith("."):
            print("Excluded: hidden file.")
            return False

        # Check exclude regex patterns first
        for regex in self._exclude_regexes:
            if regex.match(filename):
                print(f"Excluded by pattern: {regex.pattern}")
                return False

        # Check include regex patterns
        if self.include_patterns:
            for regex in self._include_regexes:
                if regex.match(filename):
                    print(f"Included by pattern: {regex.pattern}")
                    return True
            print("No include pattern matched.")
            return False

        # For files that exist, check additional properties
        if file_path.exists():
            # Ensure symbolic links are excluded unless explicitly allowed
            if file_path.is_symlink():
                print(f"Checking symbolic link: {file_path}")
                print(f"follow_symlinks: {self.follow_symlinks}")
                if not self.follow_symlinks:
                    print(f"Excluded symbolic link: {file_path}")
                    return False
                print(f"Included symbolic link: {file_path}")
                return True

            # Debugging: Log file existence
            print(f"File exists: {file_path.exists()}")

            # Check file size if max_file_size is set
            if self.max_file_size is not None:
                file_size = file_path.stat().st_size
                print(f"File size: {file_size}, max_file_size: {self.max_file_size}")
                if file_size > self.max_file_size:
                    print(f"Excluded due to file size: {file_path}")
                    return False

        # Additional checks follow here
        print(f"Final decision for file: {file_path}")
        return True

    def should_include_directory(self, dir_path: Path) -> bool:
        """
        Check if a directory should be processed.

        Args:
            dir_path: Path to the directory

        Returns:
            True if directory should be processed, False otherwise
        """
        dirname = dir_path.name

        print(f"Exclude regex patterns: {self._exclude_regexes}")
        print(f"Directory name being checked: {dirname}")

        # Check hidden directories
        if not self.include_hidden and dirname.startswith("."):
            return False

        # For directories that exist, check additional properties
        if dir_path.exists():
            # Check symbolic links
            if not self.follow_symlinks and dir_path.is_symlink():
                return False

        # Check exclude regex patterns
        for regex in self._exclude_regexes:
            if regex.match(dirname):
                return False

        # If include patterns are specified, directory must match at least one
        if self.include_patterns:
            for regex in self._include_regexes:
                if regex.match(dirname):
                    return True
            return False

        return True

    def _compile_patterns(self):
        """Compile exclude and include patterns into regex objects."""
        self._exclude_regexes = [
            re.compile(self._glob_to_regex(pattern))
            for pattern in self.exclude_patterns
        ]
        self._include_regexes = [
            re.compile(self._glob_to_regex(pattern))
            for pattern in self.include_patterns
        ]

    def set_exclude_patterns(self, patterns: Set[str]):
        """Set exclude patterns and recompile regex."""
        self.exclude_patterns = patterns
        self._compile_patterns()

    def set_include_patterns(self, patterns: Set[str]):
        """Set include patterns and recompile regex."""
        self.include_patterns = patterns
        self._compile_patterns()
