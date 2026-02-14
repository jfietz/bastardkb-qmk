import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock rich and pygit2 since they are not available
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.text"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["pygit2"] = MagicMock()

import bastardkb_build_releases as bkb

class TestDryRunUX(unittest.TestCase):
    def test_print_summary_dry_run(self):
        """Verify print_summary handles dry run correctly."""
        reporter = bkb.Reporter(verbose=False)
        reporter.console = MagicMock()

        # We need to patch Panel to inspect what's passed to it
        with patch("bastardkb_build_releases.Panel") as MockPanel:
            # Test 1: Normal run (default)
            reporter.print_summary(10, 10)

            self.assertTrue(MockPanel.called)
            panel_args, panel_kwargs = MockPanel.call_args

            # Verify the title contains "Success"
            self.assertIn("Success", panel_kwargs.get("title", ""))

            # Reset mock
            MockPanel.reset_mock()

            # Test 2: Dry run
            reporter.print_summary(10, 10, is_dry_run=True)

            self.assertTrue(MockPanel.called)
            panel_args, panel_kwargs = MockPanel.call_args

            # Verify the title contains "Dry Run"
            self.assertIn("Dry Run Successful", panel_kwargs.get("title", ""))
            self.assertEqual(panel_kwargs.get("border_style"), "blue")

if __name__ == '__main__':
    unittest.main()
