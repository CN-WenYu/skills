---
id: interactions.navigation.scroll-driven-opening
name: Scroll-driven Opening
name_zh: 滚动驱动开场展开
kind: interaction-pattern
term_status: descriptive
platforms: [ios, android, web]
aliases: [scroll-linked-opening, scroll-reveal-opening, product-opening-sequence, 滚动开场]
tags: [scroll, opening, product, reveal]
confidence: medium
last_reviewed: 2026-09-11
---

# Scroll-driven Opening

## Definition

A focal product or interface begins closed, quiet, or assembled and progressively opens or reveals attached content as the user advances through a bounded scroll section.

## Problem solved

It introduces product structure and establishes a visual anchor before the page moves into detailed content.

## Recognition cues

One centered object remains the focus, scroll position continuously controls an opening sequence, attached interface content stays registered to the object, and reverse scrolling reconstructs the closed state.

## Use when

Use for an occasional product introduction where opening or assembly reveals a meaningful feature, screen, or spatial relationship.

## Avoid when

Avoid when the object has no credible opening model, the page needs immediate information access, motion would delay repeat visitors, or several competing transformations dilute the focal action.

## States and behavior

Closed, entering, opening, open, settling, and released states; derive normalized progress from measured section bounds, map one continuous state to the product and attached content, and preserve the same path in reverse.

## Variants

Hinged product opening, cover removal, unfolding panel, interface reveal from a device, and reduced-motion static open state.

## Platform notes

Web implementations often use a pinned section; native scroll containers may use equivalent scroll-linked progress. Preserve native scrolling and release pinning when the section narrative ends.

## Accessibility and performance

Keep headings and content in semantic order, provide a visible static result for reduced motion, avoid coupling essential reading to scrubbed frames, and pre-size assets to prevent layout shifts.

## Common confusions

A generic entrance animation plays on arrival; a scroll-driven opening gives continuous, reversible control over one meaningful product state.

## Related patterns

[Scroll-driven Exploded View](scroll-driven-exploded-view.md), [Scroll-driven Horizontal Section](scroll-driven-horizontal-section.md), [Layered Parallax](../../motion/depth/layered-parallax.md), and [Interruptible Motion](../../motion/behavior/interruptible-motion.md).
