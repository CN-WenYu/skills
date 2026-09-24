"""Package the exact animation and pinned player into an offline review page."""
import hashlib
import html
import json
import math
from copy import deepcopy
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_text(value):
    return json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(',', ':')).replace('<', '\\u003c')


def animation_size(animation):
    """Measure JSON cost without changing the artwork or treating HTML as JSON."""
    size = lambda value: len(json_text(value).encode('utf-8'))
    report = {'json_bytes': size(animation), 'paths': 0, 'path_vertices': 0,
              'path_bytes': 0, 'animated_properties': 0, 'keyframes': 0, 'keyframe_bytes': 0}
    def visit(value):
        if isinstance(value, dict):
            if all(k in value for k in ('v','i','o','c')) and isinstance(value['v'], list):
                report['paths'] += 1
                report['path_vertices'] += len(value['v'])
                report['path_bytes'] += size(value)
            if value.get('a') == 1 and isinstance(value.get('k'), list):
                report['animated_properties'] += 1
                report['keyframes'] += len(value['k'])
                report['keyframe_bytes'] += size(value)
            for item in value.values(): visit(item)
        elif isinstance(value, list):
            for item in value: visit(item)
    visit(animation)
    layers = animation.get('layers', [])
    report['largest_layers'] = sorted(
        [{'index': i, 'name': item.get('nm'), 'bytes': size(item)} for i,item in enumerate(layers)],
        key=lambda item: item['bytes'], reverse=True)[:5]
    return report


def optimize_animation(animation, options=None):
    """Compact numeric writing and provably idle keyframes; round only by request."""
    from configuration import validate_optimization
    options = {} if options is None else options
    validate_optimization(options)
    precision = options.get('coordinate_precision')
    result = deepcopy(animation)
    before = animation_size(animation)
    stats = {'removed_keyframes': 0, 'static_properties': 0, 'rounded_coordinates': 0,
             'max_local_coordinate_error': 0}
    def numeric(value):
        return isinstance(value, (int,float)) and not isinstance(value, bool) and math.isfinite(value)
    def trim(prop):
        if set(prop) != {'a','k'} or prop.get('a') != 1 or not isinstance(prop.get('k'), list): return
        frames = prop['k']
        if not frames: return
        for index, frame in enumerate(frames):
            if not isinstance(frame, dict) or set(frame)-{'t','s','e','h','i','o'}: return
            if not numeric(frame.get('t')) or not isinstance(frame.get('s'), list) or not frame['s'] or not all(map(numeric,frame['s'])): return
            if frame.get('h',0) != 0: return
            if index < len(frames)-1:
                nxt = frames[index+1]
                if not isinstance(nxt,dict) or not numeric(nxt.get('t')) or nxt['t'] <= frame['t'] or frame.get('e') != nxt.get('s'): return
                if set(frame.get('i',{})) != {'x','y'} or set(frame.get('o',{})) != {'x','y'}: return
        count = len(frames)
        if all(f['s'] == frames[0]['s'] for f in frames):
            value = frames[0]['s']
            prop.update(a=0,k=value[0] if len(value)==1 else value)
            stats['static_properties'] += 1
            stats['removed_keyframes'] += count
            return
        while len(frames)>1 and frames[0]['s'] == frames[0]['e'] == frames[1]['s']:
            frames.pop(0)
        while len(frames)>1 and frames[-2]['s'] == frames[-2]['e'] == frames[-1]['s']:
            frames[-2] = {'t':frames[-2]['t'],'s':frames[-2]['s']}
            frames.pop()
        stats['removed_keyframes'] += count-len(frames)
    def rounded(value):
        if isinstance(value,list): return [rounded(item) for item in value]
        if numeric(value):
            new = round(value,precision)
            if new != value:
                stats['rounded_coordinates'] += 1
                stats['max_local_coordinate_error'] = max(stats['max_local_coordinate_error'],abs(value-new))
            return new
        return value
    def coordinates(prop):
        if not isinstance(prop,dict) or set(prop)-{'a','k'}: return
        if prop.get('a') == 0: prop['k'] = rounded(prop['k'])
        elif prop.get('a') == 1:
            for frame in prop['k']:
                for key in ('s','e'):
                    if key in frame: frame[key] = rounded(frame[key])
    def visit(value):
        if isinstance(value,dict):
            trim(value)
            if precision is not None:
                if all(k in value for k in ('v','i','o','c')) and isinstance(value['v'],list):
                    for key in ('v','i','o'): value[key] = rounded(value[key])
                # Only layer/group position and anchor are quantized. Paint,
                # scale, angle, timing, easing and gradient stops stay exact.
                transforms = value.get('ks') if isinstance(value.get('ty'),int) else value if value.get('ty')=='tr' else None
                if isinstance(transforms,dict):
                    for key in ('p','a'): coordinates(transforms.get(key))
            return {key:visit(item) for key,item in value.items()}
        if isinstance(value,list): return [visit(item) for item in value]
        if isinstance(value,float) and math.isfinite(value) and value.is_integer():
            integer = int(value)
            if len(str(integer)) < len(repr(value)): return integer
        return value
    result = visit(result)
    after = animation_size(result)
    reference_hash = digest(json_text(optimize_animation(animation)[0]).encode('utf-8')) if precision is not None else None
    return result, {'before_bytes':before['json_bytes'],'after_bytes':after['json_bytes'],
                    'saved_bytes':before['json_bytes']-after['json_bytes'],
                    'coordinate_precision':precision,'approximation':precision is not None,
                    'reference_sha256':reference_hash,
                    **stats, 'before':before,'after':after}


def player_files(package):
    package = Path(package)
    metadata = json.loads((package / 'package.json').read_text())
    if metadata.get('name') != 'lottie-web' or metadata.get('version') != '5.12.2':
        raise ValueError('Use the pinned lottie-web 5.12.2 package.')
    script = (package / 'build/player/lottie.min.js').read_text()
    license_text = (package / 'LICENSE.md').read_text()
    return script, license_text


def render_preview(animation_json, config, player, license_text):
    from configuration import download_filename
    # JSON and source script have separate escaping needs inside HTML raw-text elements.
    script = player.replace('</script', '<\\/script')
    from PIL import ImageColor
    matte = ImageColor.getcolor(config['preview_background'], 'RGBA')
    matte_css = f'rgba({matte[0]},{matte[1]},{matte[2]},{matte[3]/255})'
    width, height = config['canvas']['width'], config['canvas']['height']
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Logo animation preview</title><style>
body{{margin:0;background:#ececec;color:#222;font:15px system-ui;text-align:center}}
main{{padding:24px}}#stage{{margin:16px auto;width:min(100%,{width}px);aspect-ratio:{width}/{height};background:{matte_css};}}
#animation{{width:100%;height:100%}}button,select{{font:inherit;padding:8px;margin:4px}}
details{{max-width:720px;margin:24px auto;text-align:left}}pre{{white-space:pre-wrap}}
</style></head><body><main><h1>Logo animation preview</h1>
<div id="stage"><div id="animation"></div></div>
<button id="replay">Replay</button><button id="download-json" type="button">Download Lottie JSON</button><label>Preview background <select id="matte">
<option value="original">Selected</option><option value="#ffffff">Light</option><option value="#181818">Dark</option>
<option value="checker">Checkerboard</option></select></label>
<p>Background selection affects this preview only.</p>
<details><summary>Player license</summary><pre>{html.escape(license_text)}</pre></details></main>
<script id="animation-data" type="application/json">{animation_json}</script>
<script>{script}</script><script>
const data=JSON.parse(document.getElementById('animation-data').textContent);
window.logoAnimation=lottie.loadAnimation({{container:document.getElementById('animation'),renderer:'svg',loop:false,autoplay:true,animationData:data}});
document.getElementById('replay').onclick=()=>window.logoAnimation.goToAndPlay(0,true);
document.getElementById('download-json').onclick=()=>{{
  const blob=new Blob([document.getElementById('animation-data').textContent],{{type:'application/json;charset=utf-8'}});
  const url=URL.createObjectURL(blob), link=document.createElement('a');
  link.href=url;link.download={json_text(download_filename(config))};document.body.appendChild(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}};
document.getElementById('matte').onchange=e=>{{let stage=document.getElementById('stage');stage.style.background=e.target.value==='original'?{json.dumps(matte_css)}:e.target.value==='checker'?'repeating-conic-gradient(#ccc 0% 25%,#fff 0% 50%) 0 / 24px 24px':e.target.value;}};
</script></body></html>'''


def write_draft(directory, config, asset, animation, report, package):
    from configuration import download_filename
    filename = download_filename(config)
    directory = Path(directory)
    if directory.exists():
        raise ValueError('Draft directory already exists. Choose a new draft directory.')
    player, license_text = player_files(package)
    animation_json = json_text(animation)
    preview = render_preview(animation_json, config, player, license_text)
    files = {'animation.json': animation_json, 'preview.html': preview,
             'normalized.svg': asset['normalized_svg'], 'config.json': json_text(config),
             'PLAYER-LICENSE.txt': license_text}
    inputs = {'source': {'path': config['source'], 'sha256': digest(Path(config['source']).read_bytes())}}
    if config.get('wordmark'):
        font = config['wordmark']['font']
        inputs['font'] = {'path': font, 'sha256': digest(Path(font).read_bytes())}
    manifest = {'status': 'draft', 'download_filename': filename,
                'files': {name: digest(value.encode()) for name, value in files.items()},
                'inputs': inputs, 'player': {'version': '5.12.2', 'sha256': digest(player.encode())}}
    if config.get('optimization', {}).get('coordinate_precision') is not None:
        reference_hash = report.get('size', {}).get('reference_sha256')
        if not reference_hash:
            raise ValueError('Rounded draft requires a matching unrounded reference hash.')
        manifest['unrounded_animation_sha256'] = reference_hash
    directory.mkdir(parents=True)
    for name, data in files.items():
        (directory / name).write_text(data)
    (directory / 'manifest.json').write_text(json_text(manifest))
    (directory / 'validation.json').write_text(json_text({'structure': 'passed', 'web': 'not_run',
        'visual_review': 'pending', 'animation_sha256': manifest['files']['animation.json'], **report}))
    return manifest


def verify_draft(directory):
    from configuration import download_filename
    directory = Path(directory)
    manifest = json.loads((directory / 'manifest.json').read_text())
    expected = {'animation.json', 'preview.html', 'normalized.svg', 'config.json', 'PLAYER-LICENSE.txt'}
    if set(manifest.get('files', {})) != expected:
        raise ValueError('Incomplete draft manifest.')
    for name, expected_hash in manifest['files'].items():
        if digest((directory / name).read_bytes()) != expected_hash:
            raise ValueError(f'Draft changed: {name}. Regenerate, revalidate and request approval again.')
    if manifest.get('download_filename') != download_filename(json.loads((directory/'config.json').read_text())):
        raise ValueError('Download filename does not match the application name. Regenerate and revalidate the draft.')
    return manifest
