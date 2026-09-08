---
id: components.selection.select
name: Select
name_zh: 选择器
kind: component
term_status: standard
platforms: [ios, android, web]
aliases: [select-control, single-choice-picker, 单选选择器]
tags: [selection, form, bounded-options]
confidence: high
last_reviewed: 2026-09-08
---

# Select

## Definition

A control for choosing one value from a predefined set, with the selected value retained as data.

## Problem solved

It provides bounded single-choice input without displaying every option permanently.

## Recognition cues

The trigger shows the current value, activation reveals choices, and choosing one replaces the stored value.

## Use when

Use for a manageable known option set where free text is invalid or unnecessary.

## Avoid when

Avoid when options need comparison side by side, choices are very few, or search and free-form entry are required.

## States and behavior

Closed, open, focused, disabled, and selected states; selection updates the value and normally closes the option surface.

## Variants

Native select, picker, exposed select, and searchable select when the bounded list is large.

## Platform notes

Presentation differs across platforms; preserve bounded-value semantics rather than copying a desktop dropdown appearance.

## Accessibility and performance

Expose label, value, expanded state, focus order, and keyboard or assistive selection behavior.

## Common confusions

A menu invokes commands; a combobox combines an input with choices and may support typing.

## Related patterns

[Combobox](combobox.md), [Autocomplete](autocomplete.md), and [Menu](menu.md).
