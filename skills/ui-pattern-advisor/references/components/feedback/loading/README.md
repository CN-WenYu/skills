# Loading Feedback

Choose loading feedback from what is known about duration and progress, and from whether existing content can remain usable.

| Situation | Preferred pattern | Why |
| --- | --- | --- |
| Progress is unknown and the wait is short | [Spinner](spinner.md) or [Indeterminate Progress](indeterminate-progress.md) | Shows ongoing work without inventing precision |
| A measurable fraction is available | [Determinate Progress](determinate-progress.md) | Communicates advancement and remaining work |
| A content layout is known before data arrives | [Skeleton Screen](skeleton-screen.md) | Preserves structure and perceived continuity |
| The user explicitly refreshes existing content | [Pull to Refresh](pull-to-refresh.md) | Connects the gesture to the refresh lifecycle |

Prefer keeping useful existing content visible. Do not replace stable content with a full-screen indicator merely because a background request started. Loading feedback must end in content, empty, error, cancellation, or retry rather than remaining indefinitely.
