---
id: motion.transitions.pixelated-image-transition
name: Pixelated Image Transition
name_zh: 像素化图片转场
kind: motion-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [pixel-transition, block-dissolve, pixel-dissolve, 像素转场]
tags: [image, transition, pixel, dissolve]
confidence: medium
last_reviewed: 2026-09-10
---

# Pixelated Image Transition

## Definition

One image is replaced by another through an ordered progression of pixel-like blocks, tiles, or cells rather than a uniform fade or wipe.

## Problem solved

It gives a related image change a distinctive temporal structure while preserving a deterministic start and final image.

## Recognition cues

The frame is divided into a stable grid or block system, cells switch or dissolve in a defined order, and the final state contains only the destination image.

## Use when

Use for occasional creative showcases, themed galleries, or product imagery where stylized replacement supports the visual language.

## Avoid when

Avoid when users must continuously compare differences, when the effect delays frequent browsing, or when image identity and detail must remain clear throughout the transition.

## States and behavior

Source, transitioning, interrupted, completed, and failed states; determine cell size and order before playback, avoid random reordering during one run, and resolve cleanly to one valid image.

## Variants

Ordered tile wipe, pixel dissolve, block mosaic replacement, center-out propagation, and reduced-motion crossfade.

## Platform notes

Implementation may use masks, shaders, canvas, compositing, or prepared frames; choose the simplest primitive supported reliably by the existing stack.

## Accessibility and performance

Respect reduced motion, keep image semantics stable, cap cell count and overdraw, and avoid loading or decoding the destination during animation.

## Common confusions

Pixelation applied to one image is a static treatment; this pattern uses pixel-like regions to communicate a transition between states.

## Related patterns

[Image Comparison Slider](../../components/media/image-comparison-slider.md), [Mask Reveal](../../interactions/media/mask-reveal.md), and [Shared-element Image Expansion](shared-element-image-expansion.md).
