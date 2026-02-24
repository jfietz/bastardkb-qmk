import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies that might be missing or need control before import
# Ensure consistent mocking with test_performance.py to avoid breaking test_ux.py
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

if "pygit2" not in sys.modules:
    sys.modules["pygit2"] = MagicMock()

import bastardkb_build_releases as bkb

class TestLoggingSecurity(unittest.TestCase):
    def setUp(self):
        # Reset any previous configuration
        pass

    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('pathlib.Path.mkdir')
    @patch('os.chmod')
    @patch('os.umask')
    @patch.dict(os.environ, {"HOME": "/home/testuser", "XDG_STATE_HOME": ""})
    def test_secure_log_file_creation(self, mock_umask, mock_chmod, mock_mkdir, mock_handler):
        """Verify that logs are stored in XDG_STATE_HOME with secure permissions."""

        # Setup mocks
        mock_umask.return_value = 0o022 # Default umask

        # Configure mock_handler instance to behave like a logging.Handler
        mock_handler_instance = mock_handler.return_value
        mock_handler_instance.level = 0 # NOTSET

        # Initialize Reporter
        reporter = bkb.Reporter(verbose=False)

        # Check that XDG_STATE_HOME/bastardkb-qmk/bastardkb_build_releases.py.log is used
        # default XDG_STATE_HOME is ~/.local/state
        expected_dir = Path("/home/testuser/.local/state/bastardkb-qmk")
        expected_log_file = expected_dir / "bastardkb_build_releases.py.log"

        # Verify that RotatingFileHandler was initialized with the correct path
        # Note: The current implementation uses os.getcwd(), so this assertion is expected to FAIL until we fix it.
        # But we want to see it fail or just assert what we *want*.

        # Get the call args
        if not mock_handler.called:
             self.fail("RotatingFileHandler was not called")

        args, kwargs = mock_handler.call_args
        actual_filename = kwargs.get('filename')

        # For TDD, we assert the expected behavior.
        self.assertEqual(Path(actual_filename), expected_log_file)

        # Verify permissions
        # 1. Directory should be 0700
        mock_chmod.assert_any_call(expected_dir, 0o700)

        # 2. File creation should happen under umask 0077
        # We expect umask(0077) to be called before handler creation
        # and restored afterwards.
        mock_umask.assert_any_call(0o077)

    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('pathlib.Path.mkdir')
    @patch('os.chmod')
    @patch('os.umask')
    @patch.dict(os.environ, {"HOME": "/home/testuser", "XDG_STATE_HOME": "/custom/state"})
    def test_xdg_state_home_respected(self, mock_umask, mock_chmod, mock_mkdir, mock_handler):
        """Verify that XDG_STATE_HOME is respected."""
        mock_handler_instance = mock_handler.return_value
        mock_handler_instance.level = 0

        bkb.Reporter(verbose=False)

        expected_dir = Path("/custom/state/bastardkb-qmk")
        expected_log_file = expected_dir / "bastardkb_build_releases.py.log"

        args, kwargs = mock_handler.call_args
        actual_filename = kwargs.get('filename')
        self.assertEqual(Path(actual_filename), expected_log_file)

        mock_chmod.assert_any_call(expected_dir, 0o700)

if __name__ == '__main__':
    unittest.main()
