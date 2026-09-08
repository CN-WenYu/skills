# Knowledge Card Schema

This library stores one canonical card for each independently selectable UI concept. Directory placement answers where a concept primarily belongs; aliases and links provide secondary discovery paths.

## Required Front Matter

```yaml
---
id: motion.transitions.shared-element-image-expansion
name: Shared-element Image Expansion
name_zh: 共享元素图片展开
kind: motion-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [shared element expansion]
tags: [transition, continuity, image]
confidence: medium
last_reviewed: 2026-09-08
---
```

Allowed values:

- `kind`: `component`, `interaction-pattern`, `motion-pattern`, `feedback-pattern`, `principle`
- `term_status`: `standard`, `platform-specific`, `common-informal`, `descriptive`
- `confidence`: `high`, `medium`, `low`
- `platforms`: `cross-platform`, `ios`, `android`, `web`

Use lowercase kebab-case for filenames and tags where an established English spelling is available. English aliases use lowercase natural language; Chinese aliases preserve their normal script. IDs use dot-separated directory segments followed by the filename stem and must be globally unique.

## Required Sections

Every card contains these headings in this order:

1. `Definition`
2. `Problem solved`
3. `Recognition cues`
4. `Use when`
5. `Avoid when`
6. `States and behavior`
7. `Variants`
8. `Platform notes`
9. `Accessibility and performance`
10. `Common confusions`
11. `Related patterns`

Keep each section decision-oriented. Do not add source links, copied article text, screenshots, or claims that cannot be qualified through term status and confidence.

## Primary Home

- `components/` owns controls and views with stable semantics, structure, and state.
- `interactions/` owns user actions and multi-state workflows.
- `motion/` owns temporal behavior reusable across components.
- A component-specific motion remains with the component when it cannot be selected independently from that component.

Keep one canonical home. Cross-link related cards rather than copying their definitions.

## Splitting

Create a separate card when a concept has a distinct user problem, state model, use/avoid decision, accessibility contract, or platform behavior. Keep cosmetic variants together. Promote a family to a directory with a README when it contains at least three independent patterns or needs a selection guide. Do not create empty category directories.
