---
id: interactions.data-visualization.brush-selection
name: Brush Selection
name_zh: 图表框选
kind: interaction-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [chart-brush, range-brushing, interval-selection, 框选]
tags: [chart, selection, range, brush]
confidence: high
last_reviewed: 2026-09-09
---

# Brush Selection

## Definition

A drag or multi-point gesture selects a continuous interval or region in a visualization.

## Problem solved

It lets users focus, compare, filter, or coordinate analysis around a bounded subset of data.

## Recognition cues

A translucent band or box follows the gesture, selected bounds remain visible, and linked views may update from the selected range.

## Use when

Use when selecting a time span, numeric interval, or spatial region is itself meaningful to the task.

## Avoid when

Avoid for choosing isolated points, on charts too small for accurate dragging, or when the same gesture already pans the chart without a clear mode distinction.

## States and behavior

Idle, selecting, selected, adjusting, and cleared states; clamp bounds to the plot, support handle adjustment, and expose how to clear or apply the range.

## Variants

Horizontal interval brush, vertical range brush, rectangular brush, lasso selection, and linked-view brushing.

## Platform notes

Desktop commonly uses drag; touch interfaces need adequate handles or an explicit selection mode to avoid conflict with scrolling and zooming.

## Accessibility and performance

Provide keyboard or form controls for exact bounds, announce the selected range, and throttle linked updates during continuous movement.

## Common confusions

Zoom changes the visible domain; brushing primarily selects data, even when a later action uses that selection to zoom.

## Related patterns

[Chart Zoom](chart-zoom.md), [Data Point Highlight](../../components/data-visualization/data-point-highlight.md), and [Chart Crosshair](chart-crosshair.md).
