"""Validate only supported choices; never silently ignore a requested visual option."""
import json
import math
import re
import unicodedata
from pathlib import Path


class DecisionRequired(ValueError):
    pass


def download_filename(config):
    wordmark = config.get('wordmark')
    name = config.get('app_name', wordmark.get('text') if isinstance(wordmark, dict) else None)
    if not isinstance(name, str) or not name.strip():
        raise DecisionRequired('Provide the verified app_name for the JSON download; reuse wordmark.text when it is the application name.')
    name = unicodedata.normalize('NFC', name).lower()
    prefix = re.sub(r'[\W_]+', '_', name).strip('_')
    if not prefix or not any(c.isalnum() for c in prefix):
        raise DecisionRequired('The application name has no usable filename characters; ask for a filename prefix.')
    return f'{prefix}_loading.json'


def allowed(obj, keys, label):
    if not isinstance(obj, dict):
        raise DecisionRequired(f'{label} must be an object.')
    unknown = set(obj) - set(keys)
    if unknown:
        raise DecisionRequired(f'Unsupported {label} options: {sorted(unknown)}. Confirm their intended behavior.')


def positive(value, label, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= minimum:
        raise DecisionRequired(f'{label} must be finite and greater than {minimum}.')


def validate_optimization(options):
    allowed(options, {'coordinate_precision', 'user_request'}, 'optimization')
    if 'coordinate_precision' in options:
        precision = options['coordinate_precision']
        if isinstance(precision, bool) or not isinstance(precision, int) or not 3 <= precision <= 6:
            raise DecisionRequired('Coordinate precision must be an integer from 3 to 6.')
        if not isinstance(options.get('user_request'), str) or not options['user_request'].strip():
            raise DecisionRequired('Coordinate rounding needs user_request quoting the accepted precision; size reduction alone is not consent to approximation.')


def pair(value, label):
    if not isinstance(value, list) or len(value) != 2:
        raise DecisionRequired(f'{label} must contain two coordinates.')
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in value):
        raise DecisionRequired(f'{label} coordinates must be finite numbers.')


def css_color(value):
    from PIL import ImageColor
    if not isinstance(value, str):
        raise DecisionRequired('Colors must be explicit CSS color strings.')
    try:
        ImageColor.getcolor(value, 'RGBA')
    except (ValueError, TypeError) as error:
        raise DecisionRequired(f'Unsupported color {value!r}; choose a supported CSS color.') from error


def validate_background(bg, allow_motion=False):
    kind = bg.get('type') if isinstance(bg, dict) else None
    choices = {'transparent': {'type'}, 'solid': {'type', 'color'},
               'linear': {'type', 'start', 'end', 'stops'}, 'radial': {'type', 'center', 'radius', 'stops'}}
    if not isinstance(kind, str) or kind not in choices:
        raise DecisionRequired('Choose export_background.type: transparent, solid, linear, or radial.')
    allowed(bg, choices[kind] | ({'motion'} if allow_motion and kind != 'transparent' else set()), 'background')
    if not choices[kind] <= bg.keys():
        raise DecisionRequired(f'Incomplete {kind} background parameters; ask for the missing values.')
    if kind == 'solid':
        css_color(bg['color'])
    if kind == 'linear':
        pair(bg['start'], 'gradient start'); pair(bg['end'], 'gradient end')
        if bg['start'] == bg['end']:
            raise DecisionRequired('Gradient start and end must differ.')
    if kind == 'radial':
        pair(bg['center'], 'gradient center'); positive(bg['radius'], 'gradient radius')
    if kind in ('linear', 'radial'):
        stops = bg['stops']
        if not isinstance(stops, list) or len(stops) < 2:
            raise DecisionRequired('A gradient requires at least two confirmed stops.')
        last = -1
        for stop in stops:
            allowed(stop, {'offset', 'color', 'opacity'}, 'gradient stop')
            if not {'offset', 'color'} <= stop.keys():
                raise DecisionRequired('Each stop needs offset and color.')
            css_color(stop['color'])
            for key in ('offset', 'opacity'):
                value = stop.get(key, 1)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
                    raise DecisionRequired(f'Gradient {key} must be between 0 and 1.')
            if stop['offset'] < last:
                raise DecisionRequired('Gradient stops must be in increasing order.')
            last = stop['offset']


def validate_artwork(config):
    artwork = config.get('artwork')
    allowed(artwork, {'existing_wordmark', 'backplate'}, 'artwork roles (replace asset_roles_confirmed)')
    if artwork.get('existing_wordmark') not in ('absent', 'symbols', 'preserve'):
        raise DecisionRequired('Identify whether source lettering is absent, pictorial symbols, or a brand wordmark to preserve.')
    plate = artwork.get('backplate')
    allowed(plate, {'mode', 'element_ids', 'corners', 'paint'}, 'icon backplate')
    mode = plate.get('mode')
    if mode not in ('none', 'embedded', 'generated'):
        raise DecisionRequired('Confirm icon backplate mode: none, embedded SVG elements, or generated behind a foreground-only source.')
    keys = {'none': {'mode'}, 'embedded': {'mode', 'element_ids', 'corners'},
            'generated': {'mode', 'paint', 'corners'}}[mode]
    allowed(plate, keys, 'icon backplate')
    if not keys <= plate.keys():
        raise DecisionRequired('Confirm missing icon backplate mapping, paint or corner choice.')
    if mode == 'embedded':
        ids = plate['element_ids']
        if not isinstance(ids, list) or not ids or any(not isinstance(x, str) or not x for x in ids):
            raise DecisionRequired('Map the backplate to explicit nonempty SVG element/group IDs.')
        if len(ids) != len(set(ids)):
            raise DecisionRequired('Backplate IDs must be unique.')
    if mode != 'none':
        corners = plate['corners']
        allowed(corners, {'mode', 'radius'}, 'backplate corners')
        if corners.get('mode') not in ('preserve', 'square', 'rounded'):
            raise DecisionRequired('Confirm whether to preserve existing corners, use square corners, or round the icon backplate.')
        if corners['mode'] == 'rounded':
            positive(corners.get('radius'), 'confirmed corner radius in source SVG units')
        elif 'radius' in corners:
            raise DecisionRequired('Corner radius applies only to rounded corners.')
        if mode == 'generated':
            if corners['mode'] == 'preserve':
                raise DecisionRequired('A generated backplate requires an explicit square or rounded shape.')
            validate_background(plate['paint'])
            if plate['paint']['type'] == 'transparent':
                raise DecisionRequired('Use backplate mode none instead of a transparent generated backplate.')
    motion = config.get('motion')
    if isinstance(motion, dict) and 'preset' in motion:
        allowed(motion, {'preset', 'user_request'}, 'explicit legacy motion')
        if motion['preset'] == 'static-backplate' and (not isinstance(motion.get('user_request'), str) or not motion['user_request'].strip()):
            raise DecisionRequired('Static backplate requires the actual user_request; preservation of its color does not authorize a static entrance.')
        if motion['preset'] not in ('whole-icon', 'backplate-first', 'static-backplate'):
            raise DecisionRequired('Unsupported legacy preset; author a material-specific motion plan instead.')
        if mode == 'none' and motion['preset'] != 'whole-icon':
            raise DecisionRequired('The selected motion requires an explicitly mapped or generated icon backplate.')
    else:
        from choreography import validate_motion
        validate_motion(motion)


def validate_wordmark_motion(motion):
    from choreography import validate_easing, validate_keyframes
    allowed(motion, {'preset', 'tracks', 'rationale', 'start', 'duration', 'stagger',
                     'stagger_window', 'amplitude', 'anchor', 'user_request'}, 'wordmark motion')
    if not isinstance(motion.get('user_request'), str) or not motion['user_request'].strip():
        raise DecisionRequired('Record user_request with the actual text choice, accepted proposal or delegation; never invent consent.')
    if ('preset' in motion) == ('tracks' in motion):
        raise DecisionRequired('Choose exactly one explicit wordmark preset or authored tracks; delegation alone does not choose a preset.')
    if motion.get('anchor', 'baseline') not in ('baseline', 'center'):
        raise DecisionRequired('Unsupported wordmark anchor.')
    if 'rationale' in motion and (not isinstance(motion['rationale'], str) or not motion['rationale'].strip()):
        raise DecisionRequired('Wordmark rationale must explain its relationship to the logo motion.')
    if 'preset' in motion:
        if motion['preset'] not in ('hop', 'rise', 'fade', 'gather', 'reveal'):
            raise DecisionRequired('Unsupported wordmark preset; use authored tracks for supported custom motion.')
        for key in ('start', 'stagger', 'stagger_window', 'amplitude'):
            if key in motion: positive(motion[key], f'wordmark {key}', -1e-9)
        if 'duration' in motion: positive(motion['duration'], 'wordmark duration')
        return
    allowed(motion, {'tracks', 'rationale', 'anchor', 'user_request'}, 'authored wordmark motion')
    if 'rationale' not in motion:
        raise DecisionRequired('Explain the authored wordmark motion in rationale.')
    tracks = motion['tracks']
    if not isinstance(tracks, list) or not tracks:
        raise DecisionRequired('Wordmark tracks must be a nonempty list.')
    for track in tracks:
        allowed(track, {'target', 'units', 'keyframes', 'easing'}, 'wordmark track')
        if ('target' in track) == ('units' in track):
            raise DecisionRequired('Choose target line or explicit shaped units for each wordmark track.')
        if 'target' in track:
            if track['target'] != 'line' or len(tracks) != 1:
                raise DecisionRequired('A whole-line wordmark uses one target line track.')
        else:
            units = track['units']
            if (not isinstance(units, list) or not units or
                    any(isinstance(i, bool) or not isinstance(i, int) or i < 0 for i in units) or
                    len(set(units)) != len(units)):
                raise DecisionRequired('Wordmark units must be unique nonnegative shaped-unit indices.')
        validate_easing(track.get('easing', [.25, 0, .75, 1]))
        validate_keyframes(track.get('keyframes'))


def load_config(path):
    path = Path(path).resolve()
    config = json.loads(path.read_text())
    if isinstance(config, dict) and 'asset_roles_confirmed' in config:
        raise DecisionRequired('Replace asset_roles_confirmed with artwork.existing_wordmark and artwork.backplate; confirm background scope, corners and motion separately.')
    allowed(config, {'source', 'source_background', 'artwork', 'motion', 'preview_background', 'app_purpose', 'app_name',
                     'export_background', 'wordmark', 'canvas', 'fps', 'duration', 'hold', 'image_options', 'optimization'}, 'configuration')
    validate_optimization(config.get('optimization', {}))
    if 'app_name' in config:
        download_filename(config)
    required = {'source', 'artwork', 'motion'}
    if not required <= config.keys():
        raise DecisionRequired(f'Confirm missing choices: {sorted(required - config.keys())}.')
    validate_artwork(config)
    if 'app_purpose' in config and not isinstance(config['app_purpose'], str):
        raise DecisionRequired('Optional app_purpose must be text, not a required questionnaire.')
    config.setdefault('source_background', 'preserve')
    config.setdefault('export_background', {'type': 'transparent'})
    config.setdefault('preview_background', '#f4f4f4')
    if config['source_background'] not in ('preserve', 'remove'):
        raise DecisionRequired('Confirm whether to preserve or remove the source background.')
    validate_background(config['export_background'], allow_motion=True)
    if config['export_background']['type'] != 'transparent':
        entrance = config['export_background'].setdefault('motion', {})
        allowed(entrance, {'start', 'duration', 'user_request'}, 'export background entrance')
        positive(entrance.setdefault('start', 0), 'background start', -1e-9)
        positive(entrance.setdefault('duration', .3), 'background duration', -1e-9)
        if entrance['duration'] == 0:
            if entrance['start'] != 0 or not isinstance(entrance.get('user_request'), str) or not entrance['user_request'].strip():
                raise DecisionRequired('A static full-canvas background requires start 0 and the actual user_request.')
    css_color(config['preview_background'])
    def resolve(value):
        if not isinstance(value, str) or not value:
            raise DecisionRequired('A nonempty file path is required.')
        p = Path(value).expanduser()
        return str((path.parent / p).resolve())
    config['source'] = resolve(config['source'])
    canvas = config.setdefault('canvas', {})
    allowed(canvas, {'width', 'height', 'padding', 'icon_width'}, 'canvas')
    if 'icon_width' in canvas:
        positive(canvas['icon_width'], 'icon width')
    for key in ('width', 'height'):
        positive(canvas.setdefault(key, 512), f'canvas {key}')
        if int(canvas[key]) != canvas[key]:
            raise DecisionRequired('Canvas dimensions must be integer pixels.')
    padding = canvas.setdefault('padding', 32)
    positive(padding, 'padding', -1e-9)
    if padding * 2 >= min(canvas['width'], canvas['height']):
        raise DecisionRequired('Padding leaves no room for the artwork.')
    positive(config.setdefault('fps', 30), 'fps')
    if 'duration' in config:
        positive(config['duration'], 'duration')
    positive(config.setdefault('hold', .35), 'settled hold')
    wordmark = config.get('wordmark')
    if wordmark is not None:
        allowed(wordmark, {'text', 'font', 'size', 'color', 'font_index', 'weight', 'placement', 'gap', 'relationship', 'motion'}, 'wordmark')
        if wordmark.setdefault('placement', 'below-icon') != 'below-icon':
            raise DecisionRequired('This layout supports an external name below the complete icon; discuss another layout before generation.')
        if 'gap' in wordmark:
            positive(wordmark['gap'], 'settled wordmark gap', -1e-9)
        if 'relationship' in wordmark and wordmark['relationship'] != 'additional':
            raise DecisionRequired('Unsupported wordmark relationship.')
        if config['artwork']['existing_wordmark'] == 'preserve' and wordmark.get('relationship') != 'additional':
            raise DecisionRequired('Artwork already contains text. Confirm that the separate application name is additional before duplicating branding.')
        if not isinstance(wordmark.get('text'), str):
            raise DecisionRequired('Wordmark text must be a string.')
        weight = wordmark.setdefault('weight', 700)
        if isinstance(weight, bool) or not isinstance(weight, int) or not 1 <= weight <= 1000:
            raise DecisionRequired('Font weight must be an integer between 1 and 1000.')
        missing = [key for key in ('font', 'color') if key not in wordmark]
        if missing:
            raise DecisionRequired(f'Choose wordmark {", ".join(missing)} with the user. List installed font candidates; preview matte does not choose export text color.')
        wordmark['font'] = resolve(wordmark['font'])
        css_color(wordmark['color'])
        if 'size' in wordmark:
            positive(wordmark['size'], 'font size')
        index = wordmark.setdefault('font_index', 0)
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise DecisionRequired('font_index must be a nonnegative integer.')
        validate_wordmark_motion(wordmark.get('motion', {}))
    options = config.setdefault('image_options', {})
    allowed(options, {'mode', 'fill', 'alpha_threshold', 'no_svgo'}, 'image options')
    if options.get('mode', 'auto') not in ('auto', 'spline', 'polygon', 'pixel'):
        raise DecisionRequired('Unsupported tracing mode.')
    if options.get('fill', 'keep') not in ('keep', 'white'):
        raise DecisionRequired('Unsupported recoloring policy.')
    if 'alpha_threshold' in options:
        v = options['alpha_threshold']
        if not isinstance(v, int) or isinstance(v, bool) or not 1 <= v <= 254:
            raise DecisionRequired('alpha_threshold must be an explicitly confirmed integer from 1 to 254.')
    if 'no_svgo' in options and not isinstance(options['no_svgo'], bool):
        raise DecisionRequired('no_svgo must be boolean.')
    return config
