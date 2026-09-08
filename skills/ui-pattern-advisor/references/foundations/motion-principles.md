# Motion Principles

Motion earns its place by providing feedback, preserving spatial continuity, clarifying state, preventing a jarring change, or explaining an unfamiliar interaction. Decoration alone is not enough for frequently used UI.

Evaluate motion in this order:

1. Identify the user's action and the state change.
2. Decide whether motion adds information.
3. Preserve the spatial origin and destination of persistent objects.
4. Keep user-driven motion interruptible and continuous with gesture velocity.
5. Prefer transform and opacity for smooth rendering; avoid repeated layout work.
6. Shorten and simplify motion as interaction frequency increases.
7. Provide a reduced-motion form that keeps essential state feedback.

Do not prescribe a duration, curve, or spring value without considering element size, distance, platform conventions, input method, and existing product tokens.
