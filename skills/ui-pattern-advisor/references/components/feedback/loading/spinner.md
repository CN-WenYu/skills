---
id: components.feedback.loading.spinner
name: Spinner
name_zh: 加载旋转指示器
kind: feedback-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [activity-indicator, loading-spinner, 加载菊花]
tags: [loading, indeterminate, loop, feedback]
confidence: high
last_reviewed: 2026-09-08
---

# Spinner

## Definition

A compact looping indicator that communicates ongoing work when exact progress is unavailable.

## Problem solved

It reassures users that a local action or bounded region has not stalled.

## Recognition cues

A small cyclic mark repeats without displaying a fraction, stage, or estimated completion.

## Use when

Use for short indeterminate waits in buttons, rows, panels, or other clearly bounded regions.

## Avoid when

Avoid for long work, known progress, initial content whose structure can be represented, or background refresh that need not block use.

## States and behavior

Delayed appearance can prevent flashing for instant work; replace the indicator with success, content, empty, error, or cancellation state.

## Variants

Circular stroke, radial segments, rotating icon, and restrained dot loops; these are visual variants of the same feedback model.

## Platform notes

Prefer native activity indicators and established component sizing when available.

## Accessibility and performance

Expose a concise loading status, avoid continuous announcements, and stop animation when hidden or complete.

## Common confusions

Indeterminate progress can occupy a track and imply process scope; a spinner is compact and usually local.

## Related patterns

[Indeterminate Progress](indeterminate-progress.md) and [Skeleton Screen](skeleton-screen.md).
