import os
import sys
import unittest
import tempfile
import stat
from unittest.mock import MagicMock

# Mock dependencies before importing
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

class TestLogPermissions(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.xdg_home = os.path.join(self.tmp_dir, "state")
        os.makedirs(self.xdg_home)
        os.environ["XDG_STATE_HOME"] = self.xdg_home

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir)

    def test_directory_permissions_are_enforced(self):
        # Pre-create the log directory with 0755 (world readable)
        log_dir = os.path.join(self.xdg_home, "bastardkb-qmk")
        os.makedirs(log_dir, mode=0o755)

        # Verify it is initially world-readable
        st = os.stat(log_dir)
        self.assertTrue(bool(st.st_mode & stat.S_IROTH), "Directory should be world readable initially")

        # Initialize Reporter
        bkb.Reporter(verbose=False)

        # Check permissions again
        st = os.stat(log_dir)

        # We expect the Reporter to fix permissions to 0700.
        # This will currently FAIL.
        self.assertFalse(bool(st.st_mode & stat.S_IROTH), "Directory is still world readable")
        self.assertFalse(bool(st.st_mode & stat.S_IRGRP), "Directory is still group readable")
        self.assertEqual(st.st_mode & 0o777, 0o700, "Directory permissions are not 0700")

if __name__ == "__main__":
    unittest.main()
