---
id: interactions.data-visualization.legend-filtering
name: Legend Filtering
name_zh: 图例筛选
kind: interaction-pattern
term_status: common-informal
platforms: [ios, android, web]
aliases: [interactive-legend, series-toggle, legend-toggle, 图例切换]
tags: [chart, legend, filter, series]
confidence: high
last_reviewed: 2026-09-09
---

# Legend Filtering

## Definition

Legend items act as controls for showing, hiding, isolating, or restoring chart series or categories.

## Problem solved

It reduces visual competition and lets users compare selected series without leaving the chart context.

## Recognition cues

Legend items expose enabled state, activating an item changes visible marks, and disabled series remain discoverable for restoration.

## Use when

Use when a chart contains independently meaningful series that users may need to compare or isolate.

## Avoid when

Avoid when every series is required to interpret the whole, hiding data could mislead, or the legend lacks enough space to function as an accessible control group.

## States and behavior

All visible, subset visible, isolated, and restored states; preserve selection across related views when appropriate and define whether axes rescale after filtering.

## Variants

Binary series toggles, isolate-on-secondary-action, category filtering, and grouped legend controls.

## Platform notes

Pointer, touch, and keyboard activation should produce the same state; compact mobile layouts may move filters into a dedicated control surface while preserving legend meaning.

## Accessibility and performance

Expose each item as a named toggle with its current state, retain non-color identifiers, and avoid rebuilding unaffected chart layers.

## Common confusions

A legend explains visual encoding; legend filtering adds control behavior and must visibly communicate that affordance.

## Related patterns

[Data Point Highlight](../../components/data-visualization/data-point-highlight.md), [Chart Tooltip](../../components/data-visualization/chart-tooltip.md), and [Data Drill-down](data-drill-down.md).
