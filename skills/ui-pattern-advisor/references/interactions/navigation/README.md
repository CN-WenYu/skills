# Scroll And Navigation Interaction Selection

Choose a scroll-linked pattern from the content relationship and the user's reading task. Scroll remains the source of navigation progress; visual motion should explain structure rather than replace accessible content.

| User task | Prefer | Key boundary |
| --- | --- | --- |
| Introduce one focal product by progressively opening or assembling it | [Scroll-driven Opening](scroll-driven-opening.md) | One reversible reveal should lead into readable content. |
| Inspect a finite sequence horizontally while continuing vertical page progress | [Scroll-driven Horizontal Section](scroll-driven-horizontal-section.md) | The section must release at the real end and retain a non-scrubbed fallback. |
| Explain the internal structure of one product or system | [Scroll-driven Exploded View](scroll-driven-exploded-view.md) | Separate parts in a deliberate order without implying a false physical model. |
| Preserve recent cards as later cards overlap them | [Stacked Card Scroll](stacked-card-scroll.md) | Each card must remain identifiable and reachable. |
| Make a navigation transition follow a direct gesture | [Gesture-driven Transition](gesture-driven-transition.md) | Completion and cancellation follow distance, velocity, and platform gesture arbitration. |

Use one primary scroll-linked narrative per section. Keep text and semantic reading order independent of visual pinning, derive progress from measured section bounds, and make reverse scrolling reconstruct the same states in reverse.
