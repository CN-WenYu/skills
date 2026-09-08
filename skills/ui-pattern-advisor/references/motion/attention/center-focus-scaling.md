---
id: motion.attention.center-focus-scaling
name: Center-focus Scaling
name_zh: 中心聚焦缩放
kind: motion-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [center-emphasis-scaling, 中心项放大]
tags: [attention, carousel, focus, scale]
confidence: medium
last_reviewed: 2026-09-08
---

# Center-focus Scaling

## Definition

The item nearest a focus position grows while neighboring items remain smaller, usually as a list or carousel moves.

## Problem solved

It makes the active or most selectable item visually legible without requiring a separate selection marker.

## Recognition cues

Scale changes continuously with distance from a stable focus point and reaches its maximum at that point.

## Use when

Use for bounded carousels, pickers, or media browsing where one centered item is meaningfully active.

## Avoid when

Avoid when several items must be compared equally, text reflow would occur, or scaling would obscure neighbors.

## States and behavior

Measure each item's distance from focus, map it to a bounded scale, and synchronize the selected state at rest.

## Variants

Center scale, center scale plus opacity, and scale plus depth elevation.

## Platform notes

Prefer existing snapping or picker semantics and treat scale as reinforcement, not the only selected-state signal.

## Accessibility and performance

Expose selection semantically, preserve stable layout bounds, and reduce or remove continuous scaling under reduced motion.

## Common confusions

Cover flow adds rotation and overlap; center-focus scaling can remain flat and non-overlapping.

## Related patterns

[Velocity-based Slider Snap](../../interactions/direct-manipulation/velocity-based-slider-snap.md) and [Magnetic Attraction](magnetic-attraction.md).
