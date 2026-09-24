"""Native Lottie primitives shared by material-specific and legacy compositions."""


def static(value):
    return {'a': 0, 'k': value}


def keys(points, fps, easing=(.25, 0, .75, 1)):
    result = []
    for i, (seconds, value) in enumerate(points):
        item = {'t': round(seconds * fps, 6), 's': value}
        if i + 1 < len(points):
            item.update(e=points[i + 1][1], h=0, o={'x': [easing[0]], 'y': [easing[1]]},
                        i={'x': [easing[2]], 'y': [easing[3]]})
        result.append(item)
    return {'a': 1, 'k': result}


def layer(name, shapes, frames, anchor=(0, 0), position=(0, 0), scale=100):
    return {'ty': 4, 'nm': name, 'ddd': 0, 'sr': 1, 'ip': 0, 'op': frames, 'st': 0,
            'ks': {'a': static([*anchor, 0]), 'p': static([*position, 0]),
                   's': static([scale, scale, 100]), 'r': static(0), 'o': static(100)},
            'shapes': shapes}
