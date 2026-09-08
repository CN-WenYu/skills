---
id: components.selection.expanding-tag-selection
name: Expanding Tag Selection
name_zh: 标签展开选择
kind: component
term_status: descriptive
platforms: [ios, android, web]
aliases: [expanding-chip-selection, selectable-tag-expansion, 标签选择展开]
tags: [selection, tag, chip, expansion]
confidence: medium
last_reviewed: 2026-09-08
---

# Expanding Tag Selection

## Definition

A selectable tag or chip expands on selection to expose contextual detail or a nearby secondary action.

## Problem solved

It confirms selection while revealing information that is relevant only to the active item.

## Recognition cues

The selected tag changes footprint, surrounding tags reflow predictably, and the newly revealed content remains visually attached to it.

## Use when

Use for small tag sets where selection legitimately unlocks concise context or one secondary action.

## Avoid when

Avoid in dense wrapping lists, frequently changing filters, or when expansion would move the selected item offscreen.

## States and behavior

Unselected, selected, expanded, and collapsed states must remain deterministic; decide whether selecting another tag transfers expansion.

## Variants

Inline detail, appended action, width expansion, and a stable overlay that avoids reflow.

## Platform notes

Use established chip or token semantics where available and preserve localization-driven intrinsic sizing.

## Accessibility and performance

Expose selected and expanded states, retain adequate touch size, and reduce layout travel under reduced motion.

## Common confusions

A disclosure chip reveals attached content; a filter chip may only toggle inclusion and should not expand without purpose.

## Related patterns

[Animated Text Disclosure](../disclosure/animated-text-disclosure.md) and [Staggered Bulk Selection](../../interactions/selection/staggered-bulk-selection.md).
