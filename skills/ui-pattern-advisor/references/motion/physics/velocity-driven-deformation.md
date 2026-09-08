---
id: motion.physics.velocity-driven-deformation
name: Velocity-driven Deformation
name_zh: 速度驱动形变
kind: motion-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [velocity-based-deformation, 速度形变]
tags: [physics, gesture, velocity, deformation]
confidence: medium
last_reviewed: 2026-09-08
---

# Velocity-driven Deformation

## Definition

An object's scale, skew, stretch, or compression changes in response to movement velocity and direction.

## Problem solved

It communicates speed, weight, and directional force during direct manipulation.

## Recognition cues

The shape deforms more at higher velocity, aligns with the motion axis, and recovers as motion settles.

## Use when

Use for draggable cards, playful controls, or elastic surfaces where physical character supports the interaction.

## Avoid when

Avoid on text-heavy content, precise controls, frequently repeated navigation, or any deformation that harms readability.

## States and behavior

Track gesture velocity, map it to bounded deformation, smooth noisy changes, then spring to identity on rest or cancellation.

## Variants

Directional stretch, squash-and-stretch, skew by velocity, and trailing-edge lag.

## Platform notes

Use the platform's gesture velocity when available; normalize thresholds for density, refresh rate, and input type.

## Accessibility and performance

Remove deformation under reduced motion, preserve the original hit region, and avoid per-frame layout changes.

## Common confusions

Static squash-and-stretch follows an animation timeline; this pattern is continuously driven by measured velocity.

## Related patterns

[Collision and Spring Response](collision-and-spring-response.md) and [Gesture-driven Transition](../../interactions/navigation/gesture-driven-transition.md).
