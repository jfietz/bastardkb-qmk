import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Mock dependencies before import
sys.modules['pygit2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.text'] = MagicMock()

# Ensure the module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestStartup(unittest.TestCase):
    @patch('shutil.which')
    @patch('sys.exit')
    @patch('bastardkb_build_releases.Reporter')
    @patch('bastardkb_build_releases.Repository')
    def test_missing_qmk(self, mock_repo, mock_reporter, mock_exit, mock_which):
        """Test that missing qmk triggers a fatal error and exit."""
        # Setup mocks
        mock_which.side_effect = lambda cmd: None if cmd == 'qmk' else '/usr/bin/git'

        # Mock repository to bypass checks (though we expect to exit before this)
        mock_repo.return_value.is_bare = True

        # Mock sys.argv
        with patch.object(sys, 'argv', ['bastardkb_build_releases.py', '--dry-run']):
            try:
                bkb.main()
            except SystemExit:
                pass
            except Exception as e:
                # If no check, it might proceed and fail elsewhere, which is fine for the "before" state
                pass

        # Verify that reporter.fatal was called with the correct message
        mock_reporter_instance = mock_reporter.return_value

        # Filter calls to fatal to find the one we expect
        fatal_calls = [str(args[0]) for args, _ in mock_reporter_instance.fatal.call_args_list]
        found = any("Command not found: qmk" in arg for arg in fatal_calls)

        self.assertTrue(found, f"Expected fatal error 'Command not found: qmk' not found. Actual calls: {fatal_calls}")

        # Verify sys.exit(1) was called
        mock_exit.assert_called_with(1)

    @patch('shutil.which')
    @patch('sys.exit')
    @patch('bastardkb_build_releases.Reporter')
    @patch('bastardkb_build_releases.Repository')
    def test_missing_git(self, mock_repo, mock_reporter, mock_exit, mock_which):
        """Test that missing git triggers a fatal error and exit."""
        # Setup mocks
        mock_which.side_effect = lambda cmd: None if cmd == 'git' else '/usr/bin/qmk'

        # Mock sys.argv
        with patch.object(sys, 'argv', ['bastardkb_build_releases.py', '--dry-run']):
            try:
                bkb.main()
            except SystemExit:
                pass

        mock_reporter_instance = mock_reporter.return_value
        fatal_calls = [str(args[0]) for args, _ in mock_reporter_instance.fatal.call_args_list]
        found = any("Command not found: git" in arg for arg in fatal_calls)

        self.assertTrue(found, f"Expected fatal error 'Command not found: git' not found. Actual calls: {fatal_calls}")
        mock_exit.assert_called_with(1)

if __name__ == '__main__':
    unittest.main()
