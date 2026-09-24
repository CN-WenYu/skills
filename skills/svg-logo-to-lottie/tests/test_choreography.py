from copy import deepcopy
import json
import math
import os
import subprocess
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from animation import build_animation
from artwork import prepare_artwork
from configuration import load_config, DecisionRequired
from svg_geometry import load_svg
from typography import shape_text


def frame(time, offset=(0,0), scale=100, opacity=100, **extras):
    return dict(time=time,offset=list(offset),scale=scale,opacity=opacity,**extras)


class ChoreographyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root/'source.svg'
        self.source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<g id="one"><rect x="15" y="30" width="20" height="30" fill="red"/></g>'
            '<circle id="two" cx="70" cy="45" r="12" fill="blue"/>'
            '<path id="connection" d="M37 45Q50 30 56 45" fill="none" stroke="green" stroke-width="2" stroke-linejoin="round"/></svg>')
        self.config = {'source':str(self.source),
            'artwork':{'existing_wordmark':'symbols','backplate':{'mode':'none'}},
            'motion':{'rationale':'Two distinct nodes communicate through a curved connection.', 'tracks':[
                {'name':'Node one','element_ids':['one'],'reason':'Introduce the first node from the left.',
                 'keyframes':[frame(0,(-5,0),opacity=0),frame(.5)]},
                {'name':'Node two','element_ids':['two'],'reason':'The receiver enters after the sender.',
                 'keyframes':[frame(.2,(5,0),opacity=0),frame(.7)]},
                {'name':'Connection','element_ids':['connection'],'reason':'Trace the existing open stroke to show communication.',
                 'keyframes':[frame(.5,draw=0),frame(.8,draw=50),frame(1.1,draw=100)]}]}}

    def build(self):
        path = self.root/'config.json'
        path.write_text(json.dumps(self.config))
        config = load_config(path)
        asset = prepare_artwork(load_svg(self.source),config)
        return build_animation(asset,config),config

    def test_semantic_tracks_keep_order_and_distinct_motion(self):
        (animation,report),config = self.build()
        self.assertEqual([x['nm'] for x in animation['layers']],['Connection','Node two','Node one'])
        self.assertEqual(config['source_background'],'preserve')
        self.assertEqual(config['export_background'],{'type':'transparent'})
        self.assertEqual(report['composition']['preset'],'authored')
        self.assertEqual(report['composition']['rationale'],self.config['motion']['rationale'])
        self.assertEqual(animation['layers'][1]['ks']['p']['k'][0]['t'],6)
        self.assertEqual(animation['layers'][2]['ks']['p']['k'][0]['t'],0)
        trim = next(i for i in animation['layers'][0]['shapes'][0]['it'] if i['ty']=='tm')
        self.assertEqual(trim['e']['k'][-1]['s'],[100])
        self.assertAlmostEqual(report['settled_frame'],33)
        self.assertGreaterEqual(animation['op']/animation['fr'],1.45)

    def test_stationary_content_is_a_valid_design_choice(self):
        for t in self.config['motion']['tracks']:
            t['keyframes'] = [frame(0)]
        self.config['motion']['tracks'][-1]['keyframes'] = [frame(0,draw=100)]
        (animation,_),_ = self.build()
        self.assertTrue(all(l['ks']['p']['a']==0 and l['ks']['s']['a']==0 for l in animation['layers']))
        trim = next(i for i in animation['layers'][0]['shapes'][0]['it'] if i['ty']=='tm')
        self.assertEqual(trim['e'],{'a':0,'k':100})

    def test_filled_arrow_does_not_get_perimeter_drawing(self):
        self.source.write_text(self.source.read_text().replace('fill="none" stroke="green"','fill="green" stroke="green"'))
        with self.assertRaisesRegex(DecisionRequired,'filled/closed'):
            self.build()

    def test_missing_overlapping_and_unknown_mappings_stop(self):
        original = deepcopy(self.config['motion']['tracks'])
        cases = [original[:-1], original+[dict(original[0],name='Duplicate')],
                 [dict(original[0],element_ids=['unknown'])]+original[1:]]
        for tracks in cases:
            with self.subTest(tracks=tracks):
                self.config['motion']['tracks'] = tracks
                with self.assertRaises(DecisionRequired): self.build()

    def test_final_geometry_cannot_be_changed_by_motion(self):
        self.config['motion']['tracks'][0]['keyframes'][-1]['offset'] = [2,0]
        with self.assertRaisesRegex(DecisionRequired,'original geometry'): self.build()

    def test_interleaved_groups_cannot_change_painter_order(self):
        self.config['motion']['tracks'] = [
            {'name':'Combined','element_ids':['one','connection'],'reason':'Grouping test','keyframes':[frame(0)]},
            self.config['motion']['tracks'][1]]
        with self.assertRaisesRegex(DecisionRequired,'painter order'): self.build()

    def test_bad_keyframes_are_rejected_without_silent_defaults(self):
        original = deepcopy(self.config['motion'])
        for key,value in [('time',float('nan')),('scale',0),('offset',[0]),('opacity',120)]:
            with self.subTest(key=key):
                self.config['motion'] = deepcopy(original)
                self.config['motion']['tracks'][0]['keyframes'][0][key] = value
                with self.assertRaises(DecisionRequired): self.build()

    def test_bold_font_and_name_motion_defaults_are_materialized(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
        if not font.exists(): self.skipTest('Arial Bold unavailable')
        self.config['wordmark'] = {'text':'Connect','font':str(font),'color':'#202020',
                                   'motion':{'start':.4,'stagger':.02,'user_request':'Use the default hops.'}}
        (animation,report),config = self.build()
        self.assertEqual(config['wordmark']['weight'],700)
        self.assertEqual(report['typography']['weight'],700)
        self.assertEqual(config['wordmark']['placement'],'below-icon')
        self.assertEqual(animation['layers'][0]['ks']['p']['k'][0]['t'],12)
        self.assertEqual(animation['layers'][0]['ks']['a']['k'][1],0)
        beats = report['composition']['wordmark_motion']['beats']
        self.assertGreater(beats[1]['frames'][0]['frame'], beats[0]['frames'][0]['frame'])
        offsets = [f['offset_y'] for f in beats[0]['frames']]
        self.assertGreater(offsets[0], 0)
        self.assertLess(offsets[1], 0)
        self.assertGreater(offsets[2], 0)
        self.assertEqual(offsets[-1], 0)
        self.assertTrue(all(b[1]>=report['animated_bounds'][0][3]+24-1e-6 for b in report['animated_bounds'][1:]))

    def test_regular_font_cannot_masquerade_as_bold(self):
        font = Path('/System/Library/Fonts/Supplemental/Arial.ttf')
        if not font.exists(): self.skipTest('Arial unavailable')
        with self.assertRaisesRegex(ValueError,'weight 400, requested 700'):
            shape_text('Name',font,30,weight=700)

    def test_rotation_and_curve_enclose_intermediate_geometry(self):
        from choreography import track_bounds
        t = self.config['motion']['tracks'][0]
        t['pivot'] = [15,30]
        t['keyframes'] = [frame(0, rotation=-80, curve={'out':[25,-30],'in':[-20,-10]}), frame(1)]
        (animation,report),_ = self.build()
        layer = next(l for l in animation['layers'] if l['nm']=='Node one')
        self.assertEqual(layer['ks']['a']['k'],[15,30,0])
        self.assertEqual(layer['ks']['r']['k'][0]['s'],[-80])
        self.assertIn('to',layer['ks']['p']['k'][0])
        bounds = track_bounds({**t,'bounds':[15,30,35,60]})
        for i in range(201):
            u=i/200
            dx=3*(1-u)**2*u*25+3*(1-u)*u*u*-20
            dy=3*(1-u)**2*u*-30+3*(1-u)*u*u*-10
            angle=math.radians(-80*(1-u))
            for x,y in [(0,0),(20,0),(20,30),(0,30)]:
                px=15+dx+x*math.cos(angle)-y*math.sin(angle)
                py=30+dy+x*math.sin(angle)+y*math.cos(angle)
                self.assertTrue(bounds[0]-1e-6<=px<=bounds[2]+1e-6)
                self.assertTrue(bounds[1]-1e-6<=py<=bounds[3]+1e-6)
        self.assertTrue(set(range(31)) <= set(report['sample_frames']))

    def test_invalid_curve_and_nonzero_final_rotation_are_rejected(self):
        original=deepcopy(self.config['motion'])
        for change in ({'rotation':float('nan')}, {'curve':{'out':[1,2]}},
                       {'curve':{'out':[1,2],'in':[3]}}, {'rotation':True}):
            self.config['motion']=deepcopy(original)
            self.config['motion']['tracks'][0]['keyframes'][0].update(change)
            with self.assertRaises(DecisionRequired): self.build()
        for change in ({'rotation':10},{'curve':{'out':[0,0],'in':[0,0]}}):
            self.config['motion']=deepcopy(original)
            self.config['motion']['tracks'][0]['keyframes'][-1].update(change)
            with self.assertRaises(DecisionRequired): self.build()

    def test_all_text_effects_and_pivot_motion_in_actual_web_player(self):
        from preview import write_draft, optimize_animation
        from PIL import Image, ImageChops
        runtime=os.environ.get('LOTTIE_PLAYWRIGHT_PACKAGE')
        player=Path(os.environ.get('LOTTIE_PLAYER_PACKAGE','/tmp/logo-lottie-web-runtime/node_modules/lottie-web'))
        font=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
        if not runtime or not player.exists() or not font.exists(): self.skipTest('Web runtime and font required')
        track=self.config['motion']['tracks'][0]
        track['pivot']=[15,30]
        track['keyframes']=[frame(0,rotation=-60,curve={'out':[20,-20],'in':[-10,-20]}),frame(1)]
        self.config['canvas']={'width':512,'height':512,'icon_width':180}
        self.config['preview_background']='white'
        for preset in ('hop','rise','fade','gather','reveal'):
            with self.subTest(preset=preset):
                self.config['wordmark']={'text':'Link','font':str(font),'size':32,'color':'black',
                    'motion':{'preset':preset,'user_request':f'Use {preset} for the name.'}}
                (animation,report),config=self.build()
                asset=prepare_artwork(load_svg(self.source),config)
                animation,report['size']=optimize_animation(animation)
                draft=self.root/preset
                write_draft(draft,config,asset,animation,report,player)
                command=[sys.executable,str(Path(__file__).resolve().parents[1]/'scripts/logo_lottie.py'),
                         'validate',str(draft),'--playwright-package',runtime]
                result=subprocess.run(command,text=True,capture_output=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                evidence=json.loads((draft/'validation.json').read_text())
                samples={s['frame']:s for s in evidence['samples']}
                self.assertAlmostEqual(samples[0]['roleRotation']['Node one'],-60,delta=.1)
                self.assertAlmostEqual(samples[15]['roleRotation']['Node one'],-30,delta=.2)
                self.assertAlmostEqual(samples[30]['roleRotation']['Node one'],0,delta=.1)
                y0=samples[0]['roleAnchorY']['Node one'];y1=samples[30]['roleAnchorY']['Node one']
                self.assertLess(samples[15]['roleAnchorY']['Node one'],min(y0,y1)-5)
                self.assertEqual(evidence['download'],'passed')
                names=evidence['composition']['wordmark_layers']
                self.assertEqual(len(names),4 if preset in ('hop','gather') else 1)
                if preset=='gather':
                    first=report['composition']['wordmark_motion']['beats'][0]['frames'][0]['frame']
                    middle=round(first+.31*30,3)
                    self.assertLess(samples[middle]['roleAnchorX'][names[0]],samples[max(samples)]['roleAnchorX'][names[0]])
                if preset=='reveal':
                    c=evidence['composition'];b=c['settled_wordmark_bounds']
                    start=c['wordmark_motion']['beats'][0]['frames'][0]['frame']
                    counts=[]
                    for f in (start,round(start+.31*30,3),max(samples)):
                        im=Image.open(draft/samples[f]['screenshot']).convert('RGB')
                        crop=im.crop((int(b[0])-1,int(b[1])-1,math.ceil(b[2])+1,math.ceil(b[3])+1))
                        counts.append(sum(min(pixel)<200 for pixel in crop.getdata()))
                    self.assertEqual(counts[0],0)
                    self.assertTrue(0<counts[1]<counts[2],counts)
                    reference=json.loads((self.root/'fade/validation.json').read_text())
                    unmasked=Image.open(self.root/'fade'/reference['samples'][-1]['screenshot']).convert('RGB')
                    revealed=Image.open(draft/samples[max(samples)]['screenshot']).convert('RGB')
                    self.assertIsNone(ImageChops.difference(unmasked,revealed).getbbox(), 'Final reveal must show the complete unmasked text')


if __name__=='__main__':unittest.main()
