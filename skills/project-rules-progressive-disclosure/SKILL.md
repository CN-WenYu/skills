---
name: project-rules-progressive-disclosure
description: Use when organizing, refactoring, or adding long-lived project rules in AGENTS.md, CLAUDE.md, or similar agent instruction files. Applies progressive disclosure so entry files stay compact routers and detailed rules live in focused on-demand docs.
---

# Project Rules Progressive Disclosure

Use this skill when the task involves project instruction files such as `AGENTS.md`, `CLAUDE.md`, or docs that define agent-facing rules. The goal is to keep always-loaded context small while preserving all rules in discoverable places.

## Core Principle

Treat entry instruction files as routers, not warehouses.

- Keep high-frequency, long-lived, must-always-follow rules in the entry file.
- Keep `AGENTS.md` and `CLAUDE.md` limited to project-wide, general rules. Do not place instructions for an individual page, component, or module there; put those in the closest scope-specific child document and expose them through a short entry-file link with a clear read-when trigger.
- Before promoting a proposed rule that mentions a specific page, component, view, or module, first derive a semantics-preserving general rule. Add only that general rule to the entry file; keep the scoped condition in a child document. If it is unclear whether the abstraction preserves the intended constraint or what scope the rule needs, ask the user before editing either document.
- Move detailed, task-specific, or low-frequency rules into focused docs.
- Add short links from the entry file to those docs, with clear read-when triggers.
- Load only the minimum relevant docs for the current task.

## When To Use

Use this skill when the user asks to:

- Refactor or reduce a bloated `AGENTS.md`, `CLAUDE.md`, or equivalent file.
- Add a durable project rule but avoid making the entry file bigger.
- Create a docs/rules structure similar to Skills or progressive disclosure.
- Move command catalogs, architecture notes, data layout rules, testing workflows, UI rules, or tool-specific caveats into routed docs.
- Ensure multiple agents can find the same project rules without duplicating large content.

## Workflow

1. **Identify the entrypoints.** Read the nearest relevant `AGENTS.md` / `CLAUDE.md` / equivalent files before editing. If there are nested instruction files, nearest path wins for scoped work.
2. **Inspect the docs structure.** Prefer existing directories such as `docs/architecture/`, `docs/conventions/`, `docs/guides/`, `docs/superpowers/`, `.cursor/rules/`, or `.claude/` over inventing a new layout.
3. **Detect conflicts first.** Look for conflicting language rules, package managers, test commands, file length limits, data paths, safety rules, or tool preferences. Resolve from explicit user instruction, nearest entrypoint, and local evidence; ask only if unresolved and risky.
4. **Classify every rule.** Keep always-on rules in the entrypoint. Move details into docs when they are task-specific, long, example-heavy, command-heavy, or domain-specific.
5. **Design a read-on-demand map.** Each routed doc should have one clear responsibility and a trigger such as “read when modifying local data paths”. Avoid many tiny overlapping docs.
6. **Edit conservatively.** Preserve rule intent. Do not delete a rule because it is verbose; move it to the right doc. Do not bury safety-critical rules only in a routed doc.
7. **Validate preservation.** Check line counts, grep for representative keywords, reread the entrypoint, and verify future agents know which doc to open.

## Rule Classification

Keep in entry files:

- Language and communication defaults.
- Safety and destructive-command boundaries.
- Core tool preferences and verification requirements.
- Precedence rules and conflict resolution.
- Short docs index with read-when triggers.
- Critical repo-wide red lines, expressed briefly.

Move to focused docs:

- Architecture maps and data flow explanations.
- Local data directory ownership and cache/state/backup classification.
- Command catalogs and environment setup.
- Testing, build, release, and deployment workflows.
- UI, i18n, styling, modal, toast, or design-system details.
- Domain terminology, schemas, long examples, and troubleshooting notes.
- Historical plans/specs that are useful but not always-on.

## Preferred Entrypoint Shape

```md
# Agent Instructions

> Scope: This file is the lightweight entrypoint. Detailed task rules live in routed docs.

## Core Rules

- [language / behavior default]
- [safety boundary]
- [verification rule]
- [entrypoint is a router, not a warehouse]

## Read-On-Demand Index

| Task | Read | Trigger |
| --- | --- | --- |
| Architecture | `docs/architecture/README.md` | When changing module boundaries, data flow, or system design |
| Coding conventions | `docs/conventions/coding-style.md` | When editing source code or introducing shared patterns |
| Testing | `docs/conventions/testing.md` | When adding tests or choosing validation commands |
| Local data | `docs/architecture/local-data-layout.md` | When adding or moving local files, state, cache, backups, or logs |

## Priority

1. Current explicit user instruction.
2. Nearest scoped project instruction file.
3. This entrypoint.
4. Routed docs for the active task.
```

## Project-Agnostic Defaults

Apply these defaults unless the project entrypoint or user says otherwise:

- Preserve the project's existing docs layout and naming conventions.
- Prefer focused, durable docs over repeatedly appending long rules to entry files.
- Add only short references to `AGENTS.md`, `CLAUDE.md`, or equivalent entrypoints.
- Keep detailed examples, command catalogs, troubleshooting notes, and domain explanations in routed docs.
- When a repo has a graph/index/doc-generation command, attempt the command only if project instructions require it; if it fails, report the failure without inventing success.

## Validation Checklist

Before finishing a rules refactor or durable-rule addition:

- `wc -l` the edited entry files and new docs; ensure no file exceeds the project limit.
- Search for representative original-rule keywords across the entrypoint and routed docs.
- Confirm the entrypoint says when to read each new doc.
- Confirm no moved rule contradicts the entrypoint.
- Run only relevant tests for code changes; documentation-only changes usually need line/diff review rather than code tests.

## Guardrails

- Do not create auxiliary README/CHANGELOG files for a skill or rule refactor unless requested.
- Do not duplicate long rules in both `AGENTS.md` and `CLAUDE.md`; prefer one focused doc plus short links.
- Do not move secrets, auth paths, safety backups, or unrecoverable data into examples that imply they are disposable cache.
- Do not claim a skill or graph has been installed/updated unless the filesystem or command output confirms it.
