import unittest
import argparse
import sys
import os

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestCheckPositive(unittest.TestCase):
    def test_positive_integer(self):
        self.assertEqual(bkb.check_positive("1"), 1)
        self.assertEqual(bkb.check_positive("10"), 10)

    def test_zero_raises_error(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            bkb.check_positive("0")

    def test_negative_raises_error(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            bkb.check_positive("-1")

    def test_non_integer_raises_error(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            bkb.check_positive("abc")

if __name__ == '__main__':
    unittest.main()
