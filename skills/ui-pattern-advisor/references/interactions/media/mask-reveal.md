---
id: interactions.media.mask-reveal
name: Mask Reveal
name_zh: 遮罩揭示
kind: interaction-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [interactive-mask-reveal, spotlight-reveal, scratch-reveal, 遮罩探索]
tags: [image, reveal, mask, direct-manipulation]
confidence: medium
last_reviewed: 2026-09-10
---

# Mask Reveal

## Definition

A movable or progressively changing mask exposes part of a hidden image or layer while the surrounding content remains covered or shows another layer.

## Problem solved

It supports exploration, comparison, or staged discovery without replacing the entire image at once.

## Recognition cues

A bounded aperture or erased region follows input, revealed and covered regions remain spatially registered, and the reveal may reset or persist according to the task.

## Use when

Use when the hidden layer's spatial relationship to the visible image matters and exploration adds meaning rather than delay.

## Avoid when

Avoid when key information must be immediately visible, precise movement is required to discover content, or a simple labeled comparison would communicate more clearly.

## States and behavior

Covered, revealing, partially revealed, fully revealed, reset, and cancelled states; clamp the reveal to image bounds, preserve continuity during movement, and define whether progress is temporary or committed.

## Variants

Circular spotlight, resizable aperture, scratch-away mask, directional wipe, and press-and-hold reveal.

## Platform notes

Pointer hover may preview a temporary mask, but touch needs drag, press, or explicit controls that do not conflict with scrolling and zooming.

## Accessibility and performance

Provide a reveal-all or alternate comparison action, describe both layers semantically, respect reduced motion, and avoid high-resolution mask updates that exceed the frame budget.

## Common confusions

An image comparison slider exposes two aligned images with a single divider; mask reveal uses an aperture or accumulated region that may move in more than one dimension.

## Related patterns

[Image Comparison Slider](../../components/media/image-comparison-slider.md), [Sticker Peel](sticker-peel.md), and [Radial Theme Transition](../../motion/transitions/radial-theme-transition.md).
