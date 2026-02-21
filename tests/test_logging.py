import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Mock pygit2 and rich before import
sys.modules['pygit2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.text'] = MagicMock()

# Ensure we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import bastardkb_build_releases as bkb
from pathlib import Path

class TestSecureLogging(unittest.TestCase):
    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('pathlib.Path.mkdir') # Patching globally for Path since it is imported directly
    @patch('os.umask')
    @patch.dict(os.environ, {'XDG_STATE_HOME': '/tmp/mock_xdg_state'})
    def test_log_creation_security(self, mock_umask, mock_mkdir, mock_handler):
        # Setup mocks
        mock_handler.return_value.level = 0 # As per memory requirement

        # Capture original umask return value to verify restoration
        mock_umask.return_value = 0o022

        # Instantiate Reporter
        reporter = bkb.Reporter(verbose=False)

        # Verify directory creation with secure permissions
        mock_mkdir.assert_called_with(parents=True, exist_ok=True, mode=0o700)

        # Verify umask usage: must be called with 0o077 before handler creation
        # and restored afterwards.
        # We check that the first call sets 0o077 and subsequent call restores 0o022

        # Check calls
        calls = mock_umask.call_args_list
        self.assertTrue(len(calls) >= 2, "os.umask should be called at least twice (set and restore)")

        # Verify first call sets restrictive umask
        self.assertEqual(calls[0][0][0], 0o077, "First call to umask should set 0o077")

        # Verify second call restores original umask
        self.assertEqual(calls[1][0][0], 0o022, "Second call to umask should restore original 0o022")

        # Verify handler created with correct path
        self.assertTrue(mock_handler.called)
        _, kwargs = mock_handler.call_args
        filename = kwargs.get('filename')

        # Convert Path object to string for comparison if necessary
        filename_str = str(filename)
        expected_start = str(Path('/tmp/mock_xdg_state/bastardkb-qmk'))

        self.assertTrue(filename_str.startswith(expected_start), f"Log filename {filename_str} does not start with {expected_start}")
        self.assertTrue(filename_str.endswith('.log'), f"Log filename {filename_str} does not end with .log")

if __name__ == '__main__':
    unittest.main()
