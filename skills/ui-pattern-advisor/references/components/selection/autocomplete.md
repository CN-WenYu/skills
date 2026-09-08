---
id: components.selection.autocomplete
name: Autocomplete
name_zh: 自动补全
kind: component
term_status: standard
platforms: [ios, android, web]
aliases: [typeahead, suggestions, 输入建议]
tags: [input, suggestions, search, completion]
confidence: high
last_reviewed: 2026-09-08
---

# Autocomplete

## Definition

A text-entry behavior that predicts or suggests completions as the user types.

## Problem solved

It reduces typing, helps discovery, and can guide input toward known values without necessarily forbidding custom text.

## Recognition cues

Suggestions react to the current text and selecting one completes or replaces part of the input.

## Use when

Use when suggestions can be produced quickly and meaningfully from a large or open vocabulary.

## Avoid when

Avoid when predictions are unreliable, sensitive text should not be exposed, or a small static choice set is sufficient.

## States and behavior

Empty, typing, loading, suggestions available, no results, accepted, and error states; stale asynchronous results must not replace newer input.

## Variants

Inline completion, suggestion list, search suggestions, address completion, and command prediction.

## Platform notes

Keyboard, input-method, and native suggestion behavior vary; avoid fighting system text entry.

## Accessibility and performance

Announce suggestion availability without excessive chatter, preserve typed text, and debounce remote queries responsibly.

## Common confusions

A combobox is the composite widget pattern that often presents autocomplete; autocomplete describes the suggestion behavior itself.

## Related patterns

[Combobox](combobox.md) and [Select](select.md).
