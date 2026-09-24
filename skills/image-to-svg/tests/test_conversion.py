import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'convert_image_to_svg.py'
spec = importlib.util.spec_from_file_location('conversion', SCRIPT)
conversion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conversion)


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def invoke(self, image, *args):
        source = self.root / 'input.png'
        image.save(source)
        return subprocess.run([sys.executable, str(SCRIPT), str(source), *args],
                              text=True, capture_output=True)

    def test_auto_does_not_create_output_or_remove_background(self):
        im = Image.new('RGBA', (64, 64), 'white')
        ImageDraw.Draw(im).rectangle((16, 16, 48, 48), fill='red')
        output = self.root / 'out.svg'
        result = self.invoke(im, str(output))
        self.assertFalse(output.exists(), result.stdout)
        self.assertEqual(json.loads(result.stdout)['status'], 'needs_decision')

    def test_explicit_preserve_keeps_transparent_red_icon(self):
        im = Image.new('RGBA', (64, 64))
        ImageDraw.Draw(im).rectangle((12, 12, 52, 52), fill='#e23c29')
        output = self.root / 'out.svg'
        result = self.invoke(im, str(output), '--background', 'preserve', '--mode', 'polygon')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('#e23c29', output.read_text().lower())
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'ready')
        self.assertIn('matte_rmse', report['visual_validation'])

    def test_remove_preserves_enclosed_white_detail(self):
        im = Image.new('RGBA', (64, 64), 'white')
        draw = ImageDraw.Draw(im)
        draw.rectangle((10, 10, 54, 54), fill='red')
        draw.rectangle((25, 25, 39, 39), fill='white')
        prepared, _ = conversion.prepare(im, conversion.inspect(im), 'remove', 'keep', None)
        self.assertEqual(prepared.getpixel((0, 0))[3], 0)
        self.assertEqual(prepared.getpixel((30, 30)), (255, 255, 255, 255))

    def test_gradient_cannot_use_flat_background_removal(self):
        im = Image.new('RGBA', (64, 64))
        for x in range(64):
            for y in range(64):
                im.putpixel((x, y), (x * 4, 30, 220, 255))
        output = self.root / 'out.svg'
        result = self.invoke(im, str(output), '--background', 'remove')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'needs_decision')
        self.assertFalse(output.exists())

    def test_partial_alpha_requires_explicit_decision(self):
        im = Image.new('RGBA', (32, 32), (226, 60, 41, 128))
        result = self.invoke(im, str(self.root / 'out.svg'), '--background', 'preserve')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'needs_decision')
        self.assertFalse((self.root / 'out.svg').exists())

    def test_recolor_cannot_pass_visual_validation(self):
        im = Image.new('RGBA', (64, 64), '#e23c29')
        svg = self.root / 'wrong.svg'
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><path fill="white" d="M0 0H64V64H0Z"/></svg>')
        report = conversion.verify_render(svg, im)
        self.assertEqual(report['status'], 'low-fidelity')

    def test_existing_output_is_not_overwritten(self):
        output = self.root / 'out.svg'
        output.write_text('existing work')
        result = self.invoke(Image.new('RGBA', (32, 32), 'red'), str(output), '--background', 'preserve')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_text(), 'existing work')

    def test_similar_source_colors_are_not_merged(self):
        im = Image.new('RGBA', (100, 100))
        draw = ImageDraw.Draw(im)
        draw.rectangle((10, 10, 40, 89), fill='#ff0000')
        draw.rectangle((60, 10, 90, 89), fill='#eb0000')
        output = self.root / 'out.svg'
        result = self.invoke(im, str(output), '--background', 'preserve', '--no-svgo')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('#eb0000', output.read_text().lower())
        self.assertIn('#ff0000', output.read_text().lower())

    def test_transparent_gray_gradient_requires_decision(self):
        im = Image.new('RGBA', (100, 100))
        for x in range(10, 90):
            for y in range(10, 90):
                im.putpixel((x, y), (x + 40, x + 40, x + 40, 255))
        result = self.invoke(im, str(self.root / 'out.svg'), '--background', 'preserve')
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertFalse((self.root / 'out.svg').exists())


if __name__ == '__main__':
    unittest.main()
