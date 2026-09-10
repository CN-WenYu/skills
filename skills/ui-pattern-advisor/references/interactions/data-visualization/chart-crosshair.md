---
id: interactions.data-visualization.chart-crosshair
name: Chart Crosshair
name_zh: 图表十字线
kind: interaction-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [crosshair-cursor, chart-cursor, guideline-cursor, 十字线]
tags: [chart, cursor, comparison, values]
confidence: high
last_reviewed: 2026-09-09
---

# Chart Crosshair

## Definition

One or two guide lines track an input position and align it with values on chart axes or series.

## Problem solved

It helps users read and compare values that are difficult to align visually across a plot.

## Recognition cues

Vertical or horizontal guides intersect the plot, snap or interpolate along the domain, and coordinate axis labels or value readouts.

## Use when

Use for dense time series, multi-series comparison, or charts where precise alignment matters more than selecting a region.

## Avoid when

Avoid on sparse charts with direct labels, when interpolation would imply unsupported precision, or when the guides obscure the data.

## States and behavior

Inactive, tracking, snapped or interpolated, pinned, and dismissed states; define how the cursor chooses values between samples and keep all readouts synchronized.

## Variants

Vertical cursor, full crosshair, nearest-point snap, free cursor, and pinned comparison cursor.

## Platform notes

Hover can track continuously on desktop; touch usually needs press-and-drag, tap-to-pin, or another gesture that coexists with page scrolling.

## Accessibility and performance

Offer keyboard stepping and a textual value summary, maintain sufficient guide contrast, and avoid recomputing the entire chart on every pointer event.

## Common confusions

A crosshair establishes alignment; a tooltip presents details and may be driven by a crosshair without being the same pattern.

## Related patterns

[Chart Tooltip](../../components/data-visualization/chart-tooltip.md), [Data Point Highlight](../../components/data-visualization/data-point-highlight.md), and [Brush Selection](brush-selection.md).
