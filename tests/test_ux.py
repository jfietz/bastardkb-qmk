import unittest
import sys
import os
import subprocess
import re
from unittest.mock import MagicMock, patch

# Mock dependencies if not already mocked
# We must mock before importing bastardkb_build_releases
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

class MockPanel(MagicMock):
    def __init__(self, *args, **kwargs):
        # Don't pass args to super.__init__ to avoid spec issue
        super().__init__()
        self.args = args
        self.kwargs = kwargs
        if 'title' in kwargs:
            self.title = kwargs['title']
        if args:
            self.renderable = args[0]

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    # Mock Panel class specifically since it might be used with isinstance
    sys.modules["rich.panel"].Panel = MockPanel
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestUX(unittest.TestCase):
    def test_parallel_default_help(self):
        """Verify the help text shows the correct default for parallel."""
        # This test relies on subprocess.run, which fails if dependencies are missing.
        # We simulate main() execution with mocked sys.argv.

        with patch('sys.argv', ["bastardkb_build_releases.py", "--help"]):
            # We need to mock sys.stdout/stderr to capture output
            import io
            captured_output = io.StringIO()
            with patch('sys.stdout', new=captured_output):
                 try:
                     with self.assertRaises(SystemExit) as cm:
                         bkb.main()
                     self.assertEqual(cm.exception.code, 0)
                 except Exception:
                     pass # SystemExit is expected

            output = captured_output.getvalue()
            cpu_count = os.cpu_count() or 1
            expected_pattern = fr"Parallel option to pass to qmk-compile\..*Defaults\s+to\s+number\s+of\s+CPUs\s+\({cpu_count}\)"
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

    def test_print_summary_dry_run_success(self):
        """Verify print_summary displays correct message for dry run success."""
        reporter = bkb.Reporter(verbose=False, dry_run=True)
        reporter.console = MagicMock()
        reporter.logging = MagicMock()

        # Reset Text mock
        bkb.Text.reset_mock()

        reporter.print_summary(10, 10)

        args, _ = reporter.console.print.call_args
        from rich.panel import Panel
        self.assertIsInstance(args[0], Panel)
        self.assertIn("Dry Run Success", args[0].title)

        # Verify Text was called with correct string
        found = False
        for call in bkb.Text.call_args_list:
            if call.args and "All firmwares simulated successfully!" in call.args[0]:
                found = True
                break
        self.assertTrue(found, "Success message not found in Text calls")

    def test_print_summary_dry_run_failure(self):
        """Verify print_summary displays correct message for dry run failure."""
        reporter = bkb.Reporter(verbose=False, dry_run=True)
        reporter.console = MagicMock()
        reporter.logging = MagicMock()

        # Reset Text mock
        bkb.Text.reset_mock()

        reporter.print_summary(8, 10)

        args, _ = reporter.console.print.call_args
        from rich.panel import Panel
        self.assertIsInstance(args[0], Panel)
        self.assertIn("Dry Run Completed with Errors", args[0].title)

        found = False
        for call in bkb.Text.call_args_list:
            if call.args and "8 simulated" in call.args[0]:
                found = True
                break
        self.assertTrue(found, "Failure message not found in Text calls")

if __name__ == '__main__':
    unittest.main()
