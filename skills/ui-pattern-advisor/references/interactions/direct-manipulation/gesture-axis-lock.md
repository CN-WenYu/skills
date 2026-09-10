---
id: interactions.direct-manipulation.gesture-axis-lock
name: Gesture Axis Lock
name_zh: 手势方向锁定
kind: interaction-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [directional-lock, axis-locking, direction-lock, 手势轴锁定]
tags: [gesture, direction, arbitration, scrolling]
confidence: high
last_reviewed: 2026-09-09
---

# Gesture Axis Lock

## Definition

After a gesture passes an intent threshold, movement is assigned to one dominant axis or recognizer for the rest of that gesture.

## Problem solved

It prevents diagonal input noise from causing horizontal controls and vertical scrolling to respond at the same time.

## Recognition cues

Early movement is undecided, one direction wins after a threshold, off-axis displacement is suppressed, and ownership remains stable until release or cancellation.

## Use when

Use where nested or adjacent interactions compete across axes, such as a horizontal chart inside a vertically scrolling page.

## Avoid when

Avoid for genuinely free two-dimensional manipulation, before enough movement reveals intent, or when the platform recognizer already resolves the conflict correctly.

## States and behavior

Idle, undecided, horizontal lock, vertical lock, and ended states; combine distance and direction thresholds, keep the decision stable, and hand off only through supported gesture arbitration.

## Variants

Hard axis lock, angle-cone lock, dominant recognizer selection, and limited off-axis damping.

## Platform notes

Coordinate with native scroll views, nested scrolling, back gestures, and gesture-recognizer precedence instead of duplicating their ownership model.

## Accessibility and performance

Provide non-gesture controls for the same task, avoid thresholds that exclude limited motor control, and keep recognition work constant-time during movement.

## Common confusions

Axis lock resolves direction for the current gesture; snapping chooses a final destination after or during movement.

## Related patterns

[Gesture-driven Transition](../navigation/gesture-driven-transition.md), [Predicted Snap Preview](predicted-snap-preview.md), and [Chart Zoom](../data-visualization/chart-zoom.md).
