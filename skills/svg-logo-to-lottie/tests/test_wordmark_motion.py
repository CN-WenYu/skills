from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from animation import plan_wordmark, compile_wordmark
from configuration import DecisionRequired, load_config


def frame(time, offset=(0, 0), scale=100, opacity=100):
    return dict(time=time, offset=list(offset), scale=scale, opacity=opacity)


class WordmarkMotionTests(unittest.TestCase):
    def setUp(self):
        self.text = {'units': [{'bounds': [x, -10, x+8, 0], 'shapes': []}
                               for x in (0, 10, 20, 30)],
                     'bounds': [0, -10, 38, 0], 'width': 38}
        self.motion = {'rationale': 'Assemble the name from four directions.',
                       'user_request': 'Bring the name together from four sides.',
                       'tracks': [{'units': [i], 'keyframes': [frame(.2, offset, 90, 0),
                                                              frame(.5, tuple(v/4 for v in offset)), frame(1)]}
                                  for i, offset in enumerate(((-1, 0), (1, 0), (0, -1), (0, 1)))]}
        self.wordmark = {'text': 'ABCD', 'font': 'unused.ttf', 'size': 20,
                         'color': 'white', 'motion': self.motion}

    def load(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'
            path.write_text(json.dumps({'source': 'logo.svg',
                'artwork': {'existing_wordmark': 'absent', 'backplate': {'mode': 'none'}},
                'motion': {'preset': 'whole-icon'}, 'wordmark': self.wordmark}))
            return load_config(path)

    def test_four_sided_motion_exports_offsets_and_preserves_final_layout(self):
        self.load()
        planned, bounds, end = plan_wordmark(self.text, self.wordmark, 0)
        layers, _, samples = compile_wordmark(planned, self.wordmark, self.text, 200, 100, 30, 45)
        self.assertEqual(end, 1)
        self.assertEqual(len(layers), 4)
        for item, expected in zip(layers, ((-20, 0), (20, 0), (0, -20), (0, 20))):
            positions = item['ks']['p']['k']
            self.assertEqual(positions[0]['t'], 6)
            self.assertEqual(positions[-1]['t'], 30)
            self.assertEqual([positions[0]['s'][i]-positions[-1]['s'][i] for i in (0, 1)], list(expected))
            self.assertEqual(item['ks']['s']['k'][-1]['s'], [100, 100, 100])
            self.assertEqual(item['ks']['o']['k'][-1]['s'], [100])
        self.assertEqual([item['ks']['p']['k'][-1]['s'][0] for item in layers], [85, 95, 105, 115])
        self.assertLess(bounds[0], 0)
        self.assertLess(bounds[1], -10)
        self.assertEqual(bounds[2], 38)
        self.assertGreater(bounds[3], 0)
        self.assertTrue({.2, .5, 1} <= samples)

    def test_line_track_preserves_shaping_and_uses_authored_easing(self):
        self.motion['tracks'] = [{'target': 'line', 'easing': [0, 0, 1, 1],
                                 'keyframes': [frame(.4, (0, .2), opacity=0), frame(.8)]}]
        self.load()
        planned, _, _ = plan_wordmark(self.text, self.wordmark, 0)
        layers, _, _ = compile_wordmark(planned, self.wordmark, self.text, 200, 100, 30, 45)
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0]['ks']['p']['k'][0]['o'], {'x': [0], 'y': [0]})
        self.assertEqual(layers[0]['ks']['p']['k'][0]['s'], [100, 114, 0])

    def test_missing_duplicate_or_out_of_range_units_cannot_drop_or_split_text(self):
        original = deepcopy(self.motion['tracks'])
        for tracks in (original[:-1], original+[original[0]],
                       [dict(original[0], units=[4])]+original[1:]):
            with self.subTest(tracks=tracks):
                self.motion['tracks'] = tracks
                with self.assertRaisesRegex(DecisionRequired, 'units'):
                    plan_wordmark(self.text, self.wordmark, 0)
        self.motion['tracks'] = original
        connected = dict(self.text, units=[{'bounds': self.text['bounds'], 'shapes': []}])
        with self.assertRaisesRegex(DecisionRequired, 'units'):
            plan_wordmark(connected, self.wordmark, 0)

    def test_invalid_or_ambiguous_timeline_is_rejected(self):
        original = deepcopy(self.motion)
        changes = [lambda m: m.update(preset='hop'), lambda m: m.update(stagger=.1),
                   lambda m: m.update(rationale=''), lambda m: m.update(tracks=[]),
                   lambda m: m['tracks'][0].update(units=[True]),
                   lambda m: m['tracks'][0].update(easing=[0, 0, 1, 2]),
                   lambda m: m['tracks'][0]['keyframes'][0].update(time=-.1),
                   lambda m: m['tracks'][0]['keyframes'][1].update(time=.2),
                   lambda m: m['tracks'][0]['keyframes'][0].update(offset=[float('nan'), 0]),
                   lambda m: m['tracks'][0]['keyframes'][0].update(scale=0),
                   lambda m: m['tracks'][0]['keyframes'][0].update(opacity=101),
                   lambda m: m['tracks'][0]['keyframes'][0].update(rotation=10),
                   lambda m: m['tracks'][0]['keyframes'][-1].update(offset=[1, 0])]
        for change in changes:
            self.wordmark['motion'] = deepcopy(original)
            change(self.wordmark['motion'])
            with self.subTest(motion=self.wordmark['motion']):
                with self.assertRaises(DecisionRequired): self.load()

    def test_delegation_without_a_concrete_plan_does_not_invent_hops(self):
        self.wordmark['motion'] = {'user_request': 'Choose a restrained motion.'}
        with self.assertRaisesRegex(DecisionRequired, 'preset|tracks'):
            self.load()

    def build_real(self, directory):
        from animation import build_animation
        from artwork import prepare_artwork
        from svg_geometry import load_svg
        font = Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
        if not font.exists(): self.skipTest('Arial Bold unavailable')
        self.wordmark['font'] = str(font)
        source = directory / 'logo.svg'
        source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                          '<rect width="100" height="100" fill="blue"/></svg>')
        config = self.load()
        config.update(source=str(source), canvas={'width': 512, 'height': 512, 'icon_width': 180},
                      preview_background='white')
        asset = prepare_artwork(load_svg(source), config)
        animation, report = build_animation(asset, config)
        return config, asset, animation, report

    def test_real_shaping_preserves_final_geometry_and_rejects_motion_overflow(self):
        from animation import build_animation
        with tempfile.TemporaryDirectory() as directory:
            config, asset, animation, report = self.build_real(Path(directory))
            repeated, _ = build_animation(asset, deepcopy(config))
            self.assertEqual(animation, repeated)
            self.assertEqual(report['composition']['wordmark_motion']['preset'], 'authored')
            self.assertEqual(report['composition']['wordmark_motion']['beats'][0]['frames'][0]['offset_x'], -20)
            for box in report['animated_bounds'][1:]:
                self.assertGreaterEqual(box[1], report['animated_bounds'][0][3])
            self.motion['tracks'][0]['keyframes'][0]['offset'] = [-100, 0]
            with self.assertRaisesRegex(ValueError, 'fit|clipping'):
                self.build_real(Path(directory))

    def test_authored_text_in_actual_web_player(self):
        from preview import write_draft, optimize_animation
        runtime = os.environ.get('LOTTIE_PLAYWRIGHT_PACKAGE')
        player = os.environ.get('LOTTIE_PLAYER_PACKAGE')
        if not runtime or not player: self.skipTest('Web runtime required')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config, asset, animation, report = self.build_real(root)
            animation, report['size'] = optimize_animation(animation)
            draft = root / 'draft'
            write_draft(draft, config, asset, animation, report, player)
            command = [sys.executable, str(Path(__file__).resolve().parents[1]/'scripts/logo_lottie.py'),
                       'validate', str(draft), '--playwright-package', runtime,
                       '--browser-channel', os.environ.get('LOTTIE_BROWSER_CHANNEL', 'chromium')]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            evidence = json.loads((draft/'validation.json').read_text())
            self.assertEqual(evidence['web'], 'passed')
            self.assertEqual(evidence['download'], 'passed')
            samples = {s['frame']: s for s in evidence['samples']}
            middle, settled = samples[15], samples[30]
            for i, (dx, dy) in enumerate(((-5, 0), (5, 0), (0, -5), (0, 5)), 1):
                for axis, offset in (('X', dx), ('Y', dy)):
                    name = f'Wordmark {i}'
                    self.assertAlmostEqual(middle[f'roleAnchor{axis}'][name]-settled[f'roleAnchor{axis}'][name],
                                           offset, delta=.1)


if __name__ == '__main__':
    unittest.main()
