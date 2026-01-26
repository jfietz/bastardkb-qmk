import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestBuild(unittest.TestCase):
    def setUp(self):
        self.reporter = MagicMock()
        self.repository = MagicMock()
        self.executor = bkb.Executor(self.reporter, self.repository, dry_run=False, parallel=1)

    def test_ccache_enabled(self):
        # Mock worktree
        worktree = MagicMock()
        worktree.path = Path("/tmp/test_worktree")

        # Mock firmware
        firmware = bkb.Firmware(
            keyboard="test_keyboard",
            keymap="test_keymap",
            env_vars=[]
        )

        # Mock _run
        self.executor._run = MagicMock()
        self.executor._run.return_value = MagicMock(returncode=0)

        # Call compile
        self.executor.qmk_compile(firmware, worktree)

        # Verify arguments
        call_args = self.executor._run.call_args[0][0]

        # Check if USE_CCACHE=yes is in the env vars passed to qmk compile
        self.assertIn("USE_CCACHE=yes", call_args)

        # Ensure it is passed as an env var
        try:
            ccache_index = call_args.index("USE_CCACHE=yes")
            self.assertEqual(call_args[ccache_index-1], "--env")
        except ValueError:
            self.fail("USE_CCACHE=yes not found in arguments")

if __name__ == '__main__':
    unittest.main()
