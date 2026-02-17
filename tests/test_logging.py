import unittest
from unittest.mock import MagicMock, patch
import os
import sys
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to mock pygit2 and rich before importing bastardkb_build_releases
# because they are top-level imports and might not be installed in the test environment.
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
            # Just calling super().__init__() without args/kwargs is safest for avoiding side effects.
            super().__init__()
            if args:
                self.renderable = args[0]
            if 'title' in kwargs:
                self.title = kwargs['title']
    sys.modules["rich.panel"].Panel = MockPanel
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

import bastardkb_build_releases as bkb

class TestLoggingSecurity(unittest.TestCase):

    def test_get_state_dir_default(self):
        # Mock environment
        with patch.dict(os.environ, {}, clear=True):
            def expanduser_side_effect(path):
                 return path.replace("~", "/home/user")

            with patch('os.path.expanduser', side_effect=expanduser_side_effect):
                state_dir = bkb.get_state_dir()
                self.assertEqual(state_dir, Path('/home/user/.local/state/bastardkb-qmk'))

    def test_get_state_dir_xdg(self):
        # Mock environment
        with patch.dict(os.environ, {'XDG_STATE_HOME': '/custom/state'}, clear=True):
            state_dir = bkb.get_state_dir()
            self.assertEqual(state_dir, Path('/custom/state/bastardkb-qmk'))

    @patch.object(bkb, 'get_state_dir')
    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('os.chmod')
    def test_reporter_secure_init(self, mock_chmod, mock_handler, mock_get_state_dir):
        # Setup mock for state dir
        mock_state_dir = MagicMock()
        # Make the path join return another mock or path
        # But reporter uses state_dir / filename
        # We need __truediv__ on the mock
        mock_log_file = MagicMock()
        mock_state_dir.__truediv__.return_value = mock_log_file

        mock_get_state_dir.return_value = mock_state_dir

        mock_handler.return_value.level = 0

        reporter = bkb.Reporter(verbose=False)

        # Verify get_state_dir called
        mock_get_state_dir.assert_called_once()

        # Verify mkdir called on state dir
        # mock_state_dir is a MagicMock. mkdir is a method on it.
        mock_state_dir.mkdir.assert_called_with(parents=True, exist_ok=True)

        # Verify chmod called on state dir
        mock_chmod.assert_any_call(mock_state_dir, 0o700)

        # Verify chmod called on log file
        mock_chmod.assert_any_call(mock_log_file, 0o600)

        # Verify handler initialized with log file
        args, kwargs = mock_handler.call_args
        self.assertEqual(kwargs['filename'], mock_log_file)

if __name__ == '__main__':
    unittest.main()
