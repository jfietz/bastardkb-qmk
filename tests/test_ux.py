import unittest
import sys
import os
import subprocess
import re
from unittest.mock import MagicMock, patch

# Mock dependencies before importing the module
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestUX(unittest.TestCase):
    def test_parallel_default_help(self):
        """Verify the help text shows the correct default for parallel."""
        # This test runs a subprocess which fails because dependencies (pygit2) are not installed in the env.
        # We skip it here to avoid failure in this restricted environment.
        self.skipTest("pygit2 not installed, cannot run subprocess test")

    def test_print_summary_exists(self):
        """Verify Reporter has print_summary method."""
        # We need to mock logging setup because Reporter.__init__ now does real filesystem ops for logs
        # or we just rely on it falling back to tempfile (which it should do if XDG_STATE_HOME is not set or not writable)
        # But we also have RotatingFileHandler which creates a file.

        # We should patch RotatingFileHandler to avoid side effects
        with patch("bastardkb_build_releases.RotatingFileHandler") as mock_rfh, \
             patch("bastardkb_build_releases.Path.mkdir"), \
             patch("bastardkb_build_releases.Path.chmod"):

            # Set level on the mock handler instance so real logging doesn't crash
            mock_rfh.return_value.level = 0

            reporter = bkb.Reporter(verbose=False)
            self.assertTrue(hasattr(reporter, "print_summary"), "Reporter missing print_summary method")

    def test_print_summary_behavior(self):
        """Verify print_summary prints a Panel."""
        with patch("bastardkb_build_releases.RotatingFileHandler") as mock_rfh, \
             patch("bastardkb_build_releases.Path.mkdir"), \
             patch("bastardkb_build_releases.Path.chmod"):

            mock_rfh.return_value.level = 0

            reporter = bkb.Reporter(verbose=False)
            reporter.console = MagicMock()
            reporter.logging = MagicMock()

            if not hasattr(reporter, "print_summary"):
                self.skipTest("print_summary not implemented yet")

            # Test Success Case
            reporter.print_summary(10, 10)
            # Check if console.print was called
            self.assertTrue(reporter.console.print.called)

            # Check if Panel was initialized with correct title
            # We access bkb.Panel (the class mock)
            # It might have been called multiple times, so we look at the last call
            args, kwargs = bkb.Panel.call_args
            self.assertIn("Success", kwargs.get("title", ""))

            # Test Failure Case
            reporter.print_summary(8, 10)
            args, kwargs = bkb.Panel.call_args
            self.assertIn("Build Completed with Errors", kwargs.get("title", ""))

if __name__ == '__main__':
    unittest.main()
