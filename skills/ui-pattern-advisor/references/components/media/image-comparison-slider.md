---
id: components.media.image-comparison-slider
name: Image Comparison Slider
name_zh: 图片前后对比滑块
kind: component
term_status: common-informal
platforms: [ios, android, web]
aliases: [before-after-slider, before-and-after-slider, comparison-slider, 前后对比滑块]
tags: [image, comparison, slider, reveal]
confidence: high
last_reviewed: 2026-09-10
---

# Image Comparison Slider

## Definition

A divider reveals different portions of two spatially aligned images so users can compare the same scene or subject before and after a change.

## Problem solved

It makes localized visual differences easier to inspect than switching between two full images.

## Recognition cues

Two images occupy one fixed frame, a labeled divider separates their visible regions, and moving the handle changes only the reveal boundary.

## Use when

Use for aligned before-and-after states such as restoration, editing, construction, treatment, or rendering comparisons.

## Avoid when

Avoid when images differ in crop, camera position, scale, or subject; when the comparison is conceptual rather than spatial; or when labels alone cannot clarify the states.

## States and behavior

Idle, focused, dragging, positioned, and reset states; constrain the divider to the image bounds, preserve a stable frame, and keep both state labels understandable at every position.

## Variants

Horizontal divider, vertical divider, tap-to-position, keyboard-stepped handle, and side-by-side reduced-motion fallback.

## Platform notes

Touch requires a generous handle that coexists with page scrolling; desktop should support pointer drag, focus, arrow keys, and direct track activation when expected.

## Accessibility and performance

Expose the handle as an adjustable control with value and state labels, provide an equivalent non-drag comparison, and avoid decoding images during movement.

## Common confusions

A carousel switches between separate items; an image comparison slider continuously reveals aligned portions of two corresponding images.

## Related patterns

[Mask Reveal](../../interactions/media/mask-reveal.md) and [Pixelated Image Transition](../../motion/transitions/pixelated-image-transition.md).
