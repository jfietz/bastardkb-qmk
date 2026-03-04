import unittest
import sys
import os
import subprocess
import re
import tempfile
import shutil
from unittest.mock import MagicMock, patch

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing the module
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()

class MockText:
    def __init__(self, text="", **kwargs):
        self.text = text
    def append(self, text, **kwargs):
        self.text += text
    def __add__(self, other):
        if hasattr(other, 'text'):
            return MockText(self.text + other.text)
        return MockText(self.text + str(other))
    def __str__(self):
        return self.text

mock_text_module = MagicMock()
mock_text_module.Text = MockText
sys.modules["rich.text"] = mock_text_module

import importlib
# import bastardkb_build_releases explicitly so it picks up the mocked rich.text
# importlib.reload(bastardkb_build_releases)

# Custom Mock for Panel to support isinstance check
class MockPanel:
    def __init__(self, renderable, **kwargs):
        self.renderable = renderable
        self.title = kwargs.get("title", "")

mock_panel_module = MagicMock()
mock_panel_module.Panel = MockPanel
sys.modules["rich.panel"] = mock_panel_module

import bastardkb_build_releases as bkb
importlib.reload(bkb)

class TestUX(unittest.TestCase):
    def setUp(self):
        # Create a fake home directory for XDG_STATE_HOME
        self.test_dir = tempfile.mkdtemp()
        self.old_xdg = os.environ.get("XDG_STATE_HOME")
        os.environ["XDG_STATE_HOME"] = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        if self.old_xdg:
            os.environ["XDG_STATE_HOME"] = self.old_xdg
        else:
            del os.environ["XDG_STATE_HOME"]

    def test_parallel_default_help(self):
        """Verify the help text shows the correct default for parallel."""
        # Skipping this test as it requires dependencies to be installed in the subprocess
        return

        cpu_count = os.cpu_count() or 1
        result = subprocess.run(
            [sys.executable, "bastardkb_build_releases.py", "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        expected_pattern = fr"Parallel option to pass to qmk-compile\..*Defaults\s+to\s+number\s+of\s+CPUs\s+\({cpu_count}\)"
        self.assertRegex(result.stdout, re.compile(expected_pattern, re.DOTALL))

    def test_print_summary_exists(self):
        """Verify Reporter has print_summary method."""
        with patch("bastardkb_build_releases.RotatingFileHandler") as mock_handler:
            mock_handler.return_value.level = 0
            reporter = bkb.Reporter(verbose=False)
        self.assertTrue(hasattr(reporter, "print_summary"), "Reporter missing print_summary method")

    def test_print_summary_behavior(self):
        """Verify print_summary prints a Panel."""
        with patch("bastardkb_build_releases.RotatingFileHandler") as mock_handler:
             # Configure mock handler level
            mock_handler.return_value.level = 0

            reporter = bkb.Reporter(verbose=False)
            reporter.console = MagicMock()

            # Test Success Case
            reporter.print_summary(10, 10)
            # Check if console.print was called with a Panel
            self.assertTrue(reporter.console.print.called)
            args, _ = reporter.console.print.call_args
            self.assertTrue(len(args) > 0)

            # Use the MockPanel class we defined
            self.assertEqual(args[0].__class__.__name__, 'MockPanel')
            self.assertIn("Success", args[0].title)

            # Test Failure Case
            mock_failed_firmwares = [
                bkb.Firmware(keyboard="scylla", keymap="via"),
                bkb.Firmware(keyboard="skeletyl", keymap="default"),
            ]
            reporter.print_summary(8, 10, failed_firmwares=mock_failed_firmwares)
            args, _ = reporter.console.print.call_args
            self.assertEqual(args[0].__class__.__name__, 'MockPanel')
            self.assertIn("Build Completed with Errors", args[0].title)

            # Use str() on renderable since it is a mock string or object
            # Our bkb.Firmware string output uses {keyboard}:{keymap}
            renderable_str = str(args[0].renderable)
            self.assertIn("Failed firmwares:", renderable_str)
            self.assertIn("scylla:via", renderable_str)
            self.assertIn("skeletyl:default", renderable_str)

    @patch("bastardkb_build_releases.RotatingFileHandler")
    def test_log_location_xdg(self, mock_handler):
        # Configure the mock handler instance to have a proper level
        mock_instance = mock_handler.return_value
        mock_instance.level = 0 # NOTSET

        # Initialize Reporter
        reporter = bkb.Reporter(verbose=False)

        # Check where the log file is being created
        # We expect it to be in $XDG_STATE_HOME/bastardkb-qmk/
        expected_dir = os.path.join(self.test_dir, "bastardkb-qmk")

        # Get the filename argument passed to RotatingFileHandler
        call_args = mock_handler.call_args
        if call_args:
            filename = call_args[1].get('filename') or call_args[0][0]
            self.assertTrue(filename.startswith(expected_dir),
                            f"Log file {filename} is not in {expected_dir}")

if __name__ == '__main__':
    unittest.main()
