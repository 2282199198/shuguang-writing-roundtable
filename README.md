# 曙光圆桌写作会议

一个采用 [Agent Skills 开放规范](https://agentskills.io/specification) 的中文知识型写作 Skill。它不是只给 Codex：同一份核心目录可供 Codex、Claude Code、Cursor、Gemini CLI、GitHub Copilot，以及其他兼容 Agent Skills 的宿主加载。

![六套公众号主题](docs/theme-gallery.png)

## 大白话说明

你可以把它理解成一位总编带着一组写作工序工作：先弄清文章写给谁、要解决什么，再决定是否查资料、怎样搭结构、哪些事实必须核验，最后根据公众号、短视频或普通文章的要求交付成品。

它不是简单“帮你润色”，也不会为了显得专业而机械跑完整流程。你只要改开头，它就只处理开头；你只要核查事实，它就不擅自改写观点；任务清楚时会直接成稿。

## 能做什么

- 从模糊想法完成选题、研究、提纲和长文。
- 把零散素材或已有草稿改成可发布内容。
- 单独调用选题、证据研究、风格画像、事实核查、读者审稿或平台改写。
- 局部修改并保护已经确认、不允许改动的内容。
- 生成知识型微信公众号长文、粘贴版 HTML 和手机预览。
- 自动选择六套公众号主题：曙光石墨、晨曦金、青墨书院、深海智蓝、暖纸手记、松石研究所。
- 在宿主具备 Python 和文件工具时，运行案卷、局部修订、交付文件和公众号 HTML 校验器。

## 输入与输出

可以输入一个想法、提纲、Markdown、已有稿件、合法可用的本地材料或网页链接。

根据任务输出成稿、圆桌决议、证据与待确认项、修改说明，以及当前宿主实际能生成的平台文件。公众号公开终稿默认不在文末堆参考资料，但内部证据台账仍保留来源；高风险内容或用户明确要求时可以公开来源。

## 一句话兼容结论

- **下载没有用户限制**：GitHub 公开仓库对所有人开放。
- **核心没有绑定模型**：`skills/shuguang-writing-roundtable` 遵循开放的 `SKILL.md + references + scripts + assets` 结构。
- **不同 Agent 的差别主要在安装目录和显式命令**：写作方法相同，加载方式不同。
- **工具能力决定交付上限**：没有联网工具就不能声称完成实时核查；没有文件工具就不能冒充生成了 DOCX 或 HTML 文件。
- **自动触发不是死口令**：关键词已写进 `description`，兼容宿主会按完整意图做语义判断；最确定的方法始终是直接点名 Skill。

`agents/openai.yaml` 只是 Codex/OpenAI 的可选界面元数据，其他宿主会忽略它，核心流程不依赖该文件。

## 安装

### 方法一：GitHub CLI 自动放到正确目录

GitHub CLI 2.90.0 及以上支持多种 Agent。建议先预览，再安装：

```text
gh skill preview 2282199198/shuguang-writing-roundtable shuguang-writing-roundtable
gh skill install 2282199198/shuguang-writing-roundtable shuguang-writing-roundtable --agent universal --scope user
```

`universal` 会使用跨宿主目录。也可以把它换成你实际使用的宿主：

```text
codex
claude-code
cursor
gemini-cli
github-copilot
```

例如安装到 Claude Code：

```text
gh skill install 2282199198/shuguang-writing-roundtable shuguang-writing-roundtable --agent claude-code --scope user
```

### 方法二：下载 ZIP 后手动复制

1. 在 GitHub 页面点击 `Code` → `Download ZIP`。
2. 解压后找到 `skills/shuguang-writing-roundtable`。
3. 把整个文件夹复制到你的 Agent 技能目录，不要只复制 `SKILL.md`。
4. 重新加载技能列表或新开会话。

| 宿主 | 常用用户级目录 | 常用项目级目录 |
|---|---|---|
| Codex | `~/.codex/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Cursor | `~/.cursor/skills/` 或 `~/.agents/skills/` | `.cursor/skills/` 或 `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` 或 `~/.agents/skills/` | `.gemini/skills/` 或 `.agents/skills/` |
| GitHub Copilot | `~/.copilot/skills/` 或 `~/.agents/skills/` | `.github/skills/`、`.claude/skills/` 或 `.agents/skills/` |

Windows 中的 `~` 就是当前用户文件夹。更完整的平台说明见 [宿主兼容与安装](skills/shuguang-writing-roundtable/references/host-compatibility.md)。

### 不支持 Agent Skills 的聊天工具

把 `SKILL.md` 与本次需要的参考文件上传或放入项目上下文，然后说“请按 shuguang-writing-roundtable 执行以下任务”。工作流仍可使用，但这不等于原生安装：它通常不会自动发现，也不能保证关键词触发。

## 怎么调用

跨平台都能理解的写法：

- “使用 `shuguang-writing-roundtable`，把这个想法写成知识型公众号长文。”
- “使用曙光圆桌写作会议，先定选题，再查证关键事实并完成文章。”
- “让写作专家团只开事实编辑席，核查数字和结论，不改我的观点。”

不同宿主还可能提供自己的显式命令：

| 宿主 | 常见明确调用 |
|---|---|
| Codex | `$shuguang-writing-roundtable` |
| Claude Code | `/shuguang-writing-roundtable` |
| Cursor | `/shuguang-writing-roundtable` 或技能选择器 |
| Gemini CLI | 直接点名；用 `/skills list` 检查是否发现 |
| GitHub Copilot | `/shuguang-writing-roundtable` 或直接点名 |

自然语言也可以触发，例如“写知识型公众号长文”“核查这篇文章的事实”“只改开头”“生成公众号粘贴版”。常用召回词包括：`曙光圆桌写作会议`、`圆桌写作`、`写作专家团`、`公众号长文`、`知识型长文`、`深度文章`、`定选题`、`搭大纲`、`找论据`、`事实核查`、`证据审计`、`审稿`、`局部改稿`、`公众号排版`、`微信粘贴版`、`手机预览`。

自然语言触发由各宿主和模型决定，不能保证百分之百一致。需要确定调用时，直接点名 Skill 或使用宿主的显式技能命令。

## Agent 工具不一样时怎么办

Skill 会按当前能力降级，而不是假装工具存在：

- 只有聊天能力：完成选题、结构、成稿和人工审稿。
- 有网页检索：增加时效核查、权威来源和证据台账。
- 有文件读写：读取素材包并交付真实 Markdown、HTML 或宿主支持的其他文件。
- 有 Python 3.10+：运行内置校验器；没有 Python 时明确标注“未运行机器校验”。
- 有图片工具：可以重做视觉背景；没有时直接使用包内七张现成背景。

任何宿主都不会因为安装本 Skill 而自动获得联网、账号登录、付费服务、图片生成或公众号发布能力。

## 公众号主题

主题目录位于 `skills/shuguang-writing-roundtable/assets/wechat-themes/`。七张背景图片已经随仓库提供，不需要联网生成；需要重新设计时，目录中也保留了 Image 2.0 提示词。

背景图片只是封面、开篇横幅或章节分隔的增强层。真实发布前仍应把采用的图片上传到公众号素材库；即使删除背景，正文结构也必须保持完整。

## 本地验证

全部脚本只依赖 Python 标准库。建议使用 Python 3.10 或更高版本：

```powershell
python -X utf8 -m unittest discover -s tests -v
python -X utf8 skills/shuguang-writing-roundtable/scripts/validate_theme_catalog.py
```

## 已验证范围

- Skill 入口符合 Agent Skills 的核心目录与 `name/description` 结构。
- 公开包独立测试通过。
- 六套主题与七张背景资产通过目录和图片检查。
- 微信兼容 HTML 通过两套机器校验。
- 使用真实知识型长文完成从成稿到公众号粘贴的人工验收。

这些结果证明核心工作流和交付链路可用，不代表已在每一种 Agent 宿主、版本和工具组合上完成真实运行测试，也不代表所有题材会自动达到相同质量。医学、法律、金融、政策、新闻等高影响内容仍需当前权威来源与人工判断。

## 重要边界

- 本项目是原创、非官方实现，与“得到”或“得到大脑”没有隶属、合作、兼容认证或授权关系。
- 仓库不包含任何专有系统提示词、课程、听书、电子书、账号能力、私人笔记或用户稿件。
- 不会自动登录平台、上传资料、安装依赖、发布文章或调用付费服务。
- `agents/openai.yaml`、某个平台的斜杠或美元符号命令都只是适配层，不是核心依赖。
- 宿主没有某项工具时必须降级交付并说明限制，不能虚构联网、文件、图片、测试或发布结果。

## 许可证

本项目采用 [MIT License](LICENSE)。单独安装的 Skill 目录也内置 `LICENSE.txt`。设计来源与第三方启发说明见 [provenance-and-limits.md](skills/shuguang-writing-roundtable/references/provenance-and-limits.md)。
