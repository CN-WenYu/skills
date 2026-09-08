# Android Mapping

Prefer Material and project design-system semantics before custom visuals. Confirm whether the project uses Views or Compose and reuse its established state and animation primitives.

- Distinguish navigation tabs, segmented buttons, exposed dropdown menus, menus, and editable autocomplete fields by task rather than shape.
- Shared-element and container-transform approaches depend on navigation architecture and toolkit version.
- Preserve TalkBack semantics, focus order, minimum touch targets, back behavior, and system animation-scale preferences.
- Gesture interactions must coexist with scrolling, predictive back, nested containers, and accessibility actions.
- Test frame pacing and interruption on a representative device; compilation does not establish motion quality.
