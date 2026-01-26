import unittest
from unittest.mock import MagicMock, patch
import os
import sys
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestLogSanitization(unittest.TestCase):
    def test_log_file_sanitization(self):
        # Mock logging and tempfile to avoid side effects during Reporter init
        with patch('bastardkb_build_releases.logging'), \
             patch('bastardkb_build_releases.tempfile.mkdtemp', return_value='/tmp/mock'), \
             patch('bastardkb_build_releases.RotatingFileHandler'):

             reporter = bkb.Reporter(verbose=False)

             # Case 1: Safe name
             log1 = reporter.log_file("safe-name")
             self.assertEqual(log1.name, "safe-name.log")

             # Case 2: Unsafe name with slash - should be sanitized
             log2 = reporter.log_file("unsafe/name")
             # Current implementation fails this check, so we expect failure or we assert what we WANT
             self.assertEqual(log2.name, "unsafe_name.log")

             # Case 3: Unsafe name with ..
             log3 = reporter.log_file("../parent")
             self.assertEqual(log3.name, "___parent.log")

             # Case 4: Absolute path attempt
             log4 = reporter.log_file("/etc/passwd")
             self.assertEqual(log4.name, "_etc_passwd.log")

if __name__ == '__main__':
    unittest.main()
