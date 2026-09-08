# Web Mapping

Start with native HTML semantics and accessible headless primitives when they satisfy the required behavior. A visual dropdown may be a `select`, menu button, combobox, disclosure, or popover; choose by semantics before styling.

- Preserve keyboard navigation, focus management, accessible names, roles, states, and escape/outside-click behavior.
- Use CSS transitions or animations for predetermined motion and a suitable interaction library for gesture-driven or interruptible motion already supported by the project.
- Respect `prefers-reduced-motion` and gate hover-only behavior for devices that actually support hover.
- Prefer transform and opacity for continuous animation and test under realistic rendering load.
- Treat View Transitions, popover APIs, and browser-specific behavior as version-dependent; verify target-browser support before relying on them.
