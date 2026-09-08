---
id: interactions.direct-manipulation.velocity-based-slider-snap
name: Velocity-based Slider Snap
name_zh: 速度感知滑杆吸附
kind: interaction-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [velocity-aware-slider-snap, momentum-slider-snap, 速度吸附滑杆]
tags: [slider, velocity, snap, gesture]
confidence: medium
last_reviewed: 2026-09-08
---

# Velocity-based Slider Snap

## Definition

A discrete slider chooses its final stop from current position and release velocity, then settles to a valid value.

## Problem solved

It makes a discrete control respond naturally to flicks while guaranteeing a valid final selection.

## Recognition cues

Slow releases choose the nearest stop, faster releases may advance in the gesture direction, and the thumb never rests between values.

## Use when

Use for a small ordered range whose steps are meaningful and where gesture momentum improves traversal.

## Avoid when

Avoid for precise continuous values, destructive settings, dense scales, or controls where velocity could cause surprising jumps.

## States and behavior

Idle, dragging, released, settling, and committed states; clamp values, define position and velocity thresholds, and update the final semantic value once.

## Variants

Nearest-stop snap, one-step flick, multi-step projection, and spring or eased settling.

## Platform notes

Extend the platform slider only when native behavior cannot express the required discrete task and full accessibility remains intact.

## Accessibility and performance

Provide increment and decrement actions, announce the final value, and disable momentum-based travel for reduced motion when appropriate.

## Common confusions

Scroll snapping positions content; this pattern commits a slider's discrete semantic value.

## Related patterns

[Gesture-driven Transition](../navigation/gesture-driven-transition.md) and [Center-focus Scaling](../../motion/attention/center-focus-scaling.md).
