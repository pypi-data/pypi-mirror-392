# Merkle Tree Generator

A configurable SHA merkle tree generator for directory structures. This package creates `.merkle` files in each subdirectory containing SHA sums of files and subdirectories.

## Features

- **Configurable hash algorithms**: SHA1, SHA256, SHA512, MD5
- **Flexible file filtering**: Include/exclude patterns, file size limits, hidden files
- **Metadata support**: Optional inclusion of file metadata in hash calculation
- **Symbolic link handling**: Configurable following of symbolic links
- **Verification**: Verify existing merkle trees for integrity
- **CLI and Python API**: Use from command line or import as a library

## Installation

```bash
cd pkg/merkle
pip install -e .
```

## Command Line Usage

### Generate a merkle tree

```bash
# Basic usage with SHA256 (default)
merkle-tree /path/to/directory
# or explicitly use the generate command
merkle-tree generate /path/to/directory

# Use different hash algorithm
merkle-tree generate /path/to/directory --algorithm sha512

# Include hidden files and follow symlinks
merkle-tree generate /path/to/directory --include-hidden --follow-symlinks

# Exclude certain file patterns
merkle-tree generate /path/to/directory --exclude-pattern "*.tmp" --exclude-pattern "*.log"

# Include only specific file patterns
merkle-tree generate /path/to/directory --include-pattern "*.py" --include-pattern "*.md"

# Set maximum file size (1MB)
merkle-tree generate /path/to/directory --max-file-size 1048576

# Include file metadata in hash calculation
merkle-tree generate /path/to/directory --include-metadata

# Get only the root hash (useful for scripting)
merkle-tree generate /path/to/directory --output-root-hash
```

### Validate an existing merkle tree

```bash
# Validate merkle tree and exit with error code if invalid
merkle-tree validate /path/to/directory

# Validate with custom merkle filename
merkle-tree validate /path/to/directory --merkle-filename .custom_merkle

# Validate and output only success/failure for scripting
merkle-tree validate /path/to/directory --output-root-hash

# Validate with verbose output
merkle-tree validate /path/to/directory --verbose
```

### Verify an existing merkle tree (backward compatibility)

```bash
merkle-tree /path/to/directory --verify
```

### Use configuration file

```bash
merkle-tree /path/to/directory --config-file config.json
```

Example `config.json`:
```json
{
  "algorithm": "sha256",
  "merkle_filename": ".ibdata.merkle",
  "include_hidden": false,
  "follow_symlinks": false,
  "exclude_patterns": ["*.tmp", "*.log", "__pycache__"],
  "max_file_size": 10485760,
  "include_metadata": false,
  "chunk_size": 8192
}
```

## Python API Usage

```python
from pathlib import Path
from ibdata_pymerkle import MerkleTree, MerkleConfig, HashAlgorithm

# Basic usage with default configuration
merkle_tree = MerkleTree()
root_hash = merkle_tree.generate_tree("/path/to/directory")
print(f"Root hash: {root_hash}")

# Custom configuration
config = MerkleConfig(
    algorithm=HashAlgorithm.SHA512,
    include_hidden=True,
    exclude_patterns={"*.tmp", "*.log"},
    max_file_size=10 * 1024 * 1024,  # 10MB
    include_metadata=True
)

merkle_tree = MerkleTree(config)
root_hash = merkle_tree.generate_tree("/path/to/directory", verbose=True)

# Verify an existing tree
is_valid, errors = merkle_tree.verify_tree("/path/to/directory")
if not is_valid:
    for error in errors:
        print(f"Error: {error}")

# Get individual file/directory hashes
file_hash = merkle_tree.get_file_hash(Path("/path/to/file.txt"))
dir_hash = merkle_tree.get_directory_hash(Path("/path/to/subdirectory"))
```

## Merkle File Format

Each `.merkle` file contains JSON data with the following structure:

```json
{
  "directory": "/absolute/path/to/directory",
  "directory_hash": "abc123...",
  "algorithm": "sha256",
  "generated_at": "2023-10-16T12:34:56Z",
  "config": {
    "include_hidden": false,
    "follow_symlinks": false,
    "include_metadata": false,
    "algorithm": "sha256"
  },
  "files": {
    "file1.txt": "def456...",
    "file2.py": "789abc..."
  },
  "subdirectories": {
    "subdir1": "456def...",
    "subdir2": "abc789..."
  }
}
```

## Configuration Options

### MerkleConfig Parameters

- **algorithm**: Hash algorithm to use (`HashAlgorithm.SHA256`, `SHA512`, `SHA1`, `MD5`)
- **merkle_filename**: Name of merkle files (default: `.merkle`)
- **include_hidden**: Include hidden files/directories starting with `.` (default: `False`)
- **follow_symlinks**: Follow symbolic links (default: `False`)
- **exclude_patterns**: Set of regex patterns for files to exclude
- **include_patterns**: Set of regex patterns for files to include (if specified, only these are included)
- **max_file_size**: Maximum file size in bytes (default: `None` for no limit)
- **create_subdirectory_merkles**: Create `.merkle` files in subdirectories (default: `True`)
- **include_metadata**: Include file size and modification time in hash (default: `False`)
- **chunk_size**: Chunk size for reading files in bytes (default: `8192`)

## How It Works

1. **File Processing**: Each file's content is hashed using the specified algorithm
2. **Directory Processing**: Each directory's hash is computed from the combined hashes of all its files and subdirectories
3. **Merkle File Creation**: A `.merkle` JSON file is created in each directory containing:
   - Hashes of all files in the directory
   - Hashes of all subdirectories
   - The directory's own hash
   - Generation metadata and configuration
4. **Root Hash**: The root directory's hash represents the entire tree

## Use Cases

- **Data Integrity**: Verify that directory structures haven't changed
- **Backup Verification**: Ensure backup copies are identical to originals
- **Deployment Validation**: Verify that deployed code matches expected state
- **Change Detection**: Quickly identify which parts of a directory tree have changed
- **Content Addressing**: Use directory hashes as content identifiers

## Requirements

- Python 3.8+
- No external dependencies (uses only standard library)

## License

MIT License