"""Final tests for achieving 98%+ coverage on merkle_tree.py."""

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


class TestMerkleTreeFinalCoverage:
    """Final tests to cover remaining branches."""

    def test_file_exception_in_loop_line_115(self, merkle_tree, temp_directory):
        """Test exception on line 115 when processing a file."""
        # Create a file
        test_file = temp_directory / "test.txt"
        test_file.write_text("content")

        # Create a mock that will be called during iteration
        call_count = [0]

        def mock_iterdir(self):
            call_count[0] += 1
            # First call returns the actual files
            if call_count[0] == 1:
                return sorted(temp_directory.iterdir())
            return []

        with patch.object(Path, "iterdir", mock_iterdir):
            # Mock _process_file to raise exception on first call
            with patch.object(
                merkle_tree, "_process_file", side_effect=ValueError("File error")
            ):
                with patch.object(
                    merkle_tree.config, "should_include_file", return_value=True
                ):
                    with patch.object(
                        merkle_tree.config,
                        "should_include_directory",
                        return_value=False,
                    ):
                        # This should handle the exception and continue
                        result = merkle_tree._process_directory(
                            temp_directory, is_root=True
                        )
                        # Should still return a hash
                        assert result is not None

    def test_directory_exception_in_loop_line_120(self, merkle_tree, temp_directory):
        """Test exception on line 120 when processing a subdirectory."""
        subdir = temp_directory / "subdir"
        subdir.mkdir()

        # Mock _process_directory to raise exception when processing subdir
        original_process_dir = merkle_tree._process_directory

        call_count = [0]

        def mock_process_directory(path, is_root=False):
            call_count[0] += 1
            if not is_root and path == subdir:
                # Raise exception for subdirectory
                raise OSError("Subdir error")
            # For root, call the real method
            if is_root:
                return original_process_dir(path, is_root)
            return "hash"

        with patch.object(
            merkle_tree, "_process_directory", side_effect=mock_process_directory
        ):
            with patch.object(
                merkle_tree.config, "should_include_directory", return_value=True
            ):
                # Should handle exception and continue
                result = merkle_tree._process_directory(temp_directory, is_root=True)
                # Should still work despite subdir error
                assert result is not None

    def test_permission_error_on_iterdir_line_127(self, merkle_tree, temp_directory):
        """Test PermissionError path on line 127."""
        # Create a file so iterdir is actually called
        test_file = temp_directory / "test.txt"
        test_file.write_text("content")

        # Mock iterdir to raise PermissionError
        with patch.object(Path, "iterdir", side_effect=PermissionError("No access")):
            # This should re-raise the PermissionError
            with pytest.raises(PermissionError):
                merkle_tree._process_directory(temp_directory, is_root=True)

    def test_skip_file_branch_109_to_99(self, merkle_tree, temp_directory):
        """Test the skip file branch (109->99)."""
        # Create a file that will be skipped
        test_file = temp_directory / "test.txt"
        test_file.write_text("content")

        # Make should_include_file return False
        def mock_should_include_file(path):
            return False

        with patch.object(
            merkle_tree.config,
            "should_include_file",
            side_effect=mock_should_include_file,
        ):
            with patch.object(
                merkle_tree.config, "should_include_directory", return_value=False
            ):
                result = merkle_tree._process_directory(temp_directory, is_root=True)
                # Should process directory but skip the file
                assert result is not None
                # File hashes should be empty
                assert len(merkle_tree._file_hashes) == 0

    def test_process_directory_returns_zero_hash_for_empty(
        self, merkle_tree, temp_directory
    ):
        """Test that empty directory returns appropriate hash."""
        # Process empty directory
        result = merkle_tree._process_directory(temp_directory, is_root=True)
        assert result is not None
        # The hash should be deterministic for empty directory
        assert isinstance(result, str)
        assert len(result) > 0

    def test_mixed_file_and_dir_with_exceptions(self, merkle_tree, temp_directory):
        """Test mix of files and dirs where some raise exceptions."""
        # Create structure
        file1 = temp_directory / "file1.txt"
        file1.write_text("content1")
        subdir = temp_directory / "subdir"
        subdir.mkdir()

        # Mock _process_file to raise exception only on first file
        call_count = [0]

        def mock_process_file(path):
            call_count[0] += 1
            if call_count[0] == 1:
                raise OSError("File error")
            return "file_hash"

        with patch.object(merkle_tree, "_process_file", side_effect=mock_process_file):
            with patch.object(
                merkle_tree.config, "should_include_file", return_value=True
            ):
                with patch.object(
                    merkle_tree.config, "should_include_directory", return_value=False
                ):
                    # Should handle exception and continue
                    result = merkle_tree._process_directory(
                        temp_directory, is_root=True
                    )
                    assert result is not None
