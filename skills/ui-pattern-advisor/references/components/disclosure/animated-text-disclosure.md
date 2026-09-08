---
id: components.disclosure.animated-text-disclosure
name: Animated Text Disclosure
name_zh: 动画文本展开
kind: component
term_status: descriptive
platforms: [ios, android, web]
aliases: [animated-read-more, expandable-text, 展开全文]
tags: [disclosure, text, expand, collapse]
confidence: high
last_reviewed: 2026-09-08
---

# Animated Text Disclosure

## Definition

A long text region switches between a constrained preview and full content while preserving reading position and exposing an explicit control.

## Problem solved

It reduces initial visual density without navigating away or permanently hiding optional detail.

## Recognition cues

Text is initially clamped or shortened, a disclosure control remains visible, and the same region expands or collapses in place.

## Use when

Use when users can make an initial decision from a preview and expansion is occasional and reversible.

## Avoid when

Avoid when omitted text is required for consent, safety, comparison, or the primary task.

## States and behavior

Collapsed and expanded states update the control label and accessibility state; preserve the start of the text and avoid unexpected scroll jumps.

## Variants

Line-clamped preview, fixed-height preview, gradient edge, and read-more label.

## Platform notes

Measure dynamic text at runtime and avoid fixed heights that break localization or accessibility text sizes.

## Accessibility and performance

Use a real button, expose expanded state, keep focus stable, and replace height travel with an immediate or brief transition under reduced motion.

## Common confusions

An accordion discloses a separate region; text disclosure expands the same text content.

## Related patterns

[Expanding Tag Selection](../selection/expanding-tag-selection.md).
