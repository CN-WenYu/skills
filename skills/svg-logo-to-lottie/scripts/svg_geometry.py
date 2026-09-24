"""Strict SVG subset conversion. Output uses viewBox coordinates shifted to 0,0.

Unsupported visual semantics raise SVGError instead of silently losing artwork.
Bounds conservatively contain all cubic control points and supported strokes.
"""
from copy import deepcopy
from pathlib import Path
import math
import xml.etree.ElementTree as ET

from svg_gradients import color, declarations, gradient, gradient_definitions, opacity
from svg_paths import (SVGError, exact_bounds, geometry, multiply, number,
                       numbers, path_bounds, path_to_shapes, similarity_scale, transform)

SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)
STYLE_DEFAULTS = {'fill': 'black', 'fill-opacity': '1', 'fill-rule': 'nonzero',
                  'stroke': 'none', 'stroke-width': '1', 'stroke-opacity': '1',
                  'stroke-linecap': 'butt', 'stroke-linejoin': 'miter',
                  'stroke-miterlimit': '4', 'color': 'black', 'visibility': 'visible'}
PROPERTIES = set(STYLE_DEFAULTS) | {'opacity', 'display'}
GEOMETRY = {'path': {'d'}, 'rect': {'x', 'y', 'width', 'height', 'rx', 'ry'},
            'circle': {'cx', 'cy', 'r'}, 'ellipse': {'cx', 'cy', 'rx', 'ry'},
            'line': {'x1', 'y1', 'x2', 'y2'}, 'polyline': {'points'}, 'polygon': {'points'}}
NONVISUAL = {'id', 'role'}
METADATA = {'title', 'desc', 'metadata'}


def tag_name(element):
    if element.tag.startswith('{') and not element.tag.startswith('{'+SVG_NS+'}'):
        raise SVGError(f'Unsupported element namespace {element.tag}; remove foreign visual content.')
    return element.tag.rsplit('}', 1)[-1]


def attributes(element, tag):
    allowed = PROPERTIES | NONVISUAL | {'style', 'transform'} | GEOMETRY.get(tag, set())
    if tag == 'svg':
        allowed |= {'width', 'height', 'viewBox', 'version', 'preserveAspectRatio', 'xmlns'}
    for name in element.attrib:
        if name not in allowed and not name.startswith(('aria-', 'data-')):
            raise SVGError(f'Unsupported attribute {name!r} on <{tag}>; simplify or outline this visual feature.')
    style = {key: value for key, value in element.attrib.items() if key in PROPERTIES}
    inline = declarations(element.get('style', ''))
    unknown = set(inline)-PROPERTIES
    if unknown:
        raise SVGError(f'Unsupported inline style properties {sorted(unknown)}; flatten them into supported geometry.')
    style.update(inline)
    return style


def group_transform(alpha=1):
    return {'ty': 'tr', 'p': {'a': 0, 'k': [0, 0]}, 'a': {'a': 0, 'k': [0, 0]},
            's': {'a': 0, 'k': [100, 100]}, 'r': {'a': 0, 'k': 0},
            'o': {'a': 0, 'k': alpha*100}, 'sk': {'a': 0, 'k': 0}, 'sa': {'a': 0, 'k': 0}}


def paint(value, kind, style, definitions, bounds, matrix, viewport):
    if value == 'none':
        return None
    if value == 'currentColor':
        value = style['color']
    alpha = opacity(style[kind+'-opacity'])
    if value.startswith('url('):
        item = {'ty': 'gf' if kind == 'fill' else 'gs',
                **gradient(value, definitions, bounds, matrix, viewport)}
    else:
        rgba = color(value)
        alpha *= rgba[3]
        item = {'ty': 'fl' if kind == 'fill' else 'st', 'c': {'a': 0, 'k': rgba[:3]+[1]}}
    item['o'] = {'a': 0, 'k': alpha*100}
    if kind == 'fill':
        if style['fill-rule'] not in ('nonzero', 'evenodd'):
            raise SVGError('fill-rule must be nonzero or evenodd.')
        item['r'] = 2 if style['fill-rule'] == 'evenodd' else 1
    else:
        scale = similarity_scale(matrix)
        if scale is None:
            raise SVGError('Nonuniform or skewed stroke transforms cannot be baked faithfully; outline the stroke first.')
        caps = {'butt': 1, 'round': 2, 'square': 3}
        joins = {'miter': 1, 'round': 2, 'bevel': 3}
        if style['stroke-linecap'] not in caps or style['stroke-linejoin'] not in joins:
            raise SVGError('Unsupported stroke cap/join; use butt/round/square and miter/round/bevel.')
        width = number(style['stroke-width'])
        limit = number(style['stroke-miterlimit'])
        if width < 0 or limit < 1:
            raise SVGError('stroke-width must be nonnegative and stroke-miterlimit at least 1.')
        item.update({'w': {'a': 0, 'k': width*scale}, 'lc': caps[style['stroke-linecap']],
                     'lj': joins[style['stroke-linejoin']], 'ml': limit})
    if alpha == 0 or (kind == 'stroke' and item['w']['k'] == 0):
        return None
    if 'g' in item:
        stop_count = item['g']['p']
        stop_alphas = item['g']['k']['k'][4*stop_count+1::2]
        if not any(stop_alphas):
            return None
    return item


def load_svg(path: Path) -> dict:
    """Return width, height, reversed painter-order groups, SVG and visible bounds."""
    source = Path(path).read_text(encoding='utf-8')
    if '<!DOCTYPE' in source.upper() or '<!ENTITY' in source.upper():
        raise SVGError('SVG document types and entities are unsupported; use a self-contained SVG.')
    try:
        root = ET.fromstring(source)
    except ET.ParseError as exc:
        raise SVGError(f'Invalid SVG XML: {exc}') from exc
    if tag_name(root) != 'svg':
        raise SVGError('The document root must be <svg>.')
    if root.get('viewBox'):
        viewport = numbers(root.get('viewBox'))
        if len(viewport) != 4:
            raise SVGError('viewBox must contain x, y, width, height.')
    else:
        viewport = [0, 0, number(root.get('width')), number(root.get('height'))]
    x, y, width, height = viewport
    if width <= 0 or height <= 0:
        raise SVGError('SVG needs a positive viewBox or explicit width and height.')
    declared_width = number(root.get('width'), None)
    declared_height = number(root.get('height'), None)
    if any(value is not None and value <= 0 for value in (declared_width, declared_height)):
        raise SVGError('Root SVG viewport dimensions must be positive.')
    if declared_width is not None and declared_height is not None:
        if not math.isclose(declared_width/declared_height, width/height, rel_tol=1e-9):
            raise SVGError('Root viewport aspect ratio differs from viewBox; bake the viewport fitting/stretch into the artwork before converting.')
    definitions = gradient_definitions(root)
    shapes, visible_bounds, elements = [], [], []

    def visit(element, inherited, matrix, parent_alpha=1, hidden=False, ancestors=()):
        tag = tag_name(element)
        if tag in METADATA:
            return 0
        if tag == 'defs':
            if set(element.attrib)-{'id'}:
                raise SVGError('Unsupported attributes on <defs>.')
            for child in element:
                if tag_name(child) not in {'linearGradient', 'radialGradient'} | METADATA:
                    raise SVGError('Only gradient definitions are supported in <defs>; expand symbols and references.')
            return 0
        if tag in ('linearGradient', 'radialGradient'):
            return 0
        if tag not in GEOMETRY and tag not in ('svg', 'g'):
            raise SVGError(f'Unsupported SVG element <{tag}>; outline or expand it to plain paths.')
        own = attributes(element, tag)
        style = dict(inherited)
        for key, value in own.items():
            if key in STYLE_DEFAULTS and value != 'inherit':
                style[key] = value
        own_alpha = opacity(own.get('opacity', '1'))
        alpha = parent_alpha*own_alpha
        display = own.get('display', 'inline')
        if display not in ('inline', 'none'):
            raise SVGError('Only display:inline and display:none are supported.')
        hidden = hidden or display == 'none'
        if style['visibility'] not in ('visible', 'hidden', 'collapse'):
            raise SVGError('Unsupported visibility value.')
        matrix = multiply(matrix, transform(element.get('transform')))
        ids = ancestors + ((element.get('id'),) if element.get('id') else ())
        if tag in ('svg', 'g'):
            if tag == 'svg' and element is not root:
                raise SVGError('Nested SVG viewports are unsupported; flatten into a group first.')
            count = sum(visit(child, style, matrix, alpha, hidden, ids) for child in element)
            if own_alpha not in (0, 1) and count > 1:
                raise SVGError('Group opacity on multiple shapes requires isolated compositing; flatten/union the artwork or remove group opacity.')
            return count
        if len(element):
            for child in element:
                if tag_name(child) not in METADATA:
                    raise SVGError(f'Unsupported child in <{tag}>; remove animation and nested content.')
        d = geometry(tag, element.attrib)
        paths = path_to_shapes(d, matrix)
        if not paths:
            return 0
        bounds = exact_bounds(d)
        fill = paint(style['fill'], 'fill', style, definitions, bounds, matrix, viewport) if tag != 'line' else None
        stroke = paint(style['stroke'], 'stroke', style, definitions, bounds, matrix, viewport)
        if not fill and not stroke:
            return 0
        if alpha not in (0, 1) and fill and stroke and stroke['w']['k'] > 0:
            raise SVGError('Element opacity with both fill and stroke needs isolated compositing; separate or outline the stroke.')
        if hidden or style['visibility'] != 'visible' or alpha == 0:
            return 0
        box = path_bounds(paths)
        if stroke:
            margin = stroke['w']['k']/2
            if stroke['lj'] == 1:
                margin *= stroke['ml']
            if stroke['lc'] == 3:
                margin *= 2**.5
            box = [box[0]-margin, box[1]-margin, box[2]+margin, box[3]+margin]
        visible_bounds.append(box)
        # Lottie traverses paint operators backwards; SVG paints stroke over fill.
        items = paths + [item for item in (stroke, fill) if item]
        items.append(group_transform(alpha))
        shapes.append({'ty': 'gr', 'nm': element.get('id', tag), 'it': items})
        elements.append({'shape': shapes[-1], 'ids': ids, 'bounds': box})
        return 1

    visit(root, STYLE_DEFAULTS, (1, 0, 0, 1, -x, -y))
    if not shapes:
        raise SVGError('SVG contains no visible supported shapes.')
    bounds = [min(b[0] for b in visible_bounds), min(b[1] for b in visible_bounds),
              max(b[2] for b in visible_bounds), max(b[3] for b in visible_bounds)]
    normalized = deepcopy(root)
    for parent in list(normalized.iter()):
        for child in list(parent):
            if child.tag.rsplit('}', 1)[-1] in METADATA:
                parent.remove(child)
    normalized.set('width', f'{width:g}')
    normalized.set('height', f'{height:g}')
    normalized.set('viewBox', f'0 0 {width:g} {height:g}')
    root_transform = normalized.attrib.pop('transform', '')
    if x or y or root_transform:
        wrapper = ET.Element('{'+SVG_NS+'}g', {'transform': f'translate({-x:g} {-y:g}) {root_transform}'.strip()})
        for child in list(normalized):
            normalized.remove(child)
            wrapper.append(child)
        normalized.append(wrapper)
    return {'width': width, 'height': height, 'shapes': list(reversed(shapes)),
            'elements': list(reversed(elements)),
            'normalized_svg': ET.tostring(normalized, encoding='unicode'), 'bounds': bounds}
