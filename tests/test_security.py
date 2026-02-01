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
    @patch("os.makedirs")
    @patch("os.chmod")
    @patch("tempfile.mkdtemp")
    @patch.dict(os.environ, {"XDG_STATE_HOME": "/tmp/secure_state"}, clear=True)
    def test_log_file_location_secure(self, mock_mkdtemp, mock_chmod, mock_makedirs, mock_handler):
        mock_mkdtemp.return_value = "/tmp/mock_temp"
        mock_handler.return_value.level = 0  # logging.NOTSET

        # Re-initialize Reporter to trigger the logging setup
        # Note: We are testing the __init__ logic
        bkb.Reporter(verbose=False)

        expected_dir = Path("/tmp/secure_state/bastardkb-qmk")

        # Verify directory creation with secure permissions
        # We check if makedirs was called with the expected path and mode
        # Note: We need to ensure the implementation uses os.makedirs or compatible
        mock_makedirs.assert_called_with(expected_dir, mode=0o700, exist_ok=True)
        mock_chmod.assert_called_with(expected_dir, 0o700)

        # Verify log file location
        expected_log_file = expected_dir / "bastardkb_build_releases.py.log"
        args, kwargs = mock_handler.call_args
        self.assertEqual(Path(kwargs['filename']), expected_log_file)

    @patch("bastardkb_build_releases.RotatingFileHandler")
    @patch("os.makedirs")
    @patch("os.chmod")
    @patch("tempfile.mkdtemp")
    @patch("pathlib.Path.home")
    @patch.dict(os.environ, {}, clear=True) # Ensure XDG_STATE_HOME is unset
    def test_log_file_location_fallback(self, mock_home, mock_mkdtemp, mock_chmod, mock_makedirs, mock_handler):
        mock_mkdtemp.return_value = "/tmp/mock_temp"
        mock_home.return_value = Path("/home/user")
        mock_handler.return_value.level = 0  # logging.NOTSET

        bkb.Reporter(verbose=False)

        expected_dir = Path("/home/user/.local/state/bastardkb-qmk")

        mock_makedirs.assert_called_with(expected_dir, mode=0o700, exist_ok=True)
        mock_chmod.assert_called_with(expected_dir, 0o700)

        expected_log_file = expected_dir / "bastardkb_build_releases.py.log"
        args, kwargs = mock_handler.call_args
        self.assertEqual(Path(kwargs['filename']), expected_log_file)

if __name__ == '__main__':
    unittest.main()
