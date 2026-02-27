
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
import importlib
importlib.reload(bkb)

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
    @patch("os.makedirs")
    @patch("bastardkb_build_releases.RotatingFileHandler")
    @patch("bastardkb_build_releases.tempfile.mkdtemp")
    def test_log_directory_permissions_enforced(self, mock_mkdtemp, mock_handler, mock_makedirs, mock_chmod):
        # Setup mocks
        mock_handler.return_value = MagicMock()
        mock_handler.return_value.level = 0
        mock_mkdtemp.return_value = "/tmp/mock_temp_dir"

        # Initialize Reporter which triggers log directory setup
        reporter = bkb.Reporter(verbose=False)

        # Verify os.makedirs was called with correct mode
        # Note: We can't easily check the path since it depends on environment,
        # but we can check the mode.
        self.assertTrue(mock_makedirs.called)
        _, kwargs = mock_makedirs.call_args
        self.assertEqual(kwargs.get('mode'), 0o700)

        # Verify os.chmod was called to enforce permissions
        # This is the critical security fix verification
        self.assertTrue(mock_chmod.called)
        args, _ = mock_chmod.call_args
        # args[0] is the path, args[1] is the mode
        self.assertEqual(args[1], 0o700)

if __name__ == '__main__':
    unittest.main()
