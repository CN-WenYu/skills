# Accessibility And Performance

Every component and interaction must expose its semantic role, current state, available action, and result independently of animation. Motion may reinforce a change but cannot be the only signal.

Check:

- keyboard and assistive-technology operation;
- focus placement after navigation, disclosure, deletion, and reordering;
- adequate target size and alternatives to precision gestures;
- reduced-motion behavior that removes large translation, parallax, deformation, and repeated movement while retaining state clarity;
- cancellation and interruption for gesture-driven effects;
- transform and opacity before layout-affecting properties for continuous animation;
- real-device or representative-browser testing for frame pacing and input latency.

Never replace a native semantic control with a visually similar custom view unless the custom implementation preserves the complete interaction and accessibility contract.
