---
id: motion.physics.ripple-distortion
name: Ripple Distortion
name_zh: 水波扭曲
kind: motion-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [water-ripple-distortion, image-ripple, ripple-warp, 水波形变]
tags: [image, ripple, distortion, feedback]
confidence: medium
last_reviewed: 2026-09-10
---

# Ripple Distortion

## Definition

A localized wave-like deformation propagates through an image from an input point or defined origin, then decays back to the undistorted state.

## Problem solved

It provides expressive spatial feedback or a material-like response when distortion fits the content and brand tone.

## Recognition cues

Displacement radiates from an origin, amplitude weakens over distance or time, the image remains recognizable, and the surface returns without permanent geometry change.

## Use when

Use sparingly for water-related imagery, experimental showcases, or a bounded interaction where material response carries meaning.

## Avoid when

Avoid on text, faces, precision imagery, comparison tasks, frequent controls, or whenever distortion reduces recognition or creates discomfort.

## States and behavior

Resting, triggered, propagating, decaying, retriggered, and restored states; clamp amplitude and radius, define overlap behavior, and stop cleanly when input ends or motion is reduced.

## Variants

Tap-origin ripple, pointer-following wave, ambient low-amplitude ripple, and single-axis wave distortion.

## Platform notes

Shader and displacement support varies; use existing rendering primitives and provide an undistorted fallback when the effect is unsupported or too costly.

## Accessibility and performance

Disable or simplify under reduced motion, never distort essential controls or text, limit render resolution and overlapping waves, and verify on representative hardware.

## Common confusions

A standard ripple confirms a press through color or opacity; ripple distortion warps image sampling and should not replace required control feedback.

## Related patterns

[Velocity-driven Deformation](velocity-driven-deformation.md), [Rubber-band Overscroll](rubber-band-overscroll.md), and [Glare Hover](../attention/glare-hover.md).
