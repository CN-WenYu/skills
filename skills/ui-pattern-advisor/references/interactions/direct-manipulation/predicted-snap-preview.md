---
id: interactions.direct-manipulation.predicted-snap-preview
name: Predicted Snap Preview
name_zh: 预测落点预览
kind: interaction-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [landing-preview, snap-target-preview, projected-snap, 落点预览]
tags: [gesture, snap, preview, carousel]
confidence: medium
last_reviewed: 2026-09-09
---

# Predicted Snap Preview

## Definition

During direct manipulation, the interface previews the discrete target where the moving content is currently expected to settle.

## Problem solved

It lets users correct position or velocity before release when snapping would otherwise make the result uncertain.

## Recognition cues

One candidate target gains emphasis while dragging, the candidate may change with projected motion, and the final state resolves to the last valid target.

## Use when

Use for carousels, rulers, timelines, or selectors with meaningful snap targets and a predictable projection model.

## Avoid when

Avoid when every position is valid, targets are too dense to distinguish, prediction changes erratically, or the preview would be mistaken for a committed value.

## States and behavior

Idle, dragging, candidate acquired, candidate changed, released, settled, and cancelled states; apply hysteresis to candidate changes and keep preview logic consistent with final snapping.

## Variants

Highlighted slot, insertion marker, ghosted item, scale emphasis, and labeled target preview.

## Platform notes

Projection should match the platform's scroll or gesture physics where possible; pointer dragging and touch flicks may need different velocity weighting.

## Accessibility and performance

Announce candidate changes without excessive chatter, offer step controls for exact selection, and update only when the predicted target changes.

## Common confusions

Snap preview communicates a likely result before commitment; snapping alone only constrains the final resting position.

## Related patterns

[Velocity-based Slider Snap](velocity-based-slider-snap.md), [Gesture Axis Lock](gesture-axis-lock.md), and [Center-focus Scaling](../../motion/attention/center-focus-scaling.md).
