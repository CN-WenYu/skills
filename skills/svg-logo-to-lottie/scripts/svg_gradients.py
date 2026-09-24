"""SVG paint parsing for native Lottie fills and strokes."""
import math
import re

from PIL import ImageColor

from svg_paths import SVGError, IDENTITY, multiply, number, point, similarity_scale, transform


def opacity(value):
    text = str(value).strip()
    parsed = number(text[:-1])/100 if text.endswith('%') else number(text)
    return max(0, min(1, parsed))


def color(value):
    try:
        rgb = ImageColor.getcolor(value.strip(), 'RGBA')
    except (ValueError, TypeError) as exc:
        raise SVGError(f'Unsupported color {value!r}; use a CSS named, hex, rgb or rgba color.') from exc
    return [channel/255 for channel in rgb]


def declarations(value):
    result = {}
    for item in value.split(';'):
        if not item.strip():
            continue
        if ':' not in item:
            raise SVGError(f'Invalid inline style declaration {item!r}.')
        name, value = (x.strip() for x in item.split(':', 1))
        if '!important' in value:
            raise SVGError('Inline !important is unsupported; simplify the style first.')
        result[name] = value
    return result


def gradient_definitions(root):
    gradients = {}
    attributes = {'id', 'x1', 'x2', 'y1', 'y2', 'cx', 'cy', 'r', 'fx', 'fy', 'fr',
                  'gradientUnits', 'gradientTransform', 'spreadMethod'}
    for element in root.iter():
        tag = element.tag.rsplit('}', 1)[-1]
        if tag not in ('linearGradient', 'radialGradient'):
            continue
        unknown = set(element.attrib)-attributes
        if unknown:
            raise SVGError(f'Unsupported gradient attributes {sorted(unknown)}; flatten gradient references/styles.')
        if element.get('spreadMethod', 'pad') != 'pad':
            raise SVGError('Gradient spreadMethod must be pad; repeating gradients are unsupported.')
        if element.get('gradientUnits', 'objectBoundingBox') not in ('objectBoundingBox', 'userSpaceOnUse'):
            raise SVGError('Invalid gradientUnits.')
        identifier = element.get('id')
        if not identifier or identifier in gradients:
            raise SVGError('Each gradient needs a unique nonempty id.')
        stops = []
        for stop in element:
            if stop.tag.rsplit('}', 1)[-1] != 'stop':
                raise SVGError('Gradients may contain only color stops.')
            if len(stop):
                raise SVGError('Gradient stop children are unsupported; remove animations and use static color stops.')
            attrs = dict(stop.attrib)
            attrs.update(declarations(attrs.pop('style', '')))
            unknown = set(attrs)-{'offset', 'stop-color', 'stop-opacity', 'id'}
            if unknown:
                raise SVGError(f'Unsupported gradient stop attributes {sorted(unknown)}.')
            offset = max(stops[-1][0] if stops else 0, opacity(attrs.get('offset', '0')))
            rgba = color(attrs.get('stop-color', 'black'))
            stops.append((offset, rgba[:3], rgba[3]*opacity(attrs.get('stop-opacity', '1'))))
        if not stops:
            raise SVGError('A gradient requires color stops; replace an empty gradient with fill="none".')
        if len(stops) == 1:
            stops = [(0, stops[0][1], stops[0][2]), (1, stops[0][1], stops[0][2])]
        gradients[identifier] = (tag, element.attrib, stops)
    return gradients


def gradient(value, definitions, bounds, matrix, viewport):
    match = re.fullmatch(r'url\(\s*#([^\s)]+)\s*\)', value)
    if not match or match[1] not in definitions:
        raise SVGError(f'Unknown or external paint reference {value!r}; use a local gradient id.')
    tag, attrs, stops = definitions[match[1]]
    units = attrs.get('gradientUnits', 'objectBoundingBox')
    is_bbox = units == 'objectBoundingBox'
    x0, y0, x1, y1 = bounds
    bbox = (x1-x0, 0, 0, y1-y0, x0, y0) if is_bbox else IDENTITY
    combined = multiply(matrix, multiply(bbox, transform(attrs.get('gradientTransform'))))

    def coord(name, default, axis):
        value = attrs.get(name, default)
        if value.endswith('%'):
            amount = number(value[:-1])/100
            if is_bbox:
                return amount
            if axis == 2:
                return amount*math.hypot(viewport[2], viewport[3])/math.sqrt(2)
            return amount*viewport[axis+2]
        return number(value)

    if tag == 'linearGradient':
        start = [coord('x1', '0%', 0), coord('y1', '0%', 1)]
        end = [coord('x2', '100%', 0), coord('y2', '0%', 1)]
        dx, dy = end[0]-start[0], end[1]-start[1]
        a, b, c, d, _, _ = combined
        det = a*d-b*c
        if abs(det) < 1e-12 or dx*dx+dy*dy < 1e-20:
            raise SVGError('Degenerate gradient geometry; replace it with a solid fill.')
        nx, ny = (d*dx-b*dy)/det, (-c*dx+a*dy)/det
        scale = (dx*dx+dy*dy)/(nx*nx+ny*ny)
        start = point(combined, start)
        end = [start[0]+nx*scale, start[1]+ny*scale]
        kind = 1
    else:
        cx, cy, radius = coord('cx', '50%', 0), coord('cy', '50%', 1), coord('r', '50%', 2)
        fx = coord('fx', attrs.get('cx', '50%'), 0)
        fy = coord('fy', attrs.get('cy', '50%'), 1)
        if fx != cx or fy != cy or number(attrs.get('fr'), 0) != 0:
            raise SVGError('Off-center radial gradient focal points are unsupported; center fx/fy and use fr=0.')
        if similarity_scale(combined) is None:
            raise SVGError('Elliptical radial gradients or nonuniform gradientTransform are unsupported; use a circular gradient.')
        if radius <= 0:
            raise SVGError('Radial gradient radius must be positive.')
        start, end = point(combined, (cx, cy)), point(combined, (cx+radius, cy))
        kind = 2
    data = []
    for offset, rgb, alpha in stops:
        data.extend([offset, *rgb])
    for offset, rgb, alpha in stops:
        data.extend([offset, alpha])
    return {'t': kind, 's': {'a': 0, 'k': start}, 'e': {'a': 0, 'k': end},
            'g': {'p': len(stops), 'k': {'a': 0, 'k': data}},
            'h': {'a': 0, 'k': 0}, 'a': {'a': 0, 'k': 0}}
