import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
FONT = Path('/System/Library/Fonts/Supplemental/Arial.ttf')


class TypographyTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((SCRIPTS / 'typography.py').exists(), 'reusable typography module is missing')
        from typography import shape_text
        self.shape = shape_text
        if not FONT.exists():
            self.skipTest('Set up an Arial test font on this host')

    def test_latin_has_independent_units_and_vector_outlines(self):
        result = self.shape('Logo', FONT, 30)
        self.assertEqual(len(result['units']), 4)
        self.assertGreater(result['width'], 40)
        self.assertTrue(all(u['shapes'] for u in result['units']))

    def test_combining_accent_stays_with_base(self):
        result = self.shape('a\u0301b', FONT, 30)
        self.assertEqual(len(result['units']), 2)

    def test_arabic_is_one_connected_animation_unit(self):
        result = self.shape('مرحبا', FONT, 30)
        self.assertEqual(len(result['units']), 1)
        self.assertGreater(result['width'], 0)

    def test_missing_glyph_is_reported(self):
        with self.assertRaisesRegex(ValueError, 'glyph|字体|character'):
            self.shape('Logo\U0010ffff', FONT, 30)

    def test_mixed_direction_is_reported(self):
        with self.assertRaisesRegex(ValueError, 'direction'):
            self.shape('Logo مرحبا', FONT, 30)

    def test_newlines_are_not_silently_removed(self):
        with self.assertRaisesRegex(ValueError, 'line'):
            self.shape('Logo\nTranslator', FONT, 30)

    def test_chinese_name_uses_glyph_outlines(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
        if not font.exists(): self.skipTest('Chinese test font unavailable')
        result = self.shape('智能翻译', font, 30)
        self.assertEqual(len(result['units']), 4)
        self.assertTrue(all(unit['shapes'] for unit in result['units']))

    def test_ligature_is_one_animation_unit(self):
        import tempfile
        from fontTools.fontBuilder import FontBuilder
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
        builder = FontBuilder(1000, isTTF=True)
        builder.font.cfg['fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER'] = False
        names = ['.notdef', 'f', 'i', 'fi']
        builder.setupGlyphOrder(names)
        builder.setupCharacterMap({102: 'f', 105: 'i'})
        glyphs = {}
        for name in names:
            pen = TTGlyphPen(None)
            pen.moveTo((0, 0)); pen.lineTo((400, 0)); pen.lineTo((400, 700)); pen.lineTo((0, 700)); pen.closePath()
            glyphs[name] = pen.glyph()
        builder.setupGlyf(glyphs)
        builder.setupHorizontalMetrics({name: (500, 0) for name in names})
        builder.setupHorizontalHeader(ascent=800, descent=-200)
        builder.setupNameTable({'familyName': 'TestLigature', 'styleName': 'Regular'})
        builder.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
        builder.setupPost()
        addOpenTypeFeaturesFromString(builder.font, 'feature liga { sub f i by fi; } liga;')
        with tempfile.TemporaryDirectory() as folder:
            font = Path(folder) / 'test.ttf'
            builder.save(font)
            result = self.shape('fi', font, 30)
            self.assertEqual(len(result['units']), 1)



if __name__ == '__main__':
    unittest.main()
