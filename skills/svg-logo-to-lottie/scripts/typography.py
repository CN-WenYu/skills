"""Select a real font face, shape the name and extract font-independent outlines."""
from pathlib import Path
from importlib import import_module
import os
import sys
import unicodedata

from fontTools.ttLib import TTFont, TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

from svg_paths import path_to_shapes, union


def font_roots():
    if sys.platform == 'darwin':
        return [Path('/System/Library/Fonts'), Path('/Library/Fonts'), Path.home()/'Library/Fonts']
    if sys.platform == 'win32':
        return [Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts',
                Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/'Microsoft/Windows/Fonts']
    return [Path('/usr/share/fonts'), Path('/usr/local/share/fonts'), Path.home()/'.local/share/fonts']


def font_candidates(text, weight=700, roots=None, limit=5):
    if not text.strip() or not 1 <= weight <= 1000 or not 1 <= limit <= 20:
        raise ValueError('Provide a nonempty name, weight 1..1000 and limit 1..20.')
    validate_text(text)
    try:
        import_module('uharfbuzz')
        shaping_available = True
    except ModuleNotFoundError as error:
        if error.name != 'uharfbuzz':
            raise
        shaping_available = False
    preferred = ('arial', 'helvetica neue', 'verdana', 'trebuchet ms', 'noto sans', 'liberation sans', 'dejavu sans', 'helvetica', 'pingfang', 'hiragino', 'source han sans')
    required = {ord(c) for c in text if not c.isspace() and unicodedata.category(c) not in {'Cc','Cf'}}
    matches, warnings = [], []
    for root in font_roots() if roots is None else roots:
        root = Path(root)
        if not root.is_dir(): continue
        for path in sorted(root.rglob('*')):
            if path.suffix.lower() not in ('.ttf','.otf','.ttc') or not path.is_file(): continue
            try:
                if path.suffix.lower() == '.ttc':
                    collection = TTCollection(path, lazy=True)
                    count = len(collection.fonts)
                    collection.close()
                else:
                    count = 1
                for index in range(count):
                    with TTFont(path,fontNumber=index,lazy=True) as font:
                        family = font['name'].getDebugName(16) or font['name'].getDebugName(1) or ''
                        if not family or family.startswith('.'): continue
                        priorities = [i for i,name in enumerate(preferred) if name == family.lower()]
                        if any(tag in font for tag in ('COLR','SVG ','CBDT','sbix')): continue
                        if ('OS/2' in font and font['OS/2'].fsSelection & 1) or ('head' in font and font['head'].macStyle & 2): continue
                        actual = font['OS/2'].usWeightClass if 'OS/2' in font else 400
                        axis = next((a for a in font['fvar'].axes if a.axisTag=='wght'),None) if 'fvar' in font else None
                        if actual != weight and not (axis and axis.minValue <= weight <= axis.maxValue): continue
                        if not required <= set(font.getBestCmap() or {}): continue
                        matches.append((min(priorities) if priorities else len(preferred), family, str(path), index,
                                        font['name'].getDebugName(2) or 'Regular'))
            except Exception as error:
                warnings.append({'file': str(path), 'error': str(error)})
    candidates, families = [], set()
    for _, family, path, index, style in sorted(matches):
        if family.casefold() in families:
            continue
        try:
            if shaping_available:
                shape_text(text, path, 32, index, weight)
        except (ValueError, OSError) as error:
            warnings.append({'file': path, 'error': str(error)})
            continue
        families.add(family.casefold())
        candidates.append({'family': family, 'style': style, 'weight': weight,
                           'font': path, 'font_index': index, 'coverage': 'passed',
                           'shaping': 'passed' if shaping_available else 'pending_dependency'})
        if len(candidates) == limit:
            break
    return {'status': 'ready' if candidates else 'needs_decision', 'text': text,
            'candidates': candidates, 'warnings': warnings,
            'missing_dependencies': [] if shaping_available else ['uharfbuzz'],
            'next': 'Show these installed faces and ask the user to choose; no font has been selected.'}


def validate_text(text):
    if not text.strip() or any(c in text for c in '\n\r\t'):
        raise ValueError('Provide a nonempty single-line wordmark without tabs.')
    if any(unicodedata.category(c) in {'Cc', 'Cf'} for c in text):
        raise ValueError('Control/bidi characters require an explicit text layout decision.')
    directions = {unicodedata.bidirectional(c) for c in text}
    if 'L' in directions and directions.intersection({'R', 'AL'}):
        raise ValueError('Mixed-direction text needs a reviewed layout; it is not automatically reordered.')


def shape_text(text, font_path, size, font_index=0, weight=None):
    validate_text(text)
    if size <= 0:
        raise ValueError('Font size must be positive.')
    hb = import_module('uharfbuzz')
    data = Path(font_path).read_bytes()
    variations = {}
    with TTFont(font_path, fontNumber=font_index) as metadata:
        actual_weight = metadata['OS/2'].usWeightClass if 'OS/2' in metadata else 400
        axes = {axis.axisTag: axis for axis in metadata['fvar'].axes} if 'fvar' in metadata else {}
        if weight is not None:
            if 'wght' in axes:
                axis = axes['wght']
                if not axis.minValue <= weight <= axis.maxValue:
                    raise ValueError('Requested weight is outside this variable font axis. Choose an available real weight.')
                variations['wght'] = weight
                actual_weight = weight
            elif actual_weight != weight:
                raise ValueError(f'Font has weight {actual_weight}, requested {weight}. Select the real requested face; no synthetic bold or silent font replacement.')
        font_info = {'family': metadata['name'].getDebugName(1), 'style': metadata['name'].getDebugName(2),
                     'weight': actual_weight, 'variations': variations}
    face = hb.Face(data, font_index)
    font = hb.Font(face)
    hb.ot_font_set_funcs(font)
    if variations:
        font.set_variations(variations)
    font.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.cluster_level = hb.BufferClusterLevel.MONOTONE_GRAPHEMES
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    if any(info.codepoint == 0 for info in buffer.glyph_infos):
        raise ValueError('The selected font is missing a glyph; choose a font explicitly.')
    # Connected scripts must not be pulled apart while they enter.
    independent = buffer.script in {'Latn', 'Cyrl', 'Grek', 'Hani', 'Hira', 'Kana', 'Hang', 'Zyyy'}
    scale = size / face.upem
    grouped, all_bounds = {}, []
    cursor_x = cursor_y = 0
    with TTFont(font_path, fontNumber=font_index) as tt:
        if any(tag in tt for tag in ('COLR', 'SVG ', 'CBDT', 'sbix')):
            raise ValueError('Color/bitmap glyphs require a user-approved representation; native outlines only.')
        glyphs = tt.getGlyphSet(location=variations or None)
        order = tt.getGlyphOrder()
        for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
            glyph = glyphs[order[info.codepoint]]
            matrix = (scale, 0, 0, -scale,
                      (cursor_x + pos.x_offset) * scale, -(cursor_y + pos.y_offset) * scale)
            svg_pen = SVGPathPen(glyphs)
            glyph.draw(TransformPen(svg_pen, matrix))
            bounds_pen = BoundsPen(glyphs)
            glyph.draw(TransformPen(bounds_pen, matrix))
            if bounds_pen.bounds:
                bounds = list(bounds_pen.bounds)
                key = info.cluster if independent else 0
                unit = grouped.setdefault(key, {'shapes': [], 'bounds': []})
                unit['shapes'].extend(path_to_shapes(svg_pen.getCommands()))
                unit['bounds'].append(bounds)
                all_bounds.append(bounds)
            cursor_x += pos.x_advance
            cursor_y += pos.y_advance
    if not all_bounds:
        raise ValueError('The wordmark has no visible glyph outlines.')
    units = [{'shapes': u['shapes'], 'bounds': union(u['bounds'])} for u in grouped.values()]
    bounds = union(all_bounds)
    return {'units': units, 'bounds': bounds, 'width': bounds[2] - bounds[0],
            'advance': cursor_x * scale, 'script': buffer.script, 'direction': buffer.direction, 'font': font_info}
