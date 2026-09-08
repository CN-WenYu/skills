---
id: motion.physics.collision-and-spring-response
name: Collision and Spring Response
name_zh: 碰撞与弹簧回弹
kind: motion-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [spring-collision-response, 碰撞回弹]
tags: [physics, collision, spring, drag]
confidence: medium
last_reviewed: 2026-09-08
---

# Collision and Spring Response

## Definition

Interactive objects respect boundaries or one another, then settle using a spring response after contact or release.

## Problem solved

It communicates constraints, separation, and physical hierarchy during direct manipulation.

## Recognition cues

Objects do not overlap freely; displacement propagates or rebounds, and motion settles without a hard visual stop.

## Use when

Use for bounded drag surfaces, playful object arrangements, or selection systems where collision conveys a real rule.

## Avoid when

Avoid when collision is decorative, targets must remain precisely aligned, or simulation would obscure the actual drop result.

## States and behavior

Track movement, detect bounded contact, resolve overlap, preserve relevant velocity, and spring all affected objects to valid rest positions.

## Variants

Boundary rebound, sibling displacement, elastic separation, and chained collision response.

## Platform notes

Use deterministic layout positions as the source of truth; the spring is presentation, not stored data.

## Accessibility and performance

Provide non-gesture alternatives, cap simultaneous animated objects, and reduce rebound and travel under reduced motion.

## Common confusions

Drag-to-reorder reserves a list position; collision response models contact and may not change semantic order.

## Related patterns

[Drag-to-Reorder](../../interactions/direct-manipulation/drag-to-reorder.md) and [Velocity-driven Deformation](velocity-driven-deformation.md).
