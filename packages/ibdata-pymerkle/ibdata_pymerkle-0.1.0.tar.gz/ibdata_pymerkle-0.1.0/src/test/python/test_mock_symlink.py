import unittest
from pathlib import Path
from unittest import mock


class TestMockSymlink(unittest.TestCase):
    def test_mock_is_symlink(self):
        """Test that Path.is_symlink() can be mocked correctly."""
        with mock.patch("pathlib.Path.is_symlink", return_value=True):
            symlink = Path("symlink.txt")
            self.assertTrue(symlink.is_symlink())


if __name__ == "__main__":
    unittest.main()
