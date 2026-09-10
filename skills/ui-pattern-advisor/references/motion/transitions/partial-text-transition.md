---
id: motion.transitions.partial-text-transition
name: Partial Text Transition
name_zh: 局部文字过渡
kind: motion-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [substring-transition, changed-text-transition, partial-copy-transition, 局部文本过渡]
tags: [text, transition, continuity, content-change]
confidence: medium
last_reviewed: 2026-09-09
---

# Partial Text Transition

## Definition

Only the changed segment of a text presentation transitions while unchanged text remains visually stable.

## Problem solved

It makes a small content update noticeable without forcing users to reacquire the entire sentence, label, or value.

## Recognition cues

Stable text keeps its position and appearance, changed characters or tokens receive localized motion, and the final text remains one coherent reading unit.

## Use when

Use for short, infrequent updates where the changed segment is meaningful and can be identified reliably.

## Avoid when

Avoid for long prose, rapid streams, bidirectional or complex-script cases that cannot be segmented safely, or layouts where text reflow would undermine continuity.

## States and behavior

Stable, diffed, transitioning, completed, and interrupted states; compute semantic segments, preserve the accessible final string, and treat layout changes as part of the transition.

## Variants

Crossfade of changed tokens, vertical digit roll, replacement slide, highlight fade, and character morph where typography supports it.

## Platform notes

Text measurement, shaping, localization, and animation APIs differ; preserve native text rendering and use snapshots only when semantics remain available separately.

## Accessibility and performance

Expose one current value rather than duplicate animated text to assistive technology, respect reduced motion, and avoid per-character layout work for large strings.

## Common confusions

Animated text disclosure reveals hidden content; partial text transition communicates a replacement inside already visible content.

## Related patterns

[Animated Text Disclosure](../../components/disclosure/animated-text-disclosure.md), [Interruptible Motion](../behavior/interruptible-motion.md), and [Shared-element Image Expansion](shared-element-image-expansion.md).
