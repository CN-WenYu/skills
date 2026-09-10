---
id: motion.attention.glare-hover
name: Glare Hover
name_zh: 悬停反光
kind: motion-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [hover-glare, reflective-card-hover, specular-hover, 卡片反光]
tags: [hover, glare, card, attention]
confidence: medium
last_reviewed: 2026-09-10
---

# Glare Hover

## Definition

A restrained highlight moves across or within a surface according to pointer position, simulating a reflective response without changing the content state.

## Problem solved

It can reinforce surface orientation, material character, or hover availability on a small number of image-led cards.

## Recognition cues

The highlight remains clipped to the surface, its position follows bounded pointer coordinates, intensity stays subordinate to content, and it restores cleanly on exit.

## Use when

Use for occasional product or media cards where a reflective material cue supports the visual identity and hover already exists.

## Avoid when

Avoid when glare obscures text, faces, or image recognition; on dense operational UI; or when the effect would be the only indication that a card is interactive.

## States and behavior

Resting, entered, tracking, pressed, and exiting states; map pointer position to a bounded highlight, smooth abrupt changes, suppress during activation when distracting, and reset on exit.

## Variants

Linear sheen, radial specular spot, restrained foil highlight, static hover highlight, and no-motion contrast fallback.

## Platform notes

Enable only for devices with true hover; touch platforms should retain the card's standard press and focus feedback without inventing a persistent virtual pointer.

## Accessibility and performance

Keep contrast and text readability intact, avoid flashing and high-frequency luminance changes, respect reduced motion, and implement with bounded compositing rather than layout updates.

## Common confusions

A shine sweep follows a predetermined timeline; glare hover responds continuously to input position and is not a substitute for semantic hover or focus feedback.

## Related patterns

[Image Trail](image-trail.md), [Layered Parallax](../depth/layered-parallax.md), and [Ripple Distortion](../physics/ripple-distortion.md).
