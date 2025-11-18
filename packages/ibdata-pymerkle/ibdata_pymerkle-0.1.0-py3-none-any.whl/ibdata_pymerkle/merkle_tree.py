"""
Main merkle tree implementation.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import MerkleConfig
from .hash_utils import HashUtils

logger = logging.getLogger(__name__)


class MerkleTree:
    """
    Configurable SHA merkle tree generator for directory structures.

    Creates .merkle files in each subdirectory containing SHA sums of files
    and subdirectories. The hash of a directory is computed from the hashes
    of all its contents.
    """

    root_path: Optional[Path] = None  # Will be set during generate_tree
    config: MerkleConfig
    hash_utils: HashUtils
    _file_hashes: Dict[str, str]
    _dir_hashes: Dict[str, str]

    def __init__(self, config: MerkleConfig, hash_utils: HashUtils):
        """
        Initialize the merkle tree generator.

        Args:
            config: Configuration for the merkle tree
            hash_utils: Hash utilities to use
        """
        self.config = config
        self.hash_utils = hash_utils
        self._file_hashes = {}
        self._dir_hashes = {}

    def generate_tree(self, root_path: Path, verbose: bool = False) -> str:
        """
        Generate merkle tree for the given directory.

        Args:
            root_path: Root directory to process
            verbose: Enable verbose logging

        Returns:
            Root hash of the directory tree

        Raises:
            FileNotFoundError: If root_path doesn't exist
            NotADirectoryError: If root_path is not a directory
            PermissionError: If insufficient permissions
        """
        if verbose:
            logging.basicConfig(level=logging.INFO)

        self.root_path = Path(root_path).resolve()

        if not self.root_path.exists():
            raise FileNotFoundError(f"Path does not exist: {self.root_path}")

        if not self.root_path.is_dir():
            raise NotADirectoryError(
                f"generate_tree requires a directory, not a file: {self.root_path}"
            )

        logger.info(f"Generating merkle tree for: {self.root_path}")

        # Clear previous results
        self._file_hashes.clear()
        self._dir_hashes.clear()

        # Generate tree recursively
        root_hash = self._process_directory(self.root_path, is_root=True)

        logger.info(f"Merkle tree generation complete. Root hash: {root_hash}")

        return root_hash

    def _process_directory(self, dir_path: Path, is_root: bool = False) -> str:
        """
        Process a single directory and create its merkle file.

        Args:
            dir_path: Directory to process
            is_root: Whether this is the root directory

        Returns:
            Hash of the directory
        """
        logger.info(f"Processing directory: {dir_path}")

        # Set root_path if this is the root call and not already set
        if self.root_path is None:
            self.root_path = Path(dir_path).resolve()

        file_hashes = {}
        subdir_hashes = {}

        try:
            # Process all items in the directory
            for item in sorted(dir_path.iterdir()):
                if item.is_file():
                    if self.config.should_include_file(item):
                        try:
                            file_hash = self._process_file(item)
                            file_hashes[item.name] = file_hash
                            logger.debug(f"File {item.name}: {file_hash}")
                        except Exception as e:
                            logger.warning(f"Failed to process file {item}: {e}")

                elif item.is_dir():
                    if self.config.should_include_directory(item):
                        try:
                            subdir_hash = self._process_directory(item, is_root=False)
                            subdir_hashes[item.name] = subdir_hash
                            logger.debug(f"Directory {item.name}: {subdir_hash}")
                        except Exception as e:
                            logger.warning(f"Failed to process directory {item}: {e}")

        except PermissionError as e:
            logger.error(f"Permission denied accessing directory {dir_path}: {e}")
            raise

        # Calculate directory hash from all content hashes
        all_hashes = list(file_hashes.values()) + list(subdir_hashes.values())
        dir_hash = self.hash_utils.combine_hashes(all_hashes)

        # Create merkle file for root directory always, for subdirectories only if
        # configured
        if is_root or self.config.create_subdirectory_merkles:
            self._create_merkle_file(dir_path, file_hashes, subdir_hashes, dir_hash)

        # Store results
        self._dir_hashes[str(dir_path)] = dir_hash

        return dir_hash

    def _process_file(self, file_path: Path) -> str:
        """
        Process a single file and calculate its hash.

        Args:
            file_path: File to process

        Returns:
            Hash of the file
        """
        if self.config.include_metadata:
            # Include file metadata in hash calculation
            stat = file_path.stat()
            metadata = {"size": stat.st_size, "mtime": stat.st_mtime}
            if self.config.generate_sparse_merkle:
                metadata["sparse"] = True
                metadata["chunk_size"] = self.config.chunk_size
                metadata["sparse_merkle_threshold"] = (
                    self.config.sparse_merkle_threshold
                )
                metadata["sparse_merkle_sample_divisor"] = (
                    self.config.sparse_merkle_sample_divisor
                )

            # Hash file content and metadata together
            content_hash = (
                self.hash_utils.hash_file_sparse(
                    file_path,
                    self.config.chunk_size,
                    self.config.sparse_merkle_threshold,
                    self.config.sparse_merkle_sample_divisor,
                )
                if self.config.generate_sparse_merkle
                else self.hash_utils.hash_file(file_path, self.config.chunk_size)
            )
            metadata_str = json.dumps(metadata, sort_keys=True)
            combined = f"{content_hash}:{metadata_str}"
            file_hash = self.hash_utils.hash_string(combined)
        else:
            # Hash only file content
            file_hash = self.hash_utils.hash_file(file_path, self.config.chunk_size)

        self._file_hashes[str(file_path)] = file_hash
        return file_hash

    def _create_merkle_file(
        self,
        dir_path: Path,
        file_hashes: Dict[str, str],
        subdir_hashes: Dict[str, str],
        dir_hash: str,
    ) -> None:
        """
        Create a .merkle file in the directory.

        If the file already exists, preserve its generated_at timestamp.

        Args:
            dir_path: Directory path
            file_hashes: Dictionary of file name -> hash
            subdir_hashes: Dictionary of subdirectory name -> hash
            dir_hash: Hash of the directory
        """
        merkle_file_path = dir_path / self.config.merkle_filename

        # If merkle file exists, read its generated_at timestamp
        generated_at = datetime.now(timezone.utc).isoformat() + "Z"
        if merkle_file_path.exists():
            try:
                with open(merkle_file_path, encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if "generated_at" in existing_data:
                        generated_at = existing_data["generated_at"]
                        logger.debug(
                            f"Preserved generated_at from existing merkle file: "
                            f"{generated_at}"
                        )
            except Exception as e:
                logger.warning(
                    f"Failed to read existing merkle file {merkle_file_path}, "
                    f"will use current timestamp: {e}"
                )

        merkle_data = {
            "directory_hash": dir_hash,
            "algorithm": self.config.algorithm.value,
            "generated_at": generated_at,
            "config": {
                "include_hidden": self.config.include_hidden,
                "follow_symlinks": self.config.follow_symlinks,
                "include_metadata": self.config.include_metadata,
                "algorithm": self.config.algorithm.value,
            },
            "files": file_hashes,
            "subdirectories": subdir_hashes,
        }

        try:
            with open(merkle_file_path, "w", encoding="utf-8") as f:
                json.dump(merkle_data, f, indent=2, sort_keys=True)

            logger.debug(f"Created merkle file: {merkle_file_path}")

        except Exception as e:
            logger.error(f"Failed to create merkle file {merkle_file_path}: {e}")
            raise

    def verify_tree(self, root_path: Path) -> Tuple[bool, List[str]]:
        """
        Verify the integrity of an existing merkle tree.

        Args:
            root_path: Root directory to verify

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors: List[str] = []
        root_path = Path(root_path).resolve()

        try:
            is_valid = self._verify_directory(root_path, errors)
            return is_valid, errors
        except Exception as e:
            errors.append(f"Verification failed: {e}")
            return False, errors

    def _verify_directory(self, dir_path: Path, errors: List[str]) -> bool:
        """
        Verify a single directory's merkle file.

        Args:
            dir_path: Directory to verify
            errors: List to append errors to

        Returns:
            True if directory is valid, False otherwise
        """
        merkle_file_path = dir_path / self.config.merkle_filename

        if not merkle_file_path.exists():
            errors.append(f"Missing merkle file: {merkle_file_path}")
            return False

        try:
            with open(merkle_file_path, encoding="utf-8") as f:
                merkle_data = json.load(f)
        except Exception as e:
            errors.append(f"Failed to read merkle file {merkle_file_path}: {e}")
            return False

        # Verify file hashes
        stored_file_hashes = merkle_data.get("files", {})
        for filename, stored_hash in stored_file_hashes.items():
            file_path = dir_path / filename
            if not file_path.exists():
                errors.append(f"Missing file: {file_path}")
                continue

            try:
                current_hash = self._process_file(file_path)
                if current_hash != stored_hash:
                    errors.append(
                        f"Hash mismatch for file {file_path}: "
                        f"expected {stored_hash}, got {current_hash}"
                    )
            except Exception as e:
                errors.append(f"Failed to verify file {file_path}: {e}")

        # Verify subdirectory hashes
        stored_subdir_hashes = merkle_data.get("subdirectories", {})
        for dirname, stored_hash in stored_subdir_hashes.items():
            subdir_path = dir_path / dirname
            if not subdir_path.exists():
                errors.append(f"Missing subdirectory: {subdir_path}")
                continue

            if not self._verify_directory(subdir_path, errors):
                continue

            # Get current hash of subdirectory
            current_hash = self._process_directory(subdir_path)
            if current_hash != stored_hash:
                errors.append(
                    f"Hash mismatch for directory {subdir_path}: "
                    f"expected {stored_hash}, got {current_hash}"
                )

        return len(errors) == 0

    def get_file_hash(self, file_path: Path) -> Optional[str]:
        """Get the hash of a specific file from the last tree generation."""
        return self._file_hashes.get(str(file_path))

    def get_directory_hash(self, dir_path: Path) -> Optional[str]:
        """Get the hash of a specific directory from the last tree generation."""
        return self._dir_hashes.get(str(dir_path))
