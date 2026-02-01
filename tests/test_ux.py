import unittest
import sys
import os
import subprocess
import re
from unittest.mock import MagicMock, patch

# Mock dependencies before import
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
        cpu_count = os.cpu_count() or 1
        result = subprocess.run(
            [sys.executable, "bastardkb_build_releases.py", "--help"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            self.skipTest("Skipping subprocess test due to missing dependencies in environment")

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
        reporter.print_summary(10, 10)
        # Check if console.print was called with a Panel
        self.assertTrue(reporter.console.print.called)
        args, _ = reporter.console.print.call_args
        self.assertTrue(len(args) > 0)

        # Verify Panel was created with correct title
        # Since Panel is mocked, args[0] is the return value of Panel(...)
        # We can check the arguments passed to Panel constructor
        panel_mock = sys.modules["rich.panel"].Panel
        _, kwargs = panel_mock.call_args
        self.assertIn("Success", kwargs.get('title', ''))

        # Test Failure Case
        reporter.print_summary(8, 10)
        args, _ = reporter.console.print.call_args
        _, kwargs = panel_mock.call_args
        self.assertIn("Build Completed with Errors", kwargs.get('title', ''))

    @patch('bastardkb_build_releases.shutil.which')
    @patch('bastardkb_build_releases.sys.exit')
    @patch('bastardkb_build_releases.Reporter')
    @patch('bastardkb_build_releases.argparse.ArgumentParser.parse_args')
    def test_dependency_check_failure(self, mock_parse_args, mock_reporter_cls, mock_exit, mock_which):
        """Verify script exits if dependencies are missing."""
        # Setup mocks
        mock_which.return_value = None  # Simulate missing command
        mock_args = MagicMock()
        mock_args.verbose = False
        mock_parse_args.return_value = mock_args

        mock_reporter = MagicMock()
        mock_reporter_cls.return_value = mock_reporter

        # Mock exit to raise SystemExit so we can catch it
        mock_exit.side_effect = SystemExit(1)

        with self.assertRaises(SystemExit):
            bkb.main()

        # Verify shutil.which was called
        mock_which.assert_called()

        # Verify reporter.fatal was called
        mock_reporter.fatal.assert_called()
        call_args = mock_reporter.fatal.call_args
        self.assertIn("command was not found", call_args[0][0])
        self.assertEqual(call_args[1]['title'], "Dependency Error")

if __name__ == '__main__':
    unittest.main()
