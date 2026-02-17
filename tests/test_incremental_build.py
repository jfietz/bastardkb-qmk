import unittest
import sys
import os
from unittest.mock import MagicMock
from pathlib import Path

# Mock dependencies if not already mocked
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()

    # Mock Panel class specifically since it might be used with isinstance
    # To avoid InvalidSpecError when Panel(MockObject) is called, we define a custom class
    class MockPanel(MagicMock):
        def __init__(self, *args, **kwargs):
            # Swallow args to prevent them being interpreted as spec by MagicMock's init
            super().__init__()
            # If we want to inspect what was passed, we can store it:
            if args:
                self.renderable = args[0]
            for k, v in kwargs.items():
                setattr(self, k, v)

    sys.modules["rich.panel"].Panel = MockPanel
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestIncrementalBuild(unittest.TestCase):
    def test_qmk_compile_uses_incremental_build(self):
        """Verify qmk compile is called WITHOUT --clean flag."""
        # Setup mocks
        reporter = MagicMock()
        repository = MagicMock()
        parallel_jobs = 4
        executor = bkb.Executor(reporter, repository, dry_run=False, parallel=parallel_jobs)

        # Mock _run
        executor._run = MagicMock()
        executor._run.return_value = MagicMock(returncode=0)

        # Define a firmware
        firmware = bkb.Firmware(keyboard="test_kb", keymap="test_km", keymap_alias="alias")
        worktree = MagicMock()
        worktree.path = Path("/tmp/worktree")

        # Call the method
        executor.qmk_compile(firmware, worktree)

        # Check calls
        self.assertTrue(executor._run.called)
        args, _ = executor._run.call_args
        command_args = args[0]

        # Assert that --clean is NOT in the arguments
        self.assertNotIn("--clean", command_args, "qmk compile should be called WITHOUT --clean to enable incremental builds.")

if __name__ == '__main__':
    unittest.main()
