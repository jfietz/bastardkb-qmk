import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import subprocess

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies that might be missing
sys.modules['pygit2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.text'] = MagicMock()

import bastardkb_build_releases as bkb

class TestExecutorSecurity(unittest.TestCase):
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

class TestReporterSecurity(unittest.TestCase):
    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('bastardkb_build_releases.tempfile.mkdtemp')
    @patch('bastardkb_build_releases.logging.getLogger')
    @patch('bastardkb_build_releases.Console')
    @patch('bastardkb_build_releases.Path.home')
    def test_reporter_uses_persistent_log_dir(self, mock_home, mock_console, mock_get_logger, mock_mkdtemp, mock_file_handler):
        # Setup mocks
        mock_mkdtemp.return_value = "/secure/temp/dir"
        mock_home.return_value = Path("/home/mockuser")

        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Instantiate Reporter
        # We also need to ensure that the directory creation logic doesn't fail
        # Since we use real Path objects, checking .exists() on /home/mockuser will return False.
        # We can mock Path.mkdir and Path.chmod using patch.object, but since we create Path objects inside __init__,
        # it's tricky.
        # A simpler way is to mock os.makedirs and os.chmod if used, but code uses Path methods.

        # Let's mock the Path object that is created for log_dir.
        # But it's created dynamically: Path(xdg_state_home) / "bastardkb-qmk"

        with patch('bastardkb_build_releases.Path.exists', return_value=False), \
             patch('bastardkb_build_releases.Path.mkdir') as mock_mkdir, \
             patch('bastardkb_build_releases.Path.chmod') as mock_chmod:

            reporter = bkb.Reporter(verbose=False)

            # Check that RotatingFileHandler was called
            self.assertTrue(mock_file_handler.called, "RotatingFileHandler should be initialized")

            # Check the filename argument passed to RotatingFileHandler
            args, kwargs = mock_file_handler.call_args
            filename = kwargs.get('filename')

            # Expected path: /home/mockuser/.local/state/bastardkb-qmk/bastardkb_build_releases.py.log
            # Note: The separator might vary by OS, but we assume Linux/Unix here as per shebang
            expected_part = ".local/state/bastardkb-qmk"

            self.assertIn(expected_part, str(filename),
                            f"Log file path '{filename}' should contain '{expected_part}'")

            # Verify permissions (mkdir called with mode=0o700)
            # Find the call to mkdir for the log dir
            # mock_mkdir might be called multiple times?
            # We expect at least one call with mode=0o700 (448 decimal)

            found_chmod_call = False
            for call in mock_mkdir.call_args_list:
                # mkdir(parents=True, mode=0o700)
                if call.kwargs.get('mode') == 0o700:
                    found_chmod_call = True
                    break

            self.assertTrue(found_chmod_call, "mkdir should be called with mode 0o700")

if __name__ == '__main__':
    unittest.main()
