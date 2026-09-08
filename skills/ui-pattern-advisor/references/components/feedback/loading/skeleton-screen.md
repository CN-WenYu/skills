---
id: components.feedback.loading.skeleton-screen
name: Skeleton Screen
name_zh: 骨架屏
kind: feedback-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [content-placeholder, skeleton-loader, 内容占位骨架]
tags: [loading, placeholder, content, layout]
confidence: high
last_reviewed: 2026-09-08
---

# Skeleton Screen

## Definition

A structural placeholder approximates the layout of content that has not loaded yet.

## Problem solved

It communicates expected structure and reduces the visual jump between an empty surface and arriving content.

## Recognition cues

Neutral blocks align with future text, image, or card regions and are replaced in place by real content.

## Use when

Use when the content layout is predictable and the initial wait is perceptible but not exceptionally long.

## Avoid when

Avoid for unknown layouts, one small inline action, sensitive values that could be misleading, or errors disguised as endless loading.

## States and behavior

Placeholder, partially available, complete, empty, and error states; reserve stable geometry and transition only when content is ready.

## Variants

Static blocks, subtle shimmer, progressive sections, and image-dominant placeholders.

## Platform notes

Match real dynamic type, localization, and responsive layout ranges rather than hardcoding one idealized skeleton.

## Accessibility and performance

Hide decorative shapes from accessibility APIs, expose one loading status, and disable shimmer under reduced motion.

## Common confusions

A blank placeholder reserves space without describing structure; a skeleton intentionally represents the expected content layout.

## Related patterns

[Spinner](spinner.md) and [Indeterminate Progress](indeterminate-progress.md).
