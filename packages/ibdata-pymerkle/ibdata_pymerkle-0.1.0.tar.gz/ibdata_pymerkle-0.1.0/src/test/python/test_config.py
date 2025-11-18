import fnmatch
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from ibdata_pymerkle.config import MerkleConfig
from ibdata_pymerkle.hash_utils import HashAlgorithm
from ibdata_pymerkle.ibdata_constants import DEFAULT_MERKLE_FILENAME


class TestMerkleConfig(unittest.TestCase):
    def setUp(self):
        """Set up a default MerkleConfig instance for testing."""
        self.config = MerkleConfig()

    def test_default_values(self):
        """Test default configuration values."""
        self.assertEqual(self.config.algorithm, HashAlgorithm.SHA256)
        self.assertEqual(self.config.merkle_filename, DEFAULT_MERKLE_FILENAME)
        self.assertFalse(self.config.include_hidden)
        self.assertFalse(self.config.follow_symlinks)
        self.assertEqual(self.config.exclude_patterns, set())
        self.assertEqual(self.config.include_patterns, set())
        self.assertIsNone(self.config.max_file_size)
        self.assertTrue(self.config.create_subdirectory_merkles)
        self.assertFalse(self.config.include_metadata)
        self.assertEqual(self.config.chunk_size, 8192)
        self.assertEqual(self.config.packaging, "zip")

    def test_should_include_file(self):
        """Test the should_include_file method."""
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            file_path = Path(temp_file.name)
            self.assertTrue(self.config.should_include_file(file_path))

        hidden_file = Path(".hidden_file.txt")
        self.assertFalse(self.config.should_include_file(hidden_file))

    def test_should_include_directory(self):
        """Test the should_include_directory method."""
        dir_path = Path("test_dir")
        self.assertTrue(self.config.should_include_directory(dir_path))

        hidden_dir = Path(".hidden_dir")
        self.assertFalse(self.config.should_include_directory(hidden_dir))

    def test_invalid_chunk_size(self):
        """Test that invalid chunk sizes raise an error."""
        with self.assertRaises(ValueError):
            MerkleConfig(chunk_size=0)

    def test_exclude_patterns(self):
        """Test exclude patterns functionality."""
        self.config.set_exclude_patterns({"*.tmp", "*.log"})
        temp_file = Path("file.tmp")
        log_file = Path("file.log")
        normal_file = Path("file.txt")

        self.assertFalse(self.config.should_include_file(temp_file))
        self.assertFalse(self.config.should_include_file(log_file))
        self.assertTrue(self.config.should_include_file(normal_file))

    def test_include_patterns(self):
        """Test include patterns functionality."""
        self.config.set_include_patterns({"*.txt", "*.md"})
        txt_file = Path("file.txt")
        md_file = Path("file.md")
        log_file = Path("file.log")

        self.assertTrue(self.config.should_include_file(txt_file))
        self.assertTrue(self.config.should_include_file(md_file))
        self.assertFalse(self.config.should_include_file(log_file))

    def test_max_file_size(self):
        """Test max file size functionality."""
        self.config.max_file_size = 1024  # 1 KB
        small_file = Path("small_file.txt")
        large_file = Path("large_file.txt")

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(b"a" * 512)  # 512 bytes
            temp_file.flush()
            small_file = Path(temp_file.name)
            self.assertTrue(self.config.should_include_file(small_file))

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(b"a" * 2048)  # 2 KB
            temp_file.flush()
            large_file = Path(temp_file.name)
            self.assertFalse(self.config.should_include_file(large_file))

    def test_follow_symlinks(self):
        """Test symbolic link inclusion/exclusion based on follow_symlinks."""
        symlink = Path("symlink.txt")

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(b"test")
            temp_file.flush()
            target = Path(temp_file.name)

            # Create a symbolic link
            symlink.symlink_to(target)

            try:
                self.config.follow_symlinks = False
                self.assertFalse(self.config.should_include_file(symlink))

                self.config.follow_symlinks = True
                self.assertTrue(self.config.should_include_file(symlink))
            finally:
                if symlink.exists():
                    symlink.unlink()

    def test_include_hidden(self):
        """Test hidden file/directory inclusion/exclusion."""
        hidden_file = Path(".hidden_file.txt")
        hidden_dir = Path(".hidden_dir")

        self.config.include_hidden = False
        self.assertFalse(self.config.should_include_file(hidden_file))
        self.assertFalse(self.config.should_include_directory(hidden_dir))

        self.config.include_hidden = True
        self.assertTrue(self.config.should_include_file(hidden_file))
        self.assertTrue(self.config.should_include_directory(hidden_dir))

    def test_glob_to_regex(self):
        """Test conversion of glob patterns to regex patterns."""
        pattern = "*.txt"
        regex = self.config._glob_to_regex(pattern)
        self.assertEqual(regex, fnmatch.translate(pattern))

    def test_set_exclude_patterns(self):
        """Test setting and compiling exclude patterns."""
        patterns = {"*.tmp", "*.log"}
        self.config.set_exclude_patterns(patterns)
        self.assertEqual(self.config.exclude_patterns, patterns)

    def test_set_include_patterns(self):
        """Test setting and compiling include patterns."""
        patterns = {"*.txt", "*.md"}
        self.config.set_include_patterns(patterns)
        self.assertEqual(self.config.include_patterns, patterns)

    def test_post_init_validation(self):
        """Test validation and setup logic in __post_init__."""
        with self.assertRaises(ValueError):
            MerkleConfig(chunk_size=0)

        config = MerkleConfig(exclude_patterns=["*.tmp"], include_patterns=["*.txt"])
        self.assertIn("*.tmp", config.exclude_patterns)
        self.assertIn("*.txt", config.include_patterns)
        self.assertTrue(
            any(regex.match("file.tmp") for regex in config._exclude_regexes)
        )
        self.assertTrue(
            any(regex.match("file.txt") for regex in config._include_regexes)
        )

    def test_should_include_file_merkle_file(self):
        """Test that the merkle file itself is excluded."""
        merkle_file = Path(self.config.merkle_filename)
        self.assertFalse(self.config.should_include_file(merkle_file))

    def test_should_include_file_hidden_file(self):
        """Test that hidden files are excluded when include_hidden is False."""
        hidden_file = Path(".hidden_file.txt")
        self.config.include_hidden = False
        self.assertFalse(self.config.should_include_file(hidden_file))

    def test_should_include_directory_hidden_dir(self):
        """Test that hidden directories are excluded when include_hidden is False."""
        hidden_dir = Path(".hidden_dir")
        self.config.include_hidden = False
        self.assertFalse(self.config.should_include_directory(hidden_dir))

    def test_should_include_directory_symlink(self):
        """Test that symbolic links are excluded when follow_symlinks is False."""
        config = MerkleConfig(follow_symlinks=False)
        symlink_dir = MagicMock(spec=Path)
        symlink_dir.exists.return_value = True
        symlink_dir.is_symlink.return_value = True
        symlink_dir.name = "symlink_dir"

        result = config.should_include_directory(symlink_dir)
        assert (
            not result
        ), "Symbolic links should be excluded when follow_symlinks is False."

    def test_should_include_directory_exclude_pattern(self):
        """Test that directories matching exclude patterns are excluded."""
        config = MerkleConfig(exclude_patterns={"excluded_dir"})
        excluded_dir = MagicMock(spec=Path)
        excluded_dir.exists.return_value = True
        excluded_dir.is_symlink.return_value = False
        excluded_dir.name = "excluded_dir"

        result = config.should_include_directory(excluded_dir)
        assert not result, "Directories matching exclude patterns should be excluded."

    def test_should_include_directory_symlink_follow_true(self):
        """Test that symbolic links are included when follow_symlinks is True."""
        config = MerkleConfig(follow_symlinks=True)
        symlink_dir = MagicMock(spec=Path)
        symlink_dir.exists.return_value = True
        symlink_dir.is_symlink.return_value = True
        symlink_dir.name = "symlink_dir"

        result = config.should_include_directory(symlink_dir)
        assert result, "Symbolic links should be included when follow_symlinks is True."

    def test_should_include_directory_exclude_regex(self):
        """Test that directories matching exclude regex patterns are excluded."""
        config = MerkleConfig(exclude_patterns={"excluded*"})
        excluded_dir = MagicMock(spec=Path)
        excluded_dir.exists.return_value = True
        excluded_dir.is_symlink.return_value = False
        excluded_dir.name = "excluded_dir"

        result = config.should_include_directory(excluded_dir)
        assert (
            not result
        ), "Directories matching exclude regex patterns should be excluded."

    def test_should_include_directory_multiple_exclude_patterns(self):
        """Test that directories matching any exclude pattern are excluded."""
        config = MerkleConfig(exclude_patterns={"excluded*", "ignore*"})
        ignored_dir = MagicMock(spec=Path)
        ignored_dir.exists.return_value = True
        ignored_dir.is_symlink.return_value = False
        ignored_dir.name = "ignore_this_dir"

        result = config.should_include_directory(ignored_dir)
        assert (
            not result
        ), "Directories matching any exclude pattern should be excluded."

    def test_should_include_directory_exclude_regex_multiple_patterns(self):
        """Test that directories matching any exclude regex pattern are excluded."""
        config = MerkleConfig(exclude_patterns={"excluded*", "ignore*", "temp*"})
        temp_dir = MagicMock(spec=Path)
        temp_dir.exists.return_value = True
        temp_dir.is_symlink.return_value = False
        temp_dir.name = "temp_dir"

        result = config.should_include_directory(temp_dir)
        assert (
            not result
        ), "Directories matching any exclude regex pattern should be excluded."

    def test_packaging_default_value(self):
        """Test that packaging has default value of 'zip'."""
        config = MerkleConfig()
        self.assertEqual(config.packaging, "zip")

    def test_packaging_valid_values(self):
        """Test that all valid packaging values are accepted."""
        valid_values = ["zip", "tar", "tgz"]
        for value in valid_values:
            config = MerkleConfig(packaging=value)
            self.assertEqual(config.packaging, value)

    def test_packaging_invalid_value(self):
        """Test that invalid packaging values raise ValueError."""
        with self.assertRaises(ValueError) as context:
            MerkleConfig(packaging="invalid")
        self.assertIn("packaging must be one of", str(context.exception))


if __name__ == "__main__":
    unittest.main()
