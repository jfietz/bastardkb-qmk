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
    @patch("bastardkb_build_releases.os.makedirs")
    @patch.dict(os.environ, {"XDG_STATE_HOME": "/tmp/mock_state"})
    def test_reporter_uses_secure_log_path(self, mock_makedirs, mock_chmod, mock_handler):
        # Configure mock handler to avoid logging errors during test
        mock_handler.return_value.level = 0

        # Initialize Reporter
        bkb.Reporter(verbose=False)

        # Expected log directory
        expected_dir = os.path.join("/tmp/mock_state", "bastardkb-qmk")

        # Verify makedirs called with correct path and mode
        mock_makedirs.assert_called_with(expected_dir, mode=0o700, exist_ok=True)

        # Verify chmod called with correct permissions
        mock_chmod.assert_called_with(expected_dir, 0o700)

        # Verify handler created with correct path
        expected_log_file = os.path.join(expected_dir, "bastardkb_build_releases.py.log")
        mock_handler.assert_called_with(
            filename=expected_log_file,
            encoding="utf-8",
            maxBytes=1024 * 1024,
            backupCount=5
        )

if __name__ == '__main__':
    unittest.main()
