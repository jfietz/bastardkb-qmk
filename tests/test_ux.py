import unittest
import sys
import os
import subprocess
import re
import io
from unittest.mock import MagicMock, patch

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before import
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()

# Mock Panel as a class so isinstance checks work
mock_panel_module = MagicMock()
class MockPanel:
    def __init__(self, *args, **kwargs):
        self.title = kwargs.get("title", "")
mock_panel_module.Panel = MockPanel
sys.modules["rich.panel"] = mock_panel_module

sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

import bastardkb_build_releases as bkb

class TestUX(unittest.TestCase):
    def test_parallel_default_help(self):
        """Verify the help text shows the correct default for parallel."""
        cpu_count = os.cpu_count() or 1

        # Use in-process execution to leverage mocks
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            # We mock sys.argv to simulate running with --help
            with patch.object(sys, 'argv', ["bastardkb_build_releases.py", "--help"]):
                with self.assertRaises(SystemExit) as cm:
                    bkb.main()
                self.assertEqual(cm.exception.code, 0)

        output = fake_out.getvalue()

        # We expect the help output to show the default value matching the CPU count
        # The help text now includes "Defaults to number of CPUs (<value>)"
        # We use \s+ to account for potential line wrapping
        expected_pattern = fr"Parallel option to pass to qmk-compile\..*Defaults\s+to\s+number\s+of\s+CPUs\s+\({cpu_count}\)"

        # Using DOTALL to allow matching across lines if necessary, though argparse usually keeps it on one or wraps.
        self.assertRegex(output, re.compile(expected_pattern, re.DOTALL))

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

if __name__ == '__main__':
    unittest.main()
