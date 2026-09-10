---
id: components.data-visualization.chart-tooltip
name: Chart Tooltip
name_zh: 图表数据提示框
kind: component
term_status: standard
platforms: [ios, android, web]
aliases: [data-tooltip, value-tooltip, hovercard, 数据提示框]
tags: [chart, tooltip, details, values]
confidence: high
last_reviewed: 2026-09-09
---

# Chart Tooltip

## Definition

A contextual overlay presents values or metadata for a focused chart mark or domain position.

## Problem solved

It reveals detail on demand without permanently labeling every datum or overcrowding the visualization.

## Recognition cues

A compact overlay is anchored to the active mark or cursor, identifies the datum, and disappears or pins according to an explicit interaction rule.

## Use when

Use when users need exact values or secondary details that cannot fit as persistent labels.

## Avoid when

Avoid for essential information that must be visible without interaction, for dense content that needs a separate panel, or when the overlay repeatedly occludes the comparison target.

## States and behavior

Hidden, previewed, pinned, moved, and dismissed states; keep the anchor relationship clear, prevent viewport clipping, and avoid flicker between nearby marks.

## Variants

Single-point tooltip, shared-domain tooltip, pinned tooltip, compact value label, and external detail panel.

## Platform notes

Desktop may use hover and focus; touch should use tap, press, or crosshair tracking and must not depend on hover semantics.

## Accessibility and performance

Make the same data reachable by keyboard and assistive technology, keep focus stable, and avoid expensive layout work on every move.

## Common confusions

A generic UI tooltip explains a control; a chart tooltip reports data associated with a mark or domain position.

## Related patterns

[Chart Crosshair](../../interactions/data-visualization/chart-crosshair.md), [Data Point Highlight](data-point-highlight.md), and [Data Drill-down](../../interactions/data-visualization/data-drill-down.md).
