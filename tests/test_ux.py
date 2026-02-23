import unittest
import sys
import os
import subprocess
import re
from unittest.mock import MagicMock, patch

# Mock dependencies if they are missing
try:
    import pygit2
except ImportError:
    sys.modules["pygit2"] = MagicMock()

try:
    import rich
except ImportError:
    # We need a somewhat functional mock for rich components
    rich_mock = MagicMock()
    sys.modules["rich"] = rich_mock
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.progress"] = MagicMock()

    # Mock Panel
    # Panel is instantiated as Panel(renderable, title=...)
    # We need to access .renderable and .title on the instance
    class MockPanel(MagicMock):
        def __init__(self, renderable=None, title=None, **kwargs):
            super().__init__()
            self.renderable = renderable
            self.title = title
            # Store args for inspection
            self.args = (renderable,)
            self.kwargs = kwargs
            if title: self.kwargs['title'] = title

    mock_panel_module = MagicMock()
    mock_panel_module.Panel = MockPanel
    sys.modules["rich.panel"] = mock_panel_module

    # Mock Text
    # Text is instantiated as Text(content, ...)
    # It supports append() and str()
    class MockText:
        def __init__(self, text="", **kwargs):
            self._text_content = text

        def append(self, text, style=None):
            self._text_content += text

        def __str__(self):
            return self._text_content

        def __repr__(self):
             return f"Text({self._text_content!r})"

    mock_text_module = MagicMock()
    mock_text_module.Text = MockText
    sys.modules["rich.text"] = mock_text_module

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestUX(unittest.TestCase):
    def test_parallel_default_help(self):
        """Verify the help text shows the correct default for parallel."""
        # Skip if dependencies are mocked because subprocess will fail
        if isinstance(sys.modules.get("pygit2"), MagicMock) or isinstance(sys.modules.get("rich"), MagicMock):
            self.skipTest("Skipping subprocess test because dependencies are mocked")

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

        # Access the Panel class from the module (mocked or real)
        from rich.panel import Panel
        panel = args[0]
        self.assertIsInstance(panel, Panel)

        # Note: rich markup might be in the title, e.g. [bold green]Success[/bold green]
        # Our mock stores title in .title
        self.assertIn("Success", panel.title)

        # Test Failure Case
        reporter.print_summary(8, 10)
        args, _ = reporter.console.print.call_args
        panel = args[0]
        self.assertIsInstance(panel, Panel)
        self.assertIn("Build Completed with Errors", panel.title)

    @patch("bastardkb_build_releases.Text")
    def test_print_summary_with_failures(self, MockTextClass):
        """Verify print_summary lists failed firmwares."""
        reporter = bkb.Reporter(verbose=False)
        reporter.console = MagicMock()
        reporter.logging = MagicMock()

        # Setup MockTextClass to behave like a string builder
        text_instance = MagicMock()
        text_content = []

        def append_side_effect(text, style=None):
            text_content.append(text)

        text_instance.append.side_effect = append_side_effect

        # When Text(..., justify="...") is called
        def text_constructor(initial_text="", **kwargs):
            text_content.append(initial_text)
            return text_instance

        MockTextClass.side_effect = text_constructor

        failed_firmwares = ["keyboard1/mcu1:keymap1", "keyboard2/mcu2:keymap2"]

        reporter.print_summary(8, 10, failed_firmwares)

        # Verify content
        full_text = "".join(text_content)
        for fw in failed_firmwares:
            self.assertIn(fw, full_text)

        # Verify it was passed to Panel
        args, _ = reporter.console.print.call_args
        panel = args[0]
        # panel.renderable should be our text_instance
        self.assertEqual(panel.renderable, text_instance)

if __name__ == '__main__':
    unittest.main()
