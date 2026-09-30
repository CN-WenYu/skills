import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from preview import digest


class ComparisonTests(unittest.TestCase):
    def test_cli_links_verified_drafts_without_copying_or_overwriting(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            drafts = []
            for name in ('one space', 'two#中文'):
                directory = root/name
                directory.mkdir()
                files = {'animation.json': '{"layers":[],"nm":"UNIQUE_PAYLOAD"}',
                         'preview.html': '<html>Preview</html>', 'normalized.svg': '<svg/>',
                         'config.json': json.dumps({'app_name': 'Example'}), 'PLAYER-LICENSE.txt': 'license'}
                for filename, content in files.items(): (directory/filename).write_text(content)
                (directory/'manifest.json').write_text(json.dumps({
                    'files': {k: digest(v.encode()) for k,v in files.items()},
                    'download_filename': 'example_loading.json'}))
                drafts.append(directory)
            output = root/'compare.html'
            command = [sys.executable, str(Path(__file__).resolve().parents[1]/'scripts/logo_lottie.py'),
                       'compare', '--output', str(output), '--variant', 'One <test>', str(drafts[0]),
                       '--variant', 'Two', str(drafts[1]),
                       '--group', 'Theme <pair>', 'One <test>', '--group', 'Theme <pair>', 'Two']
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            page = output.read_text()
            self.assertIn('one%20space/preview.html', page)
            self.assertIn('two%23', page)
            self.assertIn('One &lt;test&gt;', page)
            self.assertNotIn('UNIQUE_PAYLOAD', page)
            self.assertEqual(page.count('<iframe'), 2)
            self.assertEqual(page.count('<section>'), 1)
            self.assertIn('Theme &lt;pair&gt;', page)
            unknown = command.copy()
            unknown[unknown.index(str(output))] = str(root/'unknown.html')
            unknown[-1] = 'Missing'
            self.assertNotEqual(subprocess.run(unknown, capture_output=True).returncode, 0)
            self.assertFalse((root/'unknown.html').exists())
            original = output.read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(output.read_bytes(), original)
            (drafts[1]/'preview.html').write_text('changed')
            command[command.index(str(output))] = str(root/'invalid.html')
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertFalse((root/'invalid.html').exists())


if __name__ == '__main__': unittest.main()
