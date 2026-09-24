#!/usr/bin/env python3
"""Inspect decisions, generate reproducible Lottie drafts, validate and record approval."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from configuration import DecisionRequired, load_config


def doctor():
    expected = {'Pillow': '11.3.0', 'fonttools': '4.60.1', 'uharfbuzz': '0.56.2'}
    actual = {}
    for name, version in expected.items():
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            installed = None
        actual[name] = {'expected': version, 'installed': installed, 'matches': installed == version}
    return {'status': 'ready' if all(x['matches'] for x in actual.values()) else 'needs_decision',
            'python': actual, 'commands': {x: shutil.which(x) for x in ('node', 'vtracer', 'svgo', 'rsvg-convert', 'magick')},
            'note': 'No installation performed. Player package is checked when drafting; SVG renderer/VTracer are needed only for raster input.'}


def check_dependencies():
    if doctor()['status'] != 'ready':
        raise DecisionRequired('Pinned Python dependencies are missing or differ. Run doctor and confirm the documented isolated setup.')


def inventory(source, converter):
    source = Path(source)
    if source.suffix.lower() != '.svg':
        if not converter or not Path(converter).is_file():
            raise DecisionRequired('Raster inventory requires the explicitly located image-to-svg script.')
        result = subprocess.run([sys.executable, str(converter), str(source), '--inspect'], capture_output=True, text=True, timeout=180)
        return json.loads(result.stdout)
    from svg_geometry import load_svg
    asset = load_svg(source)
    elements = []
    for entry in asset['elements']:
        items = entry['shape']['it']
        paths = [item for item in items if item['ty'] == 'sh']
        filled = any(item['ty'] in ('fl', 'gf') for item in items)
        stroked = any(item['ty'] in ('st', 'gs') for item in items)
        elements.append({'ids': entry['ids'], 'bounds': entry['bounds'], 'filled': filled, 'stroked': stroked,
                         'open_stroke_drawing': len(paths) == 1 and not paths[0]['ks']['k']['c'] and stroked and not filled})
    return {'status': 'ready', 'viewport': [asset['width'], asset['height']], 'elements': elements,
            'next': 'Inspect the artwork visually; author semantic roles and a material-specific motion plan. Geometry inventory does not infer meaning.'}


def source_asset(config, converter, temporary):
    from svg_geometry import load_svg
    source = Path(config['source'])
    if not source.is_file():
        raise DecisionRequired(f'Source file is unavailable: {source}')
    if source.suffix.lower() == '.svg':
        if config['source_background'] == 'remove':
            raise DecisionRequired('Identify the SVG background element and provide a reviewed foreground SVG; no background element is guessed.')
        if config.get('image_options'):
            raise DecisionRequired('Raster image_options do not apply to SVG input.')
        asset = load_svg(source)
    else:
        if config['artwork']['backplate']['mode'] == 'embedded':
            raise DecisionRequired('Embedded backplate IDs require a reviewed SVG. Convert and review the raster first, then identify its backplate; no automatic path selection.')
        if not converter or not Path(converter).is_file():
            raise DecisionRequired('Locate the installed image-to-svg conversion script and pass --image-converter explicitly.')
        output = Path(temporary) / 'traced.svg'
        command = [sys.executable, str(Path(converter).resolve()), str(source), str(output),
                   '--background', config['source_background']]
        for key, value in config.get('image_options', {}).items():
            if key == 'no_svgo':
                if value: command.append('--no-svgo')
            else:
                command += ['--' + key.replace('_', '-'), str(value)]
        result = subprocess.run(command, text=True, capture_output=True, timeout=180)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise DecisionRequired(f'Image conversion did not return a valid report: {result.stderr or result.stdout}') from error
        if result.returncode or report.get('status') != 'ready':
            raise DecisionRequired(f'Image conversion requires attention: {json.dumps(report, ensure_ascii=False)}')
        asset = load_svg(output)
        asset['image_report'] = report
    return asset


def inspect_config(config, converter, temporary):
    from animation import build_animation
    from artwork import prepare_artwork
    asset = source_asset(config, converter, temporary)
    b = asset['bounds']
    if b[0] < -1e-5 or b[1] < -1e-5 or b[2] > asset['width'] + 1e-5 or b[3] > asset['height'] + 1e-5:
        raise DecisionRequired('SVG geometry/stroke extends outside its viewport. Confirm a cleaned viewBox or cropping strategy before animation.')
    asset = prepare_artwork(asset, config)
    animation, report = build_animation(asset, config)
    from preview import optimize_animation
    animation, report['size'] = optimize_animation(animation, config.get('optimization'))
    if 'image_report' in asset:
        report['image_conversion'] = asset['image_report']
    return asset, animation, report


def approve(directory, statement, visually_reviewed):
    from preview import verify_draft, json_text, digest
    directory = Path(directory)
    manifest = verify_draft(directory)
    report = json.loads((directory / 'validation.json').read_text())
    if not visually_reviewed or not statement or not statement.strip():
        raise DecisionRequired('Inspect the actual sampled frames and obtain explicit user approval, then supply --visual-review and --statement.')
    if report.get('web') != 'passed' or report.get('animation_sha256') != manifest['files']['animation.json']:
        raise DecisionRequired('Run Web validation for this exact animation before recording approval.')
    if report.get('preview_sha256') != manifest['files']['preview.html']:
        raise DecisionRequired('The rendered preview does not match this draft.')
    config = json.loads((directory/'config.json').read_text())
    if config.get('optimization', {}).get('coordinate_precision') is not None:
        comparison = report.get('comparison', {})
        reference_hash = manifest.get('unrounded_animation_sha256')
        if not reference_hash or comparison.get('status') != 'measured' or comparison.get('reference_sha256') != reference_hash:
            raise DecisionRequired('Coordinate rounding needs Web comparison against the matching unrounded animation via validate --reference-json, plus visual review.')
    destination = directory / 'approval.json'
    if destination.exists():
        raise DecisionRequired('Approval already recorded; do not overwrite the original statement.')
    destination.write_text(json_text({'status': 'approved', 'statement': statement.strip(),
        'files': manifest['files'], 'validation_sha256': digest((directory / 'validation.json').read_bytes()),
        'visual_review': 'completed', 'native_platforms': 'not_verified'}))
    return {'status': 'approved', 'animation': str(directory / 'animation.json'), 'native_platforms': 'not_verified'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    p = sub.add_parser('size')
    p.add_argument('source', type=Path)
    p = sub.add_parser('fonts')
    p.add_argument('text')
    p.add_argument('--weight', type=int, default=700)
    p.add_argument('--limit', type=int, default=5)
    p = sub.add_parser('inventory')
    p.add_argument('source', type=Path)
    p.add_argument('--image-converter', type=Path)
    for name in ('inspect', 'draft'):
        p = sub.add_parser(name)
        p.add_argument('config', type=Path)
        p.add_argument('--image-converter', type=Path)
        if name == 'draft':
            p.add_argument('--output', type=Path, required=True)
            p.add_argument('--player-package', type=Path, required=True)
    p = sub.add_parser('validate')
    p.add_argument('directory', type=Path)
    p.add_argument('--playwright-package', type=Path, required=True)
    p.add_argument('--browser-channel', default='chromium')
    p.add_argument('--reference-json', type=Path)
    p = sub.add_parser('approve')
    p.add_argument('directory', type=Path)
    p.add_argument('--statement')
    p.add_argument('--visual-review', action='store_true')
    args = parser.parse_args()
    if args.command == 'doctor':
        report = doctor()
    elif args.command == 'size':
        from preview import animation_size
        payload = args.source.read_bytes()
        data = json.loads(payload)
        if not isinstance(data, dict) or not isinstance(data.get('layers'), list):
            raise ValueError('Size inspection requires a Lottie JSON object with layers.')
        report = {'status':'ready','file_bytes':len(payload),**animation_size(data)}
    elif args.command == 'fonts':
        from typography import font_candidates
        report = font_candidates(args.text, args.weight, limit=args.limit)
    elif args.command == 'inventory':
        report = inventory(args.source, args.image_converter)
    elif args.command == 'approve':
        report = approve(args.directory, args.statement, args.visual_review)
    elif args.command == 'validate':
        from preview import verify_draft
        verify_draft(args.directory)
        result = subprocess.run(['node', str(Path(__file__).with_name('validate_web.mjs')),
            str(args.directory.resolve()), str(args.playwright_package.resolve()), args.browser_channel,
            str(args.reference_json.resolve()) if args.reference_json else ''],
            capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise DecisionRequired(f'Web verification failed; inspect and resolve before delivery: {result.stdout} {result.stderr}')
        report = json.loads(result.stdout)
    else:
        config = load_config(args.config)
        check_dependencies()
        if args.command == 'draft' and args.output.exists():
            raise DecisionRequired('Draft output exists. Choose a new path to keep the previous review intact.')
        with tempfile.TemporaryDirectory(prefix='logo-inspect-') as temporary:
            asset, animation, evidence = inspect_config(config, args.image_converter, temporary)
            report = {'status': 'ready', 'structure': 'passed', 'animation': {
                'width': animation['w'], 'height': animation['h'], 'layers': len(animation['layers'])},
                'composition': evidence['composition'],
                'size': evidence['size'],
                'native_platforms': 'not_verified'}
            if args.command == 'draft':
                from preview import write_draft
                manifest = write_draft(args.output, config, asset, animation, evidence, args.player_package)
                report.update(status='draft', output=str(args.output.resolve()), files=manifest['files'])
    print(json.dumps(report, ensure_ascii=False, allow_nan=False))
    return 2 if report.get('status') == 'needs_decision' else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (DecisionRequired, ValueError, FileNotFoundError, ImportError) as error:
        print(json.dumps({'status': 'needs_decision', 'questions': [str(error)]}, ensure_ascii=False))
        raise SystemExit(2)
    except (OSError, subprocess.SubprocessError) as error:
        print(json.dumps({'status': 'failed', 'error': str(error)}, ensure_ascii=False))
        raise SystemExit(1)
