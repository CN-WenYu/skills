import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from svg_geometry import SVGError, load_svg, path_to_shapes


class SVGGeometryTests(unittest.TestCase):
    def svg(self, body, attrs='viewBox="0 0 100 100"'):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.svg'
            path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}>{body}</svg>')
            return load_svg(path)

    def test_viewbox_transform_and_painter_order(self):
        result = self.svg('<g transform="translate(10,20)"><rect x="10" y="20" width="10" height="5" fill="red"/><path d="M10 20h5v5z" fill="blue"/></g>', 'viewBox="10 20 100 100"')
        groups = result['shapes']
        self.assertEqual(groups[0]['it'][-2]['c']['k'], [0, 0, 1, 1])
        self.assertEqual(result['bounds'], [10, 20, 20, 25])
        self.assertIn('viewBox="0 0 100 100"', result['normalized_svg'])

    def test_all_path_commands_and_holes(self):
        shapes = path_to_shapes('M0 0h10v10l-5 0q-5 0-5-5t5-5c1 0 2 1 3 2s1 2 2 3a2 2 0 0 1-2 2z M2 2L3 2L3 3Z')
        self.assertEqual(len(shapes), 2)
        self.assertTrue(all(s['ks']['k']['c'] for s in shapes))
        group = self.svg('<path fill-rule="evenodd" d="M0 0H50V50H0Z M10 10H40V40H10Z"/>')['shapes'][0]
        self.assertEqual(group['it'][-2]['r'], 2)

    def test_style_stroke_and_rotated_bounds(self):
        result = self.svg('<g style="fill:none;stroke:#ff0000;stroke-width:2;stroke-linecap:round;stroke-linejoin:bevel"><line x1="0" y1="0" x2="10" y2="0" transform="translate(20 20) rotate(90) scale(2)"/></g>')
        stroke = result['shapes'][0]['it'][-2]
        self.assertEqual((stroke['ty'], stroke['w']['k'], stroke['lc'], stroke['lj']), ('st', 4, 2, 3))
        for actual, expected in zip(result['bounds'], [18, 18, 22, 42]):
            self.assertAlmostEqual(actual, expected)

    def test_linear_and_radial_gradients(self):
        for kind in ['linearGradient', 'radialGradient']:
            result = self.svg(f'<defs><{kind} id="paint"><stop offset="0%" stop-color="red"/><stop offset="100%" stop-color="blue" stop-opacity="0.5"/></{kind}></defs><rect width="80" height="80" fill="url(#paint)"/>')
            fill = result['shapes'][0]['it'][-2]
            self.assertEqual(fill['ty'], 'gf')
            self.assertEqual(fill['t'], 1 if kind == 'linearGradient' else 2)
            self.assertEqual(fill['g']['p'], 2)
            self.assertEqual(fill['g']['k']['k'][-1], .5)

    def test_group_opacity_rejected_when_multiple_visible_children(self):
        with self.assertRaisesRegex(SVGError, 'opacity'):
            self.svg('<g opacity=".5"><rect width="10" height="10"/><circle r="10"/></g>')

    def test_unsupported_features_fail_actionably(self):
        cases = ['<rect width="5" height="5" class="x"/>', '<use href="#x"/>', '<text>hi</text>', '<path d="M0 0h1" stroke-dasharray="1 1"/>', '<style>path{fill:red}</style>', '<path d="M0 0h1" filter="url(#x)"/>', '<rect width="10" height="10" mysterious-visual="1"/>']
        for body in cases:
            with self.subTest(body=body), self.assertRaises(SVGError):
                self.svg(body)

    def test_gradient_and_stroke_transform_rejections(self):
        with self.assertRaisesRegex(SVGError, 'stroke'):
            self.svg('<path d="M0 0H10" stroke="red" transform="scale(2 1)"/>')
        with self.assertRaisesRegex(SVGError, 'spreadMethod'):
            self.svg('<defs><linearGradient id="g" spreadMethod="repeat"><stop offset="0"/></linearGradient></defs><rect width="10" height="10" fill="url(#g)"/>')

    def test_compound_affine_and_root_transform_normalization(self):
        result = self.svg('<g transform="matrix(1 0 0 1 3 4)"><path transform="skewX(45)" d="M0 0L10 0L0 10Z"/></g>', 'viewBox="10 20 100 100" transform="scale(2)"')
        vertices = result['shapes'][0]['it'][0]['ks']['k']['v']
        for actual, expected in zip(vertices, [[-4, -12], [16, -12], [16, 8]]):
            for a, b in zip(actual, expected):
                self.assertAlmostEqual(a, b)
        self.assertIn('translate(-10 -20) scale(2)', result['normalized_svg'])

    def test_linear_gradient_affine_uses_inverse_transpose(self):
        result = self.svg('<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="10" y2="0"><stop offset="0"/><stop offset="1" stop-color="white"/></linearGradient></defs><rect width="10" height="10" fill="url(#g)" transform="skewX(45)"/>')
        fill = result['shapes'][0]['it'][-2]
        self.assertEqual(fill['s']['k'], [0, 0])
        self.assertAlmostEqual(fill['e']['k'][0], 5)
        self.assertAlmostEqual(fill['e']['k'][1], -5)

    def test_elliptical_radial_gradient_rejected(self):
        with self.assertRaisesRegex(SVGError, 'Elliptical'):
            self.svg('<defs><radialGradient id="g"><stop offset="0"/><stop offset="1" stop-color="white"/></radialGradient></defs><rect width="20" height="10" fill="url(#g)"/>')

    def test_nonfinite_path_rejected(self):
        with self.assertRaisesRegex(SVGError, 'finite'):
            path_to_shapes('M1e999 0L10 10')

    def test_single_shape_group_opacity_and_rounded_rect(self):
        result = self.svg('<g opacity=".5"><rect width="20" height="10" rx="2"/></g>')
        group = result['shapes'][0]
        self.assertEqual(group['it'][-1]['o']['k'], 50)
        self.assertTrue(any(pair != [0, 0] for pair in group['it'][0]['ks']['k']['i']))

    def test_stroke_paints_above_fill(self):
        result = self.svg('<rect x="10" y="10" width="20" height="20" fill="red" stroke="blue" stroke-width="4"/>')
        self.assertEqual([item['ty'] for item in result['shapes'][0]['it']], ['sh', 'st', 'fl', 'tr'])

    def test_metadata_is_not_embedded_in_preview_svg(self):
        result = self.svg('<metadata><script>alert(1)</script></metadata><rect width="10" height="10"/>')
        self.assertNotIn('script', result['normalized_svg'])

    def test_group_visibility_can_be_overridden_by_child(self):
        result = self.svg('<g visibility="hidden"><rect width="10" height="10"/><circle visibility="visible" cx="50" cy="50" r="5"/></g>')
        self.assertEqual(len(result['shapes']), 1)
        self.assertEqual(result['shapes'][0]['nm'], 'circle')

    def test_user_space_gradient_percentages_with_nonzero_viewbox(self):
        result = self.svg('<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="10%" x2="90%" y1="0%" y2="100%"><stop offset="0" stop-color="red"/><stop offset="1" stop-color="blue"/></linearGradient></defs><rect x="10" y="20" width="120" height="80" fill="url(#g)"/>', 'viewBox="10 20 120 80"')
        fill = result['shapes'][0]['it'][-2]
        self.assertEqual(fill['s']['k'], [2, -20])
        self.assertEqual(fill['e']['k'], [98, 60])
        self.assertIn('translate(-10 -20)', result['normalized_svg'])

    def test_gradient_stop_animation_rejected(self):
        with self.assertRaisesRegex(SVGError, 'stop.*children|children.*stop'):
            self.svg('<defs><linearGradient id="g"><stop offset="0"><animate attributeName="stop-color" values="red;blue" dur="1s"/></stop></linearGradient></defs><rect width="10" height="10" fill="url(#g)"/>')

    def test_root_viewport_aspect_mismatch_rejected(self):
        for aspect in ['', 'preserveAspectRatio="none"', 'preserveAspectRatio="xMinYMin slice"']:
            with self.subTest(aspect=aspect), self.assertRaisesRegex(SVGError, 'aspect ratio'):
                self.svg('<rect width="10" height="10"/>', f'viewBox="0 0 100 100" width="200" height="100" {aspect}')

    def test_proportional_root_viewport_supported(self):
        result = self.svg('<rect width="10" height="10"/>', 'viewBox="0 0 100 50" width="200px" height="100px"')
        self.assertEqual((result['width'], result['height']), (100, 50))

    def test_percentage_root_viewport_rejected(self):
        with self.assertRaisesRegex(SVGError, 'length'):
            self.svg('<rect width="10" height="10"/>', 'viewBox="0 0 100 100" width="100%" height="100%"')

    def test_fully_transparent_or_zero_width_paints_are_not_visible(self):
        paints = ['fill="red" fill-opacity="0"', 'fill="#12345600"',
                  'fill="none" stroke="blue" stroke-opacity="0"',
                  'fill="none" stroke="#12345600"',
                  'fill="none" stroke="blue" stroke-width="0"']
        for paint in paints:
            with self.subTest(paint=paint), self.assertRaisesRegex(SVGError, 'no visible'):
                self.svg(f'<rect width="20" height="20" {paint}/>')

    def test_fully_transparent_gradient_is_not_visible(self):
        for kind in ['linearGradient', 'radialGradient']:
            for paint in ['fill="url(#g)"', 'fill="none" stroke="url(#g)"']:
                with self.subTest(kind=kind, paint=paint), self.assertRaisesRegex(SVGError, 'no visible'):
                    self.svg(f'<defs><{kind} id="g"><stop offset="0" stop-color="#ff000000"/><stop offset="1" stop-color="blue" stop-opacity="0"/></{kind}></defs><rect width="20" height="20" {paint}/>')

    def test_transparent_fill_keeps_visible_stroke(self):
        result = self.svg('<rect x="20" y="20" width="20" height="20" fill="#ff000000" stroke="blue" stroke-width="4" stroke-linejoin="round" opacity=".5"/>')
        items = result['shapes'][0]['it']
        self.assertEqual([item['ty'] for item in items], ['sh', 'st', 'tr'])
        self.assertEqual(items[-1]['o']['k'], 50)
        self.assertEqual(result['bounds'], [18, 18, 42, 42])

    def test_invisible_geometry_does_not_expand_bounds(self):
        result = self.svg('<rect width="100" height="100" fill-opacity="0"/><rect x="20" y="20" width="10" height="10" fill="red" stroke="blue" stroke-opacity="0" stroke-width="100"/>')
        self.assertEqual(len(result['shapes']), 1)
        self.assertEqual(result['bounds'], [20, 20, 30, 30])
        self.assertEqual([item['ty'] for item in result['shapes'][0]['it']], ['sh', 'fl', 'tr'])

    def test_partial_solid_and_gradient_alpha_preserved(self):
        solid = self.svg('<rect width="20" height="20" fill="#ff000080" fill-opacity=".5"/>')['shapes'][0]['it'][-2]
        self.assertAlmostEqual(solid['o']['k'], 100*.5*128/255)
        result = self.svg('<defs><linearGradient id="g"><stop offset="0" stop-color="#ff000000"/><stop offset="1" stop-color="#0000ff80" stop-opacity=".5"/></linearGradient></defs><rect width="20" height="20" fill="url(#g)" fill-opacity=".25"/>')
        fill = result['shapes'][0]['it'][-2]
        self.assertEqual(fill['o']['k'], 25)
        self.assertAlmostEqual(fill['g']['k']['k'][-1], .5*128/255)


if __name__ == '__main__':
    unittest.main()
