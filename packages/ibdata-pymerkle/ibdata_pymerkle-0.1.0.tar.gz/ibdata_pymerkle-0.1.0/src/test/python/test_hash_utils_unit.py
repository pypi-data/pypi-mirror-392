import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from ibdata_pymerkle.hash_utils import HashUtils

INPUT_STRING_TEST = "test"
INPUT_STRING_TEST_HASH = (
    "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
)
INPUT_BYTES_TEST = b"test"
INPUT_BYTES_TEST_HASH = (
    "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
)
INPUT_STRING_TEST2 = "test2"
INPUT_BYTES_TEST2 = b"test2"
INPUT_BYTES_TEST2_HASH = (
    "60303ae22b998861bce3b28f33eec1be758a213c86c93c076dbe9f558c11c752"
)
INPUT_BYTES_EMPTY = b""
INPUT_BYTES_EMPTY_HASH = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)


class TestHashUtils(unittest.TestCase):
    def setUp(self):
        """Set up a HashUtils instance for testing."""
        self.hash_utils = HashUtils()

    def test_hash_string(self):
        """Test hashing a string."""
        expected_hash = self.hash_utils.hash_string(INPUT_STRING_TEST)
        self.assertIsInstance(expected_hash, str)
        self.assertEqual(len(expected_hash), 64)  # SHA256 hash length
        self.assertEqual(INPUT_STRING_TEST_HASH, expected_hash)

    def test_hash_bytes(self):
        """Test hashing bytes."""
        expected_hash = self.hash_utils.hash_bytes(INPUT_BYTES_TEST)
        self.assertIsInstance(expected_hash, str)
        self.assertEqual(len(expected_hash), 64)
        self.assertEqual(INPUT_BYTES_TEST_HASH, expected_hash)
        expected_hash_empty = self.hash_utils.hash_bytes(INPUT_BYTES_EMPTY)
        self.assertEqual(INPUT_BYTES_EMPTY_HASH, expected_hash_empty)
        expected_hash = self.hash_utils.hash_bytes(INPUT_BYTES_TEST2)
        self.assertIsInstance(expected_hash, str)
        self.assertEqual(len(expected_hash), 64)
        self.assertEqual(INPUT_BYTES_TEST2_HASH, expected_hash)

    def test_combine_hashes(self):
        """Test combining two hashes."""
        hash1 = self.hash_utils.hash_string(INPUT_STRING_TEST)
        hash2 = self.hash_utils.hash_string(INPUT_STRING_TEST2)

        combined_hash = self.hash_utils.combine_hashes(hash1, hash2)
        self.assertIsInstance(combined_hash, str)
        self.assertEqual(len(combined_hash), 64)

    def test_combine_hashes_list(self):
        """Test combining a list of hashes."""
        hash1 = self.hash_utils.hash_string(INPUT_STRING_TEST)
        hash2 = self.hash_utils.hash_string(INPUT_STRING_TEST2)

        combined_hash = self.hash_utils.combine_hashes([hash1, hash2])
        self.assertIsInstance(combined_hash, str)
        self.assertEqual(len(combined_hash), 64)
        self.assertEqual(
            "694299f8eb01a328732fb21f4163fbfaa8f60d5662f04f52ad33bec63953ec7f",
            combined_hash,
        )

    def test_hash_file_small(self):
        """Test hashing a small file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(INPUT_STRING_TEST)
            temp_path = Path(f.name)

        try:
            expected_hash = self.hash_utils.hash_string(INPUT_STRING_TEST)
            result = self.hash_utils.hash_file(temp_path)
            self.assertEqual(result, expected_hash)
        finally:
            temp_path.unlink()

    def test_hash_file_large(self):
        """Test hashing a large file with chunked reading."""
        large_data = "A" * 10000  # 10KB

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(large_data)
            temp_path = Path(f.name)

        try:
            expected_hash = hashlib.sha256(large_data.encode("utf-8")).hexdigest()
            result = self.hash_utils.hash_file(temp_path, chunk_size=1024)
            self.assertEqual(result, expected_hash)
        finally:
            temp_path.unlink()

    def test_hash_file_nonexistent(self):
        """Test hashing a nonexistent file raises FileNotFoundError."""
        nonexistent_path = Path("/nonexistent/file.txt")
        with self.assertRaises(FileNotFoundError):
            self.hash_utils.hash_file(nonexistent_path)

    @patch("builtins.open", new_callable=mock_open)
    def test_hash_file_permission_error(self, mock_file):
        """Test hashing a file with restricted permissions raises PermissionError.

        Also tests that files are accessible when permissions are correct.
        """
        test_path = Path("/test/file.txt")

        # Test 1: File is accessible and can be hashed successfully
        # Mock the read method to return data on first call,
        # then empty on subsequent calls
        mock_file.return_value.__enter__.return_value.read.side_effect = [
            INPUT_BYTES_TEST,
            b"",  # Signal end of file
        ]
        result = self.hash_utils.hash_file(test_path)
        self.assertEqual(result, INPUT_BYTES_TEST_HASH)
        mock_file.assert_called_with(test_path, "rb")

        # Test 2: File raises PermissionError when attempting to read
        mock_file.reset_mock()
        mock_file.side_effect = PermissionError("Permission denied")
        with self.assertRaises(PermissionError):
            self.hash_utils.hash_file(test_path)

    def test_combine_hashes_empty(self):
        """Test combining an empty list of hashes."""
        result = self.hash_utils.combine_hashes([])
        expected = hashlib.sha256(b"").hexdigest()
        self.assertEqual(result, expected)

    def test_combine_hashes_single(self):
        """Test combining a single hash."""
        hash1 = self.hash_utils.hash_string(INPUT_STRING_TEST)
        result = self.hash_utils.combine_hashes([hash1])
        # Note that the hash of any set of hashes is just the hash of the strings
        self.assertEqual(
            "7b3d979ca8330a94fa7e9e1b466d8b99e0bcdea1ec90596c0dcc8d7ef6b4300c", result
        )


if __name__ == "__main__":
    unittest.main()
