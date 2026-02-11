
import sys
import unittest
import os
from unittest.mock import MagicMock, patch

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before import
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# rich.panel.Panel needs to be a class that accepts arguments
class MockPanel(MagicMock):
    def __init__(self, *args, **kwargs):
        # Ignore arguments passed to Panel constructor
        super().__init__()
sys.modules["rich.panel"].Panel = MockPanel

# Import the module under test
import bastardkb_build_releases

class TestDependencyCheck(unittest.TestCase):
    def setUp(self):
        # Mock Repository to pass is_bare check
        self.mock_repo = MagicMock()
        self.mock_repo.is_bare = True
        bastardkb_build_releases.Repository = MagicMock(return_value=self.mock_repo)

        # Mock os.cpu_count to return 1 if needed (though already done in argparser)

    @patch("bastardkb_build_releases.shutil.which")
    @patch("bastardkb_build_releases.sys.exit")
    def test_missing_git(self, mock_exit, mock_which):
        # git missing
        mock_which.side_effect = lambda cmd: "/usr/bin/qmk" if cmd == "qmk" else None

        with patch("sys.argv", ["script_name", "--dry-run"]):
            try:
                bastardkb_build_releases.main()
            except SystemExit:
                pass
            except Exception as e:
                # Failing here means the code crashed instead of exiting gracefully
                self.fail(f"Crashed with exception: {e}")

        # Assert exit(1) was called
        mock_exit.assert_called_with(1)

    @patch("bastardkb_build_releases.shutil.which")
    @patch("bastardkb_build_releases.sys.exit")
    def test_missing_qmk(self, mock_exit, mock_which):
        # qmk missing
        mock_which.side_effect = lambda cmd: "/usr/bin/git" if cmd == "git" else None

        with patch("sys.argv", ["script_name", "--dry-run"]):
            try:
                bastardkb_build_releases.main()
            except SystemExit:
                pass
            except Exception as e:
                self.fail(f"Crashed with exception: {e}")

        mock_exit.assert_called_with(1)

if __name__ == "__main__":
    unittest.main()
