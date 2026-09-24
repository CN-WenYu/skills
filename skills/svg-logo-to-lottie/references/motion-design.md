# Material-Specific Motion Design

Read when designing foreground choreography. This is a decision framework and execution contract, not a fixed storyboard or collection of brand templates.

## Agent Decisions

Inspect the image and SVG inventory before designing. Identify the actor, affected objects, connectors, result cues and decoration only where supported by the artwork. The app purpose is context, not permission to invent objects/features. Abstract or inseparable marks may need a quiet geometric entrance rather than a narrative.

Form a concise concept: initial state → action/relationship → recognizable final mark. Explain why the action suits these objects and why a generic entrance would or would not suffice. Examine pivots, curved travel, contact, follow-through and occlusion where relevant. Do not turn one application's successful storyboard into an industry/category template.

Map every claimed action to supported properties: rotation about a pivot is not translation; a path reveal is not a fade; “assembly” needs meaningful convergence. Check actual exported beats against the description. If a primitive is missing, explain the limitation and agree a supported treatment; do not quietly replace the action, patch generated JSON or write a brand-specific generator.

When variants are requested, make their concepts distinct (relationship, sequence of cause/effect or visual emphasis), not merely different delays or rebound strength. Keep the approved source artwork, final geometry and branding. Review intended-scale playback for recognizable action, believable timing/occlusion and a readable final name. Automated bounds/playback checks cannot judge meaning. Revise a weak proposal before presenting it as the recommended draft.

## Text Motion Menu

Ask once with the host's native question tool before drafting unless the current session or verified project already selects the effect or delegates its choice. In the user's language, show all five effects individually, numbered, with a short description and a material-specific recommendation:

1. Staggered hop and fade (`hop`, default recommendation): independent shaped clusters rise, overshoot and rebound.
2. Gentle whole-line rise and fade (`rise`): the complete name moves slightly up without bounce.
3. Whole-line fade (`fade`): the name appears together without translation or scale.
4. Spacing convergence (`gather`): independent clusters converge from wider spacing with a fade, retaining final kerning. Connected writing remains intact; if shaping yields one inseparable unit, explain that spacing convergence is unavailable and ask for another choice.
5. Left-to-right reveal (`reveal`): a native rectangular Lottie mask reveals the whole name. This is a visual direction, not inferred language direction; other directions need an agreed implementation.
6. Agent recommendation: explicit permission to choose one supported effect and explain its fit.
7. Custom effect: ask for the intended appearance/reference, assess support and agree a treatment before generation.

Never replace items 2–5 with “other effects”. Keep hop labelled as a default recommendation, not pre-approved. Record the actual selection/delegation in `wordmark.motion.user_request`; custom intent does not authorize an invented unsupported preset. Numbering remains stable even if the recommended option is displayed first. A user explicitly asking for defaults selects hop. Reuse earlier answers without asking again.

The name's onset and settling should complement the foreground action. Cinematic character comes from hierarchy and coordinated timing, not compulsory glow, 3D, long duration or a copied studio ident. Keep the splash compact and finish legibly; persistent tail loops require an explicit request and host playback support.

## Config Contract

`motion` contains a nonempty `rationale` and `tracks`. Each track has a unique `name`, a `reason`, either `element_ids` or `target`, and explicit `keyframes`. `target` is `foreground` or `backplate`. IDs can select SVG groups; preserve together the elements forming one inseparable object. Generated plates use `target: backplate`.

Every visible shape must belong to exactly one track. Include stationary content with one identity keyframe. Tracks are rendered in original painter order, not config order. Review occlusion before drafting; if source layering cannot express the proposed interaction, revise the plan or explicitly discuss a source-layer change. Do not silently reorder layers after compilation. Interleaved grouping that changes painter order, duplicated selections and omitted shapes are rejected. IDs identify semantics established by the agent's inspection; path indices and color heuristics do not establish semantics.

Keyframes use:

- `time`: seconds, nonnegative and strictly increasing within a track.
- `offset`: [x,y] in normalized source SVG units, relative to that object's original position.
- `scale`: positive uniform percentage around the bounds center or explicit track `pivot` [x,y] in normalized source SVG units.
- Optional `rotation`: finite degrees, default 0, around the same pivot.
- Optional `curve`: `{ "out": [dx,dy], "in": [dx,dy] }` on a non-final beat; cubic position handles relative to this and the next offset respectively. Both handles are required.
- `opacity`: 0–100; before the first keyframe the first value is held.
- Optional `draw`: 0–100, present on every keyframe of a drawn-path track.

Final offset must be [0,0], scale 100, rotation 0, opacity 100 and draw 100. This contract preserves final artwork, not an arbitrary transformed approximation. Changing final layout/content is a separate source/layout decision.

For a backplate visible from frame zero, include `user_request` quoting the actual request; an authored reason alone is insufficient.

Optional track `easing` is [x1,y1,x2,y2] for a cubic-bezier with values in [0,1]. Explicit scale/position keyframes can provide overshoot when appropriate. Restricting the interpolation curve makes extrema computable; motion outside these bounds must not be concealed by clipping.

Syntax example (choose actual actions from the material):

```json
{
  "motion": {
    "rationale": "The artwork has one uninterrupted mark; retain its stable silhouette while introducing it.",
    "tracks": [{
      "name": "Main mark",
      "target": "foreground",
      "reason": "A short opacity change suits this inseparable symbol; no geometric motion is needed.",
      "keyframes": [
        {"time": 0, "offset": [0, 0], "scale": 100, "opacity": 0},
        {"time": 0.4, "offset": [0, 0], "scale": 100, "opacity": 100}
      ]
    }]
  }
}
```

Do not reuse this example when the source calls for another choreography. Set times, offsets, scales and groups from the inspected material. `inspect` reports the resulting rationale, role names, timing and bounds.

## Drawing and Support Limits

`draw` compiles to native Lottie trim paths for one open stroked SVG path per track. Stroke color, width and geometry remain intact. Drawing follows the actual path direction; inspect it before deciding whether it expresses the intended connection. An arrowhead represented by separate geometry can have its own timed track, but is not generated or repositioned automatically.

Filled arrows and closed silhouettes are not open strokes. Drawing their perimeter is not a substitute for arrow-tail-to-head revelation. Explain that a faithful reveal or user-approved centerline/head reconstruction requires additional work; do not silently turn a filled gradient arrow into a flat stroke. Tracks support native rotation/pivots and cubic position trajectories. Bounds conservatively include intermediate rotation extrema and curve control points, so tight layouts may need revision. Curved/rotating tracks are sampled at every output frame. Generic foreground masks/mattes and arbitrary path morphing are unsupported; the text-reveal preset owns only its generated rectangular mask.

Custom backplate tracks support independent opacity timing with stationary geometry. A moving plate requires a different supported composition; do not silently replace the requested behavior. See [background containment](backgrounds-and-svg.md#corners-and-clipping) and [explicit presets](lottie-export.md#configuration).

## Evaluate Design, Not Template Similarity

Check whether meaning and recognition improve, motion preserves geometry, groups stay coherent, name hierarchy is appropriate, and the settled frame is useful in the host app. Different artwork should be able to yield different plans, including no foreground movement. Reject a skill behavior that copies the reference bubbles/arrow/star sequence onto unrelated artwork.

Tests should cover authored rotation/curves and their intermediate bounds, distinct text presets and shaping, stationary content, layer-order invariants, unsupported filled-path drawing and actual Web rendering. Do not score success by matching a favorite logo's exact keyframes.
