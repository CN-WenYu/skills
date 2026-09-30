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
*{{box-sizing:border-box}}
:root{{color-scheme:light}}
body{{margin:0;background:#f3f4f5;color:#202326;font:15px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
main{{max-width:960px;margin:0 auto;padding:40px 28px 24px}}
h1{{margin:0 0 28px;font-size:clamp(22px,4vw,30px);font-weight:650;letter-spacing:-.025em;text-wrap:balance}}
.preview{{padding:28px 16px;background:#e8eaed;border-radius:16px}}
#stage{{margin:0 auto;width:min(100%,{width}px);aspect-ratio:{width}/{height};background:{matte_css};box-shadow:0 12px 32px rgba(20,26,32,.09)}}
#animation{{width:100%;height:100%}}
.toolbar{{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:24px}}
.playback{{display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
button,select{{min-height:44px;border:1px solid #b8bec5;border-radius:8px;background:#fff;color:#202326;font:inherit}}
button{{padding:10px 18px;font-weight:600;cursor:pointer}}
select{{appearance:none;padding:9px 42px 9px 12px;cursor:pointer;max-width:100%;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='m1 1 5 5 5-5' fill='none' stroke='%23505861' stroke-width='1.5'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center}}
@media(forced-colors:active){{select{{appearance:auto;background-image:none}}}}
label{{display:flex;align-items:center;gap:10px;color:#505861;font-size:14px}}
#download-json{{background:#202326;border-color:#202326;color:#fff}}
button:active{{transform:translateY(1px)}}
button:disabled{{opacity:.5;cursor:not-allowed}}
:focus-visible{{outline:3px solid #2864b4;outline-offset:4px}}
::selection{{background:#d0e1f6;color:#172c45}}
.hint{{margin:12px 0 0;color:#505861;font-size:13px}}
details{{margin-top:32px;padding-top:16px;border-top:1px solid #cdd1d6;color:#505861;font-size:13px}}
summary{{cursor:pointer;width:fit-content;padding:8px 0;text-underline-offset:3px}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.7 ui-monospace,monospace;max-width:75ch}}
@media(hover:hover){{button:hover,select:hover{{background-color:#e9edf1}}#download-json:hover{{background:#394049;border-color:#394049}}summary:hover{{color:#202326;text-decoration:underline}}}}
@media(max-width:600px){{main{{padding:24px 16px}}h1{{margin-bottom:20px}}.preview{{padding:16px 8px}}.toolbar{{align-items:stretch;gap:16px}}.playback{{width:100%;justify-content:space-between}}label{{flex-wrap:wrap;gap:4px 8px}}#download-json{{width:100%}}}}
html.embedded main{{max-width:none;padding:12px}}
html.embedded h1{{display:none}}
html.embedded .preview{{padding:0;background:none;border-radius:0}}
html.embedded .toolbar{{margin-top:16px}}
html.embedded details{{margin-top:16px}}
</style><script>if(window.parent!==window)document.documentElement.classList.add('embedded');</script></head><body><main><h1>Logo animation preview</h1>
<div class="preview"><div id="stage" role="img" aria-label="Logo animation preview"><div id="animation"></div></div></div>
<div class="toolbar"><div class="playback"><button id="replay" type="button">Replay</button><label>Preview background <select id="matte">
<option value="original">Selected</option><option value="#ffffff">Light</option><option value="#181818">Dark</option>
<option value="checker">Checkerboard</option></select></label></div>
<button id="download-json" type="button">Download Lottie JSON</button></div>
<p class="hint">Background selection affects this preview only.</p>
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
if(window.parent!==window){{
  window.addEventListener('message',event=>{{
    if(event.source===window.parent&&event.data?.type==='lottie-preview-replay')window.logoAnimation.goToAndPlay(0,true);
  }});
  const reportHeight=()=>window.parent.postMessage({{type:'lottie-preview-height',height:Math.ceil(document.querySelector('main').getBoundingClientRect().height)}},'*');
  new ResizeObserver(reportHeight).observe(document.querySelector('main'));
  reportHeight();
}}
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


def write_comparison(output, variants, groups=None):
    """Link immutable previews in a responsive review list."""
    import os
    from urllib.parse import quote
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Comparison output exists. Choose a new HTML path.')
    if len(variants) < 2:
        raise ValueError('A comparison needs at least two named variants.')
    membership = {}
    for group, label in groups or []:
        if not group.strip() or label in membership:
            raise ValueError('Groups need nonempty names and each variant can belong to only one group.')
        membership[label] = group
    sections, labels = {}, set()
    for label, directory in variants:
        if not label.strip() or label in labels:
            raise ValueError('Variant labels must be nonempty and unique.')
        labels.add(label)
        directory = Path(directory).resolve()
        verify_draft(directory)
        url = quote(Path(os.path.relpath(directory/'preview.html', output.parent)).as_posix(), safe='/')
        sections.setdefault(membership.get(label, ''), []).append((label, url))
    if membership.keys() - labels:
        raise ValueError('Group references an unknown variant label.')
    content = []
    for group, entries in sections.items():
        cards = ''.join(
            f'<article><div class="card-heading"><h3>{html.escape(label)}</h3>'
            f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">Open separately</a></div>'
            f'<iframe title="{html.escape(label, quote=True)}" src="{html.escape(url, quote=True)}"></iframe></article>'
            for label, url in entries)
        content.append(f'<section><div class="group-heading"><h2>{html.escape(group or "Versions")}</h2>'
                       f'<button type="button">Replay group</button></div><div class="grid">{cards}</div></section>')
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Compare logo animations</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f4f5;color:#202326;font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1600px;margin:auto;padding:28px}}h1{{font-size:26px;letter-spacing:-.025em;margin:0 0 8px}}
section{{margin-top:32px}}h2{{font-size:20px;margin:0}}h3{{font-size:16px;margin:0;overflow-wrap:anywhere}}
.group-heading,.card-heading{{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:20px;align-items:start}}
article{{min-width:0;background:#f3f4f5;border:1px solid #d5d9dd;border-radius:12px;padding:12px}}
a{{color:#244e83;text-underline-offset:3px;padding:10px 0}}a:hover{{color:#172c45}}
button{{min-height:44px;padding:8px 16px;border:1px solid #b8bec5;border-radius:8px;background:white;color:inherit;font:inherit;cursor:pointer}}
button:hover{{background:#e9edf1}}:focus-visible{{outline:3px solid #2864b4;outline-offset:4px}}
p{{color:#505861;margin:0}}iframe{{display:block;border:0;width:100%;height:900px}}
@media(max-width:600px){{main{{padding:20px 12px}}article{{padding:8px}}.grid{{gap:16px}}}}
</style></head><body><main><h1>Compare logo animations</h1>
<p>Browse versions below. Open separately for a larger view; download each version inside its preview.</p>
{''.join(content)}</main><script>
const frames=[...document.querySelectorAll('iframe')];
document.querySelectorAll('section button').forEach(button=>{{
  button.onclick=()=>button.closest('section').querySelectorAll('iframe').forEach(frame=>frame.contentWindow.postMessage({{type:'lottie-preview-replay'}},'*'));
}});
window.addEventListener('message',event=>{{
  const frame=frames.find(frame=>frame.contentWindow===event.source);
  if(!frame||event.data?.type!=='lottie-preview-height')return;
  const height=event.data.height;
  if(Number.isFinite(height)&&height>0&&height<=100000)frame.style.height=Math.ceil(height)+'px';
}});
</script></body></html>'''
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        stream.write(page)
    return {'status': 'ready', 'comparison': str(output), 'variants': len(variants),
            'note': 'Linked previews remain independent; comparison does not validate or approve them.'}
