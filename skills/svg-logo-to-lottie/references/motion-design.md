# Material-Specific Motion Design

Read when designing logo and text choreography. This is a decision framework and execution contract, not a fixed storyboard or collection of brand templates.

## Agent Decisions

Inspect the image and SVG inventory before designing. Identify the actor, affected objects, connectors, result cues and decoration only where supported by the artwork. The app purpose is context, not permission to invent objects/features. Abstract or inseparable marks may need a quiet geometric entrance rather than a narrative.

Form a concise concept: initial state → action/relationship → recognizable final mark. Explain why the action suits these objects and why a generic entrance would or would not suffice. Examine pivots, curved travel, contact, follow-through and occlusion where relevant. Do not turn one application's successful storyboard into an industry/category template.

Map every claimed action to supported properties before offering an executable plan: rotation about a pivot is not translation; a path reveal is not a fade; “assembly” needs meaningful convergence. Check actual exported beats against the description. If a primitive is missing, distinguish the intended design, the exact capability gap, and any supported alternative with its visual loss. Explain a scoped reusable extension when warranted, respecting source-edit and dependency authorization. Do not recommend a weaker effect solely because it is easy to generate, silently substitute it, patch generated JSON or write a brand-specific generator. “Do not modify skill source” does not itself prohibit project-local work, but also does not authorize an unrequested extension.

When variants are requested, make their concepts distinct (relationship, sequence of cause/effect or visual emphasis), not merely different delays or rebound strength. Keep the approved source artwork, final geometry and branding. Review intended-scale playback for recognizable action, believable timing/occlusion and a readable final name. Automated bounds/playback checks cannot judge meaning. Revise a weak proposal before presenting it as the recommended draft.

## Text Choreography

Analyze the name's length, script, independent shaped units, brand tone and reading hierarchy alongside the actual logo motion. Decide whether text echoes an action, completes it or stays quiet so the logo remains the focus. Describe initial state → movement → readable settlement as one composition. App category is useful context, not an automatic effect classifier.

Recommend one coherent plan, with a small number of genuinely relevant alternatives only when helpful. Reuse selected motion or explicit delegation; acceptance of an overall proposal that describes text also resolves text motion. A general request to use sensible defaults delegates a context-appropriate choice, not automatic hops. If the user requests confirmation of all unspecified visual choices, obtain it. Otherwise ask only material unresolved decisions through [decision handoff](lottie-export.md#decision-handoff); do not reauthorize known preferences or ask the user to choose keyframes.

For example, a collage concept may use alternating directional arrivals that assemble both imagery and name; a restrained long name may use a quiet whole-line entrance. These are reasoning examples, not category templates. A scanning light followed by text appearance is different from a masked text reveal: the latter has no luminous beam. Describe this difference before agreeing to an alternative.

### Optional Recipes

Use a recipe when it fits the analysis, or show relevant recipes when the user wants inspiration. There is no universal preferred preset and no requirement to list all recipes at intake.

| Preset | Actual behavior |
| --- | --- |
| `hop` | Independent shaped units rise, overshoot and rebound with opacity. |
| `rise` | The whole line moves upward slightly and fades in. |
| `fade` | The whole line fades in without movement. |
| `gather` | Independent shaped units converge from wider spacing with opacity, retaining final kerning. Unavailable for one inseparable unit. |
| `reveal` | A native rectangular mask reveals the line left to right; no beam, glow or opacity fade. Other reveal directions are unsupported. |

Use authored text tracks for supported motion beyond these recipes; do not squeeze a user's description into the nearest preset or invent a new preset name. Record the actual selection, accepted proposal or delegation in `wordmark.motion.user_request`, and the design explanation separately in `rationale`.

### Authored Text Tracks

Set `wordmark.motion.tracks` and a nonempty `rationale`, instead of `preset`. Use one `target: "line"` track for the whole shaped name, or tracks selecting `units: [0, 1, ...]`. Unit indices refer to the result of `typography.shape_text`, not Unicode character positions: spaces have no visible unit, ligatures/combining marks stay together and connected scripts remain indivisible. Inspect shaping before assigning indices (call the installed `typography.shape_text` with the selected font/index/weight); every visible unit must be assigned exactly once. A track selecting several units applies the same timeline to each without changing painter order.

Each track has explicit `keyframes` with `time` (absolute seconds), `offset` ([x,y] in em units; positive y is downward), `scale` (positive uniform percent) and `opacity` (0–100). Times must be nonnegative and strictly increasing. End at offset [0,0], scale 100 and opacity 100 to preserve the final name. Optional track `easing` has four cubic-bezier coordinates in [0,1]; express overshoot with keyframes. Optional motion `anchor: baseline|center` applies to each unit. Preset timing fields cannot be mixed with tracks; encode timing directly in each track. Rotation, curved trajectories, generic masks, light beams and text exit loops are not part of this text-track contract.

Example syntax for a gentle whole-line arrival; choose actual timing and offsets from the composition:

```json
{"rationale":"A quiet name entrance lets the intricate logo remain the focus.",
 "user_request":"Use the proposed gentle whole-line arrival.",
 "tracks":[{"target":"line","keyframes":[
   {"time":0.6,"offset":[0,0.2],"scale":100,"opacity":0},
   {"time":1.0,"offset":[0,0],"scale":100,"opacity":100}
 ]}]}
```

The name's onset and settling should complement the foreground action. Reserve the full motion envelope separately from settled spacing and keep the final name readable. Cinematic character does not require glow, 3D or long duration. Persistent tail loops require an explicit request, supported implementation and host playback support.

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
