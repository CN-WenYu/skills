---
id: motion.attention.image-trail
name: Image Trail
name_zh: 图片拖尾
kind: motion-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [cursor-image-trail, pointer-trail-gallery, image-echo-trail, 图片轨迹]
tags: [image, pointer, trail, showcase]
confidence: medium
last_reviewed: 2026-09-10
---

# Image Trail

## Definition

Short-lived image instances appear along pointer or gesture movement and fade, shrink, or dissolve after a bounded lifetime.

## Problem solved

It turns motion through an open showcase into a temporary visual sequence that can expose multiple works or reinforce pointer movement.

## Recognition cues

Movement distance or time emits discrete images, each instance has a finite lifecycle, the number of visible trails is capped, and old instances leave no interactive residue.

## Use when

Use for spacious, infrequent, pointer-oriented portfolios, galleries, or campaign surfaces where temporary imagery is the primary experience.

## Avoid when

Avoid on dense controls, reading surfaces, touch-first workflows without an intentional drag equivalent, or when trails obscure navigation and content.

## States and behavior

Idle, moving, emitted, fading, recycled, and cleared states; emit by bounded distance or cadence, rotate through prepared assets predictably, cap instances, and clear on exit or interruption.

## Variants

Alternating gallery trail, repeated single-image echo, velocity-scaled trail, drag-only trail, and tap-based static gallery fallback.

## Platform notes

Desktop pointer movement is the common trigger; touch should use a deliberate gesture or a separate gallery presentation rather than simulating hover continuously.

## Accessibility and performance

Offer a stable way to browse every image, remove repeated movement under reduced motion, reuse rendered instances, and avoid decoding or allocating assets per move event.

## Common confusions

A cursor trail renders decorative particles or strokes; an image trail uses meaningful image assets that still need a complete non-motion presentation.

## Related patterns

[Glare Hover](glare-hover.md), [Layered Parallax](../depth/layered-parallax.md), and [Center-focus Scaling](center-focus-scaling.md).
