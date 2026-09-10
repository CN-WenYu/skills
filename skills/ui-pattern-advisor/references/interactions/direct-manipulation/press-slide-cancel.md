---
id: interactions.direct-manipulation.press-slide-cancel
name: Press-slide Cancel
name_zh: 按压滑出取消
kind: interaction-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [slide-out-to-cancel, drag-out-cancel, button-slip-cancel, 按钮滑出取消]
tags: [gesture, button, cancellation, touch]
confidence: medium
last_reviewed: 2026-09-09
---

# Press-slide Cancel

## Definition

A press remains provisional while held and is cancelled when the pointer or finger leaves the control before release.

## Problem solved

It lets users retract an accidental press without requiring a separate undo after the command fires.

## Recognition cues

The control shows a pressed state on contact, removes or changes that state outside its active region, and commits only on a valid release.

## Use when

Use for touch or pointer controls whose action should occur on release and where sliding away is a familiar, low-cost correction.

## Avoid when

Avoid when the action begins on press, when leaving the bounds is part of another gesture, or when cancellation would be invisible or unreliable.

## States and behavior

Idle, pressed inside, moved outside, re-entered, committed, and cancelled states; use a documented tolerance region and fire the action at most once on valid release.

## Variants

Strict bounds, expanded cancellation boundary, re-entry allowed, and slide toward an explicit cancel target.

## Platform notes

Prefer native control tracking semantics when they already provide cancellation; custom gestures must arbitrate with scrolling and pointer capture.

## Accessibility and performance

Keep a conventional activation path for keyboard and assistive technology, preserve touch target size, and never require sliding as the only way to avoid a destructive action.

## Common confusions

This cancels before activation; undo reverses an action after it has already committed.

## Related patterns

[Gesture Axis Lock](gesture-axis-lock.md) and [Gesture-driven Transition](../navigation/gesture-driven-transition.md).
