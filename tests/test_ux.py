import unittest
import sys
import os
import subprocess
import re
from unittest.mock import MagicMock, patch

# Check for real dependencies for subprocess tests
import importlib.util
try:
    HAS_PYGIT2 = importlib.util.find_spec("pygit2") is not None
except ValueError:
    HAS_PYGIT2 = False

try:
    HAS_RICH = importlib.util.find_spec("rich") is not None
except ValueError:
    HAS_RICH = False

# Mock pygit2 and rich before import if not present
if "pygit2" not in sys.modules:
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules:
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

# Custom MockPanel to handle constructor arguments correctly
class MockPanel(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        # Consume args/kwargs to verify content
        if "title" in kwargs:
            self.title = kwargs["title"]
        if args:
            self.renderable = args[0]


class TestUX(unittest.TestCase):
    @unittest.skipUnless(HAS_PYGIT2 and HAS_RICH, "pygit2 or rich not installed")
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
        # Patch Panel to use our MockPanel so we can verify attributes
        with patch("bastardkb_build_releases.Panel", MockPanel):
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

            # Verify it is our MockPanel
            self.assertIsInstance(args[0], MockPanel)
            # Note: rich markup might be in the title, e.g. [bold green]Success[/bold green]
            self.assertIn("Success", args[0].title)

            # Test Failure Case
            reporter.print_summary(8, 10)
            args, _ = reporter.console.print.call_args
            self.assertIsInstance(args[0], MockPanel)
            self.assertIn("Build Completed with Errors", args[0].title)

if __name__ == '__main__':
    unittest.main()
