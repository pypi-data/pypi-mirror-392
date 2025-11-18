"""Tests to cover remaining gaps in config.py and merkle_tree.py."""

import tempfile
from pathlib import Path

import pytest
from ibdata_pymerkle.config import MerkleConfig


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_config_include_patterns_directory_no_match():
    """Test directory that doesn't match include patterns is excluded."""
    config = MerkleConfig(include_patterns={"src*"})
    config._compile_patterns()

    # Directory that doesn't match include pattern should be False
    result = config.should_include_directory(Path("other"))
    # Since include patterns are set and it doesn't match, should return False
    assert result is False


def test_config_exclude_patterns_directory_match():
    """Test directory matching exclude pattern is excluded."""
    config = MerkleConfig(exclude_patterns={"__pycache__", ".git"})
    config._compile_patterns()

    # These should be excluded
    assert config.should_include_directory(Path("__pycache__")) is False
    assert config.should_include_directory(Path(".git")) is False


def test_config_exclude_file_matching():
    """Test file excluding with exclude patterns."""
    config = MerkleConfig(exclude_patterns={"*.pyc", "*.pyo"})
    config._compile_patterns()

    # Compiled files should be excluded
    assert config.should_include_file(Path("module.pyc")) is False
    assert config.should_include_file(Path("module.pyo")) is False


def test_config_include_file_no_match():
    """Test file not matching include patterns when they exist."""
    config = MerkleConfig(include_patterns={"*.py", "*.txt"})
    config._compile_patterns()

    # Non-matching file should be excluded
    assert config.should_include_file(Path("readme.md")) is False


def test_config_include_file_matching():
    """Test file matching include patterns."""
    config = MerkleConfig(include_patterns={"*.py"})
    config._compile_patterns()

    # Matching file should be included
    assert config.should_include_file(Path("module.py")) is True
