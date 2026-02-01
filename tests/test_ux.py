import unittest
import sys
import os
import subprocess
import re
from unittest.mock import MagicMock, patch

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to mock dependencies if they are missing to allow import
if "pygit2" not in sys.modules:
    sys.modules["pygit2"] = MagicMock()
if "rich" not in sys.modules:
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()
    sys.modules["rich.table"] = MagicMock()

import bastardkb_build_releases as bkb

class TestUX(unittest.TestCase):
    def test_parallel_default_help(self):
        """Verify the help text shows the correct default for parallel."""
        # This test runs in a subprocess, so it will fail if dependencies are missing in the environment.
        # We check if we can run it.
        try:
            subprocess.run([sys.executable, "-c", "import pygit2"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.skipTest("pygit2 not installed in environment")

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
        """Verify print_summary prints a Panel and Table."""
        reporter = bkb.Reporter(verbose=False)
        reporter.console = MagicMock()
        reporter.logging = MagicMock()

        if not hasattr(reporter, "print_summary"):
            self.skipTest("print_summary not implemented yet")

        # Mock Firmware object
        firmware = MagicMock()
        firmware.__str__.return_value = "kb/kmap"

        # Test Success Case
        # results = Sequence[tuple["Firmware", str, Optional[Path]]]
        results = [(firmware, "success", None)] * 10

        reporter.print_summary(results)

        # Check if console.print was called.
        # It should be called for the Panel and the Table.
        self.assertTrue(reporter.console.print.called)

        # Inspect calls
        # We need to see if a Panel with "Success" was printed.
        # Since we mocked rich.panel in sys.modules, bkb.Panel is a Mock class.
        # So when bkb instantiates Panel(...), it returns a Mock object.
        # We can check if that Mock object was passed to console.print.

        # This is tricky because bkb.Panel is the Mock class.
        # args[0] will be an instance of that Mock class.

        args_list = reporter.console.print.call_args_list
        found_success = False
        for call in args_list:
            arg = call[0][0]
            # Check if arg is a Panel (which is a Mock instance here)
            # We can check if it was created with "Success" title.
            # But we don't have reference to the specific instance creation easily unless we check how Panel was called.

            # Alternatively, since we know bkb.Panel is a Mock, we can check bkb.Panel.call_args_list
            pass

        # Let's check bkb.Panel calls
        # bkb.Panel is the mock class.
        self.assertTrue(bkb.Panel.called)

        # Find call with title="...Success..."
        success_panel_call = next((call for call in bkb.Panel.call_args_list if "Success" in str(call[1].get('title', ''))), None)
        self.assertIsNotNone(success_panel_call, "Panel not created with Success title")

        # Test Failure Case
        reporter.console.reset_mock()
        bkb.Panel.reset_mock()

        results = [(firmware, "success", None)] * 8 + [(firmware, "failure", "log.txt")] * 2
        reporter.print_summary(results)

        # Find call with title="...Build Completed with Errors..."
        failure_panel_call = next((call for call in bkb.Panel.call_args_list if "Build Completed with Errors" in str(call[1].get('title', ''))), None)
        self.assertIsNotNone(failure_panel_call, "Panel not created with Failure title")

        # Verify Table was also printed
        # bkb.Table is also a Mock
        self.assertTrue(bkb.Table.called)
        self.assertTrue(reporter.console.print.called)

if __name__ == '__main__':
    unittest.main()
