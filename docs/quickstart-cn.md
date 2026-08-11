# 曙光圆桌写作会议：小白快速开始

这份指南给第一次安装 Skill、也不熟悉 GitHub 和命令行的用户。你不需要懂编程。

## 先选一种安装方法

### 方法 A：直接下载 ZIP，最容易

1. 点击下载：[v1.1.1 源码 ZIP](https://github.com/2282199198/shuguang-writing-roundtable/archive/refs/tags/v1.1.1.zip)。
2. 解压 ZIP。
3. 打开解压后的 `skills` 文件夹。
4. 找到完整文件夹 `shuguang-writing-roundtable`。
5. 把这个完整文件夹复制到你使用的 Agent 的技能目录。
6. 重新打开 Agent，或者新建一个会话。

不要只复制 `SKILL.md`。完整文件夹里还有校验脚本、公众号排版规则、主题图片和宿主说明。

### 常见 Agent 的技能目录

Windows 中，“用户主目录”就是你登录电脑后自己的文件夹。可以在文件资源管理器地址栏输入 `%USERPROFILE%` 后回车打开。

| 你使用的工具 | 建议复制到 |
|---|---|
| Codex | `用户主目录\.codex\skills\` |
| Claude Code | `用户主目录\.claude\skills\` |
| Cursor | `用户主目录\.cursor\skills\` 或项目里的 `.agents\skills\` |
| Gemini CLI | `用户主目录\.gemini\skills\` 或项目里的 `.agents\skills\` |
| GitHub Copilot | `用户主目录\.copilot\skills\` 或项目里的 `.github\skills\` |

复制完成后的正确结构应该像这样：

```text
技能目录/
└── shuguang-writing-roundtable/
    ├── SKILL.md
    ├── LICENSE.txt
    ├── agents/
    ├── references/
    ├── scripts/
    └── assets/
```

如果你的工具没有“技能目录”或不支持 Agent Skills，请看本文后面的“不支持 Agent Skills 怎么办”。

### 方法 B：使用 GitHub CLI，一条命令安装

已经安装 GitHub CLI 2.90 或更高版本的用户，可以运行：

```powershell
gh skill preview 2282199198/shuguang-writing-roundtable shuguang-writing-roundtable
gh skill install 2282199198/shuguang-writing-roundtable shuguang-writing-roundtable --agent universal --scope user
```

如果只想安装固定的 v1.1.1：

```powershell
gh skill install 2282199198/shuguang-writing-roundtable shuguang-writing-roundtable@v1.1.1 --agent universal --scope user
```

`universal` 可以替换成：

- `codex`
- `claude-code`
- `cursor`
- `gemini-cli`
- `github-copilot`

## GitHub 验证码在哪里

如果 GitHub 页面显示“Authorize your device”并要求输入八位代码，这通常不是邮箱验证码。

代码会显示在刚刚发起登录的终端、命令行窗口或应用里。操作顺序是：

1. 回到刚刚执行 GitHub 登录或安装操作的窗口。
2. 找到类似 `ABCD-EFGH` 的代码。
3. 把它输入 GitHub 授权页面。
4. 确认当前登录的是你自己的 GitHub 账号，再继续授权。

不要使用别人发给你的代码，也不要把代码、Token 或密码发给任何人。

如果找不到代码，最简单的办法是关闭授权页面，改用上面的 ZIP 下载方法。下载公开仓库不要求你提供邮箱验证码。

## 如何确认已经安装成功

安装后重新打开 Agent，或者新建一个会话，然后直接说：

> 使用曙光圆桌写作会议，把下面的想法整理成一篇知识型公众号长文。

也可以使用英文技能名：

> 使用 shuguang-writing-roundtable，先帮我定选题和大纲。

不同宿主可能还提供显式命令：

| 宿主 | 可以尝试 |
|---|---|
| Codex | `$shuguang-writing-roundtable` |
| Claude Code | `/shuguang-writing-roundtable` |
| Cursor | `/shuguang-writing-roundtable` 或技能选择器 |
| Gemini CLI | 直接点名；用 `/skills list` 查看是否发现 |
| GitHub Copilot | `/shuguang-writing-roundtable` 或直接点名 |

只要 Agent 能读取 Skill，它就应该按照“明确读者与目标 → 选择模式 → 研究和证据 → 结构与写作 → 审校与交付”的流程处理，而不是只做普通润色。

## 关键词可以怎么说

不需要背口令。以下说法都可以尝试：

- “召开曙光圆桌写作会议。”
- “让写作专家团处理这篇稿子。”
- “把这个想法写成知识型公众号长文。”
- “先定选题、搭大纲，再找论据。”
- “只核查事实，不要改我的文章。”
- “只修改开头，其他段落不要动。”
- “生成公众号微信粘贴版和手机预览。”

自然语言是否自动触发由你使用的 Agent 和模型决定，不能保证每个平台百分之百一致。最稳妥的方法是直接说“使用曙光圆桌写作会议”或使用宿主的显式技能命令。

## 三个可以直接复制的任务

### 写一篇新文章

```text
使用曙光圆桌写作会议。
主题：AI 时代应该怎样培养孩子的未来竞争力。
读者：小学生家长。
载体：知识型公众号长文。
要求：先提出核心判断，再完成文章；不要编造数据和案例。
```

### 审核已有文章

```text
使用曙光圆桌写作会议，只做事实核查和逻辑审稿。
不要直接改写全文。请列出必须修改、建议修改和证据不足的位置。
下面是文章：
……
```

### 生成公众号最终版

```text
使用曙光圆桌写作会议，把下面文章整理成公众号最终版。
选择适合知识型内容的主题，交付干净微信粘贴版和手机预览版。
公开正文不要在文末显示参考资料列表，但内部仍要保留证据台账。
下面是文章：
……
```

## 常见问题

### 1. Agent 说找不到这个 Skill

依次检查：

1. 是否复制了完整的 `shuguang-writing-roundtable` 文件夹；
2. `SKILL.md` 是否正好位于这个文件夹第一层；
3. 是否放进了当前 Agent 支持的技能目录；
4. 是否重新打开 Agent 或新建会话；
5. 是否直接说了“使用 shuguang-writing-roundtable”。

### 2. 下载后不能自动触发

自动触发不是固定快捷键。先使用完整中文名称或英文技能名明确调用。如果明确调用仍然无效，当前工具可能没有实现 Agent Skills 自动加载。

### 3. Agent 没有生成 HTML、图片或文件

Skill 不会给 Agent 增加原本没有的工具。只有当前 Agent 具备文件、终端、浏览器或图片能力时，才能生成并验证对应文件。工具不足时，它应该交付正文和操作说明，并明确哪些机器校验没有运行。

### 4. 能不能自动登录公众号并发布

不能。安装 Skill 不等于获得你的公众号账号权限。登录、上传图片、保存草稿或正式发布都需要你明确授权，并且当前 Agent 必须具备相应工具。

### 5. 为什么安装时出现安全提醒

GitHub CLI 可能提示第三方 Skill 未经 GitHub 验证。这是统一的安全提醒，不代表本 Skill 安装失败。你应该先用 `gh skill preview` 查看内容；本仓库不包含账号凭据、私人稿件或自动发布操作。

## 不支持 Agent Skills 怎么办

仍然可以使用，但不会自动发现：

1. 把 `SKILL.md` 和任务需要的 `references/` 文件上传给你的 Agent；
2. 明确说“请按 shuguang-writing-roundtable 的流程执行”；
3. 把你的想法、素材或文章一起提供。

这种方式可以复用写作流程，但不等于原生安装，也不能保证关键词自动触发。

## 最后记住两句话

1. 最稳定的调用方式是直接点名“曙光圆桌写作会议”。
2. Skill 只使用当前 Agent 真正拥有的工具，不会自动获得联网、账号登录、图片生成或公众号发布能力。
