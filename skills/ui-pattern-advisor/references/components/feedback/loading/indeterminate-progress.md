---
id: components.feedback.loading.indeterminate-progress
name: Indeterminate Progress
name_zh: 不确定型进度
kind: feedback-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [indeterminate-bar, ongoing-progress, 未知进度]
tags: [loading, progress, indeterminate, feedback]
confidence: high
last_reviewed: 2026-09-08
---

# Indeterminate Progress

## Definition

A non-fractional progress presentation shows that a scoped process is active while its completion amount is unknown.

## Problem solved

It communicates ongoing work and process scope without fabricating a percentage.

## Recognition cues

A repeating segment moves through a track or region without accumulating toward a numeric endpoint.

## Use when

Use when work is ongoing, its scope is meaningful, and no trustworthy completion fraction exists.

## Avoid when

Avoid for background work that does not affect the user, long processes needing status detail, or measurable work.

## States and behavior

Idle, active, complete, failed, and cancelled states; switch to determinate progress only when a reliable measure becomes available.

## Variants

Linear indeterminate bar, looping track segment, and region-level activity band.

## Platform notes

Prefer platform progress components and avoid inventing a percentage from elapsed time alone.

## Accessibility and performance

Expose a stable loading label, suppress repeated announcements, and reduce repetitive movement when reduced motion is requested.

## Common confusions

A spinner is a compact activity symbol; indeterminate progress can communicate the scope or location of a process through a track.

## Related patterns

[Spinner](spinner.md) and [Determinate Progress](determinate-progress.md).
