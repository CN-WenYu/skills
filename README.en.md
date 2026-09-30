# CN-WenYu Skills

[![skills.sh](https://skills.sh/b/CN-WenYu/skills)](https://skills.sh/CN-WenYu/skills)

English | [Simplified Chinese](README.md)

Reusable workflows and project-rule skills for AI coding agents. Each skill has a focused use case and can be installed and invoked on demand, without memorizing long prompts.

## Quick Start

List the installable skills:

```bash
npx skills@latest add CN-WenYu/skills --list
```

Install one skill for Codex:

```bash
npx skills@latest add CN-WenYu/skills \
  --skill decision-review \
  --agent codex \
  --yes
```

Install every skill for every agent detected by the CLI:

```bash
npx skills@latest add CN-WenYu/skills --all
```

Skills install into the current project by default. Use `--global` for a user-level installation or `--copy` to copy files instead of creating symlinks. See `npx skills@latest --help` for the complete CLI reference.

## Skill Catalog

| Skill | Use it when | Primary outcome |
| --- | --- | --- |
| [`problem-framing`](skills/problem-framing/SKILL.md) | A problem is vague, contradictory, or constrained by an existing practice | Goals, facts, assumptions, constraints, and the key next question |
| [`decision-review`](skills/decision-review/SKILL.md) | Architecture, product, or priority options have material tradeoffs | A conditional recommendation, key risks, and a minimal validation experiment |
| [`learn-clearly`](skills/learn-clearly/SKILL.md) | You need to understand a technical concept or mechanism | An intuitive explanation, technical model, and self-check questions |
| [`deconstruct-examples`](skills/deconstruct-examples/SKILL.md) | You need to analyze a page, product, workflow, proposal, or code example | Transferable principles, an operating checklist, and a low-risk trial |
| [`evidence-research`](skills/evidence-research/SKILL.md) | You need to verify facts, compare cases, or transfer an idea across domains | Traceable evidence, qualified conclusions, and open questions |
| [`project-rules-progressive-disclosure`](skills/project-rules-progressive-disclosure/SKILL.md) | You need to add, organize, or split durable project rules | A lightweight entrypoint and focused, on-demand reference documents |
| [`svg-logo-to-lottie`](skills/svg-logo-to-lottie/SKILL.md) | You need splash motion designed for the meaning of an image or SVG logo | Agent-authored choreography, genuine bold names, reusable tracks and Lottie previews |
| [`image-to-svg`](skills/image-to-svg/SKILL.md) | You need to convert PNG, JPEG, or WebP artwork into editable SVG paths without assuming a fixed background policy | Source-preserving defaults, confirmed visual changes, and color/alpha verification |
| [`ui-pattern-advisor`](skills/ui-pattern-advisor/SKILL.md) | You need to identify, explain, or choose UI components, interactions, or motion | Canonical terms, disambiguation, and contextual recommendations |
| [`ui-knowledge-curator`](skills/ui-knowledge-curator/SKILL.md) | You want to persist UI knowledge from images, links, or text | A deduplicated, classified, and validated UI knowledge library |

## Using An Installed Skill

Explicitly name the skill and describe the task:

```text
Use $decision-review to compare these two architecture options.
Use $problem-framing to clarify why this bug is difficult to reproduce.
Use $evidence-research to verify this technical claim.
Use $ui-pattern-advisor to identify this interaction and recommend the right component.
Use $ui-knowledge-curator to organize this material into the UI knowledge library.
Use $image-to-svg to convert this raster artwork into editable SVG paths with evidence-based background handling.
```

Agents that support automatic discovery can also select a skill from task semantics. Explicit invocation is best when you want to choose the thinking mode yourself.

## Logo Animation And Image Conversion

Inside an app project, requests such as “make a splash animation”, “create an app opening animation” or “animate the startup logo” trigger this skill without supplied SVG or Lottie terminology. It first inspects the project and explicitly reports missing logo, display-name or theme information before requesting the necessary input. It does not invent branding.

Outside a project, supply a logo and app name to start. After inspecting the artwork, the skill presents actionable questions and font choices instead of only saying it is waiting for confirmation. FontTools can list installed faces without HarfBuzz, with shaping explicitly marked as pending. Installation approval is separate from visual choices; missing animation dependencies do not suppress intake questions.

Raster input requires both `svg-logo-to-lottie` and `image-to-svg`; SVG input only requires the animation skill. Install each by its `--skill` name. An explicit converter script path connects the skills without assuming adjacent installation directories.

The agent analyzes the actual artwork, name, app context and reading hierarchy together before proposing a coherent icon/text composition. Text supports whole-line or shaped-unit timelines with 2D offsets, scale and opacity. Hop, rise, fade, spacing convergence and directional reveal remain optional recipes, not a mandatory questionnaire or a universal hop recommendation. Connected writing, ligatures and combining marks remain intact. Light beams, generic masks and text exit loops are not supported; a masked reveal must not be described as a scanning light.

Prefer the host Agent's native question tool and adapt to its numbering, free-text support and option limits: do not duplicate built-in numbers or Custom/Other entries, or repeat options in the prompt body. Without a usable tool, use a short numbered text choice when helpful and invite other descriptions. Ask only material unresolved questions; accepting a combined proposal that includes text also resolves its motion. Default to one draft without making preview count mandatory. Async questions require actual answers; timeout does not accept recommendations. Failed or invisible prompts need a visible text fallback.

First read the active project's logo, name, fonts and splash theme configuration. Reuse reliable values; bundle unresolved corner/color questions and a small relevant selection of installed fonts. An accent color alone does not determine name color. Explicit requests to confirm unspecified visuals, fidelity changes and missing dependency installation retain their authorization boundaries. Text configs must explicitly select a preset or authored tracks; add `preset: hop` to an old config only when its recorded decision actually chose hops, not because a field is missing.

Omitted name size and gap use 18% and 12% of the final icon width: a 400-unit icon yields size 72 and gap 48. Gap measures settled visible edges; motion space is checked separately. Explicit user/project values take precedence. Every offline preview includes a JSON download whose content is checked against the delivery file.
Downloads use the verified application name in lowercase underscore form with a `_loading.json` suffix, for example `Example App` becomes `example_app_loading.json`. If no reliable app name exists, ask before drafting instead of using the asset filename.

When the actual splash supports light/dark themes, provide both theme previews by default, with separate JSON when exported colors differ. Offer a second choreography as an opt-in comparison instead of multiplying variants automatically. Explain visual sources and reuse the selected text effect or explicit delegation without repeated questions; a recommended default is not an answer.

Supports independent tracks, open-stroke drawing and basic vector gradients; no automatic raster gradient fitting or complex foreground extraction. Use isolated Python and pinned Lottie Web/Playwright; raster conversion also needs VTracer and an SVG renderer. Dependencies are not installed automatically. Current validation covers Web; Android/iOS require separate checks.

Exports compact redundant keyframes and numeric notation by default, with a JSON size breakdown. Coordinate rounding requires an explicit choice and preserves paint, timing and easing precision. Approximate versions need Web comparison against the unrounded baseline before approval; delivery remains plain JSON.

Read [motion design and limits](skills/svg-logo-to-lottie/references/motion-design.md), [backgrounds and corners](skills/svg-logo-to-lottie/references/backgrounds-and-svg.md), [text configuration and export](skills/svg-logo-to-lottie/references/lottie-export.md), or [image conversion](skills/image-to-svg/references/conversion.md) as needed.

Multiple versions use `compare`: a top version selector shows one full-width preview at a time, with a separate-open link. Players are not tiled by default. Keep the comparison page and draft directories in their relative locations when sharing.

## Maintaining Skills

Each skill is a directory and must include `SKILL.md`:

```text
skills/
  <skill-id>/
    SKILL.md
    agents/openai.yaml  # Optional UI name, description, and invocation prompt
    scripts/            # Optional reusable executable helpers
    references/         # Optional on-demand reference material
    assets/             # Optional assets used by generated output
```

The YAML front matter in `SKILL.md` must contain a `name` matching the directory and a clear, discriminating `description`. Keep only decision-changing guidance in the body. Put long, low-frequency workflows and reference material in `references/` and state when to read them.

`ui-pattern-advisor` is the single owner of UI knowledge. Its cards are organized by component, interaction, and motion and loaded through on-demand indexes; `ui-knowledge-curator` maintains those cards and writes to the source repository only when the user explicitly asks to collect or organize material.

## Publishing And Validation

1. Update files under `skills/<skill-id>/` and check names, descriptions, and reference paths.
2. Use the skill validator available to the repository to check front matter and unfinished scaffolding.
3. Commit and push to the default branch of `CN-WenYu/skills`. Installation commands read the remote version only.
4. Run `npx skills@latest add CN-WenYu/skills --list` to confirm discoverability; install a specific skill when an end-to-end check is needed.

Public repositories can be installed directly. Private repositories require the installer to have the corresponding GitHub access and credentials. See the [skills.sh documentation](https://www.skills.sh/docs) and [open-source implementation](https://github.com/vercel-labs/skills) for CLI behavior.

## Updating Or Removing An Installed Skill

```bash
npx skills@latest update project-rules-progressive-disclosure
npx skills@latest remove project-rules-progressive-disclosure
```
