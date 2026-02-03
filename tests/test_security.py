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

    def test_reporter_secure_logging(self):
        with patch('bastardkb_build_releases.RotatingFileHandler') as mock_handler, \
             patch('bastardkb_build_releases.logging') as mock_logging, \
             patch('bastardkb_build_releases.Console') as mock_console, \
             patch('bastardkb_build_releases.os.environ.get') as mock_env_get, \
             patch('bastardkb_build_releases.os.path.expanduser') as mock_expanduser, \
             patch('bastardkb_build_releases.Path') as mock_path_cls, \
             patch('bastardkb_build_releases.tempfile.mkdtemp') as mock_mkdtemp:

            # Setup mocks
            mock_env_get.return_value = "/secure/xdg"

            # Mock the path objects
            mock_root_path = MagicMock()
            mock_path_cls.return_value = mock_root_path

            mock_app_dir = MagicMock()
            mock_root_path.__truediv__.return_value = mock_app_dir

            mock_log_file = MagicMock()
            mock_app_dir.__truediv__.return_value = mock_log_file

            # Instantiate Reporter
            # We need to make sure Reporter doesn't crash on other things
            reporter = bkb.Reporter(verbose=False)

            # Check environment get
            mock_env_get.assert_called_with("XDG_STATE_HOME")

            # Check Path creation: Path("/secure/xdg")
            # We verify it was called with the value returned by mock_env_get
            mock_path_cls.assert_any_call("/secure/xdg")

            # Check concatenation: / "bastardkb-qmk"
            mock_root_path.__truediv__.assert_called_with("bastardkb-qmk")

            # Check mkdir and chmod
            mock_app_dir.mkdir.assert_called_with(parents=True, exist_ok=True)
            mock_app_dir.chmod.assert_called_with(0o700)

            # Check RotatingFileHandler usage
            mock_handler.assert_called()
            args, kwargs = mock_handler.call_args
            self.assertEqual(kwargs['filename'], mock_log_file)

if __name__ == '__main__':
    unittest.main()
