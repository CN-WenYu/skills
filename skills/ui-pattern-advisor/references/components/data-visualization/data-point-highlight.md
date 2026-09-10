---
id: components.data-visualization.data-point-highlight
name: Data Point Highlight
name_zh: 数据点高亮
kind: feedback-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [datum-highlight, point-emphasis, selected-point-highlight, 数据点强调]
tags: [chart, highlight, selection, emphasis]
confidence: high
last_reviewed: 2026-09-09
---

# Data Point Highlight

## Definition

A datum receives persistent or transient visual emphasis relative to surrounding marks.

## Problem solved

It directs attention to a selected, anomalous, current, or otherwise important value without changing the data encoding.

## Recognition cues

The target changes size, outline, color, opacity, or annotation while nearby marks remain legible and the selected state is distinguishable from hover.

## Use when

Use when one or a small number of data points must remain identifiable during inspection, comparison, or explanation.

## Avoid when

Avoid when many points need emphasis, when color already encodes another variable, or when emphasis could be mistaken for a larger value.

## States and behavior

Default, hovered or focused, selected, emphasized by the system, and cleared states; define precedence when these states overlap and preserve the underlying scale.

## Variants

Halo, outline, size lift, contrast dimming of peers, annotation, and connected highlight across coordinated charts.

## Platform notes

Pointer hover can preview emphasis; touch and keyboard need explicit focus or selection behavior and a reliable dismissal path.

## Accessibility and performance

Do not rely on color alone, expose the emphasized datum and reason in text, and update only affected marks in dense plots.

## Common confusions

Highlighting changes attention or selection state; it does not alter the datum, its rank, or the chart scale.

## Related patterns

[Chart Tooltip](chart-tooltip.md), [Chart Crosshair](../../interactions/data-visualization/chart-crosshair.md), and [Legend Filtering](../../interactions/data-visualization/legend-filtering.md).
