import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Mock dependencies if not already mocked
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    sys.modules["rich.panel"].Panel = MagicMock
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestDependencies(unittest.TestCase):
    def setUp(self):
        self.reporter = MagicMock()

    @patch("bastardkb_build_releases.shutil.which")
    def test_dependencies_present(self, mock_which):
        # Simulate both git and qmk being present
        mock_which.side_effect = lambda x: f"/usr/bin/{x}"

        # This should not raise an exception
        try:
            bkb.check_dependencies(self.reporter)
        except SystemExit:
            self.fail("check_dependencies() raised SystemExit unexpectedly!")

        self.reporter.fatal.assert_not_called()

    @patch("bastardkb_build_releases.shutil.which")
    @patch("bastardkb_build_releases.sys.exit")
    def test_git_missing(self, mock_exit, mock_which):
        # Simulate git missing
        def which_side_effect(arg):
            if arg == "git":
                return None
            return f"/usr/bin/{arg}"

        mock_which.side_effect = which_side_effect

        bkb.check_dependencies(self.reporter)

        self.reporter.fatal.assert_called_once()
        args, kwargs = self.reporter.fatal.call_args
        self.assertIn("git", args[0])
        mock_exit.assert_called_once_with(1)

    @patch("bastardkb_build_releases.shutil.which")
    @patch("bastardkb_build_releases.sys.exit")
    def test_qmk_missing(self, mock_exit, mock_which):
        # Simulate qmk missing
        def which_side_effect(arg):
            if arg == "qmk":
                return None
            return f"/usr/bin/{arg}"

        mock_which.side_effect = which_side_effect

        bkb.check_dependencies(self.reporter)

        self.reporter.fatal.assert_called_once()
        args, kwargs = self.reporter.fatal.call_args
        self.assertIn("qmk", args[0])
        mock_exit.assert_called_once_with(1)

    @patch("bastardkb_build_releases.shutil.which")
    @patch("bastardkb_build_releases.sys.exit")
    def test_both_missing(self, mock_exit, mock_which):
        # Simulate both missing
        mock_which.return_value = None

        bkb.check_dependencies(self.reporter)

        self.reporter.fatal.assert_called_once()
        args, kwargs = self.reporter.fatal.call_args
        self.assertIn("git", args[0])
        self.assertIn("qmk", args[0])
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
