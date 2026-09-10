---
id: interactions.media.sticker-peel
name: Sticker Peel
name_zh: 贴纸揭角
kind: interaction-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [peel-to-reveal, corner-peel, page-peel, 揭角交互]
tags: [image, reveal, gesture, direct-manipulation]
confidence: medium
last_reviewed: 2026-09-10
---

# Sticker Peel

## Definition

A draggable corner or edge folds back a top visual layer to reveal content beneath it, then either completes or restores the layer according to a threshold.

## Problem solved

It gives a layered reveal a tangible spatial model and allows users to preview before committing.

## Recognition cues

A peel handle or corner establishes the affordance, fold geometry follows the drag, the underside and revealed content remain coherent, and release resolves predictably.

## Use when

Use for occasional promotional, collectible, onboarding, or playful reveal tasks where the top and bottom layers have a meaningful relationship.

## Avoid when

Avoid for frequent navigation, essential hidden content, dense interfaces, or devices and frameworks that cannot render and hit-test the fold reliably.

## States and behavior

Covered, grabbed, peeling, completion armed, completed, restoring, and cancelled states; constrain valid drag directions, keep the handle reachable, and settle from the current visual position.

## Variants

Corner peel, edge peel, partial preview, one-time removal, and tap or button alternative that completes the same reveal.

## Platform notes

Touch is the natural primary input; pointer interfaces need an explicit grab affordance and keyboard-accessible alternative rather than relying on hover alone.

## Accessibility and performance

Expose the reveal as a named action and state, provide immediate completion under reduced motion, and bound mesh, clipping, shadow, and texture work.

## Common confusions

Mask reveal changes an aperture through a layer; sticker peel gives the top layer fold, thickness, direction, and a completion threshold.

## Related patterns

[Mask Reveal](mask-reveal.md), [Gesture-driven Transition](../navigation/gesture-driven-transition.md), and [Interruptible Motion](../../motion/behavior/interruptible-motion.md).
