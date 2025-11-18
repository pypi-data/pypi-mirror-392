"""Integration test for large file handling with CLI.

This test verifies that the CLI correctly processes directories with large files.
Setup: Creates a target directory structure with randomly generated large files.
"""

import os
import shutil
from pathlib import Path

import pytest
from ibdata_pymerkle import DEFAULT_MERKLE_FILENAME


@pytest.fixture
def test_environment():
    """Set up test environment with target directory and large files."""
    # Get project root by going up from src/test/python
    project_root = Path(__file__).parent.parent.parent.parent
    target_dir = project_root / "target"

    # If target directory exists, discover existing values
    if target_dir.exists():
        target_data = target_dir / "data"
        folder3 = target_data / "folder3"
        large_file_path = folder3 / "file3.1"

        # Discover existing file size
        if large_file_path.exists():
            file_size = large_file_path.stat().st_size
        else:
            # If no file exists, create one
            folder3.mkdir(parents=True, exist_ok=True)
            min_size = 24 * 1024 * 1024  # 24MB
            max_size = 88 * 1024 * 1024  # 88MB
            import random

            file_size = random.randint(min_size, max_size)
            with open(large_file_path, "wb") as f:
                remaining = file_size
                chunk_size = 1024 * 1024  # 1MB chunks
                while remaining > 0:
                    to_write = min(chunk_size, remaining)
                    f.write(os.urandom(to_write))
                    remaining -= to_write

        yield {
            "target_dir": target_dir,
            "target_data": target_data,
            "large_file": large_file_path,
            "file_size": file_size,
            "project_root": project_root,
        }
        return

    # Create target directory structure
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy src/test/resources/data to target/data
    source_data = project_root / "src" / "test" / "resources" / "data"
    target_data = target_dir / "data"

    if source_data.exists():
        shutil.copytree(source_data, target_data)
    else:
        pytest.fail("src/test/resources/data directory does not exist")

    # Create target/folder3 directory
    folder3 = target_data / "folder3"
    folder3.mkdir(parents=True, exist_ok=True)

    # Generate random file size between 4MB and 50MB
    min_size = 24 * 1024 * 1024  # 24MB
    max_size = 88 * 1024 * 1024  # 88MB
    import random

    file_size = random.randint(min_size, max_size)
    large_file_path = folder3 / "file3.1"

    # Create large file with random bytes
    with open(large_file_path, "wb") as f:
        remaining = file_size
        chunk_size = 1024 * 1024  # 1MB chunks
        while remaining > 0:
            to_write = min(chunk_size, remaining)
            f.write(os.urandom(to_write))
            remaining -= to_write

    yield {
        "target_dir": target_dir,
        "target_data": target_data,
        "large_file": large_file_path,
        "file_size": file_size,
        "project_root": project_root,
    }

    # # Cleanup after test
    # if target_dir.exists():
    #     shutil.rmtree(target_dir)


def test_cli_against_large_file_directory(test_environment):
    """Test CLI command against target/data directory with large files."""
    from ibdata_pymerkle.cli import main

    target_data = test_environment["target_data"]
    large_file = test_environment["large_file"]
    file_size = test_environment["file_size"]

    # Verify setup
    assert target_data.exists(), "target/data directory should exist"
    assert large_file.exists(), "Large file should be created"
    assert (
        large_file.stat().st_size == file_size
    ), f"File size mismatch: expected {file_size}, got {large_file.stat().st_size}"

    # Verify target/data has content
    data_files = list(target_data.glob("**/*"))
    assert len(data_files) > 0, "target/data should have files"

    # Run CLI command directly via Python API
    try:
        exit_code = main([str(target_data)])
        assert exit_code == 0, f"CLI command failed with exit code {exit_code}"
    except Exception as e:
        pytest.fail(f"CLI command failed with exception: {str(e)}")


def test_large_file_integrity(test_environment):
    """Verify large file integrity and proper handling."""
    large_file = test_environment["large_file"]
    file_size = test_environment["file_size"]

    # Verify file exists and has correct size
    assert large_file.exists()
    actual_size = large_file.stat().st_size
    assert (
        actual_size == file_size
    ), f"File size mismatch: expected {file_size}, got {actual_size}"

    # Verify file is readable
    with open(large_file, "rb") as f:
        content = f.read()
        assert len(content) == file_size


def test_cli_against_directory_ignoring_large_file(test_environment):
    """Test CLI command against target directory while ignoring large file."""
    from ibdata_pymerkle.cli import main

    target_dir = test_environment["target_dir"]
    large_file = test_environment["large_file"]

    # Verify large file exists before exclusion test
    assert large_file.exists(), "Large file should exist"

    # Run CLI command with exclude pattern to ignore large file
    large_file_name = large_file.name
    try:
        exit_code = main(
            [
                str(target_dir),
                "--exclude-patterns",
                large_file_name,
            ]
        )
        assert (
            exit_code == 0
        ), f"CLI command with exclusion failed with exit code {exit_code}"
    except Exception as e:
        pytest.fail(f"CLI command with exclusion failed: {str(e)}")


def test_target_directory_structure(test_environment):
    """Verify complete target directory structure."""
    target_dir = test_environment["target_dir"]
    target_data = test_environment["target_data"]
    folder3 = target_data / "folder3"
    large_file = test_environment["large_file"]

    # Check directory structure
    assert target_dir.exists()
    assert target_data.exists()
    assert folder3.exists()
    assert large_file.exists()

    # Verify directory hierarchy
    assert target_data.parent == target_dir
    assert large_file.parent == folder3


def test_merkle_file_idempotent_generated_at(test_environment):
    """Test that running CLI twice preserves generated_at timestamp."""
    import json

    from ibdata_pymerkle.cli import main

    target_data = test_environment["target_data"]

    # First run - generate merkle files
    exit_code = main([str(target_data)])
    assert exit_code == 0, "First CLI run should succeed"

    # Read first merkle file
    merkle_file = target_data / DEFAULT_MERKLE_FILENAME
    with open(merkle_file) as f:
        first_data = json.load(f)
    first_generated_at = first_data["generated_at"]

    # Wait a moment to ensure time difference if timestamp wasn't preserved
    import time

    time.sleep(0.1)

    # Second run - should reuse existing merkle file's generated_at
    exit_code = main([str(target_data)])
    assert exit_code == 0, "Second CLI run should succeed"

    # Read second merkle file
    with open(merkle_file) as f:
        second_data = json.load(f)
    second_generated_at = second_data["generated_at"]

    # Verify generated_at was preserved
    assert first_generated_at == second_generated_at, (
        f"generated_at should be preserved: "
        f"{first_generated_at} != {second_generated_at}"
    )

    # Verify all other data is identical (ignoring generated_at)
    first_data_copy = first_data.copy()
    second_data_copy = second_data.copy()
    first_data_copy.pop("generated_at", None)
    second_data_copy.pop("generated_at", None)

    assert (
        first_data_copy == second_data_copy
    ), "Merkle data should be identical except for generated_at"


def test_hash_file_sparse_with_custom_parameters(test_environment):
    """Test HashUtils.hash_file_sparse with custom parameters."""
    from ibdata_pymerkle.hash_utils import HashAlgorithm, HashUtils

    large_file = test_environment["large_file"]
    file_size = test_environment["file_size"]

    # Verify large file exists and is larger than threshold
    assert large_file.exists(), "Large file should exist"
    assert file_size > 10240, "File should be larger than threshold for sparse hashing"

    # Initialize HashUtils with SHA256
    hash_utils = HashUtils(HashAlgorithm.SHA256)

    # Test parameters
    chunk_size = 8192
    threshold_size = 10240
    sample_divisor = 5

    # Calculate sparse hash
    sparse_hash = hash_utils.hash_file_sparse(
        large_file,
        chunk_size=chunk_size,
        threshold_size=threshold_size,
        sample_divisor=sample_divisor,
    )

    # Verify hash is returned (should end with *)
    assert sparse_hash, "Hash should be returned"
    assert sparse_hash.endswith("*"), "Sparse hash should end with '*'"
    assert len(sparse_hash) > 1, "Hash should be non-empty before the asterisk"

    # Verify calling again with same parameters produces same result
    sparse_hash_2 = hash_utils.hash_file_sparse(
        large_file,
        chunk_size=chunk_size,
        threshold_size=threshold_size,
        sample_divisor=sample_divisor,
    )
    assert (
        sparse_hash == sparse_hash_2
    ), "Consecutive calls should produce identical hash"


def test_hash_file_sparse_fallback_with_invalid_chunk_size(test_environment):
    """Test HashUtils.hash_file_sparse fallback with invalid chunk size."""
    from ibdata_pymerkle.hash_utils import HashAlgorithm, HashUtils

    large_file = test_environment["large_file"]
    hash_utils = HashUtils(HashAlgorithm.SHA256)

    # Test with chunk_size <= 0, should fallback to full hash
    sparse_hash = hash_utils.hash_file_sparse(
        large_file, chunk_size=0, threshold_size=1024, sample_divisor=5
    )

    # Fallback hash should NOT end with '*'
    assert sparse_hash, "Hash should be returned"
    assert not sparse_hash.endswith(
        "*"
    ), "Fallback hash should not end with '*' (should use full hash)"


def test_hash_file_sparse_fallback_with_invalid_sample_divisor(test_environment):
    """Test HashUtils.hash_file_sparse fallback with invalid sample divisor."""
    from ibdata_pymerkle.hash_utils import HashAlgorithm, HashUtils

    large_file = test_environment["large_file"]
    hash_utils = HashUtils(HashAlgorithm.SHA256)

    # Test with sample_divisor <= 1, should fallback to full hash
    sparse_hash = hash_utils.hash_file_sparse(
        large_file, chunk_size=8192, threshold_size=1024, sample_divisor=1
    )

    # Fallback hash should NOT end with '*'
    assert sparse_hash, "Hash should be returned"
    assert not sparse_hash.endswith(
        "*"
    ), "Fallback hash should not end with '*' (should use full hash)"


def test_hash_file_sparse_fallback_file_smaller_than_threshold(test_environment):
    """Test HashUtils.hash_file_sparse fallback when file is smaller than threshold."""
    from ibdata_pymerkle.hash_utils import HashAlgorithm, HashUtils

    large_file = test_environment["large_file"]
    file_size = test_environment["file_size"]
    hash_utils = HashUtils(HashAlgorithm.SHA256)

    # Use threshold larger than file size, should fallback to full hash
    threshold_size = file_size + 1000
    sparse_hash = hash_utils.hash_file_sparse(
        large_file,
        chunk_size=8192,
        threshold_size=threshold_size,
        sample_divisor=5,
    )

    # Fallback hash should NOT end with '*'
    assert sparse_hash, "Hash should be returned"
    assert not sparse_hash.endswith(
        "*"
    ), "Fallback hash should not end with '*' (should use full hash)"


def test_hash_file_sparse_fallback_file_smaller_than_chunk_size(test_environment):
    """Test HashUtils.hash_file_sparse fallback when file is smaller than chunk size."""

    from ibdata_pymerkle.hash_utils import HashAlgorithm, HashUtils

    target_dir = test_environment["target_dir"]
    small_file = target_dir / "small_test_file.bin"

    # Create a small file smaller than chunk size
    with open(small_file, "wb") as f:
        f.write(b"small content")

    try:
        hash_utils = HashUtils(HashAlgorithm.SHA256)

        # File size is 13 bytes, chunk size is 8192, should fallback
        sparse_hash = hash_utils.hash_file_sparse(
            small_file, chunk_size=8192, threshold_size=1, sample_divisor=5
        )

        # Fallback hash should NOT end with '*'
        assert sparse_hash, "Hash should be returned"
        assert not sparse_hash.endswith(
            "*"
        ), "Fallback hash should not end with '*' (should use full hash)"
    finally:
        # Cleanup
        if small_file.exists():
            small_file.unlink()


def test_hash_file_sparse_fallback_empty_file(test_environment):
    """Test HashUtils.hash_file_sparse fallback with empty file."""
    from ibdata_pymerkle.hash_utils import HashAlgorithm, HashUtils

    target_dir = test_environment["target_dir"]
    empty_file = target_dir / "empty_test_file.bin"

    # Create an empty file
    empty_file.touch()

    try:
        hash_utils = HashUtils(HashAlgorithm.SHA256)

        # Empty file (size 0), should fallback to full hash
        sparse_hash = hash_utils.hash_file_sparse(
            empty_file, chunk_size=8192, threshold_size=1, sample_divisor=5
        )

        # Fallback hash should NOT end with '*'
        assert sparse_hash, "Hash should be returned"
        assert not sparse_hash.endswith(
            "*"
        ), "Fallback hash should not end with '*' (should use full hash)"
    finally:
        # Cleanup
        if empty_file.exists():
            empty_file.unlink()


def test_hash_file_sparse_fallback_threshold_equals_chunk_size(test_environment):
    """Test HashUtils.hash_file_sparse fallback when threshold <= chunk_size."""
    from ibdata_pymerkle.hash_utils import HashAlgorithm, HashUtils

    large_file = test_environment["large_file"]
    hash_utils = HashUtils(HashAlgorithm.SHA256)

    # threshold_size <= chunk_size should trigger fallback
    sparse_hash = hash_utils.hash_file_sparse(
        large_file, chunk_size=8192, threshold_size=8192, sample_divisor=5
    )

    # Fallback hash should NOT end with '*'
    assert sparse_hash, "Hash should be returned"
    assert not sparse_hash.endswith(
        "*"
    ), "Fallback hash should not end with '*' (should use full hash)"


def test_hash_file_sparse_nonexistent_file():
    """Test HashUtils.hash_file_sparse with nonexistent file."""
    from pathlib import Path

    from ibdata_pymerkle.hash_utils import HashAlgorithm, HashUtils

    hash_utils = HashUtils(HashAlgorithm.SHA256)
    nonexistent_file = Path("/nonexistent/path/to/file.bin")

    # Should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        hash_utils.hash_file_sparse(
            nonexistent_file,
            chunk_size=8192,
            threshold_size=10240,
            sample_divisor=5,
        )
