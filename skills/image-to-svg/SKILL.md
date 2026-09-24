---
name: image-to-svg
description: Inspect and convert raster logos or icons into editable SVG paths with source-preserving defaults and explicit appearance-changing choices. Use for PNG, JPEG, WebP, transparency, flat backgrounds, and tracing-quality checks; pause for gradients, complex backgrounds, or uncertain foreground roles.
---

# Image to SVG

Owns raster inspection, tracing and fidelity checks. It does not design animation layouts or extract foreground from complex backgrounds. Read [conversion details](references/conversion.md) for dependencies, flags and report metrics.

## Workflow

1. In an application project, resolve the actual target logo/splash asset from project references before asking for another upload; do not assume the launcher icon is the splash artwork. Run `python scripts/convert_image_to_svg.py INPUT --inspect`. It reports dimensions, alpha, border/color characteristics and suspected gradients without producing an SVG.
2. Inspect the actual image. Preserve source background and colors by default, announce that choice and pass `--background preserve` explicitly. Only requested removal uses `remove`; a white border does not authorize it. Preserve brand backplates, enclosed details and corner geometry during tracing. The animation skill separately resolves the desired splash corners; retaining raster geometry does not settle that choice. Downstream preview/export backgrounds are separate from this source decision.
3. Resolve actual fidelity/resource issues before tracing: partial alpha, gradients, complex content, missing tools or loss of detail. Ask before recoloring, thresholding alpha, reconstruction or simplification. Do not install dependencies, silently switch strategies or substitute a bitmap. Approval for reconstruction does not make flat VTracer tracing recover a gradient: do not bypass its refusal by invoking the same tracer directly and labeling color bands “reconstruction”. Correct your own invocation mistakes when intent is known. Explicit requests to ask every unspecified choice override defaults.
4. Convert into a new path. Inspect the actual SVG render against the source on matching light/dark mattes; compare colors, silhouette, alpha and enclosed details. Automated thresholds do not replace visual review.

## Waiting for Decisions

Prefer a permitted native question/input tool and follow its actual response lifecycle. Await a synchronous answer; an asynchronous acknowledgement means the answer is still pending. After independent inspection, use the host's supported interruptible wait/yield mechanism (for example, Codex `clock.sleep` in intervals of at most 60 seconds), checking for replies after each return. Do not send `final`/`final_answer` or end the turn while a native prompt is pending. Keep dependent tracing, installation and delivery paused; tool success, elapsed time and preselection are not consent.

If the tool is unavailable, fails or the user cannot see the question, explain the limitation and leave the actual unanswered question in a persistent text reply, following host restrictions. A text handoff may end the turn to await the next user message; it does not complete the task. Cancellation/closure/empty replies never select a default; respect a user stop and do not reopen prompts in a loop. Reuse partial answers, and honor later explicit acceptance or delegation without repeating resolved choices.

## Boundaries and Output

- `--background auto` is inspection-only. Source preservation still requires the explicit CLI flag; it is not implicit background removal.
- Flat removal affects only border-connected pixels near the background color. A transparent white mark remains foreground.
- VTracer cannot retain continuous alpha or recover a compact continuous gradient. Preservation intent does not remove these limits: discuss a suitable source/reconstruction strategy rather than tracing many flat regions and claiming fidelity.
- Never overwrite a previous output. A failed or distorted candidate is not a successful conversion.

The CLI prints JSON: exit 0 / `ready` means a path-only SVG passed rendered comparisons; exit 2 / `needs_decision` creates no final SVG; exit 1 / `failed` reports an execution error. Present unresolved issues before continuing. Reports include source analysis, preprocessing, tracing/optimizer information and color/alpha/silhouette comparisons.
