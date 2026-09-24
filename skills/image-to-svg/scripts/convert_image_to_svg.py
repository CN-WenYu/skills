#!/usr/bin/env python3
"""Choose safe raster preprocessing, run VTracer, and validate an SVG path output."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, deque
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


RGB = tuple[int, int, int]


def distance(left: RGB, right: RGB) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def quantize(color: RGB, step: int = 16) -> RGB:
    return tuple(min(255, (channel // step) * step) for channel in color)  # type: ignore[return-value]


def border_pixels(image: Image.Image) -> list[RGB]:
    width, height = image.size
    pixels = image.load()
    result: list[RGB] = []
    for x in range(width):
        result.extend((pixels[x, 0][:3], pixels[x, height - 1][:3]))
    for y in range(1, height - 1):
        result.extend((pixels[0, y][:3], pixels[width - 1, y][:3]))
    return result


def continuous_color_ramp(image):
    """Detect sustained, small monotone color changes in opaque row/column runs."""
    pixels = image.load()
    def ramp(points):
        previous, directions, changes = None, [0, 0, 0], 0
        for point in points:
            pixel = pixels[point]
            if pixel[3] < 220:
                previous, directions, changes = None, [0, 0, 0], 0
                continue
            if previous is not None:
                delta = [pixel[i] - previous[i] for i in range(3)]
                signs = [1 if d > 0 else -1 if d < 0 else 0 for d in delta]
                if max(map(abs, delta)) > 8 or any(a and b and a != b for a, b in zip(directions, signs)):
                    directions, changes = [0, 0, 0], 0
                elif any(signs):
                    directions = [a or b for a, b in zip(directions, signs)]
                    changes += 1
                    if changes >= 7:
                        return True
            previous = pixel
        return False
    rows = range(0, image.height, max(1, image.height // 16))
    cols = range(0, image.width, max(1, image.width // 16))
    return any(ramp((x, y) for x in range(image.width)) for y in rows) or any(ramp((x, y) for y in range(image.height)) for x in cols)


def inspect(image: Image.Image) -> dict[str, object]:
    rgba = image.convert("RGBA")
    alpha = list(rgba.getchannel("A").getdata())
    rgb = rgba.convert("RGB")
    visible = [pixel for pixel, opacity in zip(rgb.getdata(), alpha) if opacity >= 220]
    border = border_pixels(rgba)
    border_bins = Counter(quantize(pixel) for pixel in border)
    dominant_bin, dominant_count = border_bins.most_common(1)[0]
    border_fraction = dominant_count / max(1, len(border))
    corners = [rgba.getpixel(point)[:3] for point in ((0, 0), (rgba.width - 1, 0), (0, rgba.height - 1), (rgba.width - 1, rgba.height - 1))]
    corner_matches = sum(quantize(corner) == dominant_bin for corner in corners) / 4
    visible_bins = Counter(quantize(pixel) for pixel in visible)
    visible_dominant = visible_bins.most_common(1)[0][0] if visible_bins else (255, 255, 255)
    transparent_fraction = sum(opacity < 220 for opacity in alpha) / max(1, len(alpha))
    meaningful_alpha = min(alpha) < 255
    flat_visible = bool(visible) and visible_bins.most_common(5)[0][1] / len(visible) > 0.70
    if meaningful_alpha:
        classification = "transparent-foreground"
    elif border_fraction >= 0.65 and corner_matches >= 0.75:
        classification = "connected-flat-background"
    else:
        classification = "preserve-background"
    border_spread = max(distance(pixel, border[0]) for pixel in border)
    flat_border = border_spread <= 24
    if not meaningful_alpha:
        classification = "connected-flat-background" if flat_border else "complex-background"
    gradient_suspected = len(set(visible)) > 32 or continuous_color_ramp(rgba) or (not meaningful_alpha and not flat_border)
    return {
        "partial_alpha": any(0 < a < 255 for a in alpha),
        "flat_border": flat_border,
        "color_count": len(visible_bins),
        "gradient_suspected": gradient_suspected,
        "width": rgba.width,
        "height": rgba.height,
        "meaningful_alpha": meaningful_alpha,
        "transparent_fraction": transparent_fraction,
        "border_fraction": border_fraction,
        "corner_matches": corner_matches,
        "dominant_border": dominant_bin,
        "dominant_visible": visible_dominant,
        "flat_visible": flat_visible,
        "classification": classification,
    }


def close_background(image: Image.Image, tolerance: float) -> Image.Image:
    """Remove only border-connected pixels near the dominant border color."""
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    border = border_pixels(rgba)
    background = Counter(border).most_common(1)[0][0]
    queue: deque[tuple[int, int]] = deque()
    seen: set[tuple[int, int]] = set()
    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(1, height - 1):
        queue.extend(((0, y), (width - 1, y)))
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen or distance(pixels[x, y][:3], background) > tolerance:
            continue
        seen.add((x, y))
        for next_point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            nx, ny = next_point
            if 0 <= nx < width and 0 <= ny < height and next_point not in seen:
                queue.append(next_point)
    for x, y in seen:
        r, g, b, _ = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)
    return rgba


def normalize_monochrome(image: Image.Image, fill: RGB) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, alpha = pixels[x, y]
            if alpha >= 128:
                pixels[x, y] = (*fill, alpha)
    return rgba


class DecisionRequired(ValueError):
    """The next operation requires a user choice, not an implicit fallback."""


def prepare(image, analysis, background, fill="keep", alpha_threshold=None):
    if background == "auto":
        raise DecisionRequired("Confirm whether to preserve or remove the source background.")
    if analysis["gradient_suspected"]:
        raise DecisionRequired("Gradient or complex artwork detected. Supply vector/transparent foreground or confirm a reconstruction strategy; flat-color tracing is not faithful.")
    if background == "remove" and not analysis["flat_border"]:
        raise DecisionRequired("Background is not a uniform edge-connected color; do not use flat background removal.")
    if analysis["partial_alpha"] and alpha_threshold is None:
        raise DecisionRequired("VTracer cannot preserve continuous alpha. Confirm an alpha threshold or supply vector artwork.")
    prepared = image.convert("RGBA")
    action = "preserve-background"
    if background == "remove":
        prepared = close_background(prepared, tolerance=24)
        action = "edge-connected-background"
    if alpha_threshold is not None:
        prepared.putalpha(prepared.getchannel("A").point(lambda a: 255 if a >= alpha_threshold else 0))
        action += "+confirmed-alpha-threshold"
    if fill == "white":
        prepared = normalize_monochrome(prepared, (255, 255, 255))
        action += "+confirmed-white-fill"
    if prepared.getchannel("A").getbbox() is None:
        raise DecisionRequired("Preprocessing removed the entire image. Confirm foreground/background selection.")
    return prepared, action


def choose_mode(analysis: dict[str, object], requested: str, preparation: str) -> str:
    if requested != "auto":
        return requested
    if preparation == "edge-connected-background" and bool(analysis["flat_visible"]):
        return "polygon"
    return "spline"


def run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except FileNotFoundError as error:
        raise RuntimeError(f"Missing dependency: {command[0]}") from error
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout).strip()
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{detail}") from error


def verify_render(svg_path, prepared):
    with tempfile.TemporaryDirectory(prefix="image-to-svg-verify-") as temp_dir:
        rendered_path = Path(temp_dir) / "rendered.png"
        if shutil.which("rsvg-convert"):
            run(["rsvg-convert", "-w", str(prepared.width), "-h", str(prepared.height),
                 "-o", str(rendered_path), str(svg_path)])
            renderer = "rsvg-convert"
        elif shutil.which("magick"):
            run(["magick", "-background", "none", str(svg_path), "-resize",
                 f"{prepared.width}x{prepared.height}!", str(rendered_path)])
            renderer = "magick"
        else:
            raise DecisionRequired("No SVG renderer available; install librsvg or ImageMagick before validating.")
        rendered = Image.open(rendered_path).convert("RGBA")
        source_alpha, render_alpha = prepared.getchannel("A"), rendered.getchannel("A")
        if render_alpha.getbbox() is None:
            return {"status": "low-fidelity", "reason": "Rendered SVG is blank"}
        def rms(left, right):
            values = ImageStat.Stat(ImageChops.difference(left, right)).rms
            return math.sqrt(sum(v * v for v in values) / len(values)) / 255
        mattes = {}
        for name, color in (("dark", (24, 24, 24, 255)), ("light", (255, 255, 255, 255))):
            bg = Image.new("RGBA", prepared.size, color)
            mattes[name] = round(rms(Image.alpha_composite(bg, prepared).convert("RGB"),
                                     Image.alpha_composite(bg, rendered).convert("RGB")), 5)
        left = {i for i, a in enumerate(source_alpha.getdata()) if a >= 128}
        right = {i for i, a in enumerate(render_alpha.getdata()) if a >= 128}
        union = left | right
        iou = len(left & right) / len(union) if union else 1.0
        alpha_rmse = rms(source_alpha, render_alpha)
        return {"status": "rendered" if max(mattes.values()) <= .08 and alpha_rmse <= .08 and iou >= .95 else "low-fidelity",
                "renderer": renderer, "matte_rmse": mattes, "alpha_rmse": round(alpha_rmse, 5),
                "silhouette_iou": round(iou, 5)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--background", choices=("auto", "remove", "preserve"), default="auto")
    parser.add_argument("--mode", choices=("auto", "spline", "polygon", "pixel"), default="auto")
    parser.add_argument("--fill", choices=("auto", "white", "keep"), default="keep")
    parser.add_argument("--alpha-threshold", type=int)
    parser.add_argument("--no-svgo", action="store_true")
    args = parser.parse_args()
    if args.alpha_threshold is not None and not 1 <= args.alpha_threshold <= 254:
        raise ValueError("alpha-threshold must be between 1 and 254")
    with Image.open(args.input) as source:
        image = source.convert("RGBA")
    analysis = inspect(image)
    if args.inspect or args.background == "auto":
        print(json.dumps({"status": "needs_decision", "analysis": analysis,
                          "questions": ["Preserve or remove the source background?", "Confirm foreground, any existing wordmark, and brand backplate roles."]}))
        return 2
    if args.output is None:
        raise ValueError("An output path is required for conversion")
    if args.output.exists():
        raise DecisionRequired("Output already exists; select a new draft path to preserve previous work.")
    prepared, preparation = prepare(image, analysis, args.background, args.fill, args.alpha_threshold)
    if not shutil.which("vtracer"):
        raise DecisionRequired("VTracer 0.6.5 is required; ask before installing it.")
    version = subprocess.run(["vtracer", "--version"], capture_output=True, text=True, check=True).stdout
    if "0.6.5" not in version:
        raise DecisionRequired("Expected VTracer 0.6.5; confirm a version migration before converting.")
    mode = choose_mode(analysis, args.mode, preparation)
    with tempfile.TemporaryDirectory(prefix="image-to-svg-") as temp_dir:
        temp = Path(temp_dir)
        prepared_path, raw = temp / "prepared.png", temp / "raw.svg"
        prepared.save(prepared_path)
        run(["vtracer", "--input", str(prepared_path), "--output", str(raw), "--mode", mode,
             "--filter_speckle", "0", "--color_precision", "8", "--corner_threshold", "60",
             "--segment_length", "3.5" if mode == "polygon" else "4", "--path_precision", "4",
             "--hierarchical", "cutout"])
        # Animation boundaries must survive optimization; omit the default merging preset.
        optimized = False
        if not args.no_svgo:
            if not shutil.which("svgo"):
                raise DecisionRequired("SVGO unavailable. Confirm --no-svgo or install SVGO 4.1.0.")
            version = subprocess.run(["svgo", "--version"], capture_output=True, text=True, check=True).stdout.strip()
            if version != "4.1.0":
                raise DecisionRequired("Expected SVGO 4.1.0; confirm a version migration.")
            config = temp / "svgo.config.mjs"
            config.write_text("export default {plugins:['removeDoctype','removeXMLProcInst','removeComments']};")
            run(["svgo", str(raw), "-o", str(raw), "--config", str(config)])
            optimized = True
        root = ET.fromstring(raw.read_text())
        tags = [node.tag.split("}")[-1] for node in root.iter()]
        if "image" in tags or "path" not in tags:
            raise RuntimeError("Output is not native SVG paths")
        visual = verify_render(raw, prepared)
        report = {"status": "ready" if visual["status"] == "rendered" else "needs_decision",
                  "input": str(args.input), "output": str(args.output), "analysis": analysis,
                  "preparation": preparation, "mode": mode, "svgo": optimized,
                  "path_count": tags.count("path"), "bytes": raw.stat().st_size,
                  "visual_validation": visual}
        if report["status"] != "ready":
            report["questions"] = ["The trace changes the visible artwork. Supply better/vector artwork or confirm a different tracing strategy."]
            print(json.dumps(report))
            return 2
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(raw.read_bytes())
        print(json.dumps(report))
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DecisionRequired as error:
        print(json.dumps({"status": "needs_decision", "questions": [str(error)]}))
        raise SystemExit(2)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, ET.ParseError) as error:
        print(json.dumps({"status": "failed", "error": str(error)}))
        raise SystemExit(1)
