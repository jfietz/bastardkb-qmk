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
        self.reporter_mock = MagicMock()
        self.repository = MagicMock()
        self.executor = bkb.Executor(self.reporter_mock, self.repository, dry_run=False, parallel=1)

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

    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('os.makedirs')
    @patch.dict(os.environ, {"XDG_STATE_HOME": "/tmp/xdg_state"})
    def test_logging_location_is_secure(self, mock_makedirs, mock_handler):
        # Ensure the handler mock has a level attribute to avoid errors if accessed
        mock_handler.return_value.level = 0

        # Instantiate Reporter
        reporter = bkb.Reporter(verbose=False)

        # Expected log directory
        expected_log_dir = Path("/tmp/xdg_state/bastardkb-qmk")

        # Check that os.makedirs was called with the expected secure path and permissions
        # Note: We check if it was called at least once with these arguments
        mock_makedirs.assert_any_call(expected_log_dir, mode=0o700, exist_ok=True)

        # Check that RotatingFileHandler was initialized with a file inside the secure directory
        # Get the arguments passed to RotatingFileHandler
        call_args = mock_handler.call_args
        if call_args:
            args, kwargs = call_args
            filename = kwargs.get('filename')
            if not filename and args:
                filename = args[0]

            # Verify filename starts with the expected directory
            self.assertTrue(
                str(filename).startswith(str(expected_log_dir)),
                f"Log file {filename} is not in secure directory {expected_log_dir}"
            )
        else:
            self.fail("RotatingFileHandler was not initialized")

if __name__ == '__main__':
    unittest.main()
