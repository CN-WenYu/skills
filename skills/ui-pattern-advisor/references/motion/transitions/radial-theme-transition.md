---
id: motion.transitions.radial-theme-transition
name: Radial Theme Transition
name_zh: 圆形主题切换
kind: motion-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [circular-theme-reveal, radial-reveal, 圆形揭示切换]
tags: [transition, theme, reveal, origin]
confidence: medium
last_reviewed: 2026-09-08
---

# Radial Theme Transition

## Definition

A new theme is revealed through a circular mask that expands from the control or location that triggered the change.

## Problem solved

It connects a global visual-state change to its cause and avoids an unexplained full-screen flash.

## Recognition cues

The reveal begins at the trigger, expands until it covers the viewport, and exposes a fully prepared alternate theme beneath it.

## Use when

Use for infrequent, deliberate theme changes when the trigger position is stable and the product supports expressive motion.

## Avoid when

Avoid for automatic system-theme changes, frequent toggling, large rendering costs, or environments without reliable masking.

## States and behavior

Prepare the destination theme, determine the trigger center and covering radius, expand the mask, then remove the temporary transition layer.

## Variants

Circular reveal, elliptical reveal, and a reduced-motion crossfade from the same trigger action.

## Platform notes

Masking and snapshot techniques differ; theme state must change atomically even if animation is cancelled or unavailable.

## Accessibility and performance

Use a short crossfade or instant change for reduced motion, maintain contrast throughout, and avoid capturing sensitive or stale content in snapshots.

## Common confusions

A generic radial reveal introduces content; this pattern specifically connects a theme-state change to its trigger.

## Related patterns

[Shared-element Image Expansion](shared-element-image-expansion.md).
