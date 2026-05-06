# Task Cognition Persistence Test Scenario

## 测试目标

验证任务认知（Task Cognition）在多轮会话干扰后保持准确性和完整性。

## 测试场景描述

一个 AI Agent 在处理多个任务时，会在不同任务之间切换，并积累大量上下文。需要验证：**当 Agent 回到某个任务时，该任务的认知要素是否保持准确，未被其他任务污染或遗忘。**

## Session Timeline

```
Session Start
│
├── [Phase 1] 创建 auth_module (目标: 用户顺畅登录系统)
│   ├── 设置 picture: "用户顺畅登录"
│   ├── 设置 requirements: ["响应 < 100ms", "支持 OAuth2"]
│   ├── 设置 constraints: ["不可明文存储密码", "必须加密传输"]
│   └── 添加 todo: "实现基础登录 API"
│
├── [Phase 2] 创建 api_gateway (干扰任务)
│   └── 创建/修改其自己的 picture, requirements, constraints
│
├── [Phase 3] 返回 auth_module，继续修改
│   ├── 添加 todo: "编写 Auth 中间件"
│   └── 添加 constraint: "必须支持 refresh token"
│
├── [Phase 4] 创建 database (更多干扰)
│   └── 创建/修改其自己的认知要素
│
├── [Phase 5] 再返回 auth_module，添加 Gotcha
│   ├── 添加 gotcha: "偏离：发现密码使用 MD5 散列"
│   └── 更新 todo 完成状态
│
├── [Phase 6] 批量创建干扰任务 (noise tasks)
│   ├── 创建 task_001 ~ task_010
│   └── 每个任务都有不同的 picture/requirements/constraints
│
├── [Phase 7] 修改 api_gateway (更多干扰)
│   └── 更新其 requirements 为完全不相关的值
│
├── [Phase 8] 返回 auth_module，验证认知完整性
│   └── 执行 Harness 验证
│
└── [Phase 9] 最终验证
    ├── 验证 auth_module 的所有认知要素
    └── 执行 compile_status_plane
```

## 验证点

### 1. Picture 持久性

| 检查项 | 预期值 | 干扰来源 |
|--------|--------|----------|
| auth_module.picture | "用户顺畅登录" | api_gateway 的 picture 不是这个 |
| 认证相关约束未被覆盖 | 保持原始值 | task_001~010 的干扰 |

### 2. Requirements 完整性

| 检查项 | 预期值 |
|--------|--------|
| requirements 列表长度 | 2 |
| requirements[0] | "响应 < 100ms" |
| requirements[1] | "支持 OAuth2" |
| 未被其他任务的 requirements 污染 | 列表内容保持一致 |

### 3. Constraints 完整性

| 检查项 | 预期值 |
|--------|--------|
| constraints 列表长度 | 3 |
| constraints 包含 | "不可明文存储密码" |
| constraints 包含 | "必须加密传输" |
| constraints 包含 | "必须支持 refresh token" |
| 未被 api_gateway 或其他任务的 constraints 覆盖 | 保持原始值 |

### 4. Todos 状态正确

| 检查项 | 预期值 |
|--------|--------|
| todos 数量 | 2 |
| todos[0].text | "实现基础登录 API" |
| todos[0].done | True |
| todos[1].text | "编写 Auth 中间件" |
| todos[1].done | False |

### 5. Gotcha 记录累积

| 检查项 | 预期值 |
|--------|--------|
| gotcha_refs 数量 | 1 |
| gotcha_refs[0] 包含 | "偏离：发现密码使用 MD5 散列" |

### 6. Harness Tier 1 验证

| 检查项 | 预期结果 |
|--------|----------|
| 所有 todos 完成? | 否 (todos[1] 未完成) |
| Tier 1 通过? | 否 |
| 预期消息 | "还有 1 项 Todo 未完成: "编写 Auth 中间件"" |

## 测试实现

```python
def test_task_cognition_persistence_after_interleaved_sessions(self, tmp_path):
    """验证任务认知在多轮会话干扰后的准确性。

    测试场景：
    1. 创建 Task A (auth_module)
    2. 创建并修改 Task B, Task C 作为干扰
    3. 多次切换回 Task A 修改其状态
    4. 验证 Task A 的认知要素未被其他任务污染
    """
    service = TaskServiceImpl(substrate_root=tmp_path)

    # Phase 1: 创建 auth_module
    service.create_task("auth_module", "用户顺畅登录")
    service.update_cognitive_triad(
        "auth_module",
        picture="用户顺畅登录",
        requirements=["响应 < 100ms", "支持 OAuth2"],
        constraints=["不可明文存储密码", "必须加密传输"],
    )
    service.update_todo("auth_module", 0, True)

    # Phase 2: 创建干扰任务 api_gateway
    service.create_task("api_gateway", "API 网关")
    service.update_cognitive_triad(
        "api_gateway",
        picture="高性能 API 网关",
        requirements=["QPS > 10000"],
        constraints=["必须使用 HTTP/2"],
    )

    # Phase 3: 返回 auth_module，继续添加
    service.add_todo("auth_module", "编写 Auth 中间件")
    service.update_cognitive_triad(
        "auth_module",
        picture="用户顺畅登录",
        requirements=["响应 < 100ms", "支持 OAuth2"],
        constraints=["不可明文存储密码", "必须加密传输", "必须支持 refresh token"],
    )

    # Phase 4: 创建更多干扰任务
    for i in range(10):
        service.create_task(f"task_{i:03d}", f"干扰任务 {i}")

    # Phase 5: 返回 auth_module，添加 Gotcha
    # Note: Gotcha 写入通过 update_cognitive_triad 或专门方法
    # 此处模拟 gotcha_refs 更新
    manifest = service.get_task("auth_module")
    updated = manifest.__class__(
        id=manifest.id,
        type=manifest.type,
        status=manifest.status,
        cognitive_triad=manifest.cognitive_triad,
        gotcha_refs=["偏离：发现密码使用 MD5 散列"],
        todos=manifest.todos,
    )
    # 写入更新...

    # Phase 6: 修改 api_gateway
    service.update_cognitive_triad(
        "api_gateway",
        picture="API 网关 v2",
        requirements=["支持 GraphQL", "支持 REST", "支持 gRPC"],
        constraints=["必须使用 HTTP/3"],
    )

    # Phase 7: 最终验证 auth_module 的认知完整性
    final_manifest = service.get_task("auth_module")

    # Picture 验证
    assert final_manifest.cognitive_triad.picture == "用户顺畅登录"

    # Requirements 验证
    assert len(final_manifest.cognitive_triad.requirements) == 2
    assert "响应 < 100ms" in final_manifest.cognitive_triad.requirements
    assert "支持 OAuth2" in final_manifest.cognitive_triad.requirements

    # Constraints 验证
    assert len(final_manifest.cognitive_triad.constraints) == 3
    assert "不可明文存储密码" in final_manifest.cognitive_triad.constraints
    assert "必须加密传输" in final_manifest.cognitive_triad.constraints
    assert "必须支持 refresh token" in final_manifest.cognitive_triad.constraints

    # Todos 验证
    assert len(final_manifest.todos) == 2
    assert final_manifest.todos[0].done is True
    assert final_manifest.todos[1].done is False
    assert final_manifest.todos[1].text == "编写 Auth 中间件"

    # Gotcha 验证
    assert len(final_manifest.gotcha_refs) == 1
    assert "偏离" in final_manifest.gotcha_refs[0]

    # Phase 8: 执行 Harness 验证
    runner = HarnessRunner()
    results = runner.verify_task(final_manifest)

    tier1 = results[0]
    assert tier1.passed is False  # 因为还有 1 项 todo 未完成
    assert "编写 Auth 中间件" in tier1.message

    # Phase 9: 状态平面验证
    assembler = PlaneAssembler(substrate_root=tmp_path)
    plane = assembler.compile_status_plane()

    assert "■ Task ID: auth_module [CREATED]" in plane
    assert "目标图景: 用户顺畅登录" in plane
```

## 预期结果

- ✅ Picture 保持原始值，未被污染
- ✅ Requirements 列表长度和内容正确
- ✅ Constraints 包含所有原始约束 + 新增约束
- ✅ Todos 状态正确
- ✅ Gotcha 记录正确累积
- ✅ Harness Tier 1 检测到未完成项
- ✅ Status Plane 正确显示 auth_module

## 可能的失败场景

| 场景 | 失败原因 |
|------|----------|
| Picture 被覆盖 | 如果有 bug 导致任务 ID 混淆 |
| Requirements 列表错乱 | 如果有 bug 导致列表引用共享 |
| Todos 状态错误 | 如果有 bug 导致状态更新失败 |
| Gotcha 丢失 | 如果有 bug 导致 gotcha_refs 未正确写入 |

## 关联测试

- `test_harness.py` - Tier 1/2/3 验证逻辑
- `test_task_service.py` - Task CRUD 操作
- `test_plane.py` - 状态平面生成