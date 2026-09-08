---
name: ui-pattern-advisor
description: Identify, explain, disambiguate, and recommend UI components, interaction patterns, animations, and motion effects from known terms, screenshots, recordings, vague descriptions, design tasks, or UI implementation context. Use this skill whenever the user asks what a UI pattern is called, what it does, which component or interaction fits a workflow, or how motion should support a state change, even when no professional term is provided. Do not use it for purely mechanical styling edits or when the component and behavior are already fully specified.
---

# UI Pattern Advisor

Use the bundled knowledge base to turn UI intent into precise language and defensible design choices. The goal is not to add motion by default; it is to preserve semantics, orientation, feedback, accessibility, and consistency with the product already being built.

## Start With Local Evidence

When a repository or design is available, inspect its existing components, design tokens, navigation conventions, accessibility behavior, and platform before recommending anything. Explicit requirements and established product patterns take precedence over the bundled reference library.

Treat screenshots and recordings as visual evidence only. They can reveal appearance and behavior, but not the exact source class, framework component, or implementation technique.

## Choose One Mode

### Explain

Use when the user supplies a known term. Read [references/catalog.md](references/catalog.md), then the matching knowledge card and relevant platform note. Return:

- canonical English and Chinese names;
- term status and confidence;
- definition and problem solved;
- use and avoid conditions;
- the closest commonly confused concepts.

### Reverse Lookup

Use when the user supplies an image, recording, code behavior, or approximate language. Search aliases, tags, recognition cues, and related patterns in the catalog and likely cards. Return the best match first, followed by no more than two alternatives when the evidence is ambiguous. Explain which visible or described cues support each candidate and state what additional observation would distinguish them.

### Recommend

Use when the user is designing or implementing UI but has not selected a component, interaction, or motion pattern. Determine:

1. the user's task and the semantic role of the control;
2. the state transition, trigger, frequency, reversibility, and input methods;
3. whether the existing design system already supplies the behavior;
4. whether motion adds feedback, spatial continuity, state clarity, or explanation;
5. accessibility, reduced-motion, keyboard, pointer, and performance constraints.

Recommend one primary pattern. Include alternatives only when a real ambiguity remains. "No animation" is the correct recommendation when motion has no functional purpose or would slow a frequent action.

## Read References On Demand

- Start with [references/catalog.md](references/catalog.md) for names, aliases, categories, and paths.
- Read [references/schema.md](references/schema.md) when interpreting term status, confidence, or taxonomy.
- Read `references/components/` for semantic controls and view structures.
- Read `references/interactions/` for gestures, selection, navigation, and action workflows.
- Read `references/motion/` for temporal behavior that can apply across components.
- Read `references/foundations/` for terminology, motion principles, accessibility, and performance.
- Read only the relevant file under `references/platforms/` after the target platform is known.

Do not load every reference file for a single question.

## Decision Boundary

Apply a low-risk recommendation directly only when the user has asked for implementation and the choice does not change product flow or information architecture. Explain and request confirmation before introducing a new navigation model, destructive gesture, hidden interaction, bulk-selection workflow, or other behavior with product consequences.

## Output

Keep naming questions concise. For design or implementation recommendations, provide:

1. **Selected pattern** — canonical name and semantic role.
2. **Why it fits** — evidence from the task, state, frequency, and existing UI.
3. **Behavior contract** — trigger, states, transition, interruption, and completion.
4. **Constraints** — platform, accessibility, reduced motion, and performance.
5. **Confidence** — high, medium, or low, with the unresolved ambiguity if any.
