---
id: interactions.navigation.scroll-driven-horizontal-section
name: Scroll-driven Horizontal Section
name_zh: 滚动驱动横向区段
kind: interaction-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [horizontal-scroll-section, vertical-to-horizontal-scroll, pinned-horizontal-scroll, 纵向滚动驱动横移]
tags: [scroll, horizontal, pinned, sequence]
confidence: medium
last_reviewed: 2026-09-11
---

# Scroll-driven Horizontal Section

## Definition

Within a bounded page section, vertical scroll progress moves a finite horizontal track of related items while the user's input direction remains unchanged.

## Problem solved

It gives a wide sequence enough room for inspection without requiring a separate horizontal gesture during a primarily vertical reading flow.

## Recognition cues

The viewport pins for one section, the track moves from first item to last according to measured overflow, every item becomes fully reachable, and normal vertical progress resumes at the true endpoint.

## Use when

Use for a short, ordered sequence of related work, features, screens, or stages whose horizontal relationship adds meaning.

## Avoid when

Avoid for long lists, independent items that need scanning or comparison, nested horizontal controls, unpredictable content widths, or any sequence that becomes inaccessible without scroll-linked motion.

## States and behavior

Before section, pinned at start, traversing, pinned at end, and released states; calculate travel from actual track and viewport sizes, clamp progress, preserve the first and last items, and reverse along the same path.

## Variants

Full-width panels, card track, annotated timeline, linked detail sequence, and reduced-motion vertical stack or native horizontal scroller.

## Platform notes

The pattern is most common on web marketing and editorial pages. On touch devices, validate nested gesture conflicts and prefer a conventional horizontal scroller or vertical stack when the pinned mapping feels indirect.

## Accessibility and performance

Keep DOM or view order aligned with reading order, ensure focus never moves content offscreen unexpectedly, provide a non-pinned layout for reduced motion, and resize calculations when content or viewport dimensions change.

## Common confusions

A normal horizontal scroller responds to horizontal input; this pattern maps vertical page progress onto a bounded horizontal presentation.

## Related patterns

[Stacked Card Scroll](stacked-card-scroll.md), [Scroll-driven Opening](scroll-driven-opening.md), and [Gesture Axis Lock](../direct-manipulation/gesture-axis-lock.md).
