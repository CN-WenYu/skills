# CN-WenYu Skills

[![skills.sh](https://skills.sh/b/CN-WenYu/skills)](https://skills.sh/CN-WenYu/skills)

供 AI 编码代理按需安装的可复用工作流与项目规范技能。

## 安装

本仓库的技能由 [skills.sh](https://www.skills.sh/) 的 CLI 直接从 GitHub 仓库发现和安装，无需另行发布 npm 包或提交注册表。

先查看仓库内可安装的技能：

```bash
npx skills@latest add CN-WenYu/skills --list
```

安装全部技能到 CLI 检测到的全部代理：

```bash
npx skills@latest add CN-WenYu/skills --all
```

只安装指定技能到 Codex：

```bash
npx skills@latest add CN-WenYu/skills \
  --skill project-rules-progressive-disclosure \
  --agent codex \
  --yes
```

默认安装到当前项目。加入 `--global` 可改为用户级安装；使用 `--copy` 可复制文件而非创建符号链接。可运行 `npx skills@latest --help` 查看本机 CLI 支持的代理标识和完整参数。

## 当前技能

| 技能 | 作用 |
| --- | --- |
| [`project-rules-progressive-disclosure`](skills/project-rules-progressive-disclosure/SKILL.md) | 将长期项目规则组织为“入口索引 + 按需加载的专题文档”，避免 `AGENTS.md`、`CLAUDE.md` 等入口文件膨胀。 |

## 维护与发布

每项技能均应采用下面的目录结构；目录名就是 `--skill` 使用的技能标识。

```text
skills/
  <skill-id>/
    SKILL.md
    scripts/        # 可选：可执行辅助脚本
    references/     # 可选：按需阅读的资料
    assets/         # 可选：可复用资源
```

`SKILL.md` 顶部必须包含 YAML front matter，至少提供稳定且唯一的 `name` 与清晰的 `description`。技能正文应说明适用场景、执行边界和验证方式；大段低频资料放入 `references/`，由正文明确指向，以减少代理加载的上下文。

```md
---
name: <skill-id>
description: <何时应使用此技能，以及它解决的问题>
---

# <技能标题>
```

要让新建或更新的技能可被其他人通过上述命令安装，只需完成以下发布链路：

1. 在本地新增或修改 `skills/<skill-id>/SKILL.md`，并检查 front matter 与目录名一致。
2. 提交并推送到 `CN-WenYu/skills` 的默认分支；安装命令读取的是 GitHub 上的版本，不会读取未推送的本地文件。
3. 确保仓库对安装者可访问。公开仓库可直接安装；私有仓库需要安装者具备相应的 GitHub 访问权限与 Git 凭据。
4. 用 `npx skills@latest add CN-WenYu/skills --list` 验证远端可发现性，再用带 `--skill <skill-id>` 的命令做一次实际安装验证。

skills.sh 会根据 CLI 的匿名安装遥测生成目录页与安装统计；没有单独的“上架”操作。README 顶部的徽章会在首次安装事件后显示统计数据。CLI 的行为与参数以 [skills.sh 文档](https://www.skills.sh/docs) 和 [开源实现](https://github.com/vercel-labs/skills) 为准。

## 更新与移除

已安装的技能可更新为 GitHub 上的最新版本：

```bash
npx skills@latest update project-rules-progressive-disclosure
```

移除指定技能：

```bash
npx skills@latest remove project-rules-progressive-disclosure
```
