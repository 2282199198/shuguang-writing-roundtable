# 宿主兼容与安装

## 核心结论

本 Skill 的核心是开放的 Agent Skills 目录：`SKILL.md`、`references/`、`scripts/` 和 `assets/`。写作流程不依赖特定模型、子 Agent、浏览器、图片模型或发布平台。`agents/openai.yaml` 只是 Codex/OpenAI 界面的可选增强；其他宿主可以忽略它。

自动触发由宿主根据 `SKILL.md` 的 `description` 进行语义判断，关键词是召回信号，不是所有宿主都执行的机械口令。需要确定调用时，直接说“使用 shuguang-writing-roundtable”或使用宿主自己的技能命令。

## 常见宿主

`~` 表示当前用户目录。优先使用各宿主当前版本支持的安装命令；手动复制时，把整个 `shuguang-writing-roundtable` 文件夹放入下列目录，而不是只复制 `SKILL.md`。

| 宿主 | 用户级目录 | 项目级目录或共享目录 | 明确调用 |
|---|---|---|---|
| Codex | `~/.codex/skills/` | `.agents/skills/` | `$shuguang-writing-roundtable` 或直接点名 |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | `/shuguang-writing-roundtable` 或直接点名 |
| Cursor | `~/.cursor/skills/`、`~/.agents/skills/` | `.cursor/skills/`、`.agents/skills/` | `/shuguang-writing-roundtable` 或技能选择器 |
| Gemini CLI | `~/.gemini/skills/`、`~/.agents/skills/` | `.gemini/skills/`、`.agents/skills/` | 直接点名；用 `/skills list` 检查发现状态 |
| GitHub Copilot | `~/.copilot/skills/`、`~/.agents/skills/` | `.github/skills/`、`.claude/skills/`、`.agents/skills/` | `/shuguang-writing-roundtable` 或直接点名 |

GitHub CLI 2.90.0 及以上可把同一份 Skill 安装到不同宿主。先预览，再把 `<agent>` 替换为 `codex`、`claude-code`、`cursor`、`gemini-cli`、`github-copilot` 或 `universal`：

```text
gh skill preview 2282199198/shuguang-writing-roundtable shuguang-writing-roundtable
gh skill install 2282199198/shuguang-writing-roundtable shuguang-writing-roundtable --agent <agent> --scope user
```

安装或更新后，按宿主机制重新加载技能列表或新开会话。不要承诺“复制链接后所有聊天网站都会自动安装”；只有实现 Agent Skills 规范或允许加载本地指令目录的宿主才能自动发现。

## 工具能力降级

先盘点当前宿主能做什么，再选择交付：

| 当前能力 | 可以完成 | 缺失时怎么做 |
|---|---|---|
| 仅有对话模型 | 选题、结构、写作、人工审稿、基于已提供材料的分析 | 不声称查过外部事实或生成了真实文件 |
| 网页检索或浏览 | 时效信息、事实核查、证据台账 | 缩小结论，标为未核实，并列出最小待查项 |
| 本地文件读取 | 处理稿件、素材包、参考文件 | 请用户粘贴或上传必要内容 |
| 文件写入 | 交付 Markdown、HTML、DOCX 等宿主实际支持的文件 | 在对话中交付正文，并明确没有生成文件 |
| 终端与 Python 3.10+ | 运行内置校验器和公众号预览脚本 | 做人工质量检查，标注“未运行机器校验” |
| 图片生成工具 | 重新设计主题背景 | 使用包内现成背景，或交付可执行的图片提示词 |

无论宿主有什么工具，都不得自动登录账号、上传私人材料、安装依赖、付费调用、发布文章或扩大外部权限。需要这些动作时先取得用户明确同意。

## 不支持 Agent Skills 的宿主

仍可把 `SKILL.md` 和本次会用到的 `references/` 文件上传或放入项目上下文，并明确说“请按 shuguang-writing-roundtable 执行以下任务”。这种方式能复用工作流，但通常没有自动发现、按需加载和稳定关键词触发；不要把它宣传成原生安装。

## 官方规范入口

- Agent Skills 开放规范：<https://agentskills.io/specification>
- Claude Code Skills：<https://code.claude.com/docs/en/skills>
- Cursor Skills：<https://cursor.com/docs/skills>
- Gemini CLI Skills：<https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md>
- GitHub Copilot Skills：<https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills>
- GitHub CLI `gh skill install`：<https://cli.github.com/manual/gh_skill_install>
