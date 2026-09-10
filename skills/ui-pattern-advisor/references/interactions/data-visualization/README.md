# Data Visualization Interaction Selection

Choose chart interaction from the user's task and the chart's data structure. Do not combine interactions merely because the charting library supports them.

| User task | Prefer | Key boundary |
| --- | --- | --- |
| Select a continuous interval or region | [Brush Selection](brush-selection.md) | Selection changes scope; it is not navigation by itself. |
| Align and compare values at one position | [Chart Crosshair](chart-crosshair.md) | Keep labels readable and avoid implying false precision. |
| Emphasize an important datum | [Data Point Highlight](../../components/data-visualization/data-point-highlight.md) | Emphasis must not alter the underlying value. |
| Inspect details for a datum | [Chart Tooltip](../../components/data-visualization/chart-tooltip.md) | Do not make hover the only access path. |
| Show, hide, or isolate series | [Legend Filtering](legend-filtering.md) | Preserve series state and chart scale predictably. |
| Inspect local structure in a dense domain | [Chart Zoom](chart-zoom.md) | Always expose the current domain and a reset path. |
| Move from an aggregate to its details | [Data Drill-down](data-drill-down.md) | Preserve hierarchy, context, and a route back. |

Combine patterns only when the tasks coexist and their gestures, focus, and state do not conflict. For example, a crosshair may drive a tooltip, while brush selection may define the domain shown by a linked detail chart.
