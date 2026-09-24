import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
FIXTURES = Path(__file__).resolve().parents[1]/'evals'/'fixtures'
sys.path.insert(0, str(SCRIPTS))
from configuration import download_filename, load_config
from typography import font_candidates, shape_text

BOLD = Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')

SCRIPT = SCRIPTS / 'logo_lottie.py'
PLAYER = Path(os.environ.get('LOTTIE_PLAYER_PACKAGE', '/tmp/logo-lottie-web-runtime/node_modules/lottie-web'))


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.svg = self.root / 'logo.svg'
        self.svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="red"/></svg>')
        self.config = {'source': str(self.svg), 'app_name': 'ExampleApp Pro', 'source_background': 'preserve',
                       'artwork': {'existing_wordmark': 'absent', 'backplate': {'mode': 'none'}},
                       'motion': {'preset': 'whole-icon'},
                       'preview_background': '#ffffff',
                       'export_background': {'type': 'transparent'}}

    def run_cli(self, command='inspect', extra=()):
        self.assertTrue(SCRIPT.exists(), 'workflow CLI is missing')
        path = self.root / 'config.json'
        path.write_text(json.dumps(self.config))
        args = [sys.executable, str(SCRIPT), command, str(path)]
        if command == 'draft':
            args += ['--output', str(self.root / 'draft'), '--player-package', str(PLAYER)]
        result = subprocess.run(args + list(extra), text=True, capture_output=True)
        return result, json.loads(result.stdout)

    def test_unspecified_canvas_background_uses_transparent_default(self):
        del self.config['export_background']
        result, report = self.run_cli()
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report['composition']['export_background'], 'transparent')
        self.assertFalse((self.root / 'draft').exists())

    def test_unsupported_svg_reports_question(self):
        self.svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><image href="logo.png"/></svg>')
        result, report = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report['status'], 'needs_decision')

    def test_invalid_background_type_reports_question_without_traceback(self):
        for kind in ([], {}, 1, None):
            with self.subTest(kind=kind):
                self.config['export_background'] = {'type': kind}
                result, report = self.run_cli()
                self.assertEqual(result.returncode, 2)
                self.assertEqual(report['status'], 'needs_decision')
                self.assertIn('export_background.type', str(report))
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse((self.root / 'draft').exists())

    def test_unknown_config_cannot_be_silently_ignored(self):
        self.config['remove_background'] = True
        result, report = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn('remove_background', str(report))

    def test_boolean_roles_do_not_confirm_scope_or_corners(self):
        del self.config['artwork']
        self.config['asset_roles_confirmed'] = True
        result, report = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn('Replace asset_roles_confirmed', str(report))

    def test_missing_motion_requires_agent_plan_not_a_corner_question(self):
        self.config['artwork']['backplate'] = {'mode': 'embedded', 'element_ids': ['plate'], 'corners': {'mode':'preserve'}}
        del self.config['motion']
        result, report = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn('motion', str(report))

    def test_existing_wordmark_requires_additional_name_confirmation(self):
        self.config['artwork']['existing_wordmark'] = 'preserve'
        self.config['wordmark'] = {'text': 'Logo', 'font': 'missing.ttf', 'color': 'white'}
        result, report = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn('additional', str(report))

    def test_draft_embeds_exact_animation_and_is_not_approved(self):
        if not PLAYER.exists(): self.skipTest('Set LOTTIE_PLAYER_PACKAGE to Lottie Web 5.12.2')
        result, report = self.run_cli('draft')
        self.assertEqual(result.returncode, 0, report)
        directory = self.root / 'draft'
        animation = (directory / 'animation.json').read_text()
        html = (directory / 'preview.html').read_text()
        self.assertIn(animation.strip(), html)
        self.assertEqual(json.loads((directory / 'manifest.json').read_text())['status'], 'draft')
        self.assertFalse((directory / 'approval.json').exists())
        self.assertFalse(any(p.suffix in ('.ttf', '.otf', '.ttc') for p in directory.iterdir()))

    def test_preview_has_exact_json_download_control(self):
        if not PLAYER.exists(): self.skipTest('Set LOTTIE_PLAYER_PACKAGE to Lottie Web 5.12.2')
        result, report = self.run_cli('draft')
        self.assertEqual(result.returncode, 0, report)
        directory = self.root / 'draft'
        html = (directory / 'preview.html').read_text()
        animation = (directory / 'animation.json').read_text()
        self.assertTrue('id="download-json"' in html, 'Independent preview needs a JSON download button')
        self.assertIn('application/json', html)
        self.assertIn(animation.strip(), html)

    def test_app_download_names_and_missing_brand(self):
        for name, expected in [('ExampleApp', 'exampleapp_loading.json'),
                               ('  My-App__ Pro! ', 'my_app_pro_loading.json'),
                               ('译文 AI', '译文_ai_loading.json')]:
            with self.subTest(name=name):
                self.assertEqual(download_filename({'app_name':name}), expected)
                self.assertEqual(download_filename({'wordmark':{'text':name}}), expected)
        for name in ('', ' ', '!!!', None):
            with self.subTest(name=name), self.assertRaises(ValueError):
                download_filename({'app_name':name})
        del self.config['app_name']
        result, report = self.run_cli('draft')
        self.assertEqual(result.returncode,2,report)
        self.assertIn('app_name',str(report))
        self.assertFalse((self.root/'draft').exists())

    def test_size_report_matches_delivered_bytes_and_preserves_paths(self):
        if not PLAYER.exists(): self.skipTest('Set LOTTIE_PLAYER_PACKAGE')
        result, report = self.run_cli('draft')
        self.assertEqual(result.returncode, 0, report)
        directory = self.root/'draft'
        self.assertEqual(report['size']['after_bytes'], (directory/'animation.json').stat().st_size)
        self.assertFalse(report['size']['approximation'])
        result = subprocess.run([sys.executable,str(SCRIPT),'size',str(directory/'animation.json')],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout)
        stats=json.loads(result.stdout)
        self.assertEqual(stats['file_bytes'], report['size']['after_bytes'])
        self.assertEqual(stats['path_vertices'], report['size']['before']['path_vertices'])

    def test_rounding_requires_consent_and_web_comparison(self):
        runtime = os.environ.get('LOTTIE_PLAYWRIGHT_PACKAGE')
        if not runtime or not PLAYER.exists(): self.skipTest('Web runtime required')
        self.svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
                            '<circle cx="50" cy="50" r="40.123456" fill="red"/></svg>')
        self.config['optimization'] = {'coordinate_precision':3}
        result, report = self.run_cli()
        self.assertEqual(result.returncode,2,report)
        self.assertIn('user_request',str(report))
        del self.config['optimization']
        result, _ = self.run_cli('draft')
        self.assertEqual(result.returncode,0)
        reference = self.root/'draft/animation.json'
        self.root = self.root/'rounded'
        self.root.mkdir()
        self.config['optimization'] = {'coordinate_precision':3,'user_request':'Use 3 decimal places for coordinates.'}
        result, report = self.run_cli('draft')
        self.assertEqual(result.returncode,0,report)
        directory = self.root/'draft'
        args=[sys.executable,str(SCRIPT),'validate',str(directory),'--playwright-package',runtime]
        result=subprocess.run(args,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        approve=[sys.executable,str(SCRIPT),'approve',str(directory),'--statement','Fixture approval','--visual-review']
        result=subprocess.run(approve,text=True,capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('comparison',result.stdout)
        validation=json.loads((directory/'validation.json').read_text())
        del validation['size']
        (directory/'validation.json').write_text(json.dumps(validation))
        result=subprocess.run(approve,text=True,capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('comparison',result.stdout)
        result=subprocess.run(args+['--reference-json',str(directory/'animation.json')],text=True,capture_output=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('matching unrounded',result.stdout+result.stderr)
        result=subprocess.run(args+['--reference-json',str(reference)],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        validation=json.loads((directory/'validation.json').read_text())
        self.assertEqual(validation['comparison']['status'],'measured')
        self.assertEqual(len(validation['comparison']['samples']),len(validation['sample_frames']))
        self.assertEqual(validation['download'],'passed')
        result=subprocess.run(approve,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_approval_requires_rendering_and_visual_review(self):
        if not PLAYER.exists(): self.skipTest('Set LOTTIE_PLAYER_PACKAGE to Lottie Web 5.12.2')
        result, _ = self.run_cli('draft')
        self.assertEqual(result.returncode, 0)
        result = subprocess.run([sys.executable, str(SCRIPT), 'approve', str(self.root / 'draft'),
                                 '--statement', 'test approval'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'draft' / 'approval.json').exists())

    def test_changed_preview_cannot_be_approved(self):
        if not PLAYER.exists(): self.skipTest('Set LOTTIE_PLAYER_PACKAGE')
        result, _ = self.run_cli('draft')
        self.assertEqual(result.returncode, 0)
        directory = self.root / 'draft'
        (directory / 'preview.html').write_text('changed preview')
        result = subprocess.run([sys.executable, str(SCRIPT), 'approve', str(directory),
                                 '--statement', 'test approval', '--visual-review'], text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('changed', result.stdout)
        self.assertFalse((directory / 'approval.json').exists())

    def test_browser_initializes_wordmark_and_replays_offline(self):
        runtime = os.environ.get('LOTTIE_PLAYWRIGHT_PACKAGE')
        if not runtime or not PLAYER.exists(): self.skipTest('Set LOTTIE_PLAYWRIGHT_PACKAGE and LOTTIE_PLAYER_PACKAGE for Web tests')
        self.config['wordmark'] = {'text': 'Logo', 'font': '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                                  'size': 30, 'color': '#202020', 'motion':{'user_request':'Use default hops.'}}
        result, report = self.run_cli('draft')
        self.assertEqual(result.returncode, 0, report)
        directory = self.root / 'draft'
        result = subprocess.run([sys.executable, str(SCRIPT), 'validate', str(directory),
                                 '--playwright-package', runtime], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        validation = json.loads((directory / 'validation.json').read_text())
        self.assertEqual(validation['web'], 'passed')
        self.assertGreater(validation['samples'][-1]['visiblePaths'], 4)
        self.assertEqual(validation['network_requests'], [])
        self.assertEqual(validation['download'], 'passed')
        self.assertEqual(validation['download_filename'], 'exampleapp_pro_loading.json')

    def test_static_export_background_needs_specific_request(self):
        self.config['export_background'] = {'type':'solid','color':'black','motion':{'duration':0}}
        result, report = self.run_cli()
        self.assertEqual(result.returncode,2,report)
        self.assertIn('user_request',str(report))
        self.config['export_background']['motion']['user_request'] = 'Keep the canvas black from the first frame.'
        result, report = self.run_cli()
        self.assertEqual(result.returncode,0,report)

    def test_theme_exports_have_distinct_colors_and_animated_backgrounds(self):
        runtime = os.environ.get('LOTTIE_PLAYWRIGHT_PACKAGE')
        if not runtime or not PLAYER.exists() or not BOLD.exists(): self.skipTest('Web runtime and Arial Bold required')
        self.config['source'] = str(FIXTURES/'icon-backplate.svg')
        self.config['artwork']['backplate'] = {'mode':'embedded','element_ids':['icon-backplate'], 'corners':{'mode':'rounded','radius':20}}
        self.config['motion'] = {'rationale':'An icon plate introduces the scene, followed by the coherent foreground.', 'tracks':[
            {'name':'Plate','target':'backplate','reason':'Introduce the retained icon background.',
             'keyframes':[beat(0,opacity=0),beat(.3)]},
            {'name':'Mark','target':'foreground','reason':'Preserve the compact mark intact.',
             'keyframes':[beat(.2,opacity=0),beat(.7)]}]}
        original = self.root
        variants = []
        for theme,matte,ink in [('light','#fafafa','#202020'),('dark','#181818','#ffffff')]:
            self.root = original/theme
            self.root.mkdir()
            self.config['wordmark'] = {'text':'Nova','font':str(BOLD),'color':ink,'motion':{'user_request':'Use default hops.'}}
            self.config['preview_background'] = matte
            self.config['export_background'] = {'type':'solid','color':matte}
            result, report = self.run_cli('draft')
            self.assertEqual(result.returncode,0,report)
            directory = self.root/'draft'
            result = subprocess.run([sys.executable,str(SCRIPT),'validate',str(directory),'--playwright-package',runtime],text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report = json.loads((directory/'validation.json').read_text())
            self.assertEqual(report['web'],'passed')
            self.assertEqual(report['samples'][0]['roleOpacity']['Background'],0)
            self.assertEqual(report['samples'][0]['roleOpacity']['Plate'],0)
            self.assertEqual(report['samples'][-1]['roleOpacity']['Background'],1)
            self.assertEqual(report['composition']['wordmark_motion']['preset'],'hop')
            variants.append(json.loads((directory/'animation.json').read_text()))
        self.assertNotEqual(variants[0]['layers'][0]['shapes'],variants[1]['layers'][0]['shapes'])
        self.assertEqual(variants[0]['layers'][0]['ks'],variants[1]['layers'][0]['ks'])
        self.assertEqual(variants[0]['op'],variants[1]['op'])

    def test_raster_flows_through_explicit_converter(self):
        if not PLAYER.exists(): self.skipTest('Set LOTTIE_PLAYER_PACKAGE')
        from PIL import Image, ImageDraw
        image = Image.new('RGBA', (64, 64))
        ImageDraw.Draw(image).rectangle((10, 10, 54, 54), fill='#e23c29')
        source = self.root / 'logo.png'
        image.save(source)
        self.config['source'] = str(source)
        converter = SCRIPT.parents[2] / 'image-to-svg' / 'scripts' / 'convert_image_to_svg.py'
        result, report = self.run_cli('draft', ('--image-converter', str(converter)))
        self.assertEqual(result.returncode, 0, report)
        self.assertIn('#e23c29', (self.root / 'draft' / 'normalized.svg').read_text().lower())

    def test_web_icon_backplate_presets_corners_and_external_name(self):
        runtime = os.environ.get('LOTTIE_PLAYWRIGHT_PACKAGE')
        if not runtime or not PLAYER.exists(): self.skipTest('Set LOTTIE_PLAYWRIGHT_PACKAGE and LOTTIE_PLAYER_PACKAGE')
        self.svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                            '<defs><linearGradient id="green"><stop offset="0" stop-color="#397d60"/>'
                            '<stop offset="1" stop-color="#07564f"/></linearGradient></defs>'
                            '<rect id="plate" width="100" height="100" fill="url(#green)"/>'
                            '<g id="foreground"><circle cx="50" cy="50" r="22" fill="white"/></g></svg>')
        self.config['artwork']['backplate'] = {'mode': 'embedded', 'element_ids': ['plate'],
                                               'corners': {'mode': 'rounded', 'radius': 20}}
        self.config['wordmark'] = {'text': 'Logo', 'font': '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                                  'size': 30, 'color': '#202020', 'motion':{'user_request':'Use default hops.'}}
        root = self.root
        for preset in ('backplate-first', 'static-backplate', 'whole-icon'):
            with self.subTest(preset=preset):
                self.root = root / preset
                self.root.mkdir()
                self.config['motion'] = {'preset': preset}
                if preset == 'static-backplate': self.config['motion']['user_request'] = 'Keep the plate visible from the start.'
                result, report = self.run_cli('draft')
                self.assertEqual(result.returncode, 0, report)
                directory = self.root / 'draft'
                result = subprocess.run([sys.executable, str(SCRIPT), 'validate', str(directory),
                                         '--playwright-package', runtime], text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                validation = json.loads((directory / 'validation.json').read_text())
                self.assertEqual(validation['web'], 'passed')
                self.assertEqual(validation['outside_content_pixels'], 0)
                self.assertEqual(validation['rounded_corner_opaque_probes'], 0)
                self.assertEqual(validation['composition']['wordmark_placement'], 'below-icon')
                self.assertNotIn('Background', validation['samples'][-1]['roleBounds'])


def beat(t, dx=0, opacity=100, **extras):
    return dict(time=t, offset=[dx,0], scale=100, opacity=opacity, **extras)


def network_config():
    return {'source':str(FIXTURES/'network.svg'), 'app_name':'Link',
        'artwork':{'existing_wordmark':'absent','backplate':{'mode':'none'}},
        'canvas':{'width':430,'height':300,'icon_width':240},
        'motion':{'rationale':'A connection links two distinct nodes; reveal their relationship through the existing curved stroke.',
            'tracks':[
                {'name':'Connection','element_ids':['connection'], 'reason':'Draw the real open path toward the receiver.',
                 'keyframes':[beat(.4,draw=0),beat(.7,draw=50),beat(1.,draw=100)]},
                {'name':'Sender','element_ids':['sender'],'reason':'Introduce the origin from the left.',
                 'keyframes':[beat(0,-4,0),beat(.45)]},
                {'name':'Receiver','element_ids':['receiver'],'reason':'Enter from the right as the connection approaches.',
                 'keyframes':[beat(.2,4,0),beat(.75)]}]}}


class AuthoredWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_inventory_reports_real_stroke_eligibility(self):
        result = subprocess.run([sys.executable,str(SCRIPTS/'logo_lottie.py'),'inventory',
                                 str(FIXTURES/'network.svg')],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(sum(e['open_stroke_drawing'] for e in report['elements']),1)
        drawn = next(e for e in report['elements'] if e['open_stroke_drawing'])
        self.assertIn('connection',drawn['ids'])
        self.assertEqual(report['viewport'],[120,100])

    def test_font_candidates_are_distinct_upright_and_not_selected(self):
        if not BOLD.exists(): self.skipTest('Arial Bold unavailable')
        fonts = self.root/'fonts'
        fonts.mkdir()
        for name in ('Arial Bold.ttf','Arial Bold Italic.ttf','Arial.ttf','Verdana Bold.ttf'):
            source = BOLD.with_name(name)
            if source.exists(): shutil.copy(source,fonts/name)
        report = font_candidates('Connect', roots=[fonts])
        self.assertEqual(report['status'], 'ready')
        self.assertGreaterEqual(len(report['candidates']), 2)
        self.assertEqual(len({c['family'] for c in report['candidates']}), len(report['candidates']))
        self.assertTrue(all(c['weight'] == 700 and 'italic' not in c['style'].lower() for c in report['candidates']))
        self.assertNotIn('font', report)
        config = network_config()
        config['wordmark'] = {'text':'Connect'}
        path = self.root/'config.json'
        path.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, 'font, color'):
            load_config(path)
        chosen = report['candidates'][0]
        config['wordmark'].update(font=chosen['font'], font_index=chosen['font_index'], color='#efefef',motion={'user_request':'Use default hops.'})
        path.write_text(json.dumps(config))
        resolved = load_config(path)
        self.assertEqual(resolved['wordmark']['color'], '#efefef')
        self.assertEqual(shape_text('Connect', chosen['font'], 32, weight=700)['font']['weight'],700)

    def test_explicit_missing_font_is_never_replaced(self):
        config = network_config()
        config['wordmark'] = {'text':'Name','font':'missing-brand.ttf','color':'white','motion':{'user_request':'Use default hops.'}}
        path = self.root/'config.json'
        path.write_text(json.dumps(config))
        with patch('typography.font_candidates',side_effect=AssertionError('must not substitute')):
            resolved = load_config(path)
            with self.assertRaises(FileNotFoundError):
                shape_text('Name',resolved['wordmark']['font'],32,weight=700)

    def test_font_cli_without_harfbuzz_lists_choices_but_cannot_shape(self):
        if not BOLD.exists(): self.skipTest('Arial Bold unavailable')
        code = (
            "import sys, runpy; sys.modules['uharfbuzz'] = None; "
            "sys.path.insert(0, sys.argv[1]); sys.argv = sys.argv[2:]; "
            "runpy.run_path(sys.argv[0], run_name='__main__')"
        )
        result = subprocess.run([sys.executable, '-c', code, str(SCRIPTS),
                                 str(SCRIPT), 'fonts', 'Lexivo Translator', '--limit', '3'],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(len(report['candidates']), 3)
        self.assertEqual(report['missing_dependencies'], ['uharfbuzz'])
        self.assertTrue(all(c['coverage'] == 'passed' and c['shaping'] == 'pending_dependency'
                            for c in report['candidates']))
        self.assertNotIn('font', report)
        with patch.dict(sys.modules, {'uharfbuzz': None}):
            with self.assertRaises(ModuleNotFoundError):
                shape_text('Lexivo Translator', BOLD, 32, weight=700)

    def test_font_choices_do_not_ignore_invalid_text_without_harfbuzz(self):
        with patch.dict(sys.modules, {'uharfbuzz': None}):
            for name in ('Two\nLines', 'Mixed عربي', 'Hidden\u200e'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    font_candidates(name, roots=[self.root])

    def test_absent_bold_coverage_reports_decision(self):
        report = font_candidates('Name',roots=[self.root])
        self.assertEqual(report['status'], 'needs_decision')
        self.assertEqual(report['candidates'], [])

    def test_name_color_is_not_chosen_from_preview(self):
        config = network_config()
        config['wordmark'] = {'text':'Name','font':str(BOLD)}
        config['preview_background'] = 'black'
        path = self.root/'config.json'
        path.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, 'color'):
            load_config(path)

    def test_text_effects_require_selection_or_delegation(self):
        config = network_config()
        config['wordmark'] = {'text':'Name','font':str(BOLD),'color':'white'}
        path = self.root/'config.json'
        for motion in ({}, {'preset':'hop'}, {'preset':'rise','stagger':0}, {'preset':'fade'},
                       {'preset':'gather'}, {'preset':'reveal'}, {'amplitude':0}, {'stagger_window':0}):
            config['wordmark']['motion'] = motion
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, 'user_request'):
                load_config(path)
            motion['user_request'] = 'Choose the text effect that best suits the foreground.'
            path.write_text(json.dumps(config))
            self.assertEqual(load_config(path)['wordmark']['motion']['user_request'], motion['user_request'])

    def test_authored_tracks_draw_and_replay_in_actual_player(self):
        runtime = os.environ.get('LOTTIE_PLAYWRIGHT_PACKAGE')
        player = Path(os.environ.get('LOTTIE_PLAYER_PACKAGE','/tmp/logo-lottie-web-runtime/node_modules/lottie-web'))
        if not runtime or not player.exists() or not BOLD.exists():
            self.skipTest('Web runtime and Arial Bold required')
        config = network_config()
        config['wordmark'] = {'text':'Link','font':str(BOLD),'size':32,'color':'#202020', 'motion':{'user_request':'Use default hops.'}}
        del config['app_name']
        path = self.root/'config.json'
        path.write_text(json.dumps(config))
        draft = self.root/'draft'
        for args in [
            ['draft',str(path),'--output',str(draft),'--player-package',str(player)],
            ['validate',str(draft),'--playwright-package',runtime]]:
            result = subprocess.run([sys.executable,str(SCRIPTS/'logo_lottie.py')]+args,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        report = json.loads((draft/'validation.json').read_text())
        self.assertEqual(report['web'],'passed')
        self.assertEqual(report['typography']['weight'],700)
        self.assertEqual(report['composition']['preset'],'authored')
        self.assertEqual(report['composition']['wordmark_motion']['preset'],'hop')
        samples = {s['frame']:s for s in report['samples']}
        final_length = report['samples'][-1]['roleStrokeLengths']['Connection']
        self.assertGreater(final_length,0)
        self.assertAlmostEqual(samples[21]['roleStrokeLengths']['Connection']/final_length,.5,delta=.06)
        self.assertEqual(samples[12]['roleStrokeLengths']['Connection'],0)
        self.assertEqual(report['network_requests'],[])
        self.assertFalse((draft/'approval.json').exists())
        self.assertEqual(report['download_filename'], 'link_loading.json')



if __name__ == '__main__': unittest.main()
