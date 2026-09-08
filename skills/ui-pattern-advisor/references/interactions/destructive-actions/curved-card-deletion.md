---
id: interactions.destructive-actions.curved-card-deletion
name: Curved Card Deletion
name_zh: 曲线卡片删除
kind: interaction-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [curved-swipe-delete, arcing-card-dismissal, 曲线滑动删除]
tags: [destructive, card, swipe, dismissal]
confidence: medium
last_reviewed: 2026-09-08
---

# Curved Card Deletion

## Definition

A card crosses a destructive swipe threshold, then exits along a bounded curved path toward the revealed delete affordance.

## Problem solved

It connects a destructive gesture, its destination, and the removal result while preserving cancellation before commitment.

## Recognition cues

The card follows the gesture initially, reveals a destructive target, and only follows the exit arc after the threshold and release commit deletion.

## Use when

Use for familiar, reversible card deletion where an undo action is available and the curved path reinforces the revealed target.

## Avoid when

Avoid for irreversible or high-impact deletion, hidden-only actions, scroll-conflicting gestures, or decorative paths without spatial meaning.

## States and behavior

Idle, dragging, armed, cancelled, committed, removed, and undo states; do not mutate data until commitment, and restore predictably on undo.

## Variants

Shallow arc, target-directed arc, straight reduced-motion exit, and confirmation-before-removal.

## Platform notes

Follow platform conventions for swipe actions, confirmation, and undo rather than making the curved exit the only deletion mechanism.

## Accessibility and performance

Expose an explicit delete action, announce removal and undo, preserve focus, and avoid large rotation or travel for reduced motion.

## Common confusions

Swipe-to-dismiss removes a transient surface; this pattern performs a destructive data action and requires stronger safeguards.

## Related patterns

[Gesture-driven Transition](../navigation/gesture-driven-transition.md).
