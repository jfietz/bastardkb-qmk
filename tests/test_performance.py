
import unittest
import sys
import os
from unittest.mock import MagicMock
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing the module
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# Mock Panel class specifically since it might be used with isinstance
# Define MockPanel directly in the test file scope so it can be used consistently
class MockPanel(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        if args:
            self.renderable = args[0]
        for key, value in kwargs.items():
            setattr(self, key, value)

mock_panel_module = MagicMock()
mock_panel_module.Panel = MockPanel
sys.modules["rich.panel"] = mock_panel_module

import bastardkb_build_releases as bkb
# Force reload to ensure mocks are picked up
import importlib
importlib.reload(bkb)

class TestPerformance(unittest.TestCase):
    def test_git_submodule_update_uses_jobs(self):
        # Setup mocks
        reporter = MagicMock()
        repository = MagicMock()
        parallel_jobs = 4

        # We need to ensure we can instantiate Executor even with mocks
        executor = bkb.Executor(reporter, repository, dry_run=False, parallel=parallel_jobs)

        # Mock worktree lookup
        worktree = MagicMock()
        worktree.name = "test_branch"
        worktree.path = Path("/tmp/test_worktree")
        repository.lookup_worktree.return_value = worktree

        # Mock _run
        executor._run = MagicMock()
        success_process = MagicMock()
        success_process.returncode = 0
        executor._run.return_value = success_process

        # Run the method
        executor.git_ensure_worktree("test_branch", update_submodules=True)

        # Verify _run was called
        # We need to find the call that matches submodule update
        found = False
        git_submodule_call_args = None

        for call in executor._run.call_args_list:
            args = call[0][0] # The first argument is the command tuple/list
            if len(args) >= 3 and args[:3] == ("git", "submodule", "update"):
                # Check if the number of jobs follows --jobs
                if "--jobs" in args:
                    try:
                        jobs_index = args.index("--jobs")
                        if str(parallel_jobs) == args[jobs_index + 1]:
                            found = True
                            git_submodule_call_args = args
                    except (ValueError, IndexError):
                        pass
                break

        self.assertTrue(found, f"git submodule update was not called with --jobs {parallel_jobs}. Called with: {git_submodule_call_args}")

    def test_total_firmware_count_reduce_callback_efficiency(self):
        # Mock FirmwareList
        firmware_list = MagicMock()
        # Mock configurations as a sequence (tuple)
        firmware_list.configurations = (1, 2, 3)

        acc = 0
        # Call the function directly
        result = bkb.total_firmware_count_reduce_callback(acc, firmware_list)
        self.assertEqual(result, 3)

    def test_qmk_compile_incremental(self):
        # Setup mocks
        reporter = MagicMock()
        repository = MagicMock()
        executor = bkb.Executor(reporter, repository, dry_run=False, parallel=1)

        # Mock _run
        executor._run = MagicMock()
        executor._run.return_value = MagicMock(returncode=0)

        # Mock Firmware and Worktree
        firmware = MagicMock()
        firmware.keyboard = "test_kb"
        firmware.keymap = "test_km"
        firmware.output_filename = "test_output"
        firmware.env_vars = []

        worktree = MagicMock()
        worktree.path = Path("/tmp/test_worktree")

        # Run the method
        executor.qmk_compile(firmware, worktree)

        # Verify arguments passed to _run
        self.assertTrue(executor._run.called)
        args = executor._run.call_args[0][0]

        # Check that --clean is NOT present
        self.assertNotIn("--clean", args, "qmk compile should not use --clean flag to allow incremental builds")

if __name__ == '__main__':
    unittest.main()
