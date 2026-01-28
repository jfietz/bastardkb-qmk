import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock modules
sys.modules['pygit2'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.text'] = MagicMock()

import bastardkb_build_releases

class TestParallelDefault(unittest.TestCase):
    def test_parallel_default_is_cpu_count(self):
        # We want to verify that the argument parser is configured with default=os.cpu_count()

        captured_default = None

        # Original add_argument to keep behavior for other args, but capturing --parallel
        original_add_argument = None

        def side_effect(*args, **kwargs):
            nonlocal captured_default
            if '--parallel' in args:
                captured_default = kwargs.get('default')
            return MagicMock() # We don't need the action object for this test

        with patch('argparse.ArgumentParser.add_argument', side_effect=side_effect):
            # We need to prevent main from actually running things that break
            with patch('bastardkb_build_releases.Reporter'), \
                 patch('bastardkb_build_releases.Repository'), \
                 patch('signal.signal'), \
                 patch('bastardkb_build_releases.Executor'), \
                 patch('bastardkb_build_releases.build'), \
                 patch('bastardkb_build_releases.copy_assets_to_output_dir'), \
                 patch('argparse.ArgumentParser.parse_args'):

                try:
                    bastardkb_build_releases.main()
                except Exception:
                    pass

        expected = os.cpu_count() or 1
        print(f"Detected default: {captured_default}, Expected: {expected}")
        self.assertEqual(captured_default, expected)

if __name__ == '__main__':
    unittest.main()
