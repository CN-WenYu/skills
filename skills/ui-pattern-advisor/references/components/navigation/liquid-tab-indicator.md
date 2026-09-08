---
id: components.navigation.liquid-tab-indicator
name: Liquid Tab Indicator
name_zh: 液态标签指示器
kind: component
term_status: common-informal
platforms: [ios, android, web]
aliases: [fluid-tab-indicator, morphing-tab-indicator, 液态Tab]
tags: [navigation, tabs, indicator, morphing]
confidence: medium
last_reviewed: 2026-09-08
---

# Liquid Tab Indicator

## Definition

A tab-selection indicator that translates and deforms fluidly between tab positions while the tab labels remain stable.

## Problem solved

It reinforces the relationship between adjacent navigation states and makes the selected tab easy to track.

## Recognition cues

One continuous indicator stretches, merges, or reshapes between fixed tab anchors instead of fading between separate markers.

## Use when

Use for a small stable tab set, infrequent enough that expressive selection feedback will not slow navigation.

## Avoid when

Avoid when tabs scroll unpredictably, labels change width frequently, selection must feel instantaneous, or the product's tone is restrained.

## States and behavior

Track previous and selected indices, move one indicator between measured anchors, and allow rapid retargeting from its current shape.

## Variants

Stretch-and-settle, capsule morph, elastic underline, and connected-blob indicators.

## Platform notes

Retain native tab semantics and selection behavior even when drawing a custom indicator.

## Accessibility and performance

Expose selection independently of motion, retain readable contrast, and provide a simple position or color change for reduced motion.

## Common confusions

An animated underline changes position but not shape; a liquid indicator deliberately deforms during travel.

## Related patterns

[Velocity-driven Deformation](../../motion/physics/velocity-driven-deformation.md) and [Collision and Spring Response](../../motion/physics/collision-and-spring-response.md).
