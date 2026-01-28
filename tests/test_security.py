import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import subprocess

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before import
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# Ensure Console can be instantiated
sys.modules["rich.console"].Console = MagicMock()

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

    def test_log_file_secure_location(self):
        with patch('bastardkb_build_releases.RotatingFileHandler') as MockRFH:
            # Configure the mock handler to have a valid level for logging comparisons
            MockRFH.return_value.level = 0

            with patch('bastardkb_build_releases.tempfile.mkdtemp') as MockMkdtemp:
                mock_temp_dir = "/tmp/mock_secure_dir"
                MockMkdtemp.return_value = mock_temp_dir

                # Instantiate Reporter
                # Note: Reporter.__init__ calls Console(), which is mocked.
                reporter = bkb.Reporter(verbose=False)

                # Check that RotatingFileHandler was called
                self.assertTrue(MockRFH.called, "RotatingFileHandler was not initialized")

                # Check the filename argument
                args, kwargs = MockRFH.call_args
                filename = kwargs.get('filename')
                if not filename and len(args) > 0:
                    filename = args[0]

                # Verify the filename starts with the secure temp dir
                self.assertTrue(str(filename).startswith(mock_temp_dir),
                               f"Log file {filename} is not in secure dir {mock_temp_dir}")

                # Verify that the log location was printed to console
                # reporter.console is a Mock
                # We expect one of the print calls to contain the log dir path
                console_print_calls = reporter.console.print.call_args_list
                found_log_msg = False
                for call in console_print_calls:
                    args, _ = call
                    if args and mock_temp_dir in str(args[0]):
                        found_log_msg = True
                        break

                self.assertTrue(found_log_msg, "Log file location was not printed to console")

if __name__ == '__main__':
    unittest.main()
