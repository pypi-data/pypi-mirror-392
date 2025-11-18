from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from ibdata_pymerkle.cli import (
    create_config_from_args,
    create_parser,
    generate_or_verify_merkle_tree,
    hash_single_file,
    main,
    validate_merkle_tree,
)
from ibdata_pymerkle.hash_utils import HashAlgorithm


def test_create_parser():
    parser = create_parser()
    assert parser is not None, "Parser should be created successfully."
    assert parser.description == "Generate and verify merkle trees for directories"
    assert any(
        arg.dest == "path" for arg in parser._actions
    ), "Parser should have 'path' positional argument."
    assert any(
        arg.dest == "file" for arg in parser._actions
    ), "Parser should have 'file' flag argument."
    assert any(
        arg.dest == "packaging" for arg in parser._actions
    ), "Parser should have 'packaging' argument."


def test_create_config_from_args():
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = HashAlgorithm.SHA256.value  # Use lowercase value
    mock_args.chunk_size = 1024
    mock_args.include_hidden = True
    mock_args.include_metadata = True
    # Flag not set, so create_subdirectory_merkles should be True
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = 1048576
    mock_args.include_patterns = ["*.txt"]
    mock_args.exclude_patterns = ["*.log"]
    mock_args.packaging = "tar"

    config = create_config_from_args(mock_args)

    assert config.algorithm == HashAlgorithm.SHA256  # Compare with enum
    assert config.chunk_size == 1024
    assert config.include_hidden is True
    assert config.include_metadata is True
    assert config.create_subdirectory_merkles is True
    assert config.max_file_size == 1048576
    assert config.include_patterns == {"*.txt"}  # Compare with a set
    assert config.exclude_patterns == {"*.log"}  # Compare with a set
    assert config.packaging == "tar"


def test_generate_or_verify_merkle_tree():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256  # Use valid enum

    with patch(
        "ibdata_pymerkle.cli.validate_merkle_tree", return_value=True
    ) as mock_validate:
        exit_code = generate_or_verify_merkle_tree(
            mock_directory, validate=True, config=mock_config, verbose=True
        )
        mock_validate.assert_called_once_with(mock_directory, mock_config, True)
        assert exit_code == 0

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.generate_tree.return_value = "mock_root_hash"

        exit_code = generate_or_verify_merkle_tree(
            mock_directory, validate=False, config=mock_config, verbose=True
        )
        mock_tree.generate_tree.assert_called_once_with(mock_directory, verbose=True)
        assert exit_code == 0


def test_validate_merkle_tree():
    mock_directory = Path("/mock/directory")
    mock_config = MagicMock()
    mock_config.algorithm = HashAlgorithm.SHA256  # Use valid enum

    with patch("ibdata_pymerkle.cli.MerkleTree") as mock_merkle_tree:
        mock_tree = mock_merkle_tree.return_value
        mock_tree.verify_tree.return_value = True

        result = validate_merkle_tree(mock_directory, config=mock_config, verbose=True)
        mock_tree.verify_tree.assert_called_once_with(mock_directory)
        assert result is True

        mock_tree.verify_tree.return_value = False
        result = validate_merkle_tree(mock_directory, config=mock_config)
        assert result is False


@patch("ibdata_pymerkle.cli.load_config_from_file", return_value={})
def test_main_with_validate(mock_load_config):
    mock_args = ["/mock/directory", "--validate"]

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser, patch(
        "ibdata_pymerkle.cli.generate_or_verify_merkle_tree", return_value=0
    ) as mock_generate_or_verify:
        # Mock the parser to return specific arguments
        mock_args_obj = MagicMock(
            path=Path("/mock/directory"),
            validate=True,
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
        )
        mock_parser.return_value.parse_args.return_value = mock_args_obj

        # Mock the configuration creation
        with patch(
            "ibdata_pymerkle.cli.create_config_from_args",
            return_value=MagicMock(validate=True),
        ), patch("pathlib.Path.exists", return_value=True), patch(
            "pathlib.Path.is_dir", return_value=True
        ):
            exit_code = main(mock_args)

        # Assert the function was called with the correct parameters
        mock_generate_or_verify.assert_called_once()

        # Assert the exit code is as expected
        assert exit_code == 0


@patch("ibdata_pymerkle.cli.load_config_from_file", return_value={})
def test_main_with_generate(mock_load_config):
    mock_args = ["/mock/directory"]

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser, patch(
        "ibdata_pymerkle.cli.generate_or_verify_merkle_tree", return_value=0
    ) as mock_generate_or_verify:
        mock_parser.return_value.parse_args.return_value = MagicMock(
            path=Path("/mock/directory"),
            validate=False,
            file=False,
            verbose=True,
            algorithm="sha256",
            chunk_size=65536,
            max_file_size=1048576,
            packaging="zip",
        )

        with patch("pathlib.Path.exists", return_value=True), patch(
            "pathlib.Path.is_dir", return_value=True
        ):
            exit_code = main(mock_args)

        mock_generate_or_verify.assert_called_once()
        assert exit_code == 0


def test_hash_single_file():
    """Test hashing a single file."""
    mock_file = Path("/mock/file.txt")
    mock_config = MagicMock()
    mock_config.algorithm.value = "sha256"
    mock_config.chunk_size = 8192

    with patch("ibdata_pymerkle.cli.HashUtils") as mock_hash_utils, patch(
        "builtins.print"
    ) as mock_print, patch("pathlib.Path.exists", return_value=True):
        mock_hasher = mock_hash_utils.return_value
        mock_hasher.hash_file.return_value = "abc123def456"

        exit_code = hash_single_file(mock_file, mock_config, verbose=False)

        assert exit_code == 0
        mock_hasher.hash_file.assert_called_once_with(mock_file, 8192)
        mock_print.assert_called()


@patch("ibdata_pymerkle.cli.generate_or_verify_merkle_tree", return_value=0)
def test_main_with_invalid_path(mock_generate_or_verify):
    mock_args = ["/invalid/path"]

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser:
        mock_parser.return_value.parse_args.return_value = MagicMock(
            path=Path("/invalid/path"), file=False, validate=False, verbose=False
        )

        with patch("pathlib.Path.exists", return_value=False):
            exit_code = main(mock_args)

            # Ensure the function exits with an error code
            assert exit_code == 1


@patch("ibdata_pymerkle.cli.generate_or_verify_merkle_tree", return_value=0)
def test_main_with_missing_file_argument(mock_generate_or_verify):
    mock_args = []  # No file argument provided

    with patch("ibdata_pymerkle.cli.create_parser") as mock_parser:
        mock_parser.return_value.parse_args.side_effect = SystemExit(
            2
        )  # Simulate argparse error

        with pytest.raises(SystemExit):
            main(mock_args)

        # Ensure the function does not call generate_or_verify_merkle_tree
        mock_generate_or_verify.assert_not_called()


def test_create_config_from_args_with_packaging_zip():
    """Test that packaging argument is correctly set to 'zip'."""
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = HashAlgorithm.SHA256.value
    mock_args.chunk_size = 1024
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = None
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "zip"

    config = create_config_from_args(mock_args)
    assert config.packaging == "zip"


def test_create_config_from_args_with_packaging_tar():
    """Test that packaging argument is correctly set to 'tar'."""
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = HashAlgorithm.SHA256.value
    mock_args.chunk_size = 1024
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = None
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "tar"

    config = create_config_from_args(mock_args)
    assert config.packaging == "tar"


def test_create_config_from_args_with_packaging_tgz():
    """Test that packaging argument is correctly set to 'tgz'."""
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = HashAlgorithm.SHA256.value
    mock_args.chunk_size = 1024
    mock_args.include_hidden = False
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = None
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "tgz"

    config = create_config_from_args(mock_args)
    assert config.packaging == "tgz"


def test_create_config_from_args_with_include_hidden():
    """Test that include_hidden argument is correctly set."""
    mock_args = MagicMock()
    mock_args.config = None
    mock_args.algorithm = HashAlgorithm.SHA256.value
    mock_args.chunk_size = 1024
    mock_args.include_hidden = True
    mock_args.include_metadata = False
    mock_args.no_subdirectory_merkles = False
    mock_args.max_file_size = None
    mock_args.include_patterns = None
    mock_args.exclude_patterns = None
    mock_args.packaging = "zip"

    config = create_config_from_args(mock_args)
    assert config.include_hidden is True
