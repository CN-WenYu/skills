---
id: components.selection.menu
name: Menu
name_zh: 菜单
kind: component
term_status: standard
platforms: [ios, android, web]
aliases: [action-menu, command-menu, 操作菜单]
tags: [commands, actions, overlay]
confidence: high
last_reviewed: 2026-09-08
---

# Menu

## Definition

A temporary list of commands or navigation actions associated with a trigger or context.

## Problem solved

It exposes secondary actions without permanently occupying interface space.

## Recognition cues

Items are verbs or destinations, activation performs an action, and the surface normally dismisses afterward.

## Use when

Use for related secondary commands that users can understand without persistent visibility.

## Avoid when

Avoid for primary actions, complex forms, long explanatory content, or selecting a stored field value.

## States and behavior

Closed, open, focused item, invoked, and dismissed; return focus to the trigger after dismissal when appropriate.

## Variants

Action menu, overflow menu, context menu, and submenu.

## Platform notes

Trigger, placement, keyboard behavior, and context-menu conventions differ; prefer native menu semantics.

## Accessibility and performance

Support predictable focus movement, dismissal, keyboard navigation, and sufficient target sizes.

## Common confusions

A select stores a chosen value; a menu performs a command even when an item displays a checkmark.

## Related patterns

[Select](select.md) and [Combobox](combobox.md).
