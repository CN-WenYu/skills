"""Small SVG geometry primitives; coordinates are baked into cubic Lottie paths."""
import math
import re

from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path


class SVGError(ValueError):
    """The artwork cannot be represented by the supported native vector subset."""


IDENTITY = (1, 0, 0, 1, 0, 0)
NUMBER = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'


def number(value, default=0):
    if value is None:
        return default
    if not re.fullmatch(NUMBER + r'(?:px)?', str(value).strip()):
        raise SVGError(f'Unsupported length {value!r}; use finite unitless or px values.')
    result = float(str(value).strip().removesuffix('px'))
    if not math.isfinite(result):
        raise SVGError('SVG coordinates must be finite.')
    return result


def numbers(value):
    if re.sub(NUMBER + r'|[\s,]', '', value):
        raise SVGError(f'Invalid numeric list: {value!r}')
    return [number(x) for x in re.findall(NUMBER, value)]


def multiply(a, b):
    return (a[0]*b[0]+a[2]*b[1], a[1]*b[0]+a[3]*b[1],
            a[0]*b[2]+a[2]*b[3], a[1]*b[2]+a[3]*b[3],
            a[0]*b[4]+a[2]*b[5]+a[4], a[1]*b[4]+a[3]*b[5]+a[5])


def point(matrix, xy):
    a, b, c, d, e, f = matrix
    x, y = xy
    return [a*x+c*y+e, b*x+d*y+f]


def transform(value):
    matrix = IDENTITY
    tail = value or ''
    while tail.strip(' ,\t\n\r'):
        match = re.match(r'\s*,?\s*([A-Za-z]+)\s*\(([^()]*)\)', tail)
        if not match:
            raise SVGError(f'Invalid transform: {tail!r}')
        name, args = match[1], numbers(match[2])
        if name == 'matrix' and len(args) == 6:
            item = args
        elif name == 'translate' and len(args) in (1, 2):
            item = (1, 0, 0, 1, args[0], args[1] if len(args) == 2 else 0)
        elif name == 'scale' and len(args) in (1, 2):
            item = (args[0], 0, 0, args[-1], 0, 0)
        elif name == 'rotate' and len(args) in (1, 3):
            angle = math.radians(args[0])
            item = (math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle), 0, 0)
            if len(args) == 3:
                x, y = args[1:]
                item = multiply(multiply((1, 0, 0, 1, x, y), item), (1, 0, 0, 1, -x, -y))
        elif name in ('skewX', 'skewY') and len(args) == 1:
            tangent = math.tan(math.radians(args[0]))
            item = (1, 0, tangent, 1, 0, 0) if name == 'skewX' else (1, tangent, 0, 1, 0, 0)
        else:
            raise SVGError(f'Unsupported transform {name} with {len(args)} arguments.')
        matrix = multiply(matrix, item)
        tail = tail[match.end():]
    if not all(math.isfinite(x) for x in matrix):
        raise SVGError('Non-finite transform matrix.')
    return matrix


def similarity_scale(matrix):
    a, b, c, d, _, _ = matrix
    x, y = math.hypot(a, b), math.hypot(c, d)
    if not math.isclose(x, y, rel_tol=1e-8, abs_tol=1e-10) or not math.isclose(a*c+b*d, 0, abs_tol=1e-8*max(x*y, 1)):
        return None
    return x


class PathPen(BasePen):
    def __init__(self, matrix=IDENTITY):
        super().__init__(None)
        self.matrix = matrix
        self.paths = []
        self.current = None

    def _moveTo(self, p):
        if self.current:
            self._endPath()
        self.current = {'v': [point(self.matrix, p)], 'i': [[0, 0]], 'o': [[0, 0]], 'c': False}

    def _lineTo(self, p):
        self.current['v'].append(point(self.matrix, p))
        self.current['i'].append([0, 0])
        self.current['o'].append([0, 0])

    def _curveToOne(self, p1, p2, p3):
        p1, p2, p3 = [point(self.matrix, p) for p in (p1, p2, p3)]
        previous = self.current['v'][-1]
        self.current['o'][-1] = [p1[i]-previous[i] for i in (0, 1)]
        self.current['v'].append(p3)
        self.current['i'].append([p2[i]-p3[i] for i in (0, 1)])
        self.current['o'].append([0, 0])

    def _closePath(self):
        if len(self.current['v']) > 1 and self.current['v'][-1] == self.current['v'][0]:
            self.current['i'][0] = self.current['i'].pop()
            self.current['v'].pop()
            self.current['o'].pop()
        self.current['c'] = True
        self._endPath()

    def _endPath(self):
        if self.current:
            self.paths.append({'ty': 'sh', 'ks': {'a': 0, 'k': self.current}, 'nm': 'SVG path'})
            self.current = None


def path_to_shapes(d, transform=IDENTITY):
    """Convert an SVG path string to cubic ``sh`` items, baking an affine matrix."""
    if re.sub(NUMBER + r'|[MmZzLlHhVvCcSsQqTtAa\s,]', '', d):
        raise SVGError('Invalid SVG path data or unsupported path command.')
    for token in re.findall(NUMBER, d):
        number(token)
    pen = PathPen(transform)
    try:
        parse_path(d, pen)
        pen._endPath()
    except (ValueError, TypeError, IndexError, AssertionError, AttributeError) as exc:
        raise SVGError(f'Invalid SVG path data: {exc}') from exc
    for shape in pen.paths:
        if not all(math.isfinite(value) for name in ('v', 'i', 'o')
                   for pair in shape['ks']['k'][name] for value in pair):
            raise SVGError('Path coordinates overflowed; reduce coordinate or transform magnitude.')
    return pen.paths


def geometry(tag, attrs):
    get = lambda name, default=0: number(attrs.get(name), default)
    if tag == 'path':
        return attrs.get('d', '')
    if tag in ('polyline', 'polygon'):
        pts = numbers(attrs.get('points', ''))
        if len(pts) % 2:
            raise SVGError('points must contain pairs of x,y coordinates.')
        return ('M' + ' '.join(map(str, pts)) + ('Z' if tag == 'polygon' else '')) if pts else ''
    if tag == 'line':
        return f'M{get("x1")} {get("y1")}L{get("x2")} {get("y2")}'
    if tag in ('circle', 'ellipse'):
        x, y = get('cx'), get('cy')
        rx, ry = (get('r'), get('r')) if tag == 'circle' else (get('rx'), get('ry'))
        if min(rx, ry) < 0:
            raise SVGError('Ellipse and circle radii cannot be negative.')
        if not rx or not ry:
            return ''
        return f'M{x-rx} {y}A{rx} {ry} 0 1 0 {x+rx} {y}A{rx} {ry} 0 1 0 {x-rx} {y}Z'
    if tag == 'rect':
        x, y, w, h = get('x'), get('y'), get('width'), get('height')
        rx = get('rx', get('ry'))
        ry = get('ry', rx)
        if min(w, h, rx, ry) < 0:
            raise SVGError('Rectangle dimensions and corner radii cannot be negative.')
        if not w or not h:
            return ''
        rx, ry = min(rx, w/2), min(ry, h/2)
        if not rx or not ry:
            return f'M{x} {y}h{w}v{h}h{-w}Z'
        return (f'M{x+rx} {y}H{x+w-rx}A{rx} {ry} 0 0 1 {x+w} {y+ry}'
                f'V{y+h-ry}A{rx} {ry} 0 0 1 {x+w-rx} {y+h}'
                f'H{x+rx}A{rx} {ry} 0 0 1 {x} {y+h-ry}'
                f'V{y+ry}A{rx} {ry} 0 0 1 {x+rx} {y}Z')
    raise SVGError(f'Unsupported SVG element <{tag}>; outline it into plain paths first.')


def path_bounds(shapes):
    points = []
    for shape in shapes:
        path = shape['ks']['k']
        for vertex, incoming, outgoing in zip(path['v'], path['i'], path['o']):
            points.extend((vertex, [vertex[i]+incoming[i] for i in (0, 1)], [vertex[i]+outgoing[i] for i in (0, 1)]))
    if not points:
        return None
    return [min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)]


def exact_bounds(d):
    pen = BoundsPen(None)
    parse_path(d, pen)
    return pen.bounds

def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]
