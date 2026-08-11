# 圆桌案卷与席位交接契约

## 目录

1. 契约原则
2. 圆桌简报
3. 选题决议
4. 研究地图
5. 证据台账
6. 架构卡
7. 成稿与版本
8. 事实核查报告
9. 读者审稿报告
10. 修订补丁
11. 发布交付包

## 1. 契约原则

结构化案卷服务于稳定协作，不应变成用户界面的负担。遵守：

1. 内容与元信息分开：正文不混入流程状态；状态不冒充正文。
2. 每项结论暴露置信度、来源和未知项。
3. 用稳定 ID 连接命题、主张、来源、段落、问题和版本。
4. 只让一个主持总编写入“已确认决策”。其他席位只能提出候选或问题。
5. 用户可见输出优先用清楚的 Markdown；只有长期项目、机器处理或用户要求时输出完整 JSON/YAML。

本文件中的 YAML 用于说明字段。需要运行 `scripts/validate_casefile.py` 时，把完整案卷保存为 UTF-8 JSON；YAML 仅在当前环境已经具备解析能力时校验，不得为此自动安装依赖。快速成稿和一次性单席会诊无需保存完整案卷。

## 2. 圆桌简报

最小字段：

```yaml
brief_id: B1
task: "要完成什么"
deliverable: "文章/口播/演讲/报告/平台文案/审稿报告等"
target_reader:
  description: "具体读者"
  current_state: "读前处境或认知"
reader_change:
  know: "读后知道什么"
  feel: "读后感受什么"
  do: "读后可能做什么"
author_position: "作者核心立场；没有则 not_provided"
source_scope:
  user_materials: []
  external_research: "allowed/forbidden/not_provided"
  private_sources: "allowed/forbidden/not_applicable"
constraints:
  platform: ""
  length: ""
  tone: ""
  deadline: ""
must_include: []
must_avoid: []
locked_content: []
assumptions: []
open_questions: []
success_test: "一句可判定标准"
```

若用户没有指定文章篇幅，普通中文长文可默认约 1200–1800 字；短内容按平台和用户意图自适应。不要把默认值伪装成平台硬规则。

## 3. 选题决议

每个真实候选方向包含：

```yaml
topic_id: T1
topic_statement: "主题 + 角度 + 认知收益"
target_reader: ""
reader_problem: ""
core_thesis: ""
cognitive_gain: ""
why_now: "若与时效无关则 not_applicable"
material_feasibility: high | medium | low
main_risk: ""
status: recommended | alternative | selected | rejected
```

只把“核心命题”锁定，不要过早把标题锁死。标题候选在成稿或发布阶段生成，避免标题牵着论证走。

## 4. 研究地图

仅在主题陌生、资料密集、存在争议、需要长篇研究或用户明确要求时保存完整结构：

```yaml
research_map_id: RM1
topic_id: T1
root_question: "全文最终要回答的读者问题"
perspectives:
  - perspective_id: V1
    lens: "机制/利益相关者/比较/边界/行动等真实视角"
    why_it_matters: "不研究会让哪个判断变浅或失真"
    question_ids: [Q1]
questions:
  - question_id: Q1
    parent_id: not_applicable
    question: "可研究且会影响正文的问题"
    priority: essential | supporting | exploratory
    affects: "命题、主张、章节或用户决策"
    expected_evidence: "需要的证据类型和优先来源"
    status: open | partial | answered | conflict | out_of_scope
    answer_summary: "当前证据允许的答案；没有则 not_provided"
    claim_ids: [C1]
    source_ids: [S1]
    next_probe: "下一步最小追问；无需继续则 not_applicable"
research_budget:
  mode: fast | full | deep | single
  rounds_used: 0
  expansion_requires_user: false
coverage_gaps: []
stop_reason: ""
```

研究地图不是固定专家意见清单。每个视角必须产生不同问题；每个问题必须能影响正文。快速模式可以只在内部维护根问题和必要问题，不向用户展示完整 YAML。

## 5. 证据台账

为会影响结论的主张建立记录：

```yaml
claim_id: C1
claim_text: "准备在稿件中表达的主张"
claim_type: fact | estimate | user_experience | opinion | inference | quote
risk: high | medium | low
needed_for: "对应命题或段落"
question_ids: [Q1]
source_ids: [S1]
status: verified | supported | disputed | unverified | not_verifiable
safe_wording: "当前证据允许的最强表述"
notes: "口径、日期、限制或冲突"
```

来源记录：

```yaml
source_id: S1
title: ""
creator_or_publisher: ""
source_type: primary | official | research | authoritative_secondary | user_material | general_web
date: ""
locator: "URL、文件名+标题路径、页码、段落或时间戳"
supports: [C1]
answers: [Q1]
independence_group: "同源转载使用同一组"
accessed_at: ""
limitations: ""
```

同一新闻稿的多篇转载不算多个独立来源。用户笔记可以支撑 `user_experience` 或作者观点，但不能自动把外部事实标成 `verified`。

## 6. 架构卡

```yaml
outline_id: O1
title_direction: "不是最终标题"
throughline: "全文只回答的一条主线"
sections:
  - section_id: P1
    function: hook | context | explain | argue | counterpoint | method | example | synthesis | close
    reader_question: "这一段回答读者什么问题"
    question_ids: [Q1]
    key_point: ""
    claim_ids: []
    source_ids: []
    transition_from_previous: ""
    approximate_length: ""
ending_delivery: "读者最终带走的成果"
tradeoffs: []
```

检查每一节是否服务主线。若删除某节不影响理解或说服，考虑删除；若核心结论没有来源或推理路径，返回证据阶段。

## 7. 成稿与版本

正文使用稳定段落/章节 ID，便于局部修改：

```yaml
draft_id: D1
based_on: [B1, T1, O1]
status: working | ready_for_fact_check | ready_for_review | final
sections:
  - section_id: P1
    content: ""
    claim_ids: []
    locked: false
author_notes: []
known_risks: []
```

普通聊天无需把正文包在 YAML 里；只在案卷中记录映射。不要为了内部 ID 破坏文章可读性。

## 8. 事实核查报告

```yaml
fact_check_id: FC1
draft_id: D1
scope: "核查了哪些类型和范围"
summary:
  checked: 0
  must_fix: 0
  should_fix: 0
  unverified: 0
issues:
  - issue_id: F1
    claim_id: C1
    location: "P3 第2段"
    original_text: ""
    category: wrong_fact | stale_data | misquote | weak_source | absolute_claim | ambiguous_scope | other
    severity: must_fix | should_fix | unverified
    finding: ""
    source_ids: []
    safe_revision: ""
    rationale: ""
passed_summary: "不要逐条堆砌低价值通过项"
limitations: []
```

`must_fix` 是明确错误、重大过时或会误导的关键陈述。`should_fix` 是来源薄弱、范围过宽、措辞绝对或精度不足。`unverified` 是已查但无法确认，不等于错误。

## 9. 读者审稿报告

```yaml
review_id: QR1
draft_id: D2
one_sentence_assessment: ""
reader_takeaway: ""
hard_gate_status: pass | fail
scores:
  reader_alignment: 0
  cognitive_gain: 0
  clarity_depth: 0
  throughline_structure: 0
  argument_support: 0
  expression_accuracy: 0
  rhythm: 0
  deliverability: 0
  author_distinctiveness: 0
strengths_to_keep: []
priority_issues:
  - priority: 1
    criterion: ""
    location: ""
    problem: ""
    reader_impact: ""
    direction: "只给方向，不代替作者决定观点"
revision_order: []
```

对不适用项使用 `not_applicable`，不要为了平均分强行打分。

## 10. 修订补丁

```yaml
revision_id: R1
from_draft: D1
to_draft: D2
request: "用户原始修改要求"
scope: [P2]
locked_content_respected: []
changes:
  - location: "P2"
    before: ""
    after: ""
    reason: ""
claims_added: []
claims_removed: []
checks_rerun: []
unchanged_summary: "明确哪些地方没动"
```

如果修改会改变事实含义，重跑对应事实核查；如果只改格式且不改变含义，只做语义回归检查。

## 11. 发布交付包

```yaml
delivery_id: DEL1
draft_id: D-final
format: markdown | plain_text | html | docx | pptx | image_set | other
platform: ""
primary_artifact: "正文或真实文件路径"
supporting_artifacts: []
titles: []
summary: ""
fact_check_note: ""
open_risks: []
assumptions: []
ready_status: ready | ready_with_caveats | blocked
```

只有真实文件存在并经过检查时，`primary_artifact` 才能写文件路径。不要生成虚假的下载链接、占位路径或“稍后可下载”承诺。

保存案卷后运行：

```text
python -X utf8 scripts/validate_casefile.py <casefile.json>
```

发布交付前按任务运行 `scripts/validate_delivery.py`；局部修订包含稳定段落 ID 时运行 `scripts/validate_revision.py`。脚本失败时不得把 `ready_status` 标为 `ready`。
