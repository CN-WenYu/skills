---
id: interactions.selection.staggered-bulk-selection
name: Staggered Bulk Selection
name_zh: 错峰批量勾选
kind: interaction-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [staggered-select-all, animated-bulk-selection, 批量选择级联反馈]
tags: [selection, bulk-action, stagger, feedback]
confidence: medium
last_reviewed: 2026-09-08
---

# Staggered Bulk Selection

## Definition

A bulk selection operation updates all selection states immediately while visual confirmations appear in a short ordered cascade.

## Problem solved

It makes the scope of a bulk action perceptible without delaying the underlying state change.

## Recognition cues

Multiple selection markers animate sequentially after one command, but the resulting selection is already logically complete.

## Use when

Use for small visible groups where a brief cascade clarifies that one action affected every item.

## Avoid when

Avoid for large or virtualized collections, frequent commands, or any implementation that delays actual selection until each animation finishes.

## States and behavior

Commit the target selection atomically, animate visible confirmations in stable order, and support immediate reversal without waiting for the cascade.

## Variants

Top-to-bottom checkmarks, short row highlights, grouped waves, and no-motion simultaneous feedback.

## Platform notes

Preserve native multi-selection and select-all semantics; animation is optional presentation.

## Accessibility and performance

Announce the resulting count once, skip or shorten the cascade for reduced motion, and cap animated visible items.

## Common confusions

Progressive selection changes data over time; staggered bulk selection changes data atomically and staggers only feedback.

## Related patterns

[Expanding Tag Selection](../../components/selection/expanding-tag-selection.md) and [Drag-to-Reorder](../direct-manipulation/drag-to-reorder.md).
