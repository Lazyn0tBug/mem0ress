---
date: 2026-05-13
topic: mem0ress-skill-design
---

# mem0ress MVP Skill 设计

## Problem Frame

`session_mvp.md` 是设计讨论阶段的产物，存在两个关键错误：

1. **Skill 格式错误**：文档假设 Hermes 的 YAML Skill 格式（`skills/*.yaml`），但 mem0ress 的实际调用方是 Claude Code，后者使用 `SKILL.md` 格式（Markdown + YAML frontmatter）
2. **Skill 数量错误**：文档描述"每个命令对应一个 Skill"，但正确的 Claude Code convention 是**一个 Skill 包含多个命令**，用 `commands` trigger 暴露

当前 MVP 的 CLI 已完整实现（`create/update/judge/close/abandon/status/report`），但 Skill 层完全缺失。本文档定义 MVP Skill 的正确设计方案。

## Requirements

**SKILL.md 格式与放置**
- R1. Skill 文件名为 `mem0ress.md`，放置于 `~/.claude/skills/mem0ress.md`（用户级 Skill，repo 不含此文件）
- R2. 文件使用 YAML frontmatter（`name`、`description`、`triggers`） + Markdown 正文格式
- R3. `triggers` 中使用 Claude Code 的 slash command 格式：`/mem0ress create`、`/mem0ress update`、`/mem0ress judge`、`/mem0ress close`（与 CLI 命令名保持一致）
- R4. CLI 命令格式：`mem0ress create`（子命令），Skill 触发器：`/mem0ress create`（slash command），两者命名对齐

**Skill 命令暴露（4 个核心命令）**
- R5. `/mem0ress create` — 创建新任务，自动生成 task_id，写入 `task.md` + 初始化 `session.md`/`gotchas.md`/`judge.md`，更新 `.current_task`
- R6. `/mem0ress update` — 追加 turn snapshot 到 `session.md`，默认操作当前 active task（`.current_task`）
- R7. `/mem0ress judge` — 执行 Tier 0/1/2 验证，结果写入 `judge.md`，默认操作当前 active task
- R8. `/mem0ress close` — 原子操作：先 judge，全部 PASS 才标记 COMPLETED；任何 tier FAIL 则拒绝关闭

**task_id 自动生成**
- R9. 不要求用户手动指定 task_id，`/mem0ress create` 时自动生成 6 位唯一 ID（例如 `2k5m3x`）
- R10. 算法：`{base36_timestamp_low}{random_alphanumeric}` — 取时间戳低 4 位 base36 + 2 位随机，合计 6 位
- R11. 局部唯一性：同一进程内连续创建的 ID 保证不重复

**`.current_task` 指针**
- R12. 纳入 MVP：每次 `/mem0ress create` 后自动写入 `.current_task`（包含 task_id + activated_at）
- R13. 默认绑定：`/mem0ress update`、`/mem0ress judge`、`/mem0ress close` 默认操作当前 active task，无需显式传入 task_id
- R14. 显式 task_id 仍支持：`/mem0ress update <task_id>` 可操作指定任务，覆盖隐式绑定
- R15. close 后清空：`.current_task` 的 task_id 置空，activated_at 保留，供下次 create 时安全检测

**命令参数传递**
- R16. `/mem0ress create` — 不接受手动 task_id，自动生成
- R17. `/mem0ress update`、`/mem0ress judge`、`/mem0ress close` — 默认操作 `.current_task`，支持显式 task_id

**PRC 补全交互**
- R18. `/mem0ress create` 后 Hermes 等客户端主动逐项询问用户补充 PRC 三要素（Picture → Requirements → Constraints），多轮交互确认后一次性传入 Skill。Skill 本身不实现追问逻辑，接收已补全的完整参数。
- R19. Agent 可在任何时刻询问"当前 PRC 是什么？"，Skill 返回已填充的 PRC 内容（从 `.current_task` 对应任务的 `task.md` 中读取）
- R20. PRC 更新暂不实现，纳入 v0.2 重构

**输出格式（Agent 友好）**
- R21. `/mem0ress judge` 输出包含每 tier 的 PASS/FAIL 状态和消息，格式为纯文本（非 Rich ANSI 渲染）
- R22. `/mem0ress close` 失败时输出具体哪个 tier 失败及其 deviation reason

**返回内容注入**
- R23. Skill 返回给 Agent 的内容包含：命令执行结果 + 简短状态描述，使 Agent 能注入下一轮上下文

**文件结构映射**
- R24. MVP 文件结构：`.mem0ress/.current_task` 纳入，`.current_task` 格式为 YAML，含 `task_id`（可选字串）和 `activated_at`（ISO8601 字串）两个字段

## Success Criteria

- [ ] `/mem0ress create` 自动生成 6 位 task_id，创建任务并更新 `.current_task`
- [ ] `/mem0ress create` 接受完整 PRC 参数（由 Hermes 多轮交互确认后一次性传入）
- [ ] Agent 可询问"当前 PRC 是什么？"获取已填充的 PRC 内容
- [ ] `/mem0ress update` 默认追加 session.md turn snapshot 到当前 active task
- [ ] `/mem0ress judge` 执行 T0/T1/T2 并输出纯文本结构化结果
- [ ] `/mem0ress close` 在 tier 全部 PASS 时标记 COMPLETED，任一 FAIL 时拒绝关闭
- [ ] Skill 使用正确的 `mem0ress.md` SKILL.md 格式（与 CLI 命令名对齐）
- [ ] 安装流程已在 README 中文档化

## Scope Boundaries

- **不实现**：`skills/` 目录于 repo 内——Skill 文件属于用户级配置
- **不实现**：abandon/status/report 命令——纳入 v0.2+
- **不实现**：Tier 2 verify_cmd 的真实 shell 执行——MVP 为 stub
- **不实现**：多 Agent 并发写——protocol 明确 v0.1 不支持
- **不实现**：PRC 更新（`update_cognitive_triad` CLI 命令暴露）——纳入 v0.2 重构

## Key Decisions

- **单体 Skill**：一个 `mem0ress.md` Skill 包含 4 个命令，符合 Claude Code convention
- **自动 task_id + `.current_task`**：简化调用，Agent 无需记忆 task_id，`.current_task` 是 MVP 的核心简化机制
- **迭代式 PRC 补全**：Hermes 在 Skill 调用前通过多轮交互诱导用户补全 Picture → Requirements → Constraints，确认后一次性传入 Skill。降低用户认知负担。
- **与 CLI 命名对齐**：`/mem0ress create` 与 `mem0ress create` 一致，Agent 学会一个即可推断另一个
- **纯文本输出**：确保 Agent 能正确解析 Skill 输出

## Dependencies / Assumptions

- D1. mem0ress CLI 已完整实现（create/update/judge/close 命令，Python 环境和 uv 依赖已配置）
- D2. 用户已将 `mem0ress.md` Skill 文件放置到 `~/.claude/skills/` 目录
- D3. Python 3.12+ 环境，`uv` 可用

## Installation

Skill 文件需用户手动安装到 Claude Code 的用户级 Skill 目录：

```bash
mkdir -p ~/.claude/skills
cp <repo-path>/skills/mem0ress.md ~/.claude/skills/mem0ress.md
```

安装后验证：在 Claude Code 中运行 `/mem0ress help`，确认 Skill 识别。

## Next Steps

-> `/ce:plan` for structured implementation planning

（注：`session_mvp.md` 中的设计决策（状态机、Tier 验证逻辑、文件协议）与 `design.md` 和 `spec.md` 保持一致，本 Skill 设计仅修正调用层格式，不改变底层协议。）