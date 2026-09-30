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
| [`svg-logo-to-lottie`](skills/svg-logo-to-lottie/SKILL.md) | 要按图片或 SVG Logo 的图形语义设计启动页动画 | AI 分析编排、真实粗体字标、可复用时间轴和 Lottie 预览 |
| [`image-to-svg`](skills/image-to-svg/SKILL.md) | 要把 PNG、JPEG 或 WebP 转成可编辑 SVG 路径，且背景处理不能靠固定假设 | 默认保留素材，外观变更先确认，验证颜色、轮廓和透明度 |
| [`ui-pattern-advisor`](skills/ui-pattern-advisor/SKILL.md) | 要识别、解释或选择 UI 组件、交互与动效 | 规范术语、模式消歧和场景化推荐 |
| [`ui-knowledge-curator`](skills/ui-knowledge-curator/SKILL.md) | 要把图片、链接或文字中的 UI 知识持久化 | 去重、分类并校验后的 UI 知识库 |

## 安装后如何使用

可显式引用技能名称并描述当前问题：

```text
Use $decision-review to compare these two architecture options.
Use $problem-framing to clarify why this bug is difficult to reproduce.
Use $evidence-research to verify this technical claim.
Use $ui-pattern-advisor to identify this interaction and recommend the right component.
Use $ui-knowledge-curator to organize this material into the UI knowledge library.
Use $image-to-svg to convert this raster artwork into editable SVG paths with evidence-based background handling.
```

技能也可由支持自动发现的代理按任务语义选择。明确调用更适合希望指定思考方式的场景。

## Logo 动画与图片转换

在应用项目中直接说“帮我做一个启动页动画”“给这个 App 做开屏动效”或“让启动 Logo 动起来”即可触发，无需先提供 SVG 或说出 Lottie。技能先检查项目；缺少 Logo、显示名称或主题资料时明确说明缺项，再询问必要信息，不编造品牌素材。

非项目场景直接提供 Logo 和应用名称即可开始。技能检查素材后列出可直接回答的必要问题及字体候选，不只回复“等待确认”；缺少 HarfBuzz 时仍可用 FontTools 列出本机字体，并明确整形尚未验证。安装授权与视觉选择分开处理，不因缺少动画依赖而省略询问。

图片输入需要同时安装 `svg-logo-to-lottie` 和 `image-to-svg`；纯 SVG 输入只需动画技能。安装时分别指定这两个 `--skill` 名称。技能组合通过显式转换脚本路径连接，不依赖安装目录相邻。

由 AI 结合实际图形、名称、应用语义和阅读层级，统一分析图标与文字的动作关系，再提出整体编排。文字支持整行或独立字形组的二维位移、缩放、透明度与时间轴；跳跃、上浮、渐入、字距收拢、定向揭示保留为可选配方，不是固定问卷，也不默认推荐跳跃。连写文字、连字和组合字符保持完整；光束、通用遮罩与文字散出循环暂不支持，不将普通揭示冒充扫光。

优先使用调用方 Agent 的内置提问工具，按其实际能力处理编号、自由输入与选项上限：不重复工具已有的编号或“自定义／其他”入口，不在题干再列一遍选项。没有可用工具时才用简短编号文本让用户选择，并允许直接描述其他想法。只询问影响结果的未定事项；整体方案已包含并确认文字动作时，不再单独追问。默认制作一版，不把预览数量设为必答题。异步问答须等待实际回答，超时不代表接受推荐；失败或问题不可见时改用可见文本提问。

先读取项目实际使用的 Logo、名称、字体与启动页主题配置；可靠信息直接复用，缺失时合并询问圆角、文字颜色和少量相关的本机字体候选。主题色不会直接被当成文字颜色。用户要求逐项确认、素材保真变更及缺失依赖安装的授权边界保持有效。文字配置必须明确指定预设或自主时间轴；旧配置若已明确选择跳跃，可补入 `preset: hop`，不因字段缺失猜测用户意图。

未指定字号与间距时，分别按最终图标宽度的 18% 与 12% 计算：400 宽图标对应字号 72、间距 48。间距指停稳后的可见边缘距离，跳跃空间单独校验；用户或项目明确值优先。每个离线预览内置 JSON 下载，验证下载内容与交付文件一致。
下载文件名使用已确认的应用名称，统一为小写下划线格式并以 `_loading.json` 结尾；例如 `Example App` 生成 `example_app_loading.json`。没有可靠应用名称时先询问，不使用 Logo 文件名代替。

项目启动页明确支持深浅主题时默认提供两种主题预览；导出颜色不同则生成各自的 JSON。可另外选择是否制作第二种动画编排，避免自动堆叠大量方案。多版使用 `compare` 生成统一入口，默认滚动浏览，空间充足时多列、窄屏单列；用 `--group` 将同一方案的深浅主题配对，支持组内一起重播和单独打开，避免挤压或裁切画布。分享时需保留对比页与各版目录的相对位置。颜色、字体与圆角来源需说明；复用已选文字动效或明确的委托，不重复询问，也不把默认推荐当成用户已选择。

导出默认精简冗余关键帧和数值写法，并报告 JSON 体积分布；坐标舍入需明确选择，保留颜色、时间和缓动精度。近似版本须与未舍入版本进行 Web 画面对比后再确认，交付仍为直接可用的 JSON。

支持独立图层时间轴、开放描边绘制和基础矢量渐变；不自动拟合图片渐变或复杂抠图。依赖使用隔离 Python、固定版本 Lottie Web／Playwright；图片转换另需 VTracer 与 SVG 渲染器，不会自动安装。当前验证覆盖 Web，Android／iOS 需另行验证。

按需阅读[编排与能力边界](skills/svg-logo-to-lottie/references/motion-design.md)、[背景与圆角](skills/svg-logo-to-lottie/references/backgrounds-and-svg.md)、[文字配置与导出流程](skills/svg-logo-to-lottie/references/lottie-export.md)和[图片转换说明](skills/image-to-svg/references/conversion.md)。

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

`ui-pattern-advisor` 是 UI 知识的唯一所有者。其知识卡片按组件、交互和动效分层，并通过目录索引按需读取；`ui-knowledge-curator` 负责维护这些卡片，只在用户明确要求收录或整理资料时写入源仓库。

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
