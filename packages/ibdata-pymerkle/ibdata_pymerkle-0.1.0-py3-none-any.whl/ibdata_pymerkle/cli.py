"""
Command-line interface for the merkle package.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .config import MerkleConfig
from .hash_utils import HashAlgorithm, HashUtils
from .merkle_tree import MerkleTree


def create_parser():
    """Create simple parser for direct usage."""
    parser = argparse.ArgumentParser(
        description="Generate and verify merkle trees for directories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    parser.add_argument(
        "path",
        type=Path,
        help="Path to file or directory to process",
    )

    parser.add_argument(
        "--algorithm",
        choices=["md5", "sha1", "sha256", "sha512"],
        default="sha256",
        help="Hash algorithm to use (default: sha256)",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=65536,
        help="Chunk size for file reading (default: 65536)",
    )

    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories",
    )

    parser.add_argument(
        "--include-metadata",
        action="store_true",
        help="Include file metadata in hash calculation",
    )

    parser.add_argument(
        "--no-subdirectory-merkles",
        action="store_true",
        help="Do not create merkle files for subdirectories",
    )

    parser.add_argument(
        "--max-file-size", type=int, help="Maximum file size to process (in bytes)"
    )

    parser.add_argument(
        "--include-patterns", nargs="*", help="File patterns to include (glob patterns)"
    )

    parser.add_argument(
        "--exclude-patterns", nargs="*", help="File patterns to exclude (glob patterns)"
    )

    parser.add_argument(
        "--packaging",
        choices=["zip", "tar", "tgz"],
        default="zip",
        help="Packaging format (default: zip)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate existing merkle tree instead of generating new one",
    )
    parser.add_argument(
        "--file",
        action="store_true",
        help="Treat the path as a file (hash only, no merkle tree)",
    )
    parser.add_argument("--config", type=Path, help="Configuration file path")

    parser.add_argument(
        "--generate-sparse-merkle",
        help="Generate sparse merkle tree",
        action="store_true",
    )

    parser.add_argument(
        "--sparse-merkle-threshold",
        type=int,
        help="Threshold size (in bytes) for sparse merkle tree generation",
    )
    return parser


def load_config_from_file(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is not valid JSON
    """
    try:
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in configuration file: {e}", e.doc, e.pos
        )


def create_config_from_args(args: argparse.Namespace) -> MerkleConfig:
    """
    Create MerkleConfig from command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        MerkleConfig instance
    """
    config_dict = {}

    # Load from file if specified
    if args.config:
        config_dict = load_config_from_file(args.config)

    # Override with command line arguments
    if args.algorithm:
        config_dict["algorithm"] = HashAlgorithm(args.algorithm)
    if hasattr(args, "chunk_size") and args.chunk_size:
        config_dict["chunk_size"] = args.chunk_size
    if args.include_hidden:
        config_dict["include_hidden"] = args.include_hidden
    if args.include_metadata:
        config_dict["include_metadata"] = args.include_metadata
    if hasattr(args, "no_subdirectory_merkles"):
        # Invert the logic: if --no-subdirectory-merkles is set,
        # create_subdirectory_merkles is False
        config_dict["create_subdirectory_merkles"] = not args.no_subdirectory_merkles
    if args.max_file_size:
        config_dict["max_file_size"] = args.max_file_size
    if args.include_patterns:
        config_dict["include_patterns"] = args.include_patterns
    if args.exclude_patterns:
        config_dict["exclude_patterns"] = args.exclude_patterns
    if args.packaging:
        config_dict["packaging"] = args.packaging
    if args.generate_sparse_merkle:
        config_dict["generate_sparse_merkle"] = args.generate_sparse_merkle
    if args.sparse_merkle_threshold:
        config_dict["sparse_merkle_threshold"] = args.sparse_merkle_threshold

    return MerkleConfig(**config_dict)


def validate_merkle_tree(
    directory: Path, config: Optional[MerkleConfig] = None, verbose: bool = False
) -> bool:
    """
    Validate an existing merkle tree.

    Args:
        directory: Directory containing the merkle tree
        config: Configuration to use (uses default if None)
        verbose: Enable verbose output

    Returns:
        True if validation passes, False otherwise
    """
    if config is None:
        config = MerkleConfig()

    hash_utils = HashUtils(config.algorithm)
    tree = MerkleTree(config, hash_utils)

    try:
        result = tree.verify_tree(directory)
        if verbose:
            print(f"Validation {'PASSED' if result else 'FAILED'}")
        return result  # type: ignore[return-value]
    except Exception as e:
        if verbose:
            print(f"Validation FAILED: {e}")
        return False


def generate_or_verify_merkle_tree(
    directory: Path,
    validate: bool = False,
    config: Optional[MerkleConfig] = None,
    verbose: bool = False,
) -> int:
    """
    Generate or verify a merkle tree based on the validate flag.

    Args:
        directory: Directory to process
        validate: Whether to validate (True) or generate (False)
        config: Configuration to use (uses default if None)
        verbose: Enable verbose output

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if config is None:
        config = MerkleConfig()

    try:
        if validate:
            success = validate_merkle_tree(directory, config, verbose)
            return 0 if success else 1
        else:
            hash_utils = HashUtils(config.algorithm)
            tree = MerkleTree(config, hash_utils)
            root_hash = tree.generate_tree(directory, verbose=verbose)
            if verbose:
                print(f"Generated merkle tree with root hash: {root_hash}")
            return 0
    except Exception as e:
        if verbose:
            print(f"Error: {e}")
        return 1


def hash_single_file(
    file_path: Path,
    config: Optional[MerkleConfig] = None,
    verbose: bool = False,
) -> int:
    """
    Hash a single file and report its hash.

    Args:
        file_path: File to hash
        config: Configuration to use (uses default if None)
        verbose: Enable verbose output

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if config is None:
        config = MerkleConfig()

    try:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        hash_utils = HashUtils(config.algorithm)
        file_hash = hash_utils.hash_file(file_path, config.chunk_size)

        if verbose:
            print(f"File: {file_path}")
            print(f"Algorithm: {config.algorithm.value}")
            print(f"Hash: {file_hash}")
        else:
            print(file_hash)

        return 0
    except Exception as e:
        if verbose:
            print(f"Error: {e}")
        return 1


def main(argv=None):
    """
    Main entry point for the CLI.

    Args:
        argv: Command line arguments (uses sys.argv if None)

    Returns:
        Exit code
    """
    parser = create_parser()

    try:
        args = parser.parse_args(argv)

        path = Path(args.path).resolve()

        # Check if path exists
        if not path.exists():
            parser.error(f"Path does not exist: {path}")

        config = create_config_from_args(args)

        # If --file flag is set, treat it as a file
        if args.file:
            if not path.is_file():
                parser.error(f"--file flag set but path is not a file: {path}")
            return hash_single_file(path, config, args.verbose)
        else:
            # Default behavior: treat as directory
            if not path.is_dir():
                parser.error(f"Path is not a directory: {path}")
            return generate_or_verify_merkle_tree(
                path, args.validate, config, args.verbose
            )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
