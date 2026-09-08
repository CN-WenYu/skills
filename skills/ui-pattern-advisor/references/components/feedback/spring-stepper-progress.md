---
id: components.feedback.spring-stepper-progress
name: Spring Stepper Progress
name_zh: 弹簧步骤进度
kind: feedback-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [animated-step-progress, 弹性步骤条]
tags: [feedback, stepper, progress, spring]
confidence: medium
last_reviewed: 2026-09-08
---

# Spring Stepper Progress

## Definition

A discrete step indicator advances between milestones with a restrained spring response that emphasizes the newly completed state.

## Problem solved

It confirms progress through a multi-step flow and distinguishes completed, current, and upcoming stages.

## Recognition cues

Progress advances one milestone at a time; the connector and active marker settle with slight elasticity instead of moving linearly.

## Use when

Use for occasional onboarding, setup, checkout, or creation flows with a stable ordered sequence.

## Avoid when

Avoid for unknown-length work, continuously measured progress, or back-and-forth steps where bounce would imply celebration.

## States and behavior

Maintain completed, current, and upcoming states; animate only the transition between known indices and preserve correctness when moving backward.

## Variants

Spring marker, elastic connector, milestone pulse, and reduced-motion color transition.

## Platform notes

Use product progress semantics rather than treating the visual stepper as navigation unless steps are actually selectable.

## Accessibility and performance

Announce the current step and total, never rely on color alone, and remove overshoot for reduced motion.

## Common confusions

Determinate progress represents a continuous fraction; a stepper represents named discrete stages.

## Related patterns

[Determinate Progress](loading/determinate-progress.md) and [Collision and Spring Response](../../motion/physics/collision-and-spring-response.md).
