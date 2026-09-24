# Exporter Workflow

Read before setup or draft generation. This is the authority for configuration, artifacts and approval checks.

## Explicit Isolated Setup

Use Python 3.10+ and the pinned files at the skill root. Ask before missing dependency installation. For an authorized setup, substitute actual absolute paths:

```sh
python3 -m venv /chosen/runtime/venv
/chosen/runtime/venv/bin/python -m pip install -r /installed/svg-logo-to-lottie/requirements.txt
mkdir -p /chosen/runtime/web
cp /installed/svg-logo-to-lottie/package.json /installed/svg-logo-to-lottie/package-lock.json /chosen/runtime/web/
npm ci --prefix /chosen/runtime/web --ignore-scripts --no-audit --no-fund
PLAYWRIGHT_BROWSERS_PATH=/chosen/runtime/browsers node /chosen/runtime/web/node_modules/playwright/cli.js install chromium --only-shell
```

Do not install globally or into system Python. The CLI never installs dependencies. Raster setup is owned by `image-to-svg`. A pre-existing supported browser can be selected explicitly with `--browser-channel msedge` or `chrome`; otherwise use the isolated Chromium above and keep the same `PLAYWRIGHT_BROWSERS_PATH` for validation.

## Standalone Intake

An attached logo and app name are sufficient to start outside a project. Use them directly; a scratch directory or the skill source repository is not an app project. Do not hunt for unrelated project branding, ask again for supplied inputs, or infer theme support from the computer's appearance. State the known asset/name and relevant inspection findings before asking for remaining choices.

Apply the entrypoint's visual-choice rules: show real font candidates and ask unresolved corners/text color, distinguish source plate from exported canvas and preview matte, and offer the optional second choreography. Explain defaults (name below the icon, bold text, animated plate); ask for text motion using the complete numbered menu in motion-design.md. Ask about ambiguous artwork roles or fidelity changes. If the user explicitly asks to confirm all unspecified backgrounds or visual decisions, present those defaults as recommendations for confirmation instead of applying them. App purpose is optional context; do not block on it.

## Decision Handoff

Bundle related unresolved decisions into a short, numbered list with a recommendation and understandable alternatives. Separate blocking choices (for example fidelity, corners, font/color or installation) from optional context/second choreography. Never bury multiple mandatory decisions in one long background question. Ask only what current inspection can support; later rounds should contain newly discovered or still unanswered issues.

Prefer a native question/input tool exposed by the current host Agent. Inspect its availability and supported mode; do not assume Codex tool names exist in every Agent, switch modes to unlock a tool or install a question service. In Codex, use an available async question tool when appropriate; a Plan-only tool is unavailable in other modes. Respect actual tool instructions over this reference.

Show the complete numbered text-motion menu in the question itself. If the tool supports enough options, make each a selectable option; if it limits options, put the complete numbered list in one free-text question accepting a number/custom description, or split into clearly labelled questions only when the schema requires it. Do not hide concrete effects behind a generic “other” option. Preserve numbering and identify the recommendation. This skill does not itself invoke tools: the calling Agent performs intake.

The calling Agent owns the question lifecycle; the skill and converter cannot keep the host UI open themselves. A call acknowledgement is not an answer. Use actual tool calls, not tool-shaped text or a final message saying that questions were sent.

- **Synchronous:** await the tool's answer, then apply only the decisions actually answered.
- **Asynchronous:** after submission, continue only independent work. When that work is exhausted, use the host's supported wait/yield mechanism until the answer arrives. In Codex, when `request_user_input_async` is available, its return only acknowledges submission; the answer arrives as a later user message. Use an available interruptible wait such as `clock.sleep` in bounded intervals (at most 60 seconds per call) and check incoming messages after each return. An expired wait interval is not a question timeout. Do not send `final`/`final_answer`, mark the task complete or end the turn while the question remains pending, even just to say “waiting for your answer”. Avoid busy polling, artificial shell work and repeated questionnaires. Keep dependent conversion, installation, draft generation, export and approval paused.
- **Answer or cancellation:** retain answered choices in session context and ask only still-required decisions after a partial answer. Preselection, elapsed time, prompt closure or an empty response never authorizes a default. If the user cancels or asks to stop, respect that intent without reopening the same prompt in a loop. If the user later explicitly accepts recommendations or delegates a choice, honor that new instruction within its scope and resume without repeating answered questions.
- **Unavailable, failed or invisible prompt:** if no permitted tool can sustain the question, or the user reports that it is invisible/closed, explain the limitation and recover the unanswered questions through a suitable native tool or a persistent text fallback. Follow host message/option restrictions. If text is the only supported handoff, put the actual question in the reply that yields to the user's next message; this ends the turn, not the unfinished task. Never replace it with only “questions sent”, claim completion or start dependent work. Do not duplicate a still-working prompt.

Dependency checks can run alongside intake. `fonts` requires FontTools, but can enumerate faces without HarfBuzz; explain `pending_dependency` as coverage checked, shaping not yet validated. Present those choices now and request the missing isolated setup separately. If even enumeration is unavailable, report the exact missing dependency and defer only the font list, not all other decisions. Never install packages or claim shaping passed to unblock a questionnaire.

## Project Context and Variants

Before asking for input inside an app project, inspect the active target/flavor, displayed app name, referenced logo/splash asset, splash implementation, theme resources and bundled brand fonts. Android examples include manifest/resource references, values-night and the actual post-launch view; iOS includes target display-name settings, asset appearances and launch/post-launch UI; Web includes the active page and its theme tokens. These are search hints, not assumed filenames. Do not use README branding or a launcher icon when the actual splash uses different assets. Resolve aliases and theme overrides. Do not run or install the app just to read these files. Distinguish a system launch screen from an in-app animated splash: generating Lottie does not establish OS launch-screen support or install it into the project. Read the actual integration point and report this boundary; integrate only when the task includes it.

Report a compact found/missing/conflicting inventory before drafting. If the project has no usable logo or visible app name, state exactly what was inspected and ask for the missing asset/name; do not substitute a package identifier, placeholder mark or invented branding. Missing theme/font data is reported separately so usable project evidence is not discarded. In a non-app or ambiguous repository, explain that project branding could not be established.

Prefer explicit current instructions, then verified target-specific project values, then user choices for unresolved items. Report the source of reused values. Existing SVG corner geometry alone is not a splash corner decision; use an actual layout radius or ask. Reuse a brand font only when its face/weight and name coverage are available. Otherwise list installed candidates. Name color may follow an existing splash text token; when absent, propose/choose a contrast-suitable color against the verified host background and explain that derivation. Brand accent alone does not determine text color. Ask when the background, intended locale/target or theme support is ambiguous. Never invent missing dark theme values.

When the actual splash supports both light and dark themes, default to two theme previews of the same choreography. Preserve brand colors unless the project supplies theme-specific artwork. If only the host background changes, the same transparent JSON can be inspected on both mattes. If exported name/background/artwork colors differ, create separate configs/JSON/HTML and validate both. A matte toggle is not a theme-specific export. Clearly label which target, theme and JSON each preview represents.

Offer an optional second choreography in the same question round as unresolved visual choices. Default to one arrangement unless requested. Keep geometry, font, color and wording fixed while comparing motion unless a design change is explicitly included. Compare a small number of distinct plans, not tiny parameter variations. Review motion first, then apply the selected plan across project themes, avoiding an unrequested styles × themes expansion. Use separate existing draft directories and the same CLI. A comparison page should embed/link each independent preview and its built-in download control; do not maintain another copied/Base64 animation payload or depend only on a relative file download link. No project-specific generator or new packaging layer is needed. Approval identifies both selected arrangement and theme files; do not mark all alternatives approved after one is chosen.

## Configuration

Paths resolve relative to the configuration file. The agent records reviewed artwork roles and its own motion reasoning; the user does not need to author this schema. Defaults are resolved and saved in the draft. Text-bearing configs require `wordmark.motion.user_request` recording the actual choice/delegation, including acceptance of the default; older configs need the existing decision recorded or a new question, not invented consent. Old `asset_roles_confirmed` configurations require explicit roles; a boolean cannot establish background scope.

A minimal config needs `source`, `artwork` and `motion`. For example, the following syntax holds an indivisible emblem still while its optional name enters. This is one design choice, not a default for other materials:

```json
{
  "source": "emblem.svg",
  "artwork": {"existing_wordmark": "absent", "backplate": {"mode": "none"}},
  "motion": {
    "rationale": "The dense interlocking emblem reads best intact; the name provides the entrance motion.",
    "tracks": [{
      "name": "Emblem",
      "target": "foreground",
      "reason": "Keep the interlocking silhouette stable and legible.",
      "keyframes": [{"time": 0, "offset": [0,0], "scale": 100, "opacity": 100}]
    }]
  },
  "wordmark": {"text": "Nova", "font": "/chosen/fonts/Brand-Bold.ttf", "color": "#203040",
               "motion": {"preset": "hop", "user_request": "Use the default hopping name."}},
  "canvas": {"width": 512, "height": 512, "padding": 32, "icon_width": 260}
}
```

Read [motion design](motion-design.md) for track schema and limitations. Explicit `motion.preset` values `whole-icon`, `backplate-first` and `static-backplate` remain supported for existing/simple compositions; they are not a default design menu. Whole-icon preserves composite opacity, while the other two keep plate geometry stationary with distinct foreground timing. `static-backplate` additionally requires `motion.user_request` quoting the actual request for first-frame visibility.

Default `source_background` is `preserve`, `export_background` is `{"type":"transparent"}`, and `preview_background` is `#f4f4f4`. SVG removal needs reviewed foreground artwork; no shape is guessed. Optional `app_purpose` is contextual text for the agent, not an automatic classifier. Set verified `app_name` when the supplied name is the application name; otherwise an explicit `wordmark.text` is used for the download filename. Canvas defaults to 512×512 with padding 32 and fps 30. Optional `icon_width` sets the final icon width; requests exceeding the motion envelope are rejected. Duration follows all tracks/name motion plus `hold` (default .35 seconds); an explicit duration must fit both. Legacy presets retain a minimum 2.4 seconds when duration is omitted.

For retained SVG backplates, use `artwork.backplate: {"mode":"embedded","element_ids":["icon-backplate"],"corners":{"mode":"preserve"}}`. A corner decision is required: include `corners: {"mode":"preserve"}` for confirmed preservation, or `corners: {"mode":"rounded","radius":20}` for an accepted radius. This plate remains inside the icon. It never makes the full canvas opaque. Read [roles and corner boundaries](backgrounds-and-svg.md) for generated plates and supported edits.

Omit `wordmark` for icon-only output. Otherwise `text`, resolved `font` and explicit `color` are required. Values come from verified project context or user choice; the loader no longer chooses a font/color. Defaults are real weight 700 and below-icon placement. Omitted size/gap follow the proportional layout below; explicit numeric values override them independently. `font_index` defaults to 0. Run `fonts` to enumerate distinct installed upright families covering the complete name at the requested weight; results include family, style, path, index and per-face coverage/shaping status. It validates shaping when HarfBuzz is available; otherwise candidates have `shaping: pending_dependency` and the report lists the missing dependency. Listing success only means choices are available; draft generation still requires the pinned dependencies and full shaping. The tool never downloads fonts and reports fewer/zero candidates honestly. Show 3–5 real options and a recommendation, not just “system bold”. Do not replace a supplied missing/incompatible font. Preserved source brand lettering needs `relationship: additional` before adding duplicate branding; pictorial letters use `artwork.existing_wordmark: symbols`.

### Wordmark Size and Spacing

When omitted, `wordmark.size` is 18% and `wordmark.gap` is 12% of the final complete icon width, including a retained backplate but excluding transparent source margins, canvas background and motion overshoot. A 400-unit icon therefore yields size 72 and gap 48. Explicit user/project size or gap takes precedence independently; do not insert arbitrary numbers merely because an example has them. Without `canvas.icon_width`, the tool solves the icon scale together with the shaped text and motion envelope, then records all resolved numeric values in the reproduction config.

`gap` means the settled icon's visible bottom to the settled text's visible top, not the baseline or the top of the jump envelope. Font size is an em size, not visible glyph height. The tool checks the actual outlines and reserves motion separately; it rejects overlap or overflow instead of silently enlarging the gap, shrinking a specified name or cropping. This replaces the previous motion-envelope gap meaning: regenerate old configs into a new draft and review the changed layout; never reuse previous approval.

These are composition units, not device pixels. Keep ratios when changing resolution; absolute pixel caps would change the design between equivalent exports. Check the complete name and intended display size in preview, especially long names and unusually wide/tall marks. If the result cannot fit or read well, explain the constraint and ask about canvas/layout changes; do not automatically wrap, truncate or alter chosen values.

Wordmark `motion` supports `preset: hop|rise|fade|gather|reveal`, `start`, `duration`, `stagger`, `stagger_window`, `amplitude` (em) and `anchor: baseline|center`. Use the [complete numbered menu](motion-design.md#text-motion-menu) before choosing. Record the actual selection, acceptance of defaults or delegation in `user_request`; never fabricate consent. Hop recommends baseline anchor, .62-second duration, .048-second stagger capped by .8 seconds, and .6em amplitude. Rise/fade/reveal use one shaped whole-line layer; gather preserves independent shaped units and defaults to simultaneous convergence. Other presets default to zero stagger. Start defaults to .2 seconds before the last icon track finishes, never before zero. Reserve selected motion bounds separately from settled spacing; do not apply hop-only validation to other effects.

Text is shaped once with HarfBuzz and outlined with FontTools for both preview and export. The same variable-font `wght` applies to shaping and outlines. Preserve kerning, combining marks and ligatures; independent clusters may enter separately, while connected scripts stay together. Whitespace affects spacing without creating a visible glyph. Supported text is single-line and single-direction. Missing glyphs, mixed direction, controls, color/bitmap fonts and oversized names require a decision; do not silently shrink, truncate, wrap or substitute. If a supplied face lacks 700, ask about its actual weight or another face rather than simulating bold.

For raster input, optional `image_options` contains `mode` (`auto|spline|polygon|pixel`), `fill` (`keep|white`), `alpha_threshold` (1..254), and `no_svgo` (boolean). Recoloring and alpha threshold must be confirmed. Unknown keys are rejected rather than ignored.

## Commands

Use the isolated interpreter and absolute installed script path:

```sh
python scripts/logo_lottie.py doctor
python scripts/logo_lottie.py inventory logo.svg
python scripts/logo_lottie.py fonts "Application Name" --weight 700 --limit 5
python scripts/logo_lottie.py inspect config.json
python scripts/logo_lottie.py draft config.json --output /output/draft-1 --player-package /chosen/runtime/web/node_modules/lottie-web
python scripts/logo_lottie.py size /output/draft-1/animation.json
python scripts/logo_lottie.py validate /output/draft-1 --playwright-package /chosen/runtime/web/node_modules/playwright
python scripts/logo_lottie.py approve /output/draft-1 --statement 'The user explicitly approved this preview and timing.' --visual-review
```

For rounded draft comparison, add `--reference-json /baseline/animation.json` to `validate`.

For raster inspect/draft, add `--image-converter /installed/image-to-svg/scripts/convert_image_to_svg.py`. Config preflight can trace a confirmed raster into temporary storage to check representability; it does not create a deliverable. Raw image inspection must precede unresolved choices.

CLI reports JSON: exit 0 means the command completed, exit 2 `needs_decision` means resolve the reported issue: ask for a substantive user decision, but correct agent-authored config/mapping mistakes locally when intent is known, exit 1 `failed` means report the execution failure before continuing. A draft is not approved. No existing draft is overwritten.

## JSON Size and Fidelity

Inspect the exported JSON, not the offline HTML (which also contains the player). `size animation.json` reports bytes, path/vertex counts, path data, keyframes and largest layers; path and keyframe categories can overlap for animated paths and must not be summed as a disjoint breakdown. Prefer an original compact SVG or faithful native cubic curves when geometry dominates. The converter preserves SVG curves; do not replace them with dense point sampling, lower tracing quality, remove holes/groups/names, or flatten curves to reduce bytes. Approximate path simplification or redrawing needs a separate user decision and source comparison. Do not promise a universal KB target.

Every inspect/draft applies exact numeric cleanup and conservative keyframe compaction before preview, download and hashing. Integral floats use integer notation when shorter. Numeric animation properties that remain constant become static; only redundant leading/trailing constant intervals are trimmed. Interior holds, actual changing intervals, easing, layer order, paths, names and paint are retained. Spatial tangents, expressions and unknown frame fields are not rewritten. Reports record before/after bytes and operations in `validation.json`; never modify an approved JSON afterward.

Decimal rounding is an approximation, not lossless compression. It is off by default. If the user accepts coordinate precision, record for example `"optimization": {"coordinate_precision": 3, "user_request": "Use three decimal places for coordinates."}`. Supported precision is 3–6. Only path vertices/handles and layer/group positions/anchors are rounded; colors, gradient stops, scales, angles, timeline times and easing retain precision. Error is measured in local coordinates and can grow under transforms; a small local rounding error alone does not prove visual equivalence. Compare measured savings at 3/4 decimals before choosing, and reuse a prior explicit choice without asking again.

Generate an unrounded baseline draft first (omit `optimization`), then a new rounded draft from the same resolved config with the accepted option. Run `validate` on the candidate with `--reference-json /baseline/animation.json`. It requires the matching baseline hash and matching canvas/timeline, compares sampled frames over black/white mattes plus alpha, and reports maximum channel error, affected pixels and RMSE. Measurements are not automatic visual approval. Inspect both previews at the intended display scale, review motion/detail/color/alpha, and obtain approval for that candidate. A rounded draft cannot be approved without comparison evidence. Regenerate/recompare after visual changes; Android/iOS need their own player checks.

Deliver plain `.json`. ZIP/gzip or `.lottie` containers do not satisfy a request for a smaller directly loadable JSON. No new optimizer service, global install or per-brand compression script is needed.

## Artifacts and Approval

- `animation.json`: native vector Lottie; no images or runtime fonts.
- `preview.html`: exact JSON and local pinned player embedded, replay, preview-only matte selector and offline JSON download. The download uses the immutable embedded JSON text with `application/json`, not the player's mutable runtime object. Downloading a draft does not approve it.
- The downloaded file uses the verified application name in lowercase with spaces, punctuation and repeated underscores collapsed to `_`, followed by `_loading.json`: `ExampleApp` becomes `exampleapp_loading.json`, and `Example App` becomes `example_app_loading.json`. Unicode letters are preserved without transliteration. `app_name` takes precedence over `wordmark.text` and does not add visible text. If neither establishes a usable name, ask before drafting; never use the source filename as the brand. Internal draft storage remains `animation.json`; download bytes are identical.
- `normalized.svg`: reviewed vector geometry for reproduction.
- `config.json`, `manifest.json`: resolved configuration and SHA-256 source/font/config/artifact hashes; font files are not copied.
- `validation.json`, `frames/`: structural/Web evidence with manual visual review pending.
- `PLAYER-LICENSE.txt`: Lottie Web license.
- `approval.json`: created only after actual user approval and manual inspection; records the approved hashes and statement.

Keep each revision in a new directory. A changed artifact fails the approval hash check. Retain the normalized SVG and resolved config for reproduction; raster reproduction also needs the original image/converter, and text reproduction needs the selected font. Files in system temporary directories are not a durable installation.

## Verification

`validate` loads a local file in Chromium with network blocked, compares embedded data to the JSON hash, samples every configured motion beat, checks visible bounds, rendered role entrance opacity, actual name vertical keyframes and authored open-stroke drawing lengths, rejects name/icon overlap, probes transparent content bounds and rounded corners, checks the rendered settled gap, replays to a stopped final frame, switches light/dark mattes, downloads JSON and verifies parsing/filename/SHA-256 against the delivery file, and writes screenshots. Structural layout bounds reject name/icon overlap throughout motion while keeping the configured gap tied to settled geometry. Corner probes apply to simple unstroked rectangles with radii at least 4 output pixels; smaller, stroked or arbitrary contours need visual review. Pixel probes do not prove every boundary. Playback success does not establish the intended background scope or grant user approval.

Run `python -m unittest discover -s tests -v`. Font-dependent tests use macOS fonts when present and otherwise report skips; integration tests accept `LOTTIE_PLAYER_PACKAGE`. Web end-to-end checks need the explicitly installed Playwright runtime. Native players remain `not_verified` in every first-version report.
