import sys
import os
import unittest
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

    @patch("os.chmod")
    @patch("bastardkb_build_releases.RotatingFileHandler")
    def test_secure_log_directory_permissions(self, mock_handler, mock_chmod):
        """Verify that the log directory explicitly has restricted permissions using os.chmod."""
        # Configure mock handler level
        mock_handler.return_value.level = 0

        # We also need to patch os.environ and set a temp dir so it doesn't touch the real filesystem
        import tempfile
        with tempfile.TemporaryDirectory() as test_dir:
            with patch.dict("os.environ", {"XDG_STATE_HOME": test_dir}):
                reporter = bkb.Reporter(verbose=False)

                # Verify os.chmod was called
                self.assertTrue(mock_chmod.called, "os.chmod was not called")

                # Verify it was called with the correct arguments (reporter.app_log_dir, 0o700)
                mock_chmod.assert_any_call(reporter.app_log_dir, 0o700)

if __name__ == '__main__':
    unittest.main()
