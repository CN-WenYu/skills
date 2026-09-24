---
name: svg-logo-to-lottie
description: Create app splash, startup, launch, opening-screen or logo animations from standalone images/SVGs and app names, or from an existing project without supplied artwork or the words SVG/Lottie. Resolve visual choices using supplied assets or verified project branding, then export native-vector Lottie with identical offline previews. Not for arbitrary page transitions or HTML conversion.
---

# Logo to Lottie

Trigger on intent such as “make a splash animation for this app”, “animate the startup screen” or “animate the app logo”; supplied SVG/Lottie terminology is not required.

The agent designs the choreography; the tools inventory geometry, execute the plan, shape text and verify output. Analyze the actual artwork and name before choosing actions. Optional app-purpose context can help, but must not become a prerequisite or a basis for invented features.

## Workflow

1. Route by context: with standalone artwork/name, use the [standalone intake](references/lottie-export.md#standalone-intake); do not search unrelated projects for branding. Inside an application repository, follow [project evidence](references/lottie-export.md#project-context-and-variants) and inspect the active target/splash first. Reuse supplied answers or authoritative project values, and ask only for missing or conflicting decisions.
2. Read [export workflow](references/lottie-export.md) for setup, config and commands. For raster input, locate/read `image-to-svg`, inspect first and pass its converter path explicitly. Parse SVG directly. Reuse isolated dependencies; missing installation needs authorization.
3. Inspect actual artwork and `inventory`. Distinguish containers, symbols, connectors, decoration and brand wordmarks; pictorial letters are not application names. Map coherent groups by reviewed IDs, never path count or color alone.
4. Resolve the visual choices below together. Read [motion design](references/motion-design.md), briefly explain the material-specific foreground plan and record its rationale. A favorite example is not a required storyboard. Read [backgrounds and SVG support](references/backgrounds-and-svg.md) for plates, corners and gradients.
5. Run `inspect`, then `draft` into new directories. Inspect [JSON size](references/lottie-export.md#json-size-and-fidelity); use automatic exact cleanup and ask before coordinate rounding or path simplification. Each HTML must play and download its exact JSON, not CSS imitation. Use the reusable tool. Run authorized Web checks and inspect actual frames for the selected text effect, foreground action/interaction, background entrance, colors, corners and clipping.
6. Present named variants and theme versions for review. Only record `approve` after explicit selection/approval and matching Web/visual evidence. Deliver the selected identical JSON; do not regenerate after approval.

## Visual Choices and Defaults

Bundle unresolved questions, reuse answers, and do not ask the user to author keyframes:

- **Corners:** when an icon backplate exists, ask whether to retain its shape or use rounded corners, recommending a concrete radius when relevant. Reuse a prior explicit corner decision or an actual project splash corner specification. Merely seeing square pixels or a platform-masked launcher icon does not answer this question. Do not round the entire canvas.
- **Text color:** reuse the actual splash text token for the target theme, or derive a legible color from a verified splash background and explain the choice. Without reliable project evidence or a prior answer, ask. Never choose black from an arbitrary light preview matte.
- **Font:** reuse a specified/project brand font with a real requested weight. Otherwise run `fonts NAME` and present 3–5 available families with face/weight and recommendation (fewer if fewer exist); let the user choose. Do not silently pick the first candidate. An explicit delegation to choose is valid, but only for the named decision.
- **Preview count:** offer one recommended choreography or an optional pair of materially different arrangements. Multi-style generation is opt-in; use one if unspecified. Dark/light theme adaptation is separate: when both are supported by the actual project, prepare both by default with the same choreography.

Prefer the host Agent's available native question tool, respecting its mode and option limits. Present every concrete text-effect choice with a number using the [text-motion menu](references/motion-design.md#text-motion-menu). Before asking, read [decision handoff](references/lottie-export.md#decision-handoff) for synchronous/asynchronous waiting and recovery. While a native question is pending, do not send a final answer or end the turn; keep dependent work paused until actual answers arrive. Missing dependencies must not suppress available analysis or choices.

Preserve source colors and icon background unless changed by the user; outer canvas stays transparent unless the project/request establishes an exported background. Keep the name below the complete icon in genuine Bold 700; omitted size/gap use 18%/12% of the final icon width as defined in [wordmark layout](references/lottie-export.md#wordmark-size-and-spacing), preserving explicit user/project values. Recommend staggered hops as the default option, then obtain the text-motion choice or explicit delegation before drafting. Reuse a prior selection or verified project motion. Match name timing to the foreground; connected scripts stay intact.

The JSON download filename uses the verified application name, normalized to lowercase underscore form and ending in `_loading.json`. If the project or standalone input does not establish the application name, ask before drafting; never infer it from the asset filename.

A retained icon background participates in the entrance from zero opacity; the agent designs its timing relative to foreground objects. Static geometry does not mean static visibility. A visible exported full-canvas layer also has an entrance; the host page/preview matte is separate. A background visible from frame zero needs a specific user instruction, not merely permission to retain its color. See the export schema for recording exceptions.

Ask before fidelity loss, reconstruction, ambiguous branding, unavailable glyph/weight or unsupported effects. Fix agent-authored config mistakes locally when intent is known. User approval of reconstruction does not authorize unrelated corner, color, font or timing choices. Structural checks, playback, visual review and user approval are distinct; Android/iOS remain unverified without target-player checks.
