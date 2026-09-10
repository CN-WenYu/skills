---
id: motion.behavior.interruptible-motion
name: Interruptible Motion
name_zh: 可中断动效
kind: motion-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [interruptible-animation, animation-takeover, continuous-interruption, 动画中途接管]
tags: [motion, interruption, gesture, continuity]
confidence: high
last_reviewed: 2026-09-09
---

# Interruptible Motion

## Definition

An in-progress animation can be redirected, reversed, or taken over by new input from its current visual state.

## Problem solved

It prevents the interface from feeling locked while motion finishes and preserves continuity when users change intent quickly.

## Recognition cues

New input immediately affects the moving object, no jump occurs at takeover, and the next transition begins with the current position and relevant velocity.

## Use when

Use for interactive navigation, scrolling, draggable elements, and frequently toggled states where input may arrive before settling completes.

## Avoid when

Avoid when interruption would leave an invalid transactional state, when motion is merely decorative and can be cancelled outright, or when the framework cannot preserve a coherent state model.

## States and behavior

Idle, animating, interrupted, user-controlled, redirected, and settled states; keep semantic state separate from presentation, sample the current presentation state, and define cancellation and completion exactly once.

## Variants

Gesture takeover, reversible transition, retargetable spring, cancel-to-current-state, and immediate reduced-motion completion.

## Platform notes

Framework interruption semantics vary; verify whether animation state, model state, and input recognizers remain synchronized during rapid reversals.

## Accessibility and performance

Respect reduced-motion preferences, preserve focus and announcements through interruption, and avoid accumulating concurrent animations or completion callbacks.

## Common confusions

An animation may be cancellable yet still jump to an endpoint; interruptible motion preserves a coherent continuation from the visible state.

## Related patterns

[Gesture-driven Transition](../../interactions/navigation/gesture-driven-transition.md), [Collision and Spring Response](../physics/collision-and-spring-response.md), and [Partial Text Transition](../transitions/partial-text-transition.md).
