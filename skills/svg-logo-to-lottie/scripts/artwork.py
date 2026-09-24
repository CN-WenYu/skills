"""Prepare explicitly identified icon backplates; never infer semantic roles from paths."""
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from configuration import DecisionRequired
from svg_geometry import load_svg
from svg_paths import number, numbers, union


def tag(element):
    return element.tag.rsplit('}', 1)[-1]


def painted_rect(paint, width, height, radius=0):
    root = ET.Element('svg', xmlns='http://www.w3.org/2000/svg', width=str(width), height=str(height))
    if paint['type'] == 'solid':
        fill = paint['color']
    else:
        defs = ET.SubElement(root, 'defs')
        attrs = {'id': 'backplate-paint', 'gradientUnits': 'userSpaceOnUse'}
        if paint['type'] == 'linear':
            start, end = paint['start'], paint['end']
            attrs.update(x1=str(start[0]), y1=str(start[1]), x2=str(end[0]), y2=str(end[1]))
            gradient = ET.SubElement(defs, 'linearGradient', attrs)
        elif paint['type'] == 'radial':
            center = paint['center']
            attrs.update(cx=str(center[0]), cy=str(center[1]), r=str(paint['radius']))
            gradient = ET.SubElement(defs, 'radialGradient', attrs)
        else:
            raise DecisionRequired('A visible rectangle needs solid, linear or radial paint.')
        for stop in paint['stops']:
            ET.SubElement(gradient, 'stop', {'offset': str(stop['offset']), 'stop-color': stop['color'],
                                           'stop-opacity': str(stop.get('opacity', 1))})
        fill = 'url(#backplate-paint)'
    ET.SubElement(root, 'rect', width=str(width), height=str(height), rx=str(radius), ry=str(radius), fill=fill)
    return root


def parse_tree(root):
    with tempfile.TemporaryDirectory(prefix='logo-artwork-') as directory:
        path = Path(directory) / 'artwork.svg'
        path.write_text(ET.tostring(root, encoding='unicode'))
        return load_svg(path)


def rect_boundary(root, element):
    """Only simple axis-aligned rectangles have a supported containment contract."""
    parents = {child: parent for parent in root.iter() for child in parent}
    current = element
    while current is not None:
        if current.get('transform'):
            return None
        current = parents.get(current)
    if tag(element) != 'rect':
        return None
    vb = numbers(root.get('viewBox')) if root.get('viewBox') else [0, 0]
    x, y = number(element.get('x'), 0) - vb[0], number(element.get('y'), 0) - vb[1]
    w, h = number(element.get('width')), number(element.get('height'))
    rx = number(element.get('rx'), number(element.get('ry'), 0))
    ry = number(element.get('ry'), rx)
    return {'bounds': [x, y, x+w, y+h], 'rx': min(rx, w/2), 'ry': min(ry, h/2)}


def prepare_artwork(asset, config):
    plate = config['artwork']['backplate']
    mode = plate['mode']
    if mode == 'none':
        asset['foreground'] = asset['shapes']
        asset['foreground_bounds'] = asset['bounds']
        return asset
    image_report = asset.get('image_report')
    if mode == 'generated':
        radius = plate['corners'].get('radius', 0)
        if radius > min(asset['width'], asset['height']) / 2:
            raise DecisionRequired('Corner radius exceeds half the icon size; confirm a smaller radius.')
        background = parse_tree(painted_rect(plate['paint'], asset['width'], asset['height'], radius))
        foreground = asset['shapes']
        foreground_bounds = asset['bounds']
        # Reuse the parser to resolve independent definitions before joining shapes.
        source_root = ET.fromstring(asset['normalized_svg'])
        namespace = '{http://www.w3.org/2000/svg}'
        root = ET.Element(namespace+'svg', width=str(asset['width']), height=str(asset['height']),
                          viewBox=f"0 0 {asset['width']} {asset['height']}")
        container = ET.SubElement(root, namespace+'g', {key: value for key, value in source_root.attrib.items()
                                  if key not in {'width', 'height', 'viewBox', 'version', 'preserveAspectRatio', 'xmlns'}})
        container.extend(list(source_root))
        backdrop = painted_rect(plate['paint'], asset['width'], asset['height'], radius)
        existing = {el.get('id') for el in root.iter() if el.get('id')}
        paint_id = 'generated-icon-paint'
        while paint_id in existing:
            paint_id += '-new'
        for el in backdrop.iter():
            el.tag = '{http://www.w3.org/2000/svg}' + tag(el)
            if el.get('id') == 'backplate-paint': el.set('id', paint_id)
            if el.get('fill') == 'url(#backplate-paint)': el.set('fill', f'url(#{paint_id})')
        for index, child in enumerate(list(backdrop)):
            root.insert(index, child)
        asset = {**asset, 'shapes': foreground + background['shapes'],
                 'bounds': union([foreground_bounds, background['bounds']]),
                 'normalized_svg': ET.tostring(root, encoding='unicode')}
        boundary = {'bounds': [0, 0, asset['width'], asset['height']], 'rx': radius, 'ry': radius, 'probe_corners': True}
        back_shapes = background['shapes']
        back_bounds = background['bounds']
    else:
        root = ET.fromstring(asset['normalized_svg'])
        selected = []
        for identity in plate['element_ids']:
            matches = [el for el in root.iter() if el.get('id') == identity]
            if len(matches) != 1:
                raise DecisionRequired(f'Backplate ID {identity!r} must match exactly one SVG element/group; no path-index guessing.')
            selected.append(matches[0])
        boundary = rect_boundary(root, selected[0]) if len(selected) == 1 else None
        if plate['corners']['mode'] != 'preserve':
            if boundary is None:
                raise DecisionRequired('Corner changes require one untransformed rect backplate. Supply reviewed geometry for other shapes; no automatic clipping.')
            radius = plate['corners'].get('radius', 0)
            b = boundary['bounds']
            if radius > min(b[2]-b[0], b[3]-b[1])/2:
                raise DecisionRequired('Corner radius exceeds half the backplate size.')
            selected[0].set('rx', str(radius)); selected[0].set('ry', str(radius))
            boundary.update(rx=radius, ry=radius)
        asset = parse_tree(root)
        entries = asset['elements']
        mapped = [bool(set(e['ids']) & set(plate['element_ids'])) for e in entries]
        for identity in plate['element_ids']:
            if not any(identity in e['ids'] for e in entries):
                raise DecisionRequired(f'Backplate ID {identity!r} has no visible shapes.')
        if not any(mapped) or all(mapped):
            raise DecisionRequired('Backplate mapping must leave visible foreground geometry.')
        first = mapped.index(True)
        if not all(mapped[first:]):
            raise DecisionRequired('Mapped backplate overlaps foreground painter order; splitting would reorder artwork. Provide reviewed groups.')
        back_shapes = [e['shape'] for e, yes in zip(entries, mapped) if yes]
        foreground = [e['shape'] for e, yes in zip(entries, mapped) if not yes]
        foreground_bounds = union([e['bounds'] for e, yes in zip(entries, mapped) if not yes])
        back_bounds = union([e['bounds'] for e, yes in zip(entries, mapped) if yes])
        if boundary:
            # A stroke may legitimately cover points outside the fill's corner arc.
            boundary['probe_corners'] = not any(item['ty'] in ('st', 'gs') for shape in back_shapes for item in shape['it'])
    asset.update(foreground=foreground, foreground_bounds=foreground_bounds,
                 backplate=back_shapes, backplate_bounds=back_bounds, backplate_boundary=boundary)
    if image_report is not None:
        asset['image_report'] = image_report
    return asset


def check_backplate_bounds(asset, bounds, label='Foreground'):
    if 'backplate' not in asset:
        return
    boundary = asset.get('backplate_boundary')
    box = boundary['bounds'] if boundary else asset['backplate_bounds']
    for x in (bounds[0], bounds[2]):
        for y in (bounds[1], bounds[3]):
            inside = box[0]-1e-6 <= x <= box[2]+1e-6 and box[1]-1e-6 <= y <= box[3]+1e-6
            if inside and boundary and boundary['rx'] > 0 and boundary['ry'] > 0:
                rx, ry = boundary['rx'], boundary['ry']
                dx = max(box[0]+rx-x, 0, x-(box[2]-rx))/rx
                dy = max(box[1]+ry-y, 0, y-(box[3]-ry))/ry
                inside = dx*dx+dy*dy <= 1+1e-6
            if not inside:
                raise DecisionRequired(f'{label} motion bounds extend outside the icon backplate/corners. Revise motion, or ask before altering/clipping source artwork.')


def check_backplate_containment(asset, foreground_scale):
    if 'backplate' not in asset:
        return
    b = asset['foreground_bounds']
    center = [(asset['bounds'][0]+asset['bounds'][2])/2, (asset['bounds'][1]+asset['bounds'][3])/2]
    # Legacy presets scale the foreground around the complete icon anchor.
    for scale in (min(1, foreground_scale[0]), max(1, foreground_scale[1])):
        bounds = [center[i%2]+(b[i]-center[i%2])*scale for i in range(4)]
        check_backplate_bounds(asset, bounds)
