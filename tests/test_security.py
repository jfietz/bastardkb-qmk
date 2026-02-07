import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import subprocess
import tempfile
import stat
import logging
import logging.handlers

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

    def test_log_file_location_and_permissions(self):
        # Create a temporary directory to act as XDG_STATE_HOME
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set XDG_STATE_HOME to temp_dir
            with patch.dict(os.environ, {"XDG_STATE_HOME": temp_dir}):
                # Mock Console to avoid output during test
                with patch('bastardkb_build_releases.Console') as MockConsole:
                    reporter = bkb.Reporter(verbose=False)

                    # Check directory location
                    log_dir = Path(temp_dir) / "bastardkb-qmk"
                    self.assertTrue(log_dir.is_dir(), "Log directory not created")

                    # Check directory permissions
                    # Note: On Windows permissions work differently, but this script seems Unix-focused.
                    if os.name == 'posix':
                        mode = stat.S_IMODE(os.stat(log_dir).st_mode)
                        self.assertEqual(mode, 0o700, f"Log directory permissions incorrect: {oct(mode)}")

                    # Check log file existence
                    log_file = log_dir / "bastardkb_build_releases.py.log"
                    self.assertTrue(log_file.is_file(), "Log file not created")

                    # Cleanup: Close and remove the handler
                    logger = logging.getLogger()
                    handlers_to_remove = []
                    for handler in logger.handlers:
                        # Check if it's the handler added by Reporter
                        if isinstance(handler, logging.handlers.RotatingFileHandler) and \
                           Path(handler.baseFilename).name == "bastardkb_build_releases.py.log":
                            handler.close()
                            handlers_to_remove.append(handler)

                    for handler in handlers_to_remove:
                        logger.removeHandler(handler)

if __name__ == '__main__':
    unittest.main()
