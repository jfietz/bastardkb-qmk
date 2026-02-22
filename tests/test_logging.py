import sys
import os
import unittest
from unittest.mock import MagicMock, patch, ANY

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies to avoid import errors if not installed
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
# Mock Panel class specifically
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

import bastardkb_build_releases as bkb

class TestLogging(unittest.TestCase):
    @patch("bastardkb_build_releases.RotatingFileHandler")
    @patch("os.makedirs")
    @patch("os.environ", {})
    @patch("os.path.expanduser")
    @patch("os.umask")
    def test_log_location_default(self, mock_umask, mock_expanduser, mock_makedirs, mock_handler):
        # Setup mocks
        mock_expanduser.return_value = "/home/user/.local/state"
        mock_umask.return_value = 0o022 # Default umask

        # Mock the handler instance to avoid attribute errors if accessed
        mock_handler_instance = MagicMock()
        mock_handler_instance.level = 0 # Allow all logs
        mock_handler.return_value = mock_handler_instance

        # Initialize Reporter
        reporter = bkb.Reporter(verbose=False)

        # Check makedirs called with correct path and mode
        expected_dir = os.path.join("/home/user/.local/state", "bastardkb-qmk")
        mock_makedirs.assert_called_with(expected_dir, mode=0o700, exist_ok=True)

        # Check handler called with correct path
        expected_log_file = os.path.join(expected_dir, "bastardkb_build_releases.log")
        mock_handler.assert_called_with(
            filename=expected_log_file,
            encoding="utf-8",
            maxBytes=1024 * 1024,
            backupCount=5
        )

        # Check umask was set to 077 and then restored
        mock_umask.assert_any_call(0o077)
        mock_umask.assert_any_call(0o022)

    @patch("bastardkb_build_releases.RotatingFileHandler")
    @patch("os.makedirs")
    @patch.dict(os.environ, {"XDG_STATE_HOME": "/custom/state"}, clear=True)
    @patch("os.umask")
    def test_log_location_xdg(self, mock_umask, mock_makedirs, mock_handler):
        # Setup mocks
        mock_umask.return_value = 0o022

        # Mock the handler instance
        mock_handler_instance = MagicMock()
        mock_handler_instance.level = 0
        mock_handler.return_value = mock_handler_instance

        # Initialize Reporter
        reporter = bkb.Reporter(verbose=False)

        # Check makedirs called with correct path and mode
        expected_dir = os.path.join("/custom/state", "bastardkb-qmk")
        mock_makedirs.assert_called_with(expected_dir, mode=0o700, exist_ok=True)

        # Check handler called with correct path
        expected_log_file = os.path.join(expected_dir, "bastardkb_build_releases.log")
        mock_handler.assert_called_with(
            filename=expected_log_file,
            encoding="utf-8",
            maxBytes=1024 * 1024,
            backupCount=5
        )

if __name__ == '__main__':
    unittest.main()
