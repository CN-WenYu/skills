"""Compose source-preserving motion tracks and shaped application names."""
import math
from PIL import ImageColor

from artwork import check_backplate_containment, painted_rect, parse_tree
from choreography import resolve_tracks, track_bounds, check_containment, compile_tracks
from motion_core import keys, layer
from typography import shape_text
from svg_geometry import group_transform
from svg_paths import union


def plan_wordmark(text, wordmark, foreground_end):
    if not text:
        return [], None, 0
    options = wordmark.get('motion', {})
    preset = options.get('preset', 'hop')
    size = wordmark['size']
    duration = options.get('duration', .62)
    start = options.get('start', max(0, foreground_end-.2))
    step = min(options.get('stagger', .048 if preset == 'hop' else 0), options.get('stagger_window', .8)/max(1, len(text['units'])-1))
    amplitude = options.get('amplitude', .6)*size
    anchors = options.get('anchor', 'baseline')
    planned, envelopes = [], []
    units = text['units']
    if preset == 'gather' and len(units)<2:
        raise ValueError('Spacing convergence needs independently shaped units; choose another text effect for connected writing or a single unit.')
    if preset in ('rise','fade','reveal'):
        units = [{'bounds':text['bounds'], 'shapes':[shape for unit in units for shape in unit['shapes']]}]
    center_x = (text['bounds'][0]+text['bounds'][2])/2
    for index, unit in enumerate(units):
        b = unit['bounds']
        anchor = [(b[0]+b[2])/2, 0 if anchors == 'baseline' else (b[1]+b[3])/2]
        t = start + index*step
        if preset == 'hop':
            beats = [(t, amplitude, 92, 0), (t+duration*.48, -amplitude*.39, 102.5, 100),
                     (t+duration*.72, amplitude*.11, 99, 100), (t+duration, 0, 100, 100)]
        elif preset == 'rise':
            beats = [(t, amplitude*.5, 100, 0), (t+duration, 0, 100, 100)]
        else:
            beats = [(t, 0, 100, 0), (t+duration, 0, 100, 100)]
        spread = (anchor[0]-center_x)*.16 if preset == 'gather' and len(units)>1 else 0
        x_offsets = [spread] + [0] * (len(beats)-1) if preset == 'gather' else [0]*len(beats)
        boxes = [[anchor[0]+(b[0]-anchor[0])*s/100, anchor[1]+(b[1]-anchor[1])*s/100+dy,
                  anchor[0]+(b[2]-anchor[0])*s/100, anchor[1]+(b[3]-anchor[1])*s/100+dy]
                 for _, dy, s, _ in beats]
        boxes = [[b[0]+dx,b[1],b[2]+dx,b[3]] for b,dx in zip(boxes,x_offsets)]
        envelope = union(boxes)
        planned.append({'unit': unit, 'anchor': anchor, 'beats': beats, 'x_offsets':x_offsets,
                        'reveal':preset=='reveal', 'bounds': envelope})
        envelopes.append(envelope)
    return planned, union(envelopes), max(p['beats'][-1][0] for p in planned)


def compile_wordmark(planned, wordmark, text, width, top, fps, frames):
    if not planned:
        return [], [], set()
    tx = (width-text['width'])/2-text['bounds'][0]
    ty = top-text['bounds'][1]
    rgba = ImageColor.getcolor(wordmark['color'], 'RGBA')
    fill = [c/255 for c in rgba]
    layers, bounds, samples = [], [], set()
    for index, p in enumerate(planned):
        anchor, beats = p['anchor'], p['beats']
        position = [anchor[0]+tx, anchor[1]+ty]
        group = {'ty': 'gr', 'nm': f'Name unit {index+1}', 'it': p['unit']['shapes']+[
            {'ty': 'fl', 'c': {'a': 0, 'k': fill[:3]+[1]}, 'o': {'a': 0, 'k': fill[3]*100}, 'r': 1}, group_transform()]}
        item = layer(f'Wordmark {index+1}', [group], frames, anchor, position)
        item['ks']['p'] = keys([(t, [position[0]+dx, position[1]+dy, 0])
                               for (t,dy,_,_),dx in zip(beats,p['x_offsets'])], fps)
        item['ks']['s'] = keys([(t, [s,s,100]) for t,_,s,_ in beats], fps)
        item['ks']['o'] = keys([(t, [o]) for t,_,_,o in beats], fps)
        if p['reveal']:
            item['hasMask'] = True
            b = p['unit']['bounds']
            def rectangle(right):
                return {'v':[[b[0]-1,b[1]-1],[right,b[1]-1],[right,b[3]+1],[b[0]-1,b[3]+1]],
                        'i':[[0,0]]*4, 'o':[[0,0]]*4, 'c':True}
            item['ks']['o'] = {'a':0,'k':100}
            item['masksProperties'] = [{'inv':False,'mode':'a','cl':True,'o':{'a':0,'k':100},
                'pt':keys([(beats[0][0],[rectangle(b[0]-1)]),(beats[-1][0],[rectangle(b[2]+1)])],fps),
                'x':{'a':0,'k':0}}]
        layers.append(item)
        b = p['bounds']
        bounds.append([b[0]+tx,b[1]+ty,b[2]+tx,b[3]+ty])
        samples.update(t for t,_,_,_ in beats)
        samples.update((a[0]+b[0])/2 for a,b in zip(beats,beats[1:]))
    return layers, bounds, samples


def layout_wordmark(asset, tracks, wordmark, canvas, foreground_end):
    width, height, padding = (canvas.get(k, d) for k, d in [('width',512),('height',512),('padding',32)])
    envelope = union([track_bounds(t) for t in tracks])
    bw, bh = envelope[2]-envelope[0], envelope[3]-envelope[1]
    icon_width = asset['bounds'][2]-asset['bounds'][0]
    available_w, available_h = width-2*padding, height-2*padding
    if min(bw, bh, icon_width, available_w, available_h) <= 0:
        raise ValueError('The artwork cannot fit the selected canvas')
    fit = min(available_w/bw, available_h/bh)
    text, planned, text_end, gap = None, [], 0, 0
    if wordmark:
        auto_size, auto_gap = 'size' not in wordmark, 'gap' not in wordmark
        probe = {**wordmark, 'size': wordmark.get('size', 1)}
        text = shape_text(probe['text'], probe['font'], probe['size'], probe.get('font_index',0), probe.get('weight'))
        _, text_envelope, _ = plan_wordmark(text, probe, foreground_end)
        # Both text geometry and hops scale linearly with em size. Solve the icon
        # scale from the motion bounds before materializing any automatic values.
        tail = text_envelope[3]-text['bounds'][1]
        coefficient = asset['bounds'][3]-envelope[1]
        fixed = 0
        if auto_size: coefficient += tail*.18*icon_width
        else: fixed += tail
        if auto_gap: coefficient += .12*icon_width
        else: fixed += wordmark['gap']
        fit = min(fit, (available_h-fixed)/coefficient)
        if fit <= 0:
            raise ValueError('Wordmark motion cannot fit; confirm a larger canvas or revised layout')
    requested = canvas.get('icon_width')
    if requested is not None:
        if requested/icon_width > fit+1e-6:
            raise ValueError('Requested icon width clips motion or the name; choose a larger canvas or revised layout')
        fit = requested/icon_width
    else:
        fit = round(icon_width*fit, 8)/icon_width
    if wordmark:
        wordmark.setdefault('size', .18*icon_width*fit)
        wordmark.setdefault('gap', .12*icon_width*fit)
        if auto_size:
            text = shape_text(wordmark['text'], wordmark['font'], wordmark['size'],
                              wordmark.get('font_index',0), wordmark.get('weight'))
        planned, text_envelope, text_end = plan_wordmark(text, wordmark, foreground_end)
        gap = wordmark['gap']
        total_height = max(bh*fit, (asset['bounds'][3]-envelope[1])*fit+gap+text_envelope[3]-text['bounds'][1])
    else:
        total_height = bh*fit
    center = [(envelope[0]+envelope[2])/2,(envelope[1]+envelope[3])/2]
    target = [width/2,(height-total_height)/2+bh*fit/2]
    return text, planned, text_end, gap, fit, center, target


def legacy_tracks(asset, preset):
    """Explicit older presets remain callable; they are not the agent's design policy."""
    split = preset != 'whole-icon'
    if split and 'backplate' not in asset:
        raise ValueError('Independent backplate motion requires mapped artwork')
    check_backplate_containment(asset, (.96, 1.015) if split else (1, 1))
    delay = .2 if preset == 'backplate-first' else 0
    def frame(time, scale, opacity):
        return {'time': time, 'offset': [0,0], 'scale': scale, 'opacity': opacity}
    tracks = [{'name': 'Foreground' if split else 'Logo', 'shapes': asset['foreground'] if split else asset['shapes'],
               'bounds': asset['bounds'], 'is_backplate': False, 'easing': [.25,0,.75,1],
               'keyframes': [frame(delay,96,0),frame(delay+.45,101.5,100),frame(delay+.75,100,100)]}]
    if split:
        tracks.append({'name': 'Icon backplate', 'shapes': asset['backplate'], 'bounds': asset['bounds'],
                       'is_backplate': True, 'easing': [.25,0,.75,1],
                       'keyframes': [frame(0,100,0),frame(.2,100,100)] if preset == 'backplate-first' else [frame(0,100,100)]})
    return tracks


def build_animation(asset, config):
    canvas = config.get('canvas', {})
    width, height, padding = canvas.get('width',512), canvas.get('height',512), canvas.get('padding',32)
    fps = config.get('fps',30)
    if min(width,height,fps) <= 0 or padding < 0:
        raise ValueError('Canvas and frame rate must be positive')
    motion = config.get('motion')
    if motion is None:
        raise ValueError('A material-specific motion plan or explicit preset is required')
    custom = 'tracks' in motion
    tracks = resolve_tracks(asset,motion) if custom else legacy_tracks(asset,motion['preset'])
    if custom:
        check_containment(asset,tracks)
    foreground_end = max(t['keyframes'][-1]['time'] for t in tracks)
    wordmark = dict(config['wordmark']) if config.get('wordmark') else None
    text, planned, text_end, gap, fit, center, target = layout_wordmark(asset,tracks,wordmark,canvas,foreground_end)
    background = config.get('export_background',{'type':'transparent'})
    entrance = background.get('motion', {})
    background_end = entrance.get('start', 0) + entrance.get('duration', .3) if background['type'] != 'transparent' else 0
    settled = max(foreground_end,text_end,background_end)
    hold = config.get('hold',.35)
    duration = config.get('duration')
    if duration is None:
        duration = max(settled+hold, 2.4 if not custom else 0)
    frames = math.ceil(duration*fps-1e-9)
    if duration < settled+hold-1e-6:
        raise ValueError('The duration is too short for the motion and settled hold; adjust the plan rather than cutting it off')
    icon_layers, icon_boxes, entrances, sample_times, drawings = compile_tracks(tracks,fps,frames,fit,center,target)
    icon_bounds = union(icon_boxes)
    settled_icon = [target[i%2]+(v-center[i%2])*fit for i,v in enumerate(asset['bounds'])]
    text_top = settled_icon[3]+gap
    text_layers,text_boxes,text_samples = compile_wordmark(planned,wordmark,text,width,text_top,fps,frames)
    boxes = [icon_bounds]+text_boxes
    if any(b[0]<padding-1e-6 or b[1]<padding-1e-6 or b[2]>width-padding+1e-6 or b[3]>height-padding+1e-6 for b in boxes):
        raise ValueError('Wordmark or animated artwork cannot fit without clipping. Confirm canvas/layout changes; do not shrink or truncate the name')
    if any(b[1]<icon_bounds[3]-1e-6 for b in text_boxes):
        raise ValueError('Wordmark motion overlaps the icon; confirm more settled gap or a revised motion plan')
    layers = text_layers+icon_layers
    if background['type'] != 'transparent':
        shapes = parse_tree(painted_rect(background,width,height))['shapes']
        bg_layer = layer('Background',shapes,frames)
        if entrance.get('duration', .3) > 0:
            start = entrance.get('start', 0)
            bg_layer['ks']['o'] = keys([(start, [0]), (background_end, [100])], fps)
            sample_times.update((start, (start+background_end)/2, background_end))
            entrances.append({'layer': 'Background', 'start_frame': start*fps, 'opaque_frame': background_end*fps})
        layers.append(bg_layer)
    for index,item in enumerate(layers,1):
        item['ind'] = index
    boundary = asset.get('backplate_boundary')
    outline = None
    if boundary:
        b = boundary['bounds']
        outline = {'bounds':[target[0]+(b[0]-center[0])*fit,target[1]+(b[1]-center[1])*fit,
                             target[0]+(b[2]-center[0])*fit,target[1]+(b[3]-center[1])*fit],
                   'rx':boundary['rx']*fit,'ry':boundary['ry']*fit,'probe_corners':boundary['probe_corners']}
    animation = {'v':'5.12.2','fr':fps,'ip':0,'op':frames,'w':width,'h':height,
                 'nm':'Logo entrance','ddd':0,'assets':[],'layers':layers,'markers':[]}
    report = {'animated_bounds':boxes,'settled_frame':settled*fps,
              'composition':{'preset':'authored' if custom else motion['preset'],
                  'rationale':motion.get('rationale'),'backplate':config.get('artwork',{}).get('backplate',{'mode':'none'}),
                  'icon_layers':[t['nm'] for t in icon_layers],'icon_bounds':icon_bounds,
                  'wordmark_placement':'below-icon' if text else None,'wordmark_gap':gap,
                  'settled_icon_bounds':settled_icon,'wordmark_size':wordmark['size'] if text else None,
                  'settled_wordmark_bounds':[(width-text['width'])/2,text_top,(width+text['width'])/2,
                                             text_top+text['bounds'][3]-text['bounds'][1]] if text else None,
                  'wordmark_layers':[t['nm'] for t in text_layers],
                  'wordmark_motion': {'preset':wordmark.get('motion',{}).get('preset','hop'),
                      'user_request':wordmark.get('motion',{}).get('user_request'),
                      'beats':[{'layer':item['nm'],'frames':[{'frame':round(t*fps,3),'offset_y':dy} for t,dy,_,_ in p['beats']]}
                               for item,p in zip(text_layers,planned)]} if text else None,
                  'entrances':entrances,'drawings':drawings,
                  'export_background':background['type'],'backplate_outline':outline,
                  'corner_containment':'bounded' if boundary else 'visual_review_required'},
              'typography':text.get('font') if text else None,
              'sample_frames':sorted({round(t*fps,3) for t in sample_times|text_samples|{0}}|{frames-1}),
              'native_platforms':'not_verified'}
    if wordmark:
        config['wordmark'].update(size=wordmark['size'],gap=gap)
        config.setdefault('canvas', {}).setdefault('icon_width', round((asset['bounds'][2]-asset['bounds'][0])*fit, 8))
    return animation,report
