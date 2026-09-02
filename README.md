# CN-WenYu Skills

[![skills.sh](https://skills.sh/b/CN-WenYu/skills)](https://skills.sh/CN-WenYu/skills)

[English](README.en.md) | 简体中文

面向 AI 编码代理的可复用工作流与项目规范技能。每个技能聚焦一个明确的工作场景，可按需安装和调用，无需记住长提示词。

## 快速开始

先查看可安装的技能：

```bash
npx skills@latest add CN-WenYu/skills --list
```

安装一个技能到 Codex：

```bash
npx skills@latest add CN-WenYu/skills \
  --skill decision-review \
  --agent codex \
  --yes
```

安装全部技能到 CLI 检测到的全部代理：

```bash
npx skills@latest add CN-WenYu/skills --all
```

默认安装到当前项目。使用 `--global` 安装到用户级目录，使用 `--copy` 复制文件而非创建符号链接。完整参数以 `npx skills@latest --help` 为准。

## 技能目录

| 技能 | 适用场景 | 产出重点 |
| --- | --- | --- |
| [`problem-framing`](skills/problem-framing/SKILL.md) | 问题模糊、矛盾，或被既有做法限制 | 目标、事实、假设、约束和关键后续问题 |
| [`decision-review`](skills/decision-review/SKILL.md) | 架构、产品或优先级存在真实取舍 | 有条件的推荐、关键风险和最小验证实验 |
| [`learn-clearly`](skills/learn-clearly/SKILL.md) | 需要理解技术概念或运行机制 | 直觉解释、专业机制与自检问题 |
| [`deconstruct-examples`](skills/deconstruct-examples/SKILL.md) | 要分析页面、产品、流程、方案或代码案例 | 可迁移原则、操作清单和低风险试做 |
| [`evidence-research`](skills/evidence-research/SKILL.md) | 需要核查事实、比较案例或跨领域借解 | 可追溯证据、限定结论与待确认问题 |
| [`project-rules-progressive-disclosure`](skills/project-rules-progressive-disclosure/SKILL.md) | 要新增、整理或拆分长期项目规则 | 轻量入口规则与按需读取的专题文档 |

## 安装后如何使用

可显式引用技能名称并描述当前问题：

```text
Use $decision-review to compare these two architecture options.
Use $problem-framing to clarify why this bug is difficult to reproduce.
Use $evidence-research to verify this technical claim.
```

技能也可由支持自动发现的代理按任务语义选择。明确调用更适合希望指定思考方式的场景。

## 维护技能

每个技能以目录为单位，并至少包含 `SKILL.md`：

```text
skills/
  <skill-id>/
    SKILL.md
    agents/openai.yaml  # 可选：界面名称、简介和默认调用提示
    scripts/            # 可选：可复用的可执行辅助工具
    references/         # 可选：按需读取的专题资料
    assets/             # 可选：生成物使用的资源
```

`SKILL.md` 的 YAML front matter 必须包含与目录一致的 `name` 和清晰、可区分的 `description`。正文仅保留会改变代理决策的说明；低频的长流程或参考资料放到 `references/`，并在正文中说明读取时机。

## 发布与验证

1. 更新 `skills/<skill-id>/` 下的技能文件，并检查名称、描述和引用路径。
2. 使用仓库可用的技能校验器检查 front matter 和未完成的脚手架内容。
3. 提交并推送到 `CN-WenYu/skills` 的默认分支。安装命令只会读取远端版本。
4. 运行 `npx skills@latest add CN-WenYu/skills --list` 确认可发现性；需要时安装指定技能进行实际验证。

公开仓库可直接安装；私有仓库要求安装者具有对应的 GitHub 访问权限与凭据。skills.sh 的 CLI 行为以 [官方文档](https://www.skills.sh/docs) 和 [开源实现](https://github.com/vercel-labs/skills) 为准。

## 更新或移除已安装的技能

```bash
npx skills@latest update project-rules-progressive-disclosure
npx skills@latest remove project-rules-progressive-disclosure
```
