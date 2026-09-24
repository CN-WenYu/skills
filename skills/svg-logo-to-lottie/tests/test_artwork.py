import json
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from animation import build_animation
from artwork import prepare_artwork
from configuration import DecisionRequired, load_config
from svg_geometry import load_svg


class ArtworkTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / 'logo.svg'
        self.source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                               '<rect id="plate" width="100" height="100" fill="green"/>'
                               '<g id="mark" transform="translate(40 40)">'
                               '<rect width="20" height="20" fill="white"/></g></svg>')
        self.config = {'source': str(self.source), 'source_background': 'preserve',
                       'preview_background': '#181818', 'export_background': {'type': 'transparent'},
                       'artwork': {'existing_wordmark': 'absent', 'backplate': {
                           'mode': 'embedded', 'element_ids': ['plate'],
                           'corners': {'mode': 'rounded', 'radius': 20}}},
                       'motion': {'preset': 'backplate-first'}}

    def prepare(self):
        path = self.root / 'config.json'
        path.write_text(json.dumps(self.config))
        config = load_config(path)
        asset = prepare_artwork(load_svg(self.source), config)
        animation, report = build_animation(asset, config)
        return asset, animation, report

    def test_corners_require_a_specific_choice(self):
        del self.config['artwork']['backplate']['corners']
        with self.assertRaisesRegex(DecisionRequired, 'corner'):
            self.prepare()

    def test_static_plate_requires_user_request(self):
        self.config['motion'] = {'rationale':'A layered entrance', 'tracks':[
            {'name':'Plate', 'target':'backplate','reason':'Brand background',
             'keyframes':[{'time':0,'offset':[0,0],'scale':100,'opacity':100}]},
            {'name':'Foreground','target':'foreground','reason':'Intact symbol',
             'keyframes':[{'time':0,'offset':[0,0],'scale':100,'opacity':100}]}]}
        with self.assertRaisesRegex(DecisionRequired, 'user_request'):
            self.prepare()
        self.config['motion']['tracks'][0]['user_request'] = 'Keep the background visible from the start.'
        self.prepare()

    def test_backplate_first_has_independent_timing_and_transparent_canvas(self):
        asset, animation, report = self.prepare()
        foreground, plate = animation['layers']
        self.assertEqual((foreground['nm'], plate['nm']), ('Foreground', 'Icon backplate'))
        self.assertEqual(foreground['ks']['o']['k'][0]['t'], 6)
        self.assertEqual(plate['ks']['o']['k'][-1]['t'], 6)
        self.assertEqual(plate['ks']['s']['a'], 0)
        self.assertTrue(all(item['nm'] != 'Background' for item in animation['layers']))
        root = ET.fromstring(asset['normalized_svg'])
        rect = next(e for e in root.iter() if e.get('id') == 'plate')
        self.assertEqual(rect.get('rx'), '20')
        self.assertEqual(report['composition']['corner_containment'], 'bounded')

    def test_static_backplate_is_visible_from_first_frame(self):
        self.config['motion'] = {'preset':'static-backplate', 'user_request':'Keep the plate visible from the start.'}
        _, animation, _ = self.prepare()
        self.assertEqual(animation['layers'][-1]['ks']['o'], {'a': 0, 'k': 100})
        self.assertEqual(animation['layers'][0]['ks']['o']['k'][0]['t'], 0)

    def test_whole_icon_keeps_composite_opacity(self):
        self.config['motion']['preset'] = 'whole-icon'
        _, animation, _ = self.prepare()
        self.assertEqual(len(animation['layers']), 1)
        self.assertEqual(animation['layers'][0]['nm'], 'Logo')
        self.assertEqual(len(animation['layers'][0]['shapes']), 2)

    def test_group_id_selects_descendants_and_preserves_transform(self):
        self.source.write_text(self.source.read_text().replace('<rect id="plate"', '<g id="plate-group"><rect id="plate"')
                               .replace('fill="green"/>', 'fill="green"/></g>'))
        self.config['artwork']['backplate'].update(element_ids=['plate-group'], corners={'mode': 'preserve'})
        asset, _, _ = self.prepare()
        self.assertEqual(asset['foreground_bounds'], [40, 40, 60, 60])
        self.assertEqual(len(asset['backplate']), 1)
        self.assertTrue(any('plate-group' in e['ids'] for e in asset['elements']))

    def test_missing_ambiguous_and_foreground_only_ids_stop(self):
        for ids in (['missing'], ['plate', 'mark'], ['mark']):
            with self.subTest(ids=ids):
                self.config['artwork']['backplate'].update(element_ids=ids, corners={'mode': 'preserve'})
                with self.assertRaises(DecisionRequired): self.prepare()

    def test_rounding_does_not_silently_clip_foreground(self):
        self.source.write_text(self.source.read_text().replace('translate(40 40)', 'translate(0 0)'))
        with self.assertRaisesRegex(DecisionRequired, 'outside.*backplate/corners'):
            self.prepare()

    def test_preserve_and_square_corners(self):
        self.source.write_text(self.source.read_text().replace('id="plate"', 'id="plate" rx="12"'))
        for mode, expected in [('preserve', 12), ('square', 0)]:
            with self.subTest(mode=mode):
                self.config['artwork']['backplate']['corners'] = {'mode': mode}
                asset, _, _ = self.prepare()
                self.assertEqual(asset['backplate_boundary']['rx'], expected)

    def test_generated_gradient_is_icon_scoped_and_namespaced(self):
        self.source.write_text(self.source.read_text().replace('<rect id="plate" width="100" height="100" fill="green"/>', ''))
        self.config['artwork']['backplate'] = {'mode': 'generated', 'corners': {'mode': 'rounded', 'radius': 20},
            'paint': {'type': 'linear', 'start': [0, 0], 'end': [100, 100],
                      'stops': [{'offset': 0, 'color': 'green'}, {'offset': 1, 'color': 'blue'}]}}
        asset, animation, _ = self.prepare()
        self.assertEqual(asset['foreground_bounds'], [40, 40, 60, 60])
        self.assertEqual(asset['bounds'], [0, 0, 100, 100])
        self.assertIn('"gf"', json.dumps(animation['layers'][-1]))
        root = ET.fromstring(asset['normalized_svg'])
        self.assertTrue(all(e.tag.startswith('{http://www.w3.org/2000/svg}') for e in root.iter()))
        normalized = self.root / 'normalized.svg'
        normalized.write_text(asset['normalized_svg'])
        self.assertEqual(load_svg(normalized)['shapes'], asset['shapes'])

    def test_name_motion_stays_below_complete_icon(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
        if not font.exists(): self.skipTest('Arial unavailable')
        self.config['wordmark'] = {'text': 'Logo', 'font': str(font), 'color': 'white', 'size': 30, 'gap': 18,
                                   'motion':{'user_request':'Use default hops.'}}
        _, _, report = self.prepare()
        icon, *glyphs = report['animated_bounds']
        self.assertTrue(glyphs)
        self.assertTrue(all(box[1] >= icon[3]-1e-6 for box in glyphs))
        composition = report['composition']
        self.assertAlmostEqual(composition['settled_wordmark_bounds'][1]-composition['settled_icon_bounds'][3], 18)

    def test_generated_plate_does_not_inherit_foreground_root_style(self):
        self.source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill-opacity=".5">'
                               '<rect x="40" y="40" width="20" height="20" fill="red"/></svg>')
        self.config['artwork']['backplate'] = {'mode': 'generated', 'corners': {'mode': 'square'},
                                               'paint': {'type': 'solid', 'color': 'green'}}
        asset, _, _ = self.prepare()
        path = self.root / 'normalized.svg'
        path.write_text(asset['normalized_svg'])
        self.assertEqual(load_svg(path)['shapes'], asset['shapes'])
        self.assertEqual(asset['backplate'][0]['it'][-2]['o']['k'], 100)

    def test_stroke_is_not_mistaken_for_leaking_corner_fill(self):
        self.source.write_text(self.source.read_text().replace('id="plate" width="100" height="100"',
            'id="plate" x="10" y="10" width="80" height="80" stroke="blue" stroke-width="10" stroke-linejoin="round"'))
        _, _, report = self.prepare()
        self.assertFalse(report['composition']['backplate_outline']['probe_corners'])


if __name__ == '__main__': unittest.main()
