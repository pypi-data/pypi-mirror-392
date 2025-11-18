"""Focused tests for the last two uncovered branches."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from ibdata_pymerkle.config import MerkleConfig
from ibdata_pymerkle.hash_utils import HashAlgorithm, HashUtils
from ibdata_pymerkle.ibdata_constants import DEFAULT_MERKLE_FILENAME
from ibdata_pymerkle.merkle_tree import MerkleTree


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def merkle_config():
    """Create a default merkle config."""
    return MerkleConfig(
        algorithm=HashAlgorithm.SHA256,
        merkle_filename=DEFAULT_MERKLE_FILENAME,
        include_hidden=False,
        follow_symlinks=False,
        include_metadata=False,
    )


@pytest.fixture
def hash_utils():
    """Create hash utilities."""
    return HashUtils(HashAlgorithm.SHA256)


@pytest.fixture
def merkle_tree(merkle_config, hash_utils):
    """Create a merkle tree instance."""
    return MerkleTree(merkle_config, hash_utils)


def test_file_skipped_when_not_included_branch_109_to_99(merkle_tree, temp_directory):
    """Specifically test the skip file branch 109->99."""
    # Create a file
    test_file = temp_directory / "test.txt"
    test_file.write_text("content")

    # Mock should_include_file to return False to trigger skip
    def mock_include_file(path):
        # Skip this file
        return False

    # Also ensure directories are skipped
    with patch.object(
        merkle_tree.config, "should_include_file", side_effect=mock_include_file
    ):
        with patch.object(
            merkle_tree.config, "should_include_directory", return_value=False
        ):
            result = merkle_tree._process_directory(temp_directory, is_root=True)
            assert result is not None
            # File should not be processed (skipped)
            assert len(merkle_tree._file_hashes) == 0


def test_permission_error_reraise_branch_127_to_131(merkle_tree, temp_directory):
    """Specifically test the PermissionError re-raise path."""
    # Create a file so we know iterdir would be called
    test_file = temp_directory / "test.txt"
    test_file.write_text("content")

    # Mock iterdir to raise PermissionError on the root directory
    original_iterdir = Path.iterdir

    def mock_iterdir(self):
        if str(self) == str(temp_directory):
            raise PermissionError("Access denied to directory")
        return original_iterdir(self)

    with patch.object(Path, "iterdir", mock_iterdir):
        # Should re-raise PermissionError
        with pytest.raises(PermissionError):
            merkle_tree._process_directory(temp_directory, is_root=True)
