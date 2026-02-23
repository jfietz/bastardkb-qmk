import unittest
import sys
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import stat
import logging

# Mock dependencies if not already mocked
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    # Mock Panel class specifically since it might be used with isinstance
    class MockPanel(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__()
            if args:
                self.renderable = args[0]
            for key, value in kwargs.items():
                setattr(self, key, value)

    sys.modules["rich.panel"].Panel = MockPanel
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestLogging(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for HOME
        self.test_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.test_dir) / ".local" / "state" / "bastardkb-qmk"
        self.log_file = self.log_dir / "bastardkb_build_releases.log"

        # Set HOME and ensure XDG_STATE_HOME is not set (to test fallback)
        # We need to unset XDG_STATE_HOME if it exists in the environment
        env_dict = os.environ.copy()
        env_dict["HOME"] = self.test_dir
        if "XDG_STATE_HOME" in env_dict:
            del env_dict["XDG_STATE_HOME"]

        self.env_patcher = patch.dict(os.environ, env_dict, clear=True)
        self.env_patcher.start()

        # Patch console to avoid printing
        self.console_patcher = patch('bastardkb_build_releases.Console')
        self.console_patcher.start()

        # Clear existing handlers
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    def tearDown(self):
        self.env_patcher.stop()
        self.console_patcher.stop()

        # Close handlers before removing directory
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

        shutil.rmtree(self.test_dir)

    def test_log_directory_creation_and_permissions(self):
        """Verify that the log directory is created with secure permissions (0700)."""
        # Create reporter which initializes logging
        bkb.Reporter(verbose=False)

        # Check directory exists
        self.assertTrue(self.log_dir.exists(), f"Log directory {self.log_dir} should exist")
        self.assertTrue(self.log_dir.is_dir(), f"{self.log_dir} should be a directory")

        # Check directory permissions
        mode = stat.S_IMODE(self.log_dir.stat().st_mode)
        self.assertEqual(mode, 0o700, f"Log directory permissions should be 0700 (got {oct(mode)})")

    def test_log_file_permissions(self):
        """Verify that the log file is created with secure permissions (0600)."""
        # Create reporter which initializes logging
        bkb.Reporter(verbose=False)

        # Check file exists
        self.assertTrue(self.log_file.exists(), f"Log file {self.log_file} should exist")

        # Check file permissions
        mode = stat.S_IMODE(self.log_file.stat().st_mode)
        self.assertEqual(mode, 0o600, f"Log file permissions should be 0600 (got {oct(mode)})")

if __name__ == '__main__':
    unittest.main()
