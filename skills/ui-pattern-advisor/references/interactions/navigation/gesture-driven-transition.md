---
id: interactions.navigation.gesture-driven-transition
name: Gesture-driven Transition
name_zh: 手势驱动转场
kind: interaction-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [interactive-transition, gesture-controlled-navigation, interactive-back-gesture, edge-swipe-back, 交互式转场, 跟手返回]
tags: [gesture, navigation, transition, interactive, back]
confidence: high
last_reviewed: 2026-09-08
---

# Gesture-driven Transition

## Definition

A navigation transition whose progress follows a continuous user gesture and can complete or cancel from its current state.

## Problem solved

It makes spatial navigation directly manipulable and keeps the result predictable before commitment.

## Recognition cues

View position tracks the finger or pointer, the actual destination is progressively revealed, progress is reversible, and release outcome depends on distance, velocity, and direction.

## Use when

Use for established navigation or dismissal gestures with a clear axis, destination, and cancellation path.

## Avoid when

Avoid when the gesture conflicts with scrolling or system navigation, hides the only route, or has no accessible alternative.

## States and behavior

Idle, tracking, committed, cancelled, and settling states; capture stable start and destination states before tracking, derive progress from movement, then settle from the current visual position using velocity and thresholds.

## Variants

Edge-swipe back, full-screen swipe back, swipe-to-close, interactive sheet dismissal, and gallery paging.

## Platform notes

Integrate with system navigation, back, scroll, and gesture arbitration rather than replacing them casually. Edge regions, system back gestures, and nested horizontal scrolling need explicit precedence.

## Accessibility and performance

Provide buttons or system actions for the same outcome, preserve focus on cancellation, and keep the transition interruptible.

## Common confusions

A gesture-triggered transition starts after a swipe; a gesture-driven transition continuously follows gesture progress.

## Related patterns

[Shared-element Image Expansion](../../motion/transitions/shared-element-image-expansion.md), [Gesture Axis Lock](../direct-manipulation/gesture-axis-lock.md), and [Interruptible Motion](../../motion/behavior/interruptible-motion.md).
