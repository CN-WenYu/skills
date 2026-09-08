# CN-WenYu Skills

[![skills.sh](https://skills.sh/b/CN-WenYu/skills)](https://skills.sh/CN-WenYu/skills)

English | [Simplified Chinese](README.md)

Reusable workflows and project-rule skills for AI coding agents. Each skill has a focused use case and can be installed and invoked on demand, without memorizing long prompts.

## Quick Start

List the installable skills:

```bash
npx skills@latest add CN-WenYu/skills --list
```

Install one skill for Codex:

```bash
npx skills@latest add CN-WenYu/skills \
  --skill decision-review \
  --agent codex \
  --yes
```

Install every skill for every agent detected by the CLI:

```bash
npx skills@latest add CN-WenYu/skills --all
```

Skills install into the current project by default. Use `--global` for a user-level installation or `--copy` to copy files instead of creating symlinks. See `npx skills@latest --help` for the complete CLI reference.

## Skill Catalog

| Skill | Use it when | Primary outcome |
| --- | --- | --- |
| [`problem-framing`](skills/problem-framing/SKILL.md) | A problem is vague, contradictory, or constrained by an existing practice | Goals, facts, assumptions, constraints, and the key next question |
| [`decision-review`](skills/decision-review/SKILL.md) | Architecture, product, or priority options have material tradeoffs | A conditional recommendation, key risks, and a minimal validation experiment |
| [`learn-clearly`](skills/learn-clearly/SKILL.md) | You need to understand a technical concept or mechanism | An intuitive explanation, technical model, and self-check questions |
| [`deconstruct-examples`](skills/deconstruct-examples/SKILL.md) | You need to analyze a page, product, workflow, proposal, or code example | Transferable principles, an operating checklist, and a low-risk trial |
| [`evidence-research`](skills/evidence-research/SKILL.md) | You need to verify facts, compare cases, or transfer an idea across domains | Traceable evidence, qualified conclusions, and open questions |
| [`project-rules-progressive-disclosure`](skills/project-rules-progressive-disclosure/SKILL.md) | You need to add, organize, or split durable project rules | A lightweight entrypoint and focused, on-demand reference documents |
| [`ui-pattern-advisor`](skills/ui-pattern-advisor/SKILL.md) | You need to identify, explain, or choose UI components, interactions, or motion | Canonical terms, disambiguation, and contextual recommendations |
| [`ui-knowledge-curator`](skills/ui-knowledge-curator/SKILL.md) | You want to persist UI knowledge from images, links, or text | A deduplicated, classified, and validated UI knowledge library |

## Using An Installed Skill

Explicitly name the skill and describe the task:

```text
Use $decision-review to compare these two architecture options.
Use $problem-framing to clarify why this bug is difficult to reproduce.
Use $evidence-research to verify this technical claim.
Use $ui-pattern-advisor to identify this interaction and recommend the right component.
Use $ui-knowledge-curator to organize this material into the UI knowledge library.
```

Agents that support automatic discovery can also select a skill from task semantics. Explicit invocation is best when you want to choose the thinking mode yourself.

## Maintaining Skills

Each skill is a directory and must include `SKILL.md`:

```text
skills/
  <skill-id>/
    SKILL.md
    agents/openai.yaml  # Optional UI name, description, and invocation prompt
    scripts/            # Optional reusable executable helpers
    references/         # Optional on-demand reference material
    assets/             # Optional assets used by generated output
```

The YAML front matter in `SKILL.md` must contain a `name` matching the directory and a clear, discriminating `description`. Keep only decision-changing guidance in the body. Put long, low-frequency workflows and reference material in `references/` and state when to read them.

`ui-pattern-advisor` is the single owner of UI knowledge. Its cards are organized by component, interaction, and motion and loaded through on-demand indexes; `ui-knowledge-curator` maintains those cards and writes to the source repository only when the user explicitly asks to collect or organize material.

## Publishing And Validation

1. Update files under `skills/<skill-id>/` and check names, descriptions, and reference paths.
2. Use the skill validator available to the repository to check front matter and unfinished scaffolding.
3. Commit and push to the default branch of `CN-WenYu/skills`. Installation commands read the remote version only.
4. Run `npx skills@latest add CN-WenYu/skills --list` to confirm discoverability; install a specific skill when an end-to-end check is needed.

Public repositories can be installed directly. Private repositories require the installer to have the corresponding GitHub access and credentials. See the [skills.sh documentation](https://www.skills.sh/docs) and [open-source implementation](https://github.com/vercel-labs/skills) for CLI behavior.

## Updating Or Removing An Installed Skill

```bash
npx skills@latest update project-rules-progressive-disclosure
npx skills@latest remove project-rules-progressive-disclosure
```
