---
id: interactions.data-visualization.chart-zoom
name: Chart Zoom
name_zh: 图表缩放
kind: interaction-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [plot-zoom, domain-zoom, visualization-zoom, 数据域缩放]
tags: [chart, zoom, domain, navigation]
confidence: high
last_reviewed: 2026-09-09
---

# Chart Zoom

## Definition

An interaction changes the visible data domain so users can inspect a narrower or wider range without changing the underlying data.

## Problem solved

It makes local trends and dense marks inspectable when the full domain cannot show sufficient detail.

## Recognition cues

Axis ranges change, marks reproject into the plot, the current extent remains understandable, and a reset or zoom-out route is available.

## Use when

Use for large continuous domains, dense time series, maps, or plots where overview and local inspection are both necessary.

## Avoid when

Avoid when all relevant values already fit legibly, when domain changes would hide critical context, or when users could mistake zoom for data filtering.

## States and behavior

Overview, zooming, zoomed, panning, and reset states; clamp valid domains, preserve the gesture focal point, and keep axes and linked views synchronized.

## Variants

Pinch zoom, wheel zoom, button zoom, drag-to-zoom, overview navigator, and semantic zoom that changes representation by scale.

## Platform notes

Desktop wheel and drag behaviors need explicit modifier and pan rules; touch pinch must coexist with page scrolling and platform gestures.

## Accessibility and performance

Provide zoom controls and a reset action, announce the visible range, retain context for low-vision users, and avoid full data recomputation during continuous transforms.

## Common confusions

Zoom changes the visible domain; filtering changes which data belongs to the current view, and drill-down changes hierarchy or level of detail.

## Related patterns

[Brush Selection](brush-selection.md), [Data Drill-down](data-drill-down.md), and [Chart Crosshair](chart-crosshair.md).
