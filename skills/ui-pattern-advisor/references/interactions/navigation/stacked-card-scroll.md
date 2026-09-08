---
id: interactions.navigation.stacked-card-scroll
name: Stacked Card Scroll
name_zh: 堆叠卡片滚动
kind: interaction-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [card-stack-scroll, stacking-cards, 卡片堆叠滚动]
tags: [scroll, cards, stacking, navigation]
confidence: medium
last_reviewed: 2026-09-08
---

# Stacked Card Scroll

## Definition

Cards remain partially pinned and visually compress into a stack as later cards scroll into the same region.

## Problem solved

It preserves recent context and gives a sequence of cards a strong spatial progression.

## Recognition cues

Earlier cards stop or slow near a boundary, later cards overlap them in order, and scale or elevation separates the layers.

## Use when

Use for a short curated sequence where overlap communicates progression and each card remains identifiable.

## Avoid when

Avoid for dense reading, long feeds, independent cards requiring comparison, or content that becomes inaccessible under overlap.

## States and behavior

Map scroll progress to bounded pinning, offset, scale, and stacking order; release cards predictably after their section ends.

## Variants

Sticky stack, compressing deck, depth stack, and snap-by-card stack.

## Platform notes

Preserve native scroll physics and back or focus navigation; do not turn a normal list into an inaccessible custom scroller.

## Accessibility and performance

Maintain logical reading order, ensure focused content is visible, reduce overlap motion, and limit active composited layers.

## Common confusions

Layered parallax separates depth planes without necessarily overlapping semantic items; stacked-card scroll changes card presentation along one sequence.

## Related patterns

[Layered Parallax](../../motion/depth/layered-parallax.md) and [Center-focus Scaling](../../motion/attention/center-focus-scaling.md).
