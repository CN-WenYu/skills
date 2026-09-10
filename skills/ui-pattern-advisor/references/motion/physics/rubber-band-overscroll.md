---
id: motion.physics.rubber-band-overscroll
name: Rubber-band Overscroll
name_zh: 橡皮筋式边界阻尼
kind: motion-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [elastic-overscroll, rubber-banding, overscroll-resistance, 边界阻尼]
tags: [scroll, overscroll, resistance, boundary]
confidence: high
last_reviewed: 2026-09-09
---

# Rubber-band Overscroll

## Definition

Content moves with increasing resistance beyond a scroll or drag boundary, then returns to the valid extent after release.

## Problem solved

It communicates that the boundary has been reached while preserving continuity and a sense of direct manipulation.

## Recognition cues

Additional input produces diminishing displacement past the edge, release returns content to the boundary, and the effect does not reveal new semantic content by itself.

## Use when

Use where platform convention or a custom bounded surface benefits from elastic edge feedback.

## Avoid when

Avoid when overscroll triggers another action, when the platform already supplies the effect, or when elasticity makes a strict control feel imprecise.

## States and behavior

In bounds, boundary reached, overscrolling, released, and returning states; apply bounded nonlinear resistance, ignore overscroll as stored position, and return from the current displacement.

## Variants

Scroll-edge rubber banding, bounded drag resistance, stretch effect, and reduced-motion static edge feedback.

## Platform notes

Use native overscroll behavior when available. iOS commonly uses elastic scrolling, Android may use stretch or glow depending on version and component, and web behavior varies by browser and CSS configuration.

## Accessibility and performance

Do not encode essential state only through motion, honor reduced motion, and prefer compositor-friendly transforms without detaching semantics from visible content.

## Common confusions

Pull to refresh assigns an action to crossing an overscroll threshold; rubber-band overscroll only communicates and resists the boundary.

## Related patterns

[Pull to Refresh](../../components/feedback/loading/pull-to-refresh.md), [Collision and Spring Response](collision-and-spring-response.md), and [Interruptible Motion](../behavior/interruptible-motion.md).
