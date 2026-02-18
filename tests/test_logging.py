import sys
import os
import unittest
import tempfile
import stat
from pathlib import Path
from unittest.mock import MagicMock, patch, call

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing the module under test

# Define a custom Mock for Panel to avoid InvalidSpecError when initialized with positional args
class MockPanel(MagicMock):
    def __init__(self, *args, **kwargs):
        # Do not pass positional args to MagicMock.__init__ as it interprets the first one as 'spec'
        super().__init__(**kwargs)
        if args:
            self.renderable = args[0]

if 'rich' not in sys.modules:
    sys.modules['rich'] = MagicMock()
    sys.modules['rich.console'] = MagicMock()
    sys.modules['rich.live'] = MagicMock()
    sys.modules['rich.panel'] = MagicMock()
    # Use the custom MockPanel class
    sys.modules['rich.panel'].Panel = MockPanel
    sys.modules['rich.progress'] = MagicMock()
    sys.modules['rich.text'] = MagicMock()

if 'pygit2' not in sys.modules:
    sys.modules['pygit2'] = MagicMock()

# Now import the module under test
import bastardkb_build_releases as bkb

class TestLoggingSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as XDG_STATE_HOME
        self.xdg_state_home = tempfile.mkdtemp()
        os.environ['XDG_STATE_HOME'] = self.xdg_state_home

        # Also mock logging to prevent actual file creation during tests if not intended
        self.logging_patcher = patch('bastardkb_build_releases.logging')
        self.mock_logging = self.logging_patcher.start()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.xdg_state_home)
        self.logging_patcher.stop()
        if 'XDG_STATE_HOME' in os.environ:
            del os.environ['XDG_STATE_HOME']

    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('os.umask', side_effect=os.umask)
    def test_secure_logging_setup(self, mock_umask, mock_handler):
        # Mock the handler instance
        mock_handler_instance = mock_handler.return_value
        mock_handler_instance.level = 0

        # Instantiate Reporter
        reporter = bkb.Reporter(verbose=False)

        # 1. Verify log directory location
        expected_log_dir = Path(self.xdg_state_home) / 'bastardkb-qmk'
        self.assertTrue(expected_log_dir.is_dir(), "Log directory was not created")

        # 2. Verify log directory permissions
        mode = os.stat(expected_log_dir).st_mode
        self.assertEqual(mode & 0o777, 0o700, f"Log directory permissions should be 700, got {oct(mode & 0o777)}")

        # 3. Verify RotatingFileHandler was initialized with correct path
        expected_log_file = expected_log_dir / 'bastardkb_build_releases.py.log'

        call_args = mock_handler.call_args
        self.assertIsNotNone(call_args, "RotatingFileHandler was not called")

        args, kwargs = call_args
        filename = kwargs.get('filename') or args[0]
        self.assertEqual(Path(filename), expected_log_file, "Log file path is incorrect")

        # 4. Verify umask was set to 0o077 before creating the handler
        mock_umask.assert_any_call(0o077)
        self.assertIn(call(0o077), mock_umask.call_args_list)

if __name__ == '__main__':
    unittest.main()
