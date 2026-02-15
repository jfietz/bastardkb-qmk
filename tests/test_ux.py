import unittest
import sys
import os
import subprocess
import re
from unittest.mock import MagicMock, patch

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
        from rich.panel import Panel
        self.assertIsInstance(args[0], Panel)
        # Note: rich markup might be in the title, e.g. [bold green]Success[/bold green]
        self.assertIn("Success", args[0].title)

        # Test Failure Case
        reporter.print_summary(8, 10)
        args, _ = reporter.console.print.call_args
        self.assertIsInstance(args[0], Panel)
        self.assertIn("Build Completed with Errors", args[0].title)

    def test_print_summary_content(self):
        """Verify print_summary content includes success rate and log path."""
        reporter = bkb.Reporter(verbose=False)
        reporter.console = MagicMock()
        reporter.logging = MagicMock()

        # Test Success Case
        reporter.print_summary(10, 10)
        args, _ = reporter.console.print.call_args
        panel = args[0]
        # Check if renderable is a Text object and check its content
        self.assertTrue(hasattr(panel.renderable, "plain"))
        self.assertIn("100.0% success rate", panel.renderable.plain)

        # Test Failure Case
        reporter.print_summary(8, 10)
        args, _ = reporter.console.print.call_args
        panel = args[0]
        # Text object has a 'plain' property that returns the unstyled text
        self.assertTrue(hasattr(panel.renderable, "plain"))
        self.assertIn("80.0%", panel.renderable.plain)
        # Verify log directory is present
        self.assertIn(reporter.log_dir, panel.renderable.plain)

if __name__ == '__main__':
    unittest.main()
