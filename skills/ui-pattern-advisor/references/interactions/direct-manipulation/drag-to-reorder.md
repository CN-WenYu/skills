---
id: interactions.direct-manipulation.drag-to-reorder
name: Drag-to-Reorder
name_zh: 拖拽排序
kind: interaction-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [reorderable-list, sortable-list, 拖动重排]
tags: [gesture, reorder, list, direct-manipulation]
confidence: high
last_reviewed: 2026-09-08
---

# Drag-to-Reorder

## Definition

A user moves an item through an ordered collection while neighboring items make space for its prospective position.

## Problem solved

It allows direct editing of sequence or priority while previewing the resulting order.

## Recognition cues

The dragged item remains identifiable, a placeholder or shifting gap shows insertion position, and release commits the new order.

## Use when

Use when order is user-controlled, collections are manageable, and direct manipulation improves understanding.

## Avoid when

Avoid for very large lists without alternatives, fixed ranking, destructive movement, or gestures that conflict with scrolling.

## States and behavior

Idle, picked up, dragging, candidate position, dropped, and cancelled states; commit data only on a valid drop and restore it on cancellation.

## Variants

Handle-only drag, long-press drag, grid reorder, and cross-container movement.

## Platform notes

Prefer native reorder APIs and established edit modes when they provide complete semantics and scrolling behavior.

## Accessibility and performance

Provide move-before, move-after, or equivalent actions; announce position changes and virtualize without losing the dragged item's identity.

## Common confusions

Freeform dragging changes position in space; reorder changes semantic order within a collection.

## Related patterns

[Collision and Spring Response](../../motion/physics/collision-and-spring-response.md) and [Staggered Bulk Selection](../selection/staggered-bulk-selection.md).
