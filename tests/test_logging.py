import sys
import unittest
from unittest.mock import MagicMock, patch, call
import os
from pathlib import Path

# Mock dependencies before importing the module under test
sys.modules['pygit2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.text'] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestLogging(unittest.TestCase):
    def setUp(self):
        # We need to mock RotatingFileHandler because it tries to open files
        self.rfh_patcher = patch('bastardkb_build_releases.RotatingFileHandler')
        self.mock_rfh = self.rfh_patcher.start()

        # We also need to patch logging.getLogger so we don't pollute the global logger
        self.logger_patcher = patch('bastardkb_build_releases.logging.getLogger')
        self.mock_logger = self.logger_patcher.start()

        # Mocking console to avoid printing
        self.console_patcher = patch('bastardkb_build_releases.Console')
        self.mock_console = self.console_patcher.start()

    def tearDown(self):
        self.rfh_patcher.stop()
        self.logger_patcher.stop()
        self.console_patcher.stop()

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.chmod')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.touch')
    def test_get_state_dir_xdg(self, mock_touch, mock_exists, mock_chmod, mock_mkdir):
        """Test that XDG_STATE_HOME is respected."""
        mock_exists.return_value = False
        with patch.dict(os.environ, {'XDG_STATE_HOME': '/tmp/xdg_state'}):
            reporter = bkb.Reporter(verbose=False)
            state_dir = reporter.get_state_dir()
            self.assertEqual(state_dir, Path('/tmp/xdg_state/bastardkb-qmk'))

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.chmod')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.touch')
    def test_get_state_dir_default(self, mock_touch, mock_exists, mock_chmod, mock_mkdir):
        """Test fallback to ~/.local/state."""
        mock_exists.return_value = False
        with patch.dict(os.environ, {}, clear=True):
            with patch('pathlib.Path.home', return_value=Path('/home/testuser')):
                reporter = bkb.Reporter(verbose=False)
                state_dir = reporter.get_state_dir()
                self.assertEqual(state_dir, Path('/home/testuser/.local/state/bastardkb-qmk'))

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.chmod')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.touch')
    def test_log_initialization_secure(self, mock_touch, mock_exists, mock_chmod, mock_mkdir):
        """Test that log directory and file are initialized with secure permissions."""
        # Setup mocks
        # We simulate that the directory does NOT exist, and the file does NOT exist.
        mock_exists.side_effect = [False, False, False, False]

        with patch.dict(os.environ, {'XDG_STATE_HOME': '/tmp/secure_logs'}):
            reporter = bkb.Reporter(verbose=False)

            expected_dir = Path('/tmp/secure_logs/bastardkb-qmk')
            expected_log = expected_dir / 'bastardkb_build_releases.py.log'

            # Verify mkdir called for directory with correct permissions?
            # Note: We rely on chmod in our implementation for strict 0700.
            # But checking if at least one attempt to secure it was made.

            # Implementation does:
            # self.state_dir.mkdir(parents=True, mode=0o700)
            # self.state_dir.chmod(0o700)

            # Verify mkdir call
            # Note: call_args depends on implementation detail, but we can check if it was called.
            self.assertTrue(mock_mkdir.called)

            # Verify chmod called on directory and file
            # 0o700 for dir, 0o600 for file
            mock_chmod.assert_any_call(0o700)
            mock_chmod.assert_any_call(0o600)

            # Verify RotatingFileHandler initialized with correct path
            self.mock_rfh.assert_called_with(
                filename=str(expected_log),
                encoding="utf-8",
                maxBytes=1024 * 1024,
                backupCount=5
            )

if __name__ == '__main__':
    unittest.main()
