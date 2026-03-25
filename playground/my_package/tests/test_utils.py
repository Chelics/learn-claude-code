"""Tests for utility functions.

This module contains unit tests for the utility functions in my_package.
"""

import unittest

from my_package import utils


class TestUtils(unittest.TestCase):
    """Test cases for the utils module."""

    def test_name(self) -> None:
        """Test that the name function returns the correct package name."""
        result = utils.name()
        self.assertEqual(result, "my_package")

    def test_greet(self) -> None:
        """Test that the greet function generates the correct message."""
        result = utils.greet("Alice")
        self.assertEqual(result, "Hello, Alice!")

    def test_add(self) -> None:
        """Test that the add function correctly adds two numbers."""
        self.assertEqual(utils.add(2, 3), 5)
        self.assertEqual(utils.add(-1, 1), 0)
        self.assertEqual(utils.add(0, 0), 0)

    def test_multiply(self) -> None:
        """Test that the multiply function correctly multiplies two numbers."""
        self.assertEqual(utils.multiply(2, 3), 6)
        self.assertEqual(utils.multiply(-2, 3), -6)
        self.assertEqual(utils.multiply(0, 5), 0)


if __name__ == "__main__":
    unittest.main()
