---
id: interactions.data-visualization.data-drill-down
name: Data Drill-down
name_zh: 数据下钻
kind: interaction-pattern
term_status: standard
platforms: [ios, android, web]
aliases: [drill-down, hierarchical-drill-down, detail-drill, 数据钻取]
tags: [chart, hierarchy, navigation, detail]
confidence: high
last_reviewed: 2026-09-09
---

# Data Drill-down

## Definition

Selecting an aggregate navigates or transforms the view to reveal its underlying members or a more detailed hierarchical level.

## Problem solved

It connects summary analysis to explanation while preserving the relationship between parent and child data.

## Recognition cues

An aggregate mark has a detail affordance, activation changes hierarchy or granularity, and breadcrumbs, labels, or back controls retain context.

## Use when

Use when data has a meaningful hierarchy and users need to investigate what contributes to an aggregate.

## Avoid when

Avoid for flat data, when a tooltip already contains the needed detail, or when hierarchy and navigation state cannot be communicated clearly.

## States and behavior

Summary, loading detail, detailed level, deeper level, back, and error states; preserve filters, label the current level, and restore the prior context on return.

## Variants

In-place drill-down, linked detail panel, navigation to a detail page, and drill-through to related records.

## Platform notes

Use familiar navigation and back behavior for the platform; compact screens often benefit from a dedicated detail view rather than replacing an already dense chart in place.

## Accessibility and performance

Expose expandable or navigable semantics, move focus to the new context, announce level changes, and retain a non-visual path through the hierarchy.

## Common confusions

Zoom reveals the same data at a narrower domain; drill-down changes the level of aggregation or traverses a hierarchy.

## Related patterns

[Chart Tooltip](../../components/data-visualization/chart-tooltip.md), [Chart Zoom](chart-zoom.md), and [Legend Filtering](legend-filtering.md).
