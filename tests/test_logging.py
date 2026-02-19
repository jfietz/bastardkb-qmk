import sys
import os
import unittest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path

# Mock external dependencies before importing the module under test
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

class TestLoggingSecurity(unittest.TestCase):
    def setUp(self):
        # Clean up environment variable for XDG_STATE_HOME if set
        self.original_xdg_state_home = os.environ.get("XDG_STATE_HOME")
        if "XDG_STATE_HOME" in os.environ:
            del os.environ["XDG_STATE_HOME"]

    def tearDown(self):
        if self.original_xdg_state_home:
            os.environ["XDG_STATE_HOME"] = self.original_xdg_state_home
        elif "XDG_STATE_HOME" in os.environ:
            del os.environ["XDG_STATE_HOME"]

    @patch("bastardkb_build_releases.Path")
    @patch("os.environ")
    def test_get_state_dir_xdg_env(self, mock_environ, mock_path):
        """Verify get_state_dir respects XDG_STATE_HOME env var."""
        mock_environ.get.return_value = "/tmp/xdg_state_home"

        # Setup mock path behavior
        mock_state_dir = MagicMock()
        mock_path.return_value.__truediv__.return_value = mock_state_dir

        result = bkb.get_state_dir()

        # Verify Path was initialized with XDG_STATE_HOME
        mock_path.assert_any_call("/tmp/xdg_state_home")

        # Verify result is correct
        self.assertEqual(result, mock_state_dir)

        # Verify directory creation and permissions
        mock_state_dir.mkdir.assert_called_with(parents=True, exist_ok=True)
        mock_state_dir.chmod.assert_called_with(0o700)

    @patch("bastardkb_build_releases.Path")
    @patch("os.path.expanduser")
    def test_get_state_dir_default(self, mock_expanduser, mock_path):
        """Verify get_state_dir defaults to ~/.local/state."""
        # Unset XDG_STATE_HOME so it falls back
        # We need to make sure os.environ.get returns the default
        # But in the code: os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
        # So we can't easily patch os.environ.get to return the fallback without side effects if we mock it completely.
        # Instead, let's rely on the real os.environ.get logic but control expanduser.

        mock_expanduser.return_value = "/home/user/.local/state"

        # Setup mock path behavior
        mock_state_dir = MagicMock()
        mock_path.return_value.__truediv__.return_value = mock_state_dir

        result = bkb.get_state_dir()

        mock_expanduser.assert_called_with("~/.local/state")
        mock_path.assert_any_call("/home/user/.local/state")
        self.assertEqual(result, mock_state_dir)
        mock_state_dir.chmod.assert_called_with(0o700)

    @patch("bastardkb_build_releases.get_state_dir")
    @patch("bastardkb_build_releases.RotatingFileHandler")
    @patch("os.umask")
    def test_reporter_logging_permissions(self, mock_umask, mock_handler, mock_get_state_dir):
        """Verify Reporter uses correct log path and sets permissions."""
        mock_state_dir = MagicMock()
        mock_get_state_dir.return_value = mock_state_dir

        expected_log_file = mock_state_dir.__truediv__.return_value

        # Mock umask to return a previous mask
        mock_umask.return_value = 0o022

        # Ensure the handler mock has a level attribute to satisfy logging module
        mock_handler.return_value.level = 0

        reporter = bkb.Reporter(verbose=False)

        # Verify get_state_dir called
        mock_get_state_dir.assert_called_once()

        # Verify log file path construction
        mock_state_dir.__truediv__.assert_called_with("bastardkb_build_releases.log")

        # Verify umask usage (called twice: once to set 0o077, once to restore)
        # Note: We expect umask(0o077) before handler init, and umask(0o022) after
        self.assertEqual(mock_umask.call_count, 2)
        mock_umask.assert_any_call(0o077)
        mock_umask.assert_any_call(0o022)

        # Verify RotatingFileHandler called with correct filename
        mock_handler.assert_called_with(
            filename=expected_log_file,
            encoding="utf-8",
            maxBytes=1024 * 1024,
            backupCount=5
        )

if __name__ == '__main__':
    unittest.main()
