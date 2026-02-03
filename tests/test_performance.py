import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock modules that might not be installed or cause issues
sys.modules['pygit2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.text'] = MagicMock()

# Now import the module under test
import bastardkb_build_releases as bkb

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.reporter = MagicMock()
        self.repository = MagicMock()
        # Set parallel=4 explicitly
        self.executor = bkb.Executor(self.reporter, self.repository, dry_run=False, parallel=4)

    def test_git_submodule_update_uses_jobs(self):
        # Mock worktree lookup
        worktree = MagicMock()
        worktree.name = "test_branch"
        worktree.path = Path("/tmp/test_worktree")
        self.repository.lookup_worktree.return_value = worktree

        # Mock _run to return success
        self.executor._run = MagicMock()
        self.executor._run.return_value.returncode = 0

        # Call git_ensure_worktree with update_submodules=True
        self.executor.git_ensure_worktree("test_branch", update_submodules=True)

        # Verify _run was called with --jobs 4
        # We search for the specific call arguments
        called_with_jobs = False
        for call in self.executor._run.call_args_list:
            args = call[0][0]
            # args is a tuple of command arguments
            if "submodule" in args and "update" in args:
                if "--jobs" in args and "4" in args:
                    called_with_jobs = True

        self.assertTrue(called_with_jobs, "git submodule update should be called with --jobs 4")

    def test_qmk_compile_flattening(self):
        # Verify that qmk_compile constructs correct arguments with environment variables
        firmware = bkb.Firmware(
            keyboard="test/kb",
            keymap="default",
            env_vars=("VAR1=1", "VAR2=2")
        )
        worktree = MagicMock()
        worktree.path = Path("/tmp")

        self.executor._run = MagicMock()
        self.executor._run.return_value.returncode = 0

        self.executor.qmk_compile(firmware, worktree)

        # Check arguments
        call_args = self.executor._run.call_args[0][0]

        # Check that -e VAR1=1 and -e VAR2=2 are present and correctly interleaved
        # We expect ... -e VAR1=1 -e VAR2=2 ...

        # Find all indices of "-e"
        indices = [i for i, x in enumerate(call_args) if x == "-e"]

        # We expect at least 2 env vars + maybe others (the script adds TARGET and USE_CCACHE via -e? No, via --env)
        # Wait, the script uses --env for TARGET and USE_CCACHE, but -e for extra env_vars.
        # "reduce(iconcat, (("-e", env_var) ...))"

        found_vars = []
        for i in indices:
            if i + 1 < len(call_args):
                found_vars.append(call_args[i+1])

        self.assertIn("VAR1=1", found_vars)
        self.assertIn("VAR2=2", found_vars)

if __name__ == '__main__':
    unittest.main()
