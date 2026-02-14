import unittest
import sys
import os
import subprocess
import re
from unittest.mock import MagicMock, patch

# Mock dependencies if not already mocked
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    # Mock Panel class specifically since it might be used with isinstance
    sys.modules["rich.panel"].Panel = MagicMock
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestUX(unittest.TestCase):
    def setUp(self):
        # Patch dependencies that interact with the filesystem
        self.mock_handler = patch('bastardkb_build_releases.RotatingFileHandler').start()
        # Ensure the mock handler has a level attribute
        self.mock_handler.return_value.level = 0

        self.mock_mkdir = patch('pathlib.Path.mkdir').start()
        self.mock_chmod = patch('os.chmod').start()
        self.mock_touch = patch('pathlib.Path.touch').start()
        self.mock_mkdtemp = patch('tempfile.mkdtemp', return_value='/tmp/mock_log_dir').start()

    def tearDown(self):
        patch.stopall()

    def test_parallel_default_help(self):
        """Verify the help text shows the correct default for parallel."""
        # check if dependencies are installed in the environment for subprocess
        try:
            subprocess.check_call([sys.executable, "-c", "import rich; import pygit2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            self.skipTest("Dependencies (rich, pygit2) missing, skipping integration test")

        cpu_count = os.cpu_count() or 1
        result = subprocess.run(
            [sys.executable, "bastardkb_build_releases.py", "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)

        # We expect the help output to show the default value matching the CPU count
        # The help text now includes "Defaults to number of CPUs (<value>)"
        # We use \s+ to account for potential line wrapping
        expected_pattern = fr"Parallel option to pass to qmk-compile\..*Defaults\s+to\s+number\s+of\s+CPUs\s+\({cpu_count}\)"

        # Using DOTALL to allow matching across lines if necessary, though argparse usually keeps it on one or wraps.
        self.assertRegex(result.stdout, re.compile(expected_pattern, re.DOTALL))

    def test_print_summary_exists(self):
        """Verify Reporter has print_summary method."""
        reporter = bkb.Reporter(verbose=False)
        self.assertTrue(hasattr(reporter, "print_summary"), "Reporter missing print_summary method")

    def test_print_summary_behavior(self):
        """Verify print_summary prints a Panel."""
        reporter = bkb.Reporter(verbose=False)
        reporter.console = MagicMock()
        reporter.logging = MagicMock()

        if not hasattr(reporter, "print_summary"):
            self.skipTest("print_summary not implemented yet")

        # Test Success Case
        with patch('bastardkb_build_releases.Panel') as MockPanel:
            reporter.print_summary(10, 10)
            self.assertTrue(MockPanel.called)
            # Verify Panel was initialized with expected title
            kwargs = MockPanel.call_args[1]
            self.assertIn("Success", kwargs.get('title', ''))

        # Test Failure Case
        with patch('bastardkb_build_releases.Panel') as MockPanel:
            reporter.print_summary(8, 10)
            self.assertTrue(MockPanel.called)
            # Verify Panel was initialized with expected title
            kwargs = MockPanel.call_args[1]
            self.assertIn("Build Completed with Errors", kwargs.get('title', ''))

if __name__ == '__main__':
    unittest.main()
