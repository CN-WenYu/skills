---
id: components.feedback.loading.pull-to-refresh
name: Pull to Refresh
name_zh: 下拉刷新
kind: interaction-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [swipe-to-refresh, 下拉更新]
tags: [loading, gesture, refresh, scroll]
confidence: high
last_reviewed: 2026-09-08
---

# Pull to Refresh

## Definition

A user pulls beyond the leading boundary of a scrollable surface to request newer content.

## Problem solved

It provides a compact, direct refresh action for content whose update direction matches the scroll boundary.

## Recognition cues

Overscroll reveals a threshold indicator; release after crossing the threshold begins a refresh tied to that same surface.

## Use when

Use on refreshable feeds or lists where the gesture is established and a visible alternative can also be provided when needed.

## Avoid when

Avoid on non-scroll surfaces, when overscroll already has another meaning, or when refresh could discard unsaved state.

## States and behavior

Idle, pulling, armed, refreshing, succeeded, failed, and cancelled states; only an armed release starts work.

## Variants

Native refresh control, custom threshold indicator, and refresh with last-updated status.

## Platform notes

Use native scroll integration where possible; desktop web may need an explicit refresh action because the gesture is not discoverable.

## Accessibility and performance

Provide a non-gesture action, announce refresh results, and keep existing content readable while refreshing.

## Common confusions

Infinite scroll loads older or additional content near the trailing edge; pull to refresh requests newer content at the leading edge.

## Related patterns

[Spinner](spinner.md) and [Indeterminate Progress](indeterminate-progress.md).
