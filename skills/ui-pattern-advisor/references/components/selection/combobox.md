---
id: components.selection.combobox
name: Combobox
name_zh: 组合框
kind: component
term_status: standard
platforms: [ios, android, web]
aliases: [editable-select, input-with-listbox, 输入选择框]
tags: [selection, input, popup, listbox]
confidence: high
last_reviewed: 2026-09-08
---

# Combobox

## Definition

A composite input whose field controls a popup of candidate values and whose selection or typed value becomes the control value.

## Problem solved

It supports efficient choice from a large set while allowing keyboard input, filtering, or optional custom values.

## Recognition cues

One focusable input owns a popup, typing changes candidates, and selection updates the field value.

## Use when

Use when the option set is large or users benefit from typing to narrow choices.

## Avoid when

Avoid when a short static list, visible choices, or an action menu is clearer.

## States and behavior

Collapsed, expanded, inputting, candidate-focused, selected, invalid, and disabled states require coordinated focus and value management.

## Variants

Strict bounded combobox, editable combobox, multi-value tokenizing combobox, and asynchronous combobox.

## Platform notes

Some mobile platforms use a search screen or picker rather than a desktop-style anchored popup; preserve the input-plus-options task.

## Accessibility and performance

Expose the input, expanded state, active candidate, result count, and selection without moving DOM or accessibility focus unpredictably.

## Common confusions

Autocomplete may merely suggest text; a combobox defines one composite control with a managed popup and value.

## Related patterns

[Autocomplete](autocomplete.md), [Select](select.md), and [Menu](menu.md).
