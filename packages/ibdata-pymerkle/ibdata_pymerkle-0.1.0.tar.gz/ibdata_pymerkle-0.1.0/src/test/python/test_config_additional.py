import unittest
from pathlib import Path
from unittest import mock

from ibdata_pymerkle.config import MerkleConfig


class TestMerkleConfigAdditional(unittest.TestCase):
    def setUp(self):
        """Set up a default MerkleConfig instance for testing."""
        self.config = MerkleConfig()

    def test_hidden_file_exclusion(self):
        """Test that hidden files are excluded by default."""
        hidden_file = Path(".hidden_file.txt")
        self.assertFalse(self.config.should_include_file(hidden_file))

    def test_hidden_file_inclusion(self):
        """Test that hidden files are included when include_hidden is True."""
        self.config.include_hidden = True
        hidden_file = Path(".hidden_file.txt")
        self.assertTrue(self.config.should_include_file(hidden_file))

    def test_symbolic_link_exclusion(self):
        """Test that symbolic links are excluded by default."""
        self.config.follow_symlinks = False
        print(f"follow_symlinks set to: {self.config.follow_symlinks}")
        with mock.patch("pathlib.Path.is_symlink", return_value=True), mock.patch(
            "pathlib.Path.exists", return_value=True
        ):
            symlink = Path("symlink.txt")
            print(f"Mocked is_symlink: {symlink.is_symlink()}")
            print(f"Mocked exists: {symlink.exists()}")
            self.assertFalse(self.config.should_include_file(symlink))

    def test_symbolic_link_inclusion(self):
        """Test that symbolic links are included when follow_symlinks is True."""
        self.config.follow_symlinks = True
        with mock.patch("pathlib.Path.is_symlink", return_value=True), mock.patch(
            "pathlib.Path.exists", return_value=True
        ):
            symlink = Path("symlink.txt")
            print(f"Mocked is_symlink: {symlink.is_symlink()}")
            print(f"Mocked exists: {symlink.exists()}")
            self.assertTrue(self.config.should_include_file(symlink))

    def test_symbolic_link_logic(self):
        """Minimal test to isolate symbolic link logic."""
        self.config.follow_symlinks = False
        with mock.patch("pathlib.Path.is_symlink", return_value=True), mock.patch(
            "pathlib.Path.exists", return_value=True
        ):
            symlink = Path("symlink.txt")
            print(f"Mocked is_symlink return value: {symlink.is_symlink()}")
            print(f"Mocked exists return value: {symlink.exists()}")
            result = self.config.should_include_file(symlink)
            print(f"Test result for symbolic link: {result}")
            self.assertFalse(result)

    def test_symbolic_link_minimal(self):
        """Minimal test to isolate symbolic link logic."""
        self.config.follow_symlinks = False
        with mock.patch("pathlib.Path.is_symlink", return_value=True), mock.patch(
            "pathlib.Path.exists", return_value=True
        ):
            symlink = Path("symlink.txt")
            result = self.config.should_include_file(symlink)
            print(f"Minimal test result for symbolic link: {result}")
            self.assertFalse(result)

    def test_max_file_size(self):
        """Test that files exceeding max_file_size are excluded."""
        self.config.max_file_size = 1024  # 1 KB
        with mock.patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = unittest.mock.Mock(
                st_mode=0o100777
            )  # Regular file mode
            mock_stat.return_value.st_size = 2048  # 2 KB
            large_file = Path("large_file.txt")
            self.assertFalse(self.config.should_include_file(large_file))

    def test_file_size_within_limit(self):
        """Test that files within max_file_size are included."""
        self.config.max_file_size = 1024  # 1 KB
        with mock.patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = unittest.mock.Mock(
                st_mode=0o100777
            )  # Regular file mode
            mock_stat.return_value.st_size = 512  # 512 bytes
            small_file = Path("small_file.txt")
            self.assertTrue(self.config.should_include_file(small_file))


if __name__ == "__main__":
    unittest.main()
