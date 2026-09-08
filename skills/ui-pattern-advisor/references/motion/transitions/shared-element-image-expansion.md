---
id: motion.transitions.shared-element-image-expansion
name: Shared-element Image Expansion
name_zh: 共享元素图片展开
kind: motion-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [shared-element-transition, hero-image-transition, 图片连续展开]
tags: [transition, continuity, image, navigation]
confidence: high
last_reviewed: 2026-09-08
---

# Shared-element Image Expansion

## Definition

An image preserves its perceived identity while moving and resizing from a source view into a destination layout.

## Problem solved

It maintains orientation and object continuity during navigation between overview and detail states.

## Recognition cues

The same image appears to travel between known frames while crop, corner radius, and surrounding content transition around it.

## Use when

Use when a selected thumbnail or card image is the clear visual anchor of the destination.

## Avoid when

Avoid when source and destination imagery differ, the element is offscreen, or navigation must be immediate and highly repetitive.

## States and behavior

Capture source and destination geometry, animate a shared representation, coordinate surrounding content, and support cancellation when navigation is interactive.

## Variants

Thumbnail-to-detail, card-to-fullscreen, and grid-item-to-gallery transitions.

## Platform notes

Framework APIs and lifecycle constraints differ; preserve the semantic navigation model even when the visual implementation uses a snapshot.

## Accessibility and performance

Move focus to destination content, provide a reduced-motion crossfade, and avoid decoding or relayout during the transition.

## Common confusions

A scale transition enlarges a view in place; a shared-element transition connects two distinct layouts through one perceived object.

## Related patterns

[Radial Theme Transition](radial-theme-transition.md) and [Gesture-driven Transition](../../interactions/navigation/gesture-driven-transition.md).
