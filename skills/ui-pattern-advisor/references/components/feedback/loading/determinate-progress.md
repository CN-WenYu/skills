---
id: components.feedback.loading.determinate-progress
name: Determinate Progress
name_zh: 确定型进度
kind: feedback-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [measured-progress, progress-bar, 可量化进度]
tags: [loading, progress, measurable, feedback]
confidence: high
last_reviewed: 2026-09-08
---

# Determinate Progress

## Definition

A progress indicator represents a trustworthy measured fraction or completed portion of known work.

## Problem solved

It helps users estimate remaining effort and decide whether to wait, cancel, or continue elsewhere.

## Recognition cues

The indicator advances from a defined start toward completion and may include a percentage, count, or named stage.

## Use when

Use when progress can be measured consistently enough that movement reflects real advancement.

## Avoid when

Avoid when the denominator is unknown, progress would jump arbitrarily, or a fake percentage would create false certainty.

## States and behavior

Not started, active, paused, complete, failed, and cancelled states; progress should be monotonic unless the task explicitly changes scope.

## Variants

Linear bar, circular ring, segmented stages, item count, and byte or time progress.

## Platform notes

Use native progress semantics and separate user navigation from progress when steps are not directly selectable.

## Accessibility and performance

Expose current and maximum values, throttle announcements and visual updates, and avoid animating through values the process never reported.

## Common confusions

A stepper communicates discrete workflow position; determinate progress communicates measured completion.

## Related patterns

[Indeterminate Progress](indeterminate-progress.md) and [Spring Stepper Progress](../spring-stepper-progress.md).
