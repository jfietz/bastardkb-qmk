
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock modules before importing bastardkb_build_releases
sys.modules['pygit2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.text'] = MagicMock()

import bastardkb_build_releases

class TestCliDefaults(unittest.TestCase):
    @patch('argparse.ArgumentParser')
    def test_parallel_default(self, mock_parser_class):
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # We need to run the code that sets up arguments.
        # Since it's in main(), we can try to run main() but catch the SystemExit
        # or we can refactor main.
        # But we can't easily run main() because it does other things like Repository() init which we need to mock.

        # Let's mock everything main uses.
        with patch('signal.signal'), \
             patch('bastardkb_build_releases.Repository'), \
             patch('bastardkb_build_releases.Executor'), \
             patch('bastardkb_build_releases.build'), \
             patch('bastardkb_build_releases.copy_assets_to_output_dir'), \
             patch('sys.exit'): # Prevent exit

            # We also need to mock parser.parse_args to return something valid
            mock_args = MagicMock()
            mock_args.verbose = False
            mock_args.dry_run = True
            mock_args.parallel = 1
            mock_args.repository = '.'
            mock_args.output_dir = MagicMock()
            mock_args.filter = '.*'
            mock_parser.parse_args.return_value = mock_args

            bastardkb_build_releases.main()

            # Now inspect calls to add_argument
            found_parallel = False
            import os
            expected_default = os.cpu_count() or 1

            for call in mock_parser.add_argument.call_args_list:
                args, kwargs = call
                if '-j' in args or '--parallel' in args:
                    found_parallel = True
                    self.assertEqual(kwargs.get('default'), expected_default,
                                     f"Default should be {expected_default}, got {kwargs.get('default')}")

            self.assertTrue(found_parallel, "Parallel argument not found")

if __name__ == '__main__':
    unittest.main()
