---
id: motion.attention.magnetic-attraction
name: Magnetic Attraction
name_zh: 磁吸效果
kind: motion-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [magnetic-hover, magnetic-button, 磁性吸附]
tags: [attention, pointer, proximity, transform]
confidence: medium
last_reviewed: 2026-09-08
---

# Magnetic Attraction

## Definition

A target shifts subtly toward a nearby pointer or draggable object, then returns when proximity ends.

## Problem solved

It strengthens the perceived relationship between an input position and an interactive target.

## Recognition cues

Movement begins before direct contact, follows only a limited distance, and settles back without changing layout.

## Use when

Use sparingly for optional pointer-rich surfaces, playful controls, or drag targets where proximity is meaningful.

## Avoid when

Avoid on dense work UI, touch-only primary flows, precise layouts, or controls whose apparent and actual hit areas would diverge.

## States and behavior

Idle, proximity, attracted, pressed or dropped, and return; clamp displacement and preserve interruptibility.

## Variants

Pointer attraction, drag-target attraction, and nearby-label attraction share the same proximity model.

## Platform notes

Pointer variants fit web and pointer-enabled iPadOS; touch platforms need a drag or gesture source rather than hover.

## Accessibility and performance

Keep hit testing stable, disable positional motion for reduced-motion users, and animate transforms rather than layout.

## Common confusions

Snap-to-target acts after movement or release; magnetic attraction begins while the source is nearby.

## Related patterns

[Center-focus Scaling](center-focus-scaling.md) and [Collision and Spring Response](../physics/collision-and-spring-response.md).
