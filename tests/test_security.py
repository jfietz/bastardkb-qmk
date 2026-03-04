import sys
import os
import unittest
import tempfile
import stat
from unittest.mock import MagicMock, patch
from pathlib import Path
import subprocess

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing the module
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

import bastardkb_build_releases as bkb

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.reporter = MagicMock()
        self.repository = MagicMock()
        self.executor = bkb.Executor(self.reporter, self.repository, dry_run=False, parallel=1)

    def test_git_submodule_update_failure_raises_error(self):
        # Mock worktree lookup
        worktree = MagicMock()
        worktree.name = "test_branch"
        worktree.path = Path("/tmp/test_worktree")
        self.repository.lookup_worktree.return_value = worktree

        # Mock _run to return failure for git submodule update
        self.executor._run = MagicMock()

        # Return a failure process
        failure_process = MagicMock()
        failure_process.returncode = 1
        self.executor._run.return_value = failure_process

        # We expect the code to exit or raise an error when submodule update fails.
        with self.assertRaises(SystemExit):
            self.executor.git_ensure_worktree("test_branch", update_submodules=True)

        # Verify _run was called with git submodule update
        # We need to find the call that matches submodule update
        found = False
        for call in self.executor._run.call_args_list:
            args = call[0][0]
            if len(args) >= 3 and args[:3] == ("git", "submodule", "update"):
                found = True
                break
        self.assertTrue(found, "git submodule update was not called")

    @patch("bastardkb_build_releases.RotatingFileHandler")
    def test_app_log_dir_permissions_are_enforced_on_existing_dir(self, mock_handler):
        # Configure the mock handler
        mock_handler.return_value.level = 0

        with tempfile.TemporaryDirectory() as td:
            # Pre-create the log directory with permissive permissions (e.g., 0o777)
            app_log_dir = os.path.join(td, "bastardkb-qmk")
            os.makedirs(app_log_dir)
            os.chmod(app_log_dir, 0o777)

            with patch.dict(os.environ, {"XDG_STATE_HOME": td}):
                # Initialize reporter
                reporter = bkb.Reporter(verbose=False)

                # Verify that permissions were restricted to 0o700
                st = os.stat(app_log_dir)
                perms = stat.S_IMODE(st.st_mode)
                self.assertEqual(perms, 0o700, f"Expected 0o700 permissions, got {oct(perms)}")


if __name__ == '__main__':
    unittest.main()
