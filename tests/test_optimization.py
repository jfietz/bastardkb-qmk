import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Mock dependencies before importing the module
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestOptimization(unittest.TestCase):
    def test_qmk_compile_env_vars_flattening(self):
        # Setup
        reporter = MagicMock()
        repository = MagicMock()
        executor = bkb.Executor(reporter, repository, dry_run=True, parallel=1)

        firmware = bkb.Firmware(
            keyboard="test/keyboard",
            keymap="default",
            env_vars=("VAR1=val1", "VAR2=val2")
        )
        worktree = MagicMock()
        worktree.path = "path/to/worktree"

        # Execute
        # We need to verify that env vars are flattened correctly in the command
        # Executor._run is called with argv
        with patch.object(executor, '_run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            executor.qmk_compile(firmware, worktree)

            # Verify
            args = mock_run.call_args[0][0]
            # args should contain ... -e VAR1=val1 -e VAR2=val2 ...
            self.assertIn("-e", args)
            self.assertIn("VAR1=val1", args)
            self.assertIn("VAR2=val2", args)

            # Check order/indices if possible, or just presence
            indices = [i for i, x in enumerate(args) if x == "-e"]
            self.assertEqual(len(indices), 2) # 2 for env_vars. TARGET and USE_CCACHE use --env

            # Check --env usage
            env_indices = [i for i, x in enumerate(args) if x == "--env"]
            self.assertEqual(len(env_indices), 2)

            # Check specifically for our env vars
            # We expect ... -e VAR1=val1 -e VAR2=val2
            # Find index of VAR1=val1
            idx1 = args.index("VAR1=val1")
            self.assertEqual(args[idx1-1], "-e")

            idx2 = args.index("VAR2=val2")
            self.assertEqual(args[idx2-1], "-e")

    def test_default_parallelism(self):
        # We need to test that main() calls Executor with parallel=os.cpu_count()
        # We need to mock sys.argv, Repository, and Executor

        with patch('sys.argv', ['script_name']), \
             patch('bastardkb_build_releases.Repository') as mock_repo_cls, \
             patch('bastardkb_build_releases.Executor') as mock_executor_cls, \
             patch('bastardkb_build_releases.Reporter'), \
             patch('bastardkb_build_releases.build'), \
             patch('bastardkb_build_releases.copy_assets_to_output_dir'):

            mock_repo = mock_repo_cls.return_value
            mock_repo.is_bare = True

            bkb.main()

            # Check Executor initialization
            args, kwargs = mock_executor_cls.call_args
            # Executor(reporter, repository, dry_run, parallel)
            # parallel is the 4th arg (index 3)
            parallel_arg = args[3]

            expected = os.cpu_count() or 1
            self.assertEqual(parallel_arg, expected)

    def test_build_total_count(self):
        # Verify the sum calculation logic
        executor = MagicMock()
        reporter = MagicMock()
        # Mock Progress
        # We need to patch rich classes instantiated in build()
        # Since we mocked modules at top level, we can inspect the mocks

        firmware_list1 = bkb.FirmwareList("branch1", (MagicMock(), MagicMock())) # 2 firmwares
        firmware_list2 = bkb.FirmwareList("branch2", (MagicMock(),)) # 1 firmware
        firmwares = (firmware_list1, firmware_list2)

        # build instantiates Progress via reporter.console?
        # No, it instantiates Progress directly.
        # from rich.progress import Progress

        # Since we mocked sys.modules["rich.progress"], bkb.Progress is a MagicMock
        mock_progress_cls = bkb.Progress
        mock_progress_instance = mock_progress_cls.return_value

        # We need to mock Group and Live as well to avoid errors

        bkb.build(executor, reporter, firmwares, MagicMock())

        # Verify that overall_progress task was added with total=3
        # overall_progress is the 3rd Progress instance created?
        # Let's inspect calls to Progress() constructor
        # 1. empty_status
        # 2. overall_status
        # 3. overall_progress

        # Depending on how mocks work, we might need to be careful.
        # If Progress is a mock class, Progress() returns a new mock.

        # But we can also test the logic by extracting it or trusting that if it runs without error
        # and we changed the implementation to sum(), it is correct.

        # Actually, let's verify usage of sum() vs reduce() is hard via blackbox testing
        # without inspecting source code or having a precise side effect.
        # But we can check if the total passed to add_task is correct.

        # Find the call to add_task with 'total='
        # overall_progress.add_task("", total=total_firmware_count)

        found = False

        # Standard Mock return values are the same instance unless side_effect is set.
        # So bkb.Progress() returns the SAME mock instance every time by default.
        progress_instance = bkb.Progress.return_value

        # Check calls to add_task
        # call_args_list will have calls for all "3" instances (which are the same object)

        # We expect a call with total=3
        for call in progress_instance.add_task.call_args_list:
            kwargs = call[1]
            if 'total' in kwargs:
                if kwargs['total'] == 3:
                    found = True
                    break

        self.assertTrue(found, "Did not find add_task call with total=3")

if __name__ == '__main__':
    unittest.main()
