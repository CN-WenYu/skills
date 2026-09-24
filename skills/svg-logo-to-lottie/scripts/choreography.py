"""Execute an agent-authored motion plan without inferring artwork semantics."""
from copy import deepcopy
import math
from xml.etree import ElementTree as ET

from artwork import check_backplate_bounds
from svg_paths import union
from configuration import DecisionRequired, allowed, pair, positive
from motion_core import keys, layer, static


def validate_motion(motion):
    allowed(motion, {'rationale', 'tracks'}, 'material-specific motion')
    if not isinstance(motion.get('rationale'), str) or not motion['rationale'].strip():
        raise DecisionRequired('Analyze the artwork and record why this choreography suits it; do not ask the user to author keyframes.')
    tracks = motion.get('tracks')
    if not isinstance(tracks, list) or not tracks:
        raise DecisionRequired('The motion plan needs at least one semantic track, including intentionally stationary content.')
    names = set()
    for track in tracks:
        allowed(track, {'name', 'element_ids', 'target', 'reason', 'keyframes', 'easing', 'user_request', 'pivot'}, 'motion track')
        if 'pivot' in track:
            pair(track['pivot'], 'rotation/scale pivot in source SVG units')
        name = track.get('name')
        if not isinstance(name, str) or not name.strip() or name in names or name == 'Background' or name.startswith('Wordmark '):
            raise DecisionRequired('Motion track names must be unique, nonempty and not use reserved Background/Wordmark names.')
        names.add(name)
        if 'user_request' in track and (not isinstance(track['user_request'], str) or not track['user_request'].strip()):
            raise DecisionRequired('Track user_request must quote an actual instruction, not invented consent.')
        if not isinstance(track.get('reason'), str) or not track['reason'].strip():
            raise DecisionRequired('Record each semantic track role and the reason for its action (or stillness).')
        if ('element_ids' in track) == ('target' in track):
            raise DecisionRequired('Select either explicit SVG element_ids or one target: foreground/backplate.')
        if 'target' in track and track['target'] not in ('foreground', 'backplate'):
            raise DecisionRequired('Unsupported motion target.')
        if 'element_ids' in track:
            ids = track['element_ids']
            if not isinstance(ids, list) or not ids or any(not isinstance(x, str) or not x for x in ids) or len(set(ids)) != len(ids):
                raise DecisionRequired('Track element_ids must be a nonempty list of unique SVG IDs.')
        easing = track.setdefault('easing', [.25, 0, .75, 1])
        if not isinstance(easing, list) or len(easing) != 4 or any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or not 0 <= x <= 1 for x in easing):
            raise DecisionRequired('Use four cubic-bezier coordinates in [0,1]; express overshoot explicitly in keyframes so bounds remain provable.')
        frames = track.get('keyframes')
        if not isinstance(frames, list) or not frames:
            raise DecisionRequired('Each track requires explicit keyframes; one identity frame means stationary.')
        previous = -1
        drawing = any(isinstance(f, dict) and 'draw' in f for f in frames)
        for index, frame in enumerate(frames):
            allowed(frame, {'time', 'offset', 'scale', 'opacity', 'draw', 'rotation', 'curve'}, 'motion keyframe')
            if not {'time', 'offset', 'scale', 'opacity'} <= frame.keys():
                raise DecisionRequired('Every keyframe needs time, offset, scale and opacity; no implicit carry-forward.')
            positive(frame['time'], 'keyframe time', -1e-9)
            if frame['time'] <= previous:
                raise DecisionRequired('Track keyframe times must be strictly increasing.')
            previous = frame['time']
            pair(frame['offset'], 'keyframe offset in source SVG units')
            positive(frame['scale'], 'keyframe scale percent')
            angle = frame.get('rotation', 0)
            if isinstance(angle, bool) or not isinstance(angle, (float, int)) or not math.isfinite(angle):
                raise DecisionRequired('Rotation must be a finite angle in degrees.')
            if 'curve' in frame:
                curve = frame['curve']
                allowed(curve, {'out', 'in'}, 'outgoing position curve')
                if set(curve) != {'out', 'in'} or index == len(frames)-1:
                    raise DecisionRequired('A position curve needs out/in handles and a following keyframe.')
                for handle in curve.values(): pair(handle, 'relative position curve handle')
            for field in ('opacity', 'draw') if drawing else ('opacity',):
                value = frame.get(field)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 100:
                    raise DecisionRequired(f'Every keyframe {field} must be between 0 and 100.')
        last = frames[-1]
        if last['offset'] != [0, 0] or last['scale'] != 100 or last['opacity'] != 100 or last.get('rotation', 0) != 0 or (drawing and last['draw'] != 100):
            raise DecisionRequired('Tracks must settle at the original geometry: offset [0,0], scale 100, opacity 100, rotation 0, draw 100.')


def resolve_tracks(asset, motion):
    validate_motion(motion)
    entries = asset.get('elements', [])
    # Shape identity survives artwork preparation; generated backplates are appended separately.
    foreground = {id(shape) for shape in asset.get('foreground', asset['shapes'])}
    plate = {id(shape) for shape in asset.get('backplate', [])}
    by_shape = {id(e['shape']): e for e in entries}
    source_ids = [el.get('id') for el in ET.fromstring(asset['normalized_svg']).iter() if el.get('id')]
    resolved, ownership = [], {}
    for track in motion['tracks']:
        if 'target' in track:
            shapes = asset.get(track['target'], asset['shapes'] if track['target'] == 'foreground' else [])
        else:
            ids = set(track['element_ids'])
            for identity in ids:
                if source_ids.count(identity) != 1 or not any(identity in e['ids'] for e in entries):
                    raise DecisionRequired(f'Track ID {identity!r} must identify exactly one visible SVG element/group.')
            shapes = [e['shape'] for e in entries if ids.intersection(e['ids'])]
        if not shapes:
            raise DecisionRequired(f'Track {track["name"]!r} selects no visible shapes.')
        if plate.intersection(map(id, shapes)) and foreground.intersection(map(id, shapes)):
            raise DecisionRequired('Keep icon backplate and foreground as separate semantic tracks.')
        boxes = []
        for shape in shapes:
            identity = id(shape)
            if identity in ownership:
                raise DecisionRequired('Motion tracks overlap; every visible shape must have exactly one owner.')
            ownership[identity] = len(resolved)
            boxes.append(by_shape[identity]['bounds'] if identity in by_shape else asset['backplate_bounds'])
        resolved.append({**track, 'shapes': shapes, 'bounds': union(boxes), 'is_backplate': bool(plate.intersection(map(id, shapes)))})
    if set(ownership) != {id(s) for s in asset['shapes']}:
        raise DecisionRequired('Motion plan omits visible artwork. Include a stationary track for content that should not move.')
    order = [ownership[id(s)] for s in asset['shapes']]
    runs = [value for index, value in enumerate(order) if index == 0 or value != order[index-1]]
    if len(runs) != len(set(runs)):
        raise DecisionRequired('Semantic track grouping would change painter order. Split the interleaved track without changing artwork.')
    return [resolved[index] for index in runs]


def track_bounds(track):
    b = track['bounds']
    cx, cy = track.get('pivot', [(b[0]+b[2])/2, (b[1]+b[3])/2])
    boxes = []
    frames = track['keyframes']
    if not any(f.get('rotation',0) or 'curve' in f for f in frames):
        return union([[cx+(b[0]-cx)*f['scale']/100+f['offset'][0],
                       cy+(b[1]-cy)*f['scale']/100+f['offset'][1],
                       cx+(b[2]-cx)*f['scale']/100+f['offset'][0],
                       cy+(b[3]-cy)*f['scale']/100+f['offset'][1]] for f in frames])
    for f, end in zip(frames, frames[1:]+frames[-1:]):
        positions = [f['offset'], end['offset']]
        if 'curve' in f:
            positions += [[f['offset'][i]+f['curve']['out'][i] for i in (0,1)],
                          [end['offset'][i]+f['curve']['in'][i] for i in (0,1)]]
        lo, hi = sorted(math.radians(x.get('rotation', 0)) for x in (f,end))
        corners = []
        for x in (b[0]-cx,b[2]-cx):
            for y in (b[1]-cy,b[3]-cy):
                # Enclose every rotated corner, including extrema between beats.
                phase = math.atan2(y,x)
                angles = [lo,hi]
                for axis in (0,math.pi/2):
                    base = axis-phase
                    if hi-lo >= 2*math.pi:
                        angles.extend((base,base+math.pi))
                    else:
                        angles.extend(base+k*math.pi for k in range(math.ceil((lo-base)/math.pi),math.floor((hi-base)/math.pi)+1))
                for angle in angles:
                    for s in (f['scale']/100,end['scale']/100):
                        corners.append(((x*math.cos(angle)-y*math.sin(angle))*s,
                                        (x*math.sin(angle)+y*math.cos(angle))*s))
        boxes.append([cx+min(p[0] for p in positions)+min(p[0] for p in corners),
                      cy+min(p[1] for p in positions)+min(p[1] for p in corners),
                      cx+max(p[0] for p in positions)+max(p[0] for p in corners),
                      cy+max(p[1] for p in positions)+max(p[1] for p in corners)])
    return union(boxes)


def check_containment(asset, tracks):
    if 'backplate' not in asset:
        return
    # A stationary plate gives every foreground track the same containment boundary.
    plates = [t for t in tracks if t['is_backplate']]
    if any(f['offset'] != [0, 0] or f['scale'] != 100 or f.get('rotation',0) != 0 or 'curve' in f for t in plates for f in t['keyframes']):
        raise DecisionRequired('Material-specific backplates currently support opacity timing only. Keep geometry stationary or use the explicit whole-icon preset.')
    for track in tracks:
        if track['is_backplate'] and track['keyframes'][0]['opacity'] != 0 and not track.get('user_request'):
            raise DecisionRequired('Include a backplate entrance from zero opacity, or record the actual user_request for a background visible from the first frame.')
        if not track['is_backplate']:
            check_backplate_bounds(asset, track_bounds(track), f'Track {track["name"]!r}')


def compile_tracks(tracks, fps, frames, fit, center, target):
    layers, boxes, entrances, samples, drawings = [], [], [], set(), []
    for track in tracks:
        shapes = deepcopy(track['shapes'])
        keyframes = track['keyframes']
        if 'draw' in keyframes[0]:
            if len(shapes) != 1:
                raise DecisionRequired('Path drawing requires one open stroked SVG path per track; split independent paths explicitly.')
            items = shapes[0]['it']
            paths = [x for x in items if x['ty'] == 'sh']
            if len(paths) != 1 or paths[0]['ks']['k']['c'] or any(x['ty'] in ('fl', 'gf') for x in items) or not any(x['ty'] in ('st', 'gs') for x in items):
                raise DecisionRequired('Drawing supports an open stroke, not a filled/closed silhouette. Do not trace an arrow perimeter; discuss a faithful reveal or approved stroke reconstruction.')
            end = (static(keyframes[0]['draw']) if all(f['draw'] == keyframes[0]['draw'] for f in keyframes)
                   else keys([(f['time'], [f['draw']]) for f in keyframes], fps, track['easing']))
            items.insert(-1, {'ty': 'tm', 's': static(0), 'e': end, 'o': static(0), 'm': 1})
            drawings.append({'layer': track['name'], 'keyframes': [{'frame': f['time']*fps, 'percent': f['draw']} for f in keyframes]})
        b = track['bounds']
        anchor = track.get('pivot', [(b[0]+b[2])/2, (b[1]+b[3])/2])
        position = [target[i]+(anchor[i]-center[i])*fit for i in (0, 1)]
        item = layer(track['name'], shapes, frames, anchor, position, fit*100)
        def prop(field, mapper):
            values = [(f['time'], mapper(f[field])) for f in keyframes]
            return static(values[0][1]) if all(v == values[0][1] for _, v in values) else keys(values, fps, track['easing'])
        item['ks']['p'] = prop('offset', lambda v: [position[0]+v[0]*fit, position[1]+v[1]*fit, 0])
        if any('curve' in f for f in keyframes):
            item['ks']['p'] = keys([(f['time'], [position[i]+f['offset'][i]*fit for i in (0,1)]+[0])
                                     for f in keyframes], fps, track['easing'])
            for frame, source in zip(item['ks']['p']['k'][:-1],keyframes):
                curve = source.get('curve', {'out':[0,0], 'in':[0,0]})
                frame.update(to=[v*fit for v in curve['out']]+[0], ti=[v*fit for v in curve['in']]+[0])
        angles = [(f['time'], [f.get('rotation',0)]) for f in keyframes]
        item['ks']['r'] = static(angles[0][1][0]) if all(v==angles[0][1] for _,v in angles) else keys(angles,fps,track['easing'])
        item['ks']['s'] = prop('scale', lambda v: [v*fit, v*fit, 100])
        item['ks']['o'] = (static(keyframes[0]['opacity']) if all(f['opacity'] == keyframes[0]['opacity'] for f in keyframes)
                           else keys([(f['time'], [f['opacity']]) for f in keyframes], fps, track['easing']))
        layers.append(item)
        box = track_bounds(track)
        boxes.append([target[0]+(box[0]-center[0])*fit, target[1]+(box[1]-center[1])*fit,
                      target[0]+(box[2]-center[0])*fit, target[1]+(box[3]-center[1])*fit])
        samples.update(f['time'] for f in keyframes)
        samples.update((a['time']+b['time'])/2 for a,b in zip(keyframes,keyframes[1:]))
        if any(f.get('rotation',0) or 'curve' in f for f in keyframes):
            samples.update(i/fps for i in range(math.floor(keyframes[0]['time']*fps),math.ceil(keyframes[-1]['time']*fps)+1))
        if keyframes[0]['opacity'] == 0:
            entrances.append({'layer': track['name'], 'start_frame': keyframes[0]['time']*fps,
                              'opaque_frame': keyframes[-1]['time']*fps})
    return layers, boxes, entrances, samples, drawings
