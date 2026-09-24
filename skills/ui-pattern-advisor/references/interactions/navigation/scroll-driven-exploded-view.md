---
id: interactions.navigation.scroll-driven-exploded-view
name: Scroll-driven Exploded View
name_zh: 滚动驱动爆炸视图
kind: interaction-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [scroll-linked-exploded-view, exploded-product-scroll, scroll-disassembly, 滚动拆解视图]
tags: [scroll, exploded-view, product, structure]
confidence: medium
last_reviewed: 2026-09-11
---

# Scroll-driven Exploded View

## Definition

A product, device, or system remains visually anchored while scroll progress separates its parts in a planned order and attaches explanations to the currently exposed structure.

## Problem solved

It explains internal hierarchy and assembly relationships that are difficult to understand from a single exterior image or simultaneous static explosion.

## Recognition cues

The complete object establishes context, outer parts separate before inner details, only a small number of stages compete for attention, labels follow the active stage, and reverse scrolling reassembles the same object.

## Use when

Use when internal components, layers, or assembly order are central to understanding a real product or clearly labeled conceptual model.

## Avoid when

Avoid when source assets cannot support accurate separation, the sequence would imply false construction, many parts lack a readable hierarchy, or a static diagram communicates the structure more directly.

## States and behavior

Assembled, outer separation, internal reveal, detail focus, fully separated, and reassembled states; assign stable progress ranges, keep a visual anchor, move each part toward one deterministic target, and reconstruct exactly on reverse scroll.

## Variants

Three-dimensional model, layered raster or vector composition, pre-rendered state sequence, sectional cutaway, and static annotated exploded diagram.

## Platform notes

Choose the simplest asset strategy that preserves the needed perspective and material quality. Web and native rendering capabilities differ, but labels should remain in a separate readable interface layer.

## Accessibility and performance

Provide an ordered textual explanation and static overview, respect reduced motion, keep labels crisp and focusable, bound active layers and texture size, and avoid loading detailed assets during the scrub.

## Common confusions

Layered parallax moves depth planes at different rates; an exploded view deliberately separates named parts to explain structure or assembly.

## Related patterns

[Scroll-driven Opening](scroll-driven-opening.md), [Layered Parallax](../../motion/depth/layered-parallax.md), and [Shared-element Image Expansion](../../motion/transitions/shared-element-image-expansion.md).
