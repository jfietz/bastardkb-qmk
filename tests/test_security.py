import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import subprocess

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    @patch("bastardkb_build_releases.os.chmod")
    @patch("bastardkb_build_releases.Path.mkdir")
    @patch.dict(os.environ, {"XDG_STATE_HOME": "/tmp/test_xdg_state"})
    def test_secure_logging_setup(self, mock_mkdir, mock_chmod, mock_handler):
        """Verify that logs are stored in a secure directory with restricted permissions."""
        # Ensure the handler mock has a level attribute to avoid AttributeError
        mock_handler.return_value.level = 0

        # Initialize Reporter
        # We need to mock Console to avoid actual output or rich dependency issues
        with patch("bastardkb_build_releases.Console"):
            reporter = bkb.Reporter(verbose=False)

        # Expected paths
        expected_log_dir = Path("/tmp/test_xdg_state/bastardkb-qmk")
        expected_log_file = expected_log_dir / "bastardkb_build_releases.py.log"

        # Verify directory creation
        # Since Path.mkdir is mocked on the class, we verify it was called.
        # However, checking if it was called on the *specific* path instance is tricky
        # because Path objects are immutable and the mock is on the class method.
        # But we can verify os.chmod was called on the correct path.

        # Verify directory permissions (0700)
        # Note: We need to ensure we match the Path object or string
        # os.chmod takes a path (string or PathLike).
        # The code passes a Path object.
        mock_chmod.assert_any_call(expected_log_dir, 0o700)

        # Verify file permissions (0600)
        mock_chmod.assert_any_call(expected_log_file, 0o600)

        # Verify RotatingFileHandler initialized with correct path
        mock_handler.assert_called_with(
            filename=str(expected_log_file),
            encoding="utf-8",
            maxBytes=1024 * 1024,
            backupCount=5
        )

if __name__ == '__main__':
    unittest.main()
