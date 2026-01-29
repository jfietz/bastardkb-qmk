import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import logging

# Mock dependencies before import
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

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
        found = False
        for call in self.executor._run.call_args_list:
            args = call[0][0]
            if len(args) >= 3 and args[:3] == ("git", "submodule", "update"):
                found = True
                break
        self.assertTrue(found, "git submodule update was not called")

    def test_reporter_log_file_location(self):
        """Verify that the main log file is created in the secure temp directory."""
        # We need to instantiate Reporter.
        # It calls RotatingFileHandler, which we might want to mock or let run if it writes to disk.
        # But we want to verify the 'filename' passed to RotatingFileHandler.

        with patch("bastardkb_build_releases.RotatingFileHandler") as mock_handler:
            # Also mock Console and logging.getLogger to avoid side effects
            with patch("bastardkb_build_releases.Console"), \
                 patch("logging.getLogger"):

                reporter = bkb.Reporter(verbose=True)

                # Check arguments passed to RotatingFileHandler
                args, kwargs = mock_handler.call_args
                filename = kwargs.get('filename')

                # We expect filename to be inside reporter.log_dir
                self.assertTrue(filename.startswith(reporter.log_dir),
                                f"Log file {filename} is not inside secure temp dir {reporter.log_dir}")

if __name__ == '__main__':
    unittest.main()
