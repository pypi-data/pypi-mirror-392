"""Additional tests for cli.py to improve code coverage."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from ibdata_pymerkle.cli import (
    create_config_from_args,
    generate_or_verify_merkle_tree,
    hash_single_file,
    load_config_from_file,
    main,
    validate_merkle_tree,
)
from ibdata_pymerkle.hash_utils import HashAlgorithm


# Tests for load_config_from_file error handling
def test_load_config_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config_from_file(Path("/nonexistent/config.json"))


def test_load_config_from_file_invalid_json():
    import json
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{ invalid json")
        temp_path = f.name

    try:
        with pytest.raises(json.JSONDecodeError):
            load_config_from_file(Path(temp_path))
    finally:
        import os

        os.unlink(temp_path)


# Tests for validate_merkle_tree exception handling
def test_validate_merkle_tree_with_exception():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.verify_tree.side_effect = Exception("Tree verification failed")

        result = validate_merkle_tree(mock_directory, config=mock_config, verbose=False)
        assert result is False


def test_validate_merkle_tree_with_exception_verbose():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.verify_tree.side_effect = Exception("Tree verification failed")

        result = validate_merkle_tree(mock_directory, config=mock_config, verbose=True)
        assert result is False


def test_validate_merkle_tree_verbose_passed():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.verify_tree.return_value = True

        result = validate_merkle_tree(mock_directory, config=mock_config, verbose=False)
        assert result is True


# Tests for generate_or_verify_merkle_tree exception handling
def test_generate_or_verify_merkle_tree_validate_false_verbose():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.generate_tree.return_value = "mock_hash"

        exit_code = generate_or_verify_merkle_tree(
            mock_directory, validate=False, config=mock_config, verbose=False
        )
        assert exit_code == 0


def test_generate_or_verify_merkle_tree_exception_no_verbose():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.generate_tree.side_effect = Exception("Generation failed")

        exit_code = generate_or_verify_merkle_tree(
            mock_directory, validate=False, config=mock_config, verbose=False
        )
        assert exit_code == 1


def test_generate_or_verify_merkle_tree_exception_verbose():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.generate_tree.side_effect = Exception("Generation failed")

        exit_code = generate_or_verify_merkle_tree(
            mock_directory, validate=False, config=mock_config, verbose=True
        )
        assert exit_code == 1


def test_generate_or_verify_merkle_tree_validate_true_failure():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256

    with patch("ibdata_pymerkle.cli.validate_merkle_tree", return_value=False):
        exit_code = generate_or_verify_merkle_tree(
            mock_directory, validate=True, config=mock_config, verbose=False
        )
        assert exit_code == 1


# Tests for main function exception handling
@patch("ibdata_pymerkle.cli.load_config_from_file", return_value={})
def test_main_with_exception(mock_load_config):
    mock_args = ["/mock/directory"]

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser, patch(
        "pathlib.Path.exists", return_value=True
    ), patch("pathlib.Path.is_dir", return_value=True), patch(
        "ibdata_pymerkle.cli.create_config_from_args",
        side_effect=Exception("Config creation failed"),
    ):
        mock_parser.return_value.parse_args.return_value = MagicMock(
            path=Path("/mock/directory"),
            validate=False,
            file=False,
            verbose=False,
            algorithm="sha256",
            chunk_size=65536,
            max_file_size=1048576,
            include_hidden=False,
            include_metadata=False,
            no_subdirectory_merkles=False,
            include_patterns=None,
            exclude_patterns=None,
            config=None,
            packaging="zip",
        )

        exit_code = main(mock_args)
        assert exit_code == 1


# Tests for create_config_from_args with config file loading
@patch("ibdata_pymerkle.cli.load_config_from_file")
def test_create_config_from_args_with_config_file(mock_load_config):
    mock_load_config.return_value = {"algorithm": "sha512", "chunk_size": 8192}

    mock_args = MagicMock()
    mock_args.config = Path("/path/to/config.json")
    mock_args.algorithm = "sha256"
    mock_args.chunk_size = 1024
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = None
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "zip"

    config = create_config_from_args(mock_args)
    mock_load_config.assert_called_once_with(Path("/path/to/config.json"))
    assert config.algorithm == HashAlgorithm.SHA256


# Test for create_config_from_args with config file loading and packaging override
@patch("ibdata_pymerkle.cli.load_config_from_file")
def test_create_config_from_args_with_config_file_packaging_override(mock_load_config):
    mock_load_config.return_value = {"algorithm": "sha256", "packaging": "tar"}

    mock_args = MagicMock()
    mock_args.config = Path("/path/to/config.json")
    mock_args.algorithm = None
    mock_args.chunk_size = None
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = None
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "tgz"

    config = create_config_from_args(mock_args)
    # The CLI argument should override the config file
    assert config.packaging == "tgz"


# Test for create_config_from_args with None values
def test_create_config_from_args_with_none_values():
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = None
    mock_args.chunk_size = None
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = None
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "zip"

    config = create_config_from_args(mock_args)
    assert config is not None


# Test for main function with subcommand validate
@patch("ibdata_pymerkle.cli.load_config_from_file", return_value={})
def test_main_with_file_option_validate(mock_load_config):
    mock_args = ["/mock/directory", "--validate"]

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser, patch(
        "ibdata_pymerkle.cli.generate_or_verify_merkle_tree", return_value=0
    ) as mock_generate_or_verify, patch(
        "pathlib.Path.exists", return_value=True
    ), patch(
        "pathlib.Path.is_dir", return_value=True
    ):
        mock_args_obj = MagicMock(
            path=Path("/mock/directory"),
            file=False,
            verbose=False,
            validate=True,
            algorithm="sha256",
            chunk_size=65536,
            max_file_size=1048576,
            include_hidden=False,
            include_metadata=False,
            no_subdirectory_merkles=False,
            include_patterns=None,
            exclude_patterns=None,
            config=None,
            packaging="zip",
        )
        mock_parser.return_value.parse_args.return_value = mock_args_obj

        exit_code = main(mock_args)

        mock_generate_or_verify.assert_called_once()
        assert exit_code == 0


# Test for main function with file option generate
@patch("ibdata_pymerkle.cli.load_config_from_file", return_value={})
def test_main_with_file_option_generate(mock_load_config):
    mock_args = ["/mock/directory"]

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser, patch(
        "ibdata_pymerkle.cli.generate_or_verify_merkle_tree", return_value=0
    ) as mock_generate_or_verify, patch(
        "pathlib.Path.exists", return_value=True
    ), patch(
        "pathlib.Path.is_dir", return_value=True
    ):
        mock_args_obj = MagicMock(
            path=Path("/mock/directory"),
            file=False,
            verbose=False,
            validate=False,
            algorithm="sha256",
            chunk_size=65536,
            max_file_size=1048576,
            include_hidden=False,
            include_metadata=False,
            no_subdirectory_merkles=False,
            include_patterns=None,
            exclude_patterns=None,
            config=None,
            packaging="zip",
        )
        mock_parser.return_value.parse_args.return_value = mock_args_obj

        exit_code = main(mock_args)

        mock_generate_or_verify.assert_called_once()
        assert exit_code == 0


# Test for validate_merkle_tree with None config
def test_validate_merkle_tree_none_config():
    mock_directory = Path("/mock/directory")

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.verify_tree.return_value = True

        result = validate_merkle_tree(mock_directory, config=None, verbose=False)
        assert result is True


# Test for generate_or_verify_merkle_tree with None config
def test_generate_or_verify_merkle_tree_none_config():
    mock_directory = Path("/mock/directory")

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.generate_tree.return_value = "mock_hash"

        exit_code = generate_or_verify_merkle_tree(
            mock_directory, validate=False, config=None, verbose=False
        )
        assert exit_code == 0


# Test for generate_or_verify_merkle_tree validation failure with verbose
def test_generate_or_verify_merkle_tree_validate_exception_verbose():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256

    with patch(
        "ibdata_pymerkle.cli.validate_merkle_tree",
        side_effect=Exception("Validation error"),
    ):
        exit_code = generate_or_verify_merkle_tree(
            mock_directory, validate=True, config=mock_config, verbose=True
        )
        assert exit_code == 1


# Test for generate_or_verify_merkle_tree validation failure without verbose
def test_generate_or_verify_merkle_tree_validate_exception_no_verbose():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256

    with patch(
        "ibdata_pymerkle.cli.validate_merkle_tree",
        side_effect=Exception("Validation error"),
    ):
        exit_code = generate_or_verify_merkle_tree(
            mock_directory, validate=True, config=mock_config, verbose=False
        )
        assert exit_code == 1


# Test for create_config_from_args with max_file_size set
def test_create_config_from_args_with_max_file_size():
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = "sha256"
    mock_args.chunk_size = 65536
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = 5242880  # 5MB - This should trigger the branch
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "zip"

    config = create_config_from_args(mock_args)
    assert config.max_file_size == 5242880


# Test for create_config_from_args with max_file_size=0
def test_create_config_from_args_with_max_file_size_zero():
    """Test that max_file_size=0 is treated as falsy and not set."""
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = "sha256"
    mock_args.chunk_size = 65536
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = 0  # This should not be set
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "zip"

    config = create_config_from_args(mock_args)
    # max_file_size should use the default from MerkleConfig since 0 is falsy
    assert config is not None


# Test for create_config_from_args with all fields set
def test_create_config_from_args_all_fields():
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = "sha512"
    mock_args.chunk_size = 32768
    mock_args.include_hidden = True
    mock_args.include_metadata = True
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = 10485760  # 10MB
    mock_args.include_patterns = ["*.py", "*.txt"]
    mock_args.exclude_patterns = ["*.log", "*.tmp"]
    mock_args.packaging = "tar"

    config = create_config_from_args(mock_args)
    assert config.algorithm == HashAlgorithm.SHA512
    assert config.chunk_size == 32768
    assert config.include_hidden is True
    assert config.include_metadata is True
    assert config.create_subdirectory_merkles is True
    assert config.max_file_size == 10485760
    assert config.include_patterns == {"*.py", "*.txt"}
    assert config.exclude_patterns == {"*.log", "*.tmp"}
    assert config.packaging == "tar"


# Test for create_config_from_args with chunk_size=0
def test_create_config_from_args_with_chunk_size_zero():
    """Test that chunk_size=0 is treated as falsy and not set."""
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = "sha256"
    mock_args.chunk_size = 0  # This should not be set since it's falsy
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = None
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "zip"

    config = create_config_from_args(mock_args)
    assert config is not None


def test_hash_single_file_verbose():
    """Test hashing a single file with verbose output."""

    mock_file = Path("/mock/file.txt")
    mock_config = MagicMock()
    mock_config.algorithm.value = "sha256"
    mock_config.chunk_size = 8192

    with patch("ibdata_pymerkle.cli.HashUtils") as mock_hash_utils, patch(
        "builtins.print"
    ) as mock_print, patch("pathlib.Path.exists", return_value=True):
        mock_hasher = mock_hash_utils.return_value
        mock_hasher.hash_file.return_value = "abc123def456"

        exit_code = hash_single_file(mock_file, mock_config, verbose=True)

        assert exit_code == 0
        mock_hasher.hash_file.assert_called_once_with(mock_file, 8192)
        # Check that print was called with verbose output
        assert mock_print.call_count >= 3  # File, Algorithm, Hash


def test_hash_single_file_not_found():
    """Test hashing a file that doesn't exist."""

    mock_file = Path("/nonexistent/file.txt")
    mock_config = MagicMock()
    mock_config.algorithm.value = "sha256"
    mock_config.chunk_size = 8192

    with patch("pathlib.Path.exists", return_value=False):
        exit_code = hash_single_file(mock_file, mock_config, verbose=False)

        assert exit_code == 1


def test_main_with_single_file():
    """Test main function when processing a single file."""
    from ibdata_pymerkle.cli import main

    mock_file = Path("/mock/file.txt")

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser, patch(
        "ibdata_pymerkle.cli.hash_single_file", return_value=0
    ) as mock_hash_single_file, patch("pathlib.Path.exists", return_value=True), patch(
        "pathlib.Path.is_file", return_value=True
    ), patch(
        "pathlib.Path.is_dir", return_value=False
    ):
        mock_args_obj = MagicMock(
            path=mock_file,
            file=True,
            verbose=False,
            validate=False,
            algorithm="sha256",
            chunk_size=65536,
            max_file_size=1048576,
            include_hidden=False,
            include_metadata=False,
            no_subdirectory_merkles=False,
            include_patterns=None,
            exclude_patterns=None,
            config=None,
            packaging="zip",
        )
        mock_parser.return_value.parse_args.return_value = mock_args_obj

        exit_code = main([str(mock_file), "--file"])

        mock_hash_single_file.assert_called_once()
        assert exit_code == 0


def test_main_with_directory():
    """Test main function when processing a directory."""
    from ibdata_pymerkle.cli import main

    mock_dir = Path("/mock/directory")

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser, patch(
        "ibdata_pymerkle.cli.generate_or_verify_merkle_tree", return_value=0
    ) as mock_generate, patch("pathlib.Path.exists", return_value=True), patch(
        "pathlib.Path.is_file", return_value=False
    ), patch(
        "pathlib.Path.is_dir", return_value=True
    ):
        mock_args_obj = MagicMock(
            path=mock_dir,
            file=False,
            verbose=False,
            validate=False,
            algorithm="sha256",
            chunk_size=65536,
            max_file_size=1048576,
            include_hidden=False,
            include_metadata=False,
            no_subdirectory_merkles=False,
            include_patterns=None,
            exclude_patterns=None,
            config=None,
            packaging="zip",
        )
        mock_parser.return_value.parse_args.return_value = mock_args_obj

        exit_code = main([str(mock_dir)])

        mock_generate.assert_called_once()
        assert exit_code == 0


def test_hash_single_file_exception():
    """Test hash_single_file with exception handling."""

    mock_file = Path("/mock/file.txt")
    mock_config = MagicMock()
    mock_config.algorithm.value = "sha256"
    mock_config.chunk_size = 8192

    with patch("ibdata_pymerkle.cli.HashUtils") as mock_hash_utils, patch(
        "pathlib.Path.exists", return_value=True
    ), patch("builtins.print"):
        mock_hasher = mock_hash_utils.return_value
        mock_hasher.hash_file.side_effect = Exception("Hashing failed")

        exit_code = hash_single_file(mock_file, mock_config, verbose=False)

        assert exit_code == 1


def test_hash_single_file_exception_verbose():
    """Test hash_single_file with exception handling in verbose mode."""

    mock_file = Path("/mock/file.txt")
    mock_config = MagicMock()
    mock_config.algorithm.value = "sha256"
    mock_config.chunk_size = 8192

    with patch("ibdata_pymerkle.cli.HashUtils") as mock_hash_utils, patch(
        "pathlib.Path.exists", return_value=True
    ), patch("builtins.print") as mock_print:
        mock_hasher = mock_hash_utils.return_value
        mock_hasher.hash_file.side_effect = Exception("Hashing failed")

        exit_code = hash_single_file(mock_file, mock_config, verbose=True)

        assert exit_code == 1
        # Check that error was printed
        assert mock_print.call_count >= 1


def test_hash_single_file_with_none_config():
    """Test hash_single_file with None config to trigger MerkleConfig()."""

    mock_file = Path("/mock/file.txt")

    with patch("ibdata_pymerkle.cli.HashUtils") as mock_hash_utils, patch(
        "pathlib.Path.exists", return_value=True
    ), patch("builtins.print"):
        mock_hasher = mock_hash_utils.return_value
        mock_hasher.hash_file.return_value = "abc123def456"

        exit_code = hash_single_file(mock_file, config=None, verbose=False)

        assert exit_code == 0
        mock_hasher.hash_file.assert_called_once()


def test_main_with_neither_file_nor_directory():
    """Test main function when path is neither file nor directory."""
    from ibdata_pymerkle.cli import main

    mock_path = Path("/mock/path")

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser, patch(
        "pathlib.Path.exists", return_value=True
    ), patch("pathlib.Path.is_file", return_value=False), patch(
        "pathlib.Path.is_dir", return_value=False
    ):
        mock_args_obj = MagicMock(
            path=mock_path,
            file=False,
            verbose=False,
            validate=False,
            algorithm="sha256",
            chunk_size=65536,
            max_file_size=1048576,
            include_hidden=False,
            include_metadata=False,
            no_subdirectory_merkles=False,
            include_patterns=None,
            exclude_patterns=None,
            config=None,
            packaging="zip",
        )
        mock_parser.return_value.parse_args.return_value = mock_args_obj
        mock_parser.return_value.error.side_effect = SystemExit(2)

        with pytest.raises(SystemExit):
            main([str(mock_path)])


def test_main_exception_handling():
    """Test main function exception handling."""
    from ibdata_pymerkle.cli import main

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser, patch(
        "builtins.print"
    ):
        mock_parser.return_value.parse_args.side_effect = Exception("Parse error")

        exit_code = main(["--file", "/mock/path"])

        assert exit_code == 1


def test_create_config_from_args_with_no_subdirectory_merkles():
    """Test --no-subdirectory-merkles flag sets create_subdirectory_merkles to False."""
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = "sha256"
    mock_args.chunk_size = 65536
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = True
    mock_args.max_file_size = None
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "zip"

    config = create_config_from_args(mock_args)
    assert config.create_subdirectory_merkles is False
