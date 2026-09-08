---
id: components.selection.ripple-feedback-for-related-switches
name: Ripple Feedback for Related Switches
name_zh: 关联开关涟漪反馈
kind: feedback-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [related-toggle-ripple, 关联切换反馈]
tags: [selection, switch, dependency, ripple]
confidence: medium
last_reviewed: 2026-09-08
---

# Ripple Feedback for Related Switches

## Definition

A localized ripple or highlight propagates from a changed switch to nearby controls whose availability or state is affected.

## Problem solved

It explains that one setting caused a visible change elsewhere in the same group.

## Recognition cues

The effect originates at the changed control, remains within a related group, and coincides with dependent controls updating.

## Use when

Use when a switch immediately enables, disables, reveals, or changes a small set of nearby settings and that dependency may otherwise be missed.

## Avoid when

Avoid when controls are unrelated, the dependency is already obvious, or the effect resembles an additional tap target.

## States and behavior

Commit the switch state, update dependents, emit one bounded group-level cue, and suppress repeated overlapping ripples.

## Variants

Radial ripple, short group highlight, connector pulse, and reduced-motion color emphasis.

## Platform notes

Do not replace platform switch feedback; this is an optional explanation layer for dependent state.

## Accessibility and performance

Expose enabled or disabled state semantically, announce meaningful dependency changes, and avoid motion-only explanation.

## Common confusions

A standard touch ripple confirms one press; this pattern communicates a causal relationship between controls.

## Related patterns

[Spring Stepper Progress](../feedback/spring-stepper-progress.md).
