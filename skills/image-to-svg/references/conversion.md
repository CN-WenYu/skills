# Conversion Commands and Limits

Read when setting up dependencies, selecting confirmed conversion parameters, or interpreting a report.

## Setup

Use an isolated Python environment and the pinned requirements file. Ask before installing missing tools. Do not install into system Python or silently update globally installed versions.

```sh
python3 -m venv /chosen/runtime/venv
/chosen/runtime/venv/bin/python -m pip install -r /installed/image-to-svg/requirements.txt
```

VTracer CLI 0.6.5 is required. The Python package is not required. If installation is approved, use an isolated Cargo prefix, for example `cargo install vtracer --version 0.6.5 --root /chosen/runtime/vtracer`, and add that bin directory to the command's PATH. Use SVGO 4.1.0 and librsvg or ImageMagick for rendering. Confirm installation or explicit `--no-svgo` if SVGO is unavailable.

## Inspect and Convert

```sh
python scripts/convert_image_to_svg.py logo.png --inspect
python scripts/convert_image_to_svg.py logo.png logo.svg --background preserve --mode spline
python scripts/convert_image_to_svg.py logo.png foreground.svg --background remove --mode polygon
```

Resolve script paths relative to the installed skill, not the caller's working directory. Inspection may be used without VTracer or SVGO.

Options:

- `--background auto|preserve|remove`: `auto` only inspects; the other choices record explicit source-background intent.
- `--mode auto|spline|polygon|pixel`: override when known geometry calls for it. The automatic tracing heuristic is a starting point; it cannot prove edge quality.
- `--fill keep|white|auto`: `keep` is the default; legacy `auto` also preserves source RGB. `white` requires explicit recoloring intent.
- `--alpha-threshold 1..254`: omitted by default. VTracer does not preserve continuous alpha; request a threshold decision or vector source when partial transparency is present.
- `--no-svgo`: explicit omission. Otherwise the pinned optimizer runs only non-geometric cleanup; it does not merge paths/groups or remove IDs.

Pure-color background removal is blocked for nonuniform borders. Suspected gradients/complex content are blocked for tracing until a different strategy is agreed; do not pass different flags to suppress the decision. Transparent vector foreground plus confirmed gradient parameters can instead be handed to `svg-logo-to-lottie`.

## Validation

Compare against the prepared image whose changes the user explicitly approved. Render using librsvg, or ImageMagick when librsvg is unavailable. Composite both images on identical dark and light mattes; ignore RGB hidden behind zero alpha.

Current conservative automated acceptance bounds are matte RGB RMSE <= 0.08, alpha RMSE <= 0.08, and silhouette IoU >= 0.95. These detect gross failures, not all perceptual changes. A low-fidelity result returns `needs_decision`, does not write the final SVG, and asks for better source artwork or a reviewed tracing strategy. Empty artwork, missing rendering tools and overwritten destinations are not accepted.

Run regression tests with the isolated interpreter:

```sh
python -m unittest discover -s tests -v
```
