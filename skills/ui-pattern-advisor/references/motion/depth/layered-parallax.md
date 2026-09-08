---
id: motion.depth.layered-parallax
name: Layered Parallax
name_zh: 分层视差
kind: motion-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [3d-parallax, 多层视差]
tags: [depth, parallax, scroll, pointer]
confidence: high
last_reviewed: 2026-09-08
---

# Layered Parallax

## Definition

Foreground, subject, and background layers move by different amounts in response to scroll, tilt, or pointer position.

## Problem solved

It communicates depth and spatial hierarchy without changing the underlying information structure.

## Recognition cues

Several aligned layers share an input but travel at different ratios, making near content appear to move more.

## Use when

Use for occasional product showcases, media covers, onboarding, or decorative scenes with separable visual layers.

## Avoid when

Avoid on dense reading surfaces, core navigation, accessibility-critical content, or imagery without safe crop margins.

## States and behavior

Map one bounded input to stable per-layer offsets and return all layers to rest without cumulative drift.

## Variants

Scroll parallax, pointer parallax, device-tilt parallax, and card-depth parallax.

## Platform notes

Input availability and permission differ; provide a static composition when pointer or motion-sensor input is absent.

## Accessibility and performance

Disable depth translation for reduced motion, keep text on a stable layer, and avoid large offscreen textures or layout changes.

## Common confusions

Simple 3D tilt rotates one surface; layered parallax moves multiple depth planes independently.

## Related patterns

[Stacked Card Scroll](../../interactions/navigation/stacked-card-scroll.md).
