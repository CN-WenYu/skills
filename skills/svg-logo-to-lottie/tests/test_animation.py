import sys
from copy import deepcopy
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))


class AnimationTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((SCRIPTS / 'animation.py').exists(), 'reusable animation exporter missing')
        from animation import build_animation
        self.build = build_animation
        self.asset = {'width': 100, 'height': 100, 'bounds': [0, 0, 100, 100],
                      'shapes': [{'ty': 'gr', 'it': [{'ty': 'rc', 'p': {'a': 0, 'k': [50, 50]},
                                   's': {'a': 0, 'k': [100, 100]}, 'r': {'a': 0, 'k': 0}},
                                  {'ty': 'fl', 'c': {'a': 0, 'k': [1, 0, 0, 1]}, 'o': {'a': 0, 'k': 100}}]}]}
        self.config = {'canvas': {'width': 512, 'height': 512}, 'export_background': {'type': 'transparent'},
                       'motion': {'preset': 'whole-icon'}}

    def test_missing_motion_does_not_apply_a_hidden_preset(self):
        del self.config['motion']
        with self.assertRaisesRegex(ValueError, 'motion plan or explicit preset'):
            self.build(self.asset, self.config)

    def test_transparent_export_has_no_background_assets_or_fonts(self):
        animation, report = self.build(self.asset, self.config)
        self.assertEqual(animation['assets'], [])
        self.assertNotIn('fonts', animation)
        self.assertEqual(len(animation['layers']), 1)
        self.assertEqual(animation['op'] / animation['fr'], 2.4)
        self.assertTrue(all(layer['ty'] == 4 for layer in animation['layers']))

    def test_gradient_background_is_native_and_behind_logo(self):
        self.config['export_background'] = {'type': 'linear', 'start': [0, 0], 'end': [512, 512],
                                             'stops': [{'offset': 0, 'color': '#e23c29'}, {'offset': 1, 'color': '#5522bb'}]}
        animation, _ = self.build(self.asset, self.config)
        self.assertEqual(animation['layers'][-1]['nm'], 'Background')
        self.assertEqual(animation['layers'][-1]['ks']['o']['k'][0]['s'], [0])
        self.assertEqual(animation['layers'][-1]['ks']['o']['k'][-1]['s'], [100])
        self.assertIn('"gf"', __import__('json').dumps(animation['layers'][-1]))

    def test_text_overshoot_remains_inside_canvas(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
        if not font.exists(): self.skipTest('Arial unavailable')
        self.config['wordmark'] = {'text': 'Logo', 'font': str(font), 'size': 30, 'color': '#222222'}
        animation, report = self.build(self.asset, self.config)
        self.assertEqual(len(animation['layers']), 5)
        for box in report['animated_bounds']:
            self.assertGreaterEqual(box[0], 0)
            self.assertGreaterEqual(box[1], 0)
            self.assertLessEqual(box[2], 512)
            self.assertLessEqual(box[3], 512)
        self.assertLess(report['settled_frame'], animation['op'])

    def test_auto_wordmark_layout_scales_from_icon_width(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
        if not font.exists(): self.skipTest('Arial unavailable')
        self.config['canvas'] = {'width': 800, 'height': 760, 'padding': 40, 'icon_width': 400}
        self.config['wordmark'] = {'text': 'Logo', 'font': str(font), 'color': '#222222'}
        animation, report = self.build(self.asset, self.config)
        self.assertEqual(self.config['wordmark']['size'], 72)
        self.assertEqual(self.config['wordmark']['gap'], 48)
        self.assertEqual(report['composition']['wordmark_gap'], 48)
        self.assertEqual(report['composition']['wordmark_size'], 72)
        self.assertEqual(animation['w'], 800)

    def test_automatic_icon_and_text_keep_proportions_and_reproduce(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
        if not font.exists(): self.skipTest('Arial unavailable')
        for canvas_size in (320, 512, 1024):
            with self.subTest(canvas=canvas_size):
                config = {'canvas': {'width': canvas_size, 'height': canvas_size},
                          'motion': {'preset': 'whole-icon'},
                          'wordmark': {'text': 'Logo', 'font': str(font), 'color': 'black'}}
                animation, report = self.build(self.asset, config)
                c = report['composition']
                icon_width = c['settled_icon_bounds'][2]-c['settled_icon_bounds'][0]
                self.assertAlmostEqual(c['wordmark_size']/icon_width, .18)
                self.assertAlmostEqual(c['wordmark_gap']/icon_width, .12)
                self.assertAlmostEqual(c['settled_wordmark_bounds'][1]-c['settled_icon_bounds'][3], .12*icon_width)
                repeated, _ = self.build(self.asset, deepcopy(config))
                self.assertEqual(animation, repeated)

    def test_explicit_wordmark_values_and_partial_overrides_are_preserved(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
        if not font.exists(): self.skipTest('Arial unavailable')
        for override in ({'size': 60}, {'gap': 55}, {'size': 60, 'gap': 55}):
            with self.subTest(override=override):
                config = {'canvas': {'width': 800, 'height': 760, 'icon_width': 400},
                          'motion': {'preset': 'whole-icon'},
                          'wordmark': {'text': 'Logo', 'font': str(font), 'color': 'black', **override}}
                self.build(self.asset, config)
                self.assertEqual(config['wordmark']['size'], override.get('size', 72))
                self.assertEqual(config['wordmark']['gap'], override.get('gap', 48))

    def test_small_explicit_gap_cannot_hide_motion_overlap(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
        if not font.exists(): self.skipTest('Arial unavailable')
        self.config['wordmark'] = {'text': 'Logo', 'font': str(font), 'color': 'black', 'size': 72, 'gap': 0}
        with self.assertRaisesRegex(ValueError, 'overlaps'):
            self.build(self.asset, self.config)

    def test_long_name_is_not_shrunk_or_truncated(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
        if not font.exists(): self.skipTest('Arial unavailable')
        self.config['wordmark'] = {'text': 'A' * 100, 'font': str(font), 'size': 30, 'color': '#222222'}
        with self.assertRaisesRegex(ValueError, 'fit|wide'):
            self.build(self.asset, self.config)

    def test_too_short_duration_cannot_cut_off_bounce(self):
        self.config['duration'] = .2
        with self.assertRaisesRegex(ValueError, 'duration|short'):
            self.build(self.asset, self.config)


class ExportSizeTests(unittest.TestCase):
    def test_exact_compaction_keeps_motion_intervals_and_artwork(self):
        from motion_core import keys
        from preview import optimize_animation
        path = {'v': [[.123456789, 0.0], [10.0, 20.0]],
                'i': [[0.0, 0.0]]*2, 'o': [[0.0, 0.0]]*2, 'c': False}
        moving = keys([(0,[0,0]),(1,[0,0]),(2,[10,0]),(3,[10,0]),(4,[10,0]),(5,[20,0]),(6,[20,0])],30)
        animation = {'layers': [{'nm':'Keep name', 'ks': {'p':moving, 'o':keys([(0,[100]),(1,[100])],30)},
                                'shapes':[{'ty':'sh','ks':{'a':0,'k':path}}]}]}
        original = deepcopy(animation)
        result, report = optimize_animation(animation)
        self.assertEqual(animation, original)
        self.assertEqual(result['layers'][0]['shapes'], original['layers'][0]['shapes'])
        frames = result['layers'][0]['ks']['p']['k']
        self.assertEqual([f['t'] for f in frames],[30,60,90,120,150])
        self.assertEqual(frames[0], moving['k'][1])
        self.assertEqual(frames[-2], moving['k'][4])
        self.assertEqual(result['layers'][0]['ks']['o'], {'a':0,'k':100})
        self.assertEqual(result['layers'][0]['nm'], 'Keep name')
        self.assertLess(report['after_bytes'], report['before_bytes'])
        self.assertEqual(optimize_animation(result)[0], result)

    def test_rounding_only_coordinates_needs_explicit_decision(self):
        from preview import optimize_animation
        animation = {'fr':29.9700001,'layers':[{'ty':4,'ks':{'p':{'a':0,'k':[.123456,5.234567,0]},
                                                    's':{'a':0,'k':[99.123456,99.123456,100]}},
            'shapes':[{'ty':'sh','ks':{'a':0,'k':{'v':[[.123456,0]],'i':[[0,0]],'o':[[.123456,0]],'c':False}}},
                      {'ty':'fl','c':{'a':0,'k':[.123456,.234567,.345678,1]}},
                      {'ty':'gf','g':{'p':2,'k':{'a':0,'k':[0,.123456,0,0,1,0,.234567,0]}}}]}]}
        with self.assertRaisesRegex(ValueError, 'user_request'):
            optimize_animation(animation, {'coordinate_precision':3})
        result, report = optimize_animation(animation, {'coordinate_precision':3,'user_request':'Use three decimal places for coordinates.'})
        self.assertEqual(result['layers'][0]['ks']['p']['k'], [.123,5.235,0])
        self.assertEqual(result['layers'][0]['ks']['s'],animation['layers'][0]['ks']['s'])
        self.assertEqual(result['layers'][0]['shapes'][1:],animation['layers'][0]['shapes'][1:])
        self.assertEqual(result['fr'], animation['fr'])
        self.assertEqual(report['after']['path_vertices'], 1)
        self.assertGreater(report['rounded_coordinates'], 0)

    def test_spatial_tangents_expressions_and_unknown_fields_are_not_trimmed(self):
        from motion_core import keys
        from preview import optimize_animation
        for extra in ({'to':[1,0],'ti':[-1,0]}, {'x':'expression'}, {'h':1}):
            prop = keys([(0,[0,0]),(1,[0,0]),(2,[1,0])],30)
            prop['k'][0].update(extra)
            original = {'layers':[{'ks':{'p':prop}}]}
            self.assertEqual(optimize_animation(original)[0], original)


if __name__ == '__main__': unittest.main()
