import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import tempfile
import stat
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock external dependencies if not present
try:
    import rich
    import pygit2
except ImportError:
    # We need to mock these BEFORE importing bastardkb_build_releases
    sys.modules['pygit2'] = MagicMock()
    # Need to handle submodules carefully if they are imported specifically
    rich_mock = MagicMock()
    sys.modules['rich'] = rich_mock
    sys.modules['rich.console'] = MagicMock()
    sys.modules['rich.live'] = MagicMock()
    sys.modules['rich.panel'] = MagicMock()
    sys.modules['rich.progress'] = MagicMock()
    sys.modules['rich.text'] = MagicMock()

import bastardkb_build_releases as bkb

class TestLogging(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.xdg_state_home = self.temp_dir.name
        self.env_patcher = patch.dict(os.environ, {"XDG_STATE_HOME": self.xdg_state_home})
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()
        self.temp_dir.cleanup()

    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('os.umask')
    def test_log_location_and_permissions(self, mock_umask, mock_handler):
        # Configure mock handler
        mock_handler.return_value.level = 0

        # Configure mock umask to return a value (e.g. 0o022) so logic that saves/restores it works
        mock_umask.return_value = 0o022

        # Initialize Reporter
        reporter = bkb.Reporter(verbose=False)

        # 1. Verify Log File Location
        args, kwargs = mock_handler.call_args
        if not args and not kwargs:
             self.fail("RotatingFileHandler not called")

        filename = kwargs.get('filename')
        if filename is None and len(args) > 0:
            filename = args[0]

        expected_dir = Path(self.xdg_state_home) / "bastardkb-qmk"
        expected_file = expected_dir / "bastardkb_build_releases.log"

        self.assertEqual(str(filename), str(expected_file))

        # 2. Verify Directory Creation and Permissions
        self.assertTrue(expected_dir.exists())
        self.assertTrue(expected_dir.is_dir())

        # Check permissions (stat.S_IMODE gets the permission bits)
        mode = os.stat(expected_dir).st_mode
        permissions = stat.S_IMODE(mode)
        # Expected 0o700 (rwx------)
        self.assertEqual(permissions, 0o700, f"Directory permissions are {oct(permissions)}, expected 0o700")

        # 3. Verify File Permission Logic (via umask)
        # We expect umask(0o077) to be called to set private permissions
        mock_umask.assert_any_call(0o077)

        # We also expect umask to be restored to original (0o022)
        mock_umask.assert_called_with(0o022)

if __name__ == '__main__':
    unittest.main()
