import sys
import os
import unittest
from unittest.mock import MagicMock

# Mock dependencies BEFORE import
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import target
import bastardkb_build_releases as bkb

class TestPerformance(unittest.TestCase):
    def test_git_ensure_worktree_uses_parallel_submodule_update(self):
        # Setup
        reporter = MagicMock()
        repository = MagicMock()
        # Mock worktree lookup to return a valid worktree
        worktree = MagicMock()
        worktree.name = "test_worktree"
        worktree.path = "test_path"
        repository.lookup_worktree.return_value = worktree

        # Initialize Executor with parallel=4
        parallel_count = 4
        executor = bkb.Executor(reporter, repository, dry_run=False, parallel=parallel_count)

        # Mock _run
        executor._run = MagicMock()
        executor._run.return_value.returncode = 0

        # Execute
        executor.git_ensure_worktree("test_branch", update_submodules=True)

        # Verify
        # We expect one call to _run
        self.assertTrue(executor._run.called)
        args, kwargs = executor._run.call_args
        command = args[0]

        # Check if --jobs 4 is in the command
        # The command tuple is like ("git", "submodule", "update", "--init", "--recursive")
        # We expect it to eventually include "--jobs" and "4"
        self.assertIn("--jobs", command, f"Command {command} should contain '--jobs'")
        self.assertIn(str(parallel_count), command, f"Command {command} should contain '{parallel_count}'")

if __name__ == '__main__':
    unittest.main()
