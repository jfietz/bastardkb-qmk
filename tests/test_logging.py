import sys
import os
import unittest
from unittest.mock import MagicMock, patch, call
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestLoggingSecurity(unittest.TestCase):
    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('pathlib.Path.mkdir')
    @patch('os.umask')
    @patch.dict(os.environ, {"XDG_STATE_HOME": "/tmp/test_xdg_state"}, clear=True)
    def test_log_file_secure_creation(self, mock_umask, mock_mkdir, mock_handler):
        # Setup mocks
        mock_handler.return_value.level = 0
        mock_umask.return_value = 0o022 # Default umask

        # Mock Console to avoid output during tests
        with patch('bastardkb_build_releases.Console'):
            reporter = bkb.Reporter(verbose=False)

            # Check that get_state_dir was called correctly (implicit via handler call)
            # The expected log dir is /tmp/test_xdg_state/bastardkb-qmk
            expected_log_dir = Path("/tmp/test_xdg_state/bastardkb-qmk")
            expected_log_file = expected_log_dir / f"{os.path.basename(bkb.__file__)}.log"

            # Verify mkdir was called with correct permissions
            # We need to find the call for the state dir
            # Note: Path.mkdir is called on the Path object.
            # Since we patched Path.mkdir, all mkdir calls are captured.
            # We look for the one on our expected path.
            # However, since Path objects are immutable and created on the fly,
            # checking 'self' in the mock call is tricky.
            # But the 'parents=True' and 'mode=0o700' arguments should be present.

            # Instead of relying on checking 'self', we can check if mkdir was called with correct kwargs.
            # But wait, we patched Path.mkdir globally.
            # Let's see if we can assert it was called at least once with the right mode.
            mock_mkdir.assert_called_with(parents=True, mode=0o700)

            # Verify umask was set to 0o077 and then restored
            # Calls should be: umask(0o077), then umask(original)
            expected_calls = [call(0o077), call(0o022)]
            mock_umask.assert_has_calls(expected_calls)

            # Verify RotatingFileHandler was initialized with the correct file path
            args, kwargs = mock_handler.call_args
            filename = kwargs.get('filename')
            self.assertEqual(filename, expected_log_file)

if __name__ == '__main__':
    unittest.main()
