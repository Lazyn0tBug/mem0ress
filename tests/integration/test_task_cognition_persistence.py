"""Integration test: Task cognition persistence after interleaved sessions."""

import pytest
from pathlib import Path

from mem0ress.service.impl.task_service import TaskServiceImpl
from mem0ress.plane import PlaneAssembler
from mem0ress.harness import HarnessRunner


class TestTaskCognitionPersistence:
    """验证任务认知在多轮会话干扰后的准确性。"""

    def test_task_cognition_persistence_after_interleaved_sessions(self, tmp_path):
        """Test Task A's cognition remains accurate after many interleaved sessions.

        Scenario:
        1. Create Task A (auth_module) with specific cognition
        2. Create/modify Task B, Task C as interference
        3. Return to Task A multiple times to modify it
        4. Create batch noise tasks (task_000 ~ task_009)
        5. Modify Task B further
        6. Return to Task A and verify all cognition elements are intact
        """
        service = TaskServiceImpl(substrate_root=tmp_path)
        runner = HarnessRunner()

        # === Phase 1: Create auth_module ===
        service.create_task("auth_module", "用户顺畅登录")
        service.update_cognitive_triad(
            "auth_module",
            picture="用户顺畅登录",
            requirements=["响应 < 100ms", "支持 OAuth2"],
            constraints=["不可明文存储密码", "必须加密传输"],
        )
        service.update_todo("auth_module", 0, True)  # Mark first todo done

        # === Phase 2: Create interference task api_gateway ===
        service.create_task("api_gateway", "API 网关")
        service.update_cognitive_triad(
            "api_gateway",
            picture="高性能 API 网关",
            requirements=["QPS > 10000"],
            constraints=["必须使用 HTTP/2"],
        )

        # === Phase 3: Return to auth_module, add more todos and constraints ===
        service.add_todo("auth_module", "编写 Auth 中间件")
        service.update_cognitive_triad(
            "auth_module",
            picture="用户顺畅登录",
            requirements=["响应 < 100ms", "支持 OAuth2"],
            constraints=[
                "不可明文存储密码",
                "必须加密传输",
                "必须支持 refresh token",
            ],
        )

        # === Phase 4: Create more interference tasks (database) ===
        service.create_task("database", "数据库设计")
        service.update_cognitive_triad(
            "database",
            picture="关系型数据库",
            requirements=["支持 ACID", "支持事务"],
            constraints=["必须使用 InnoDB"],
        )

        # === Phase 5: Return to auth_module, add Gotcha record ===
        # Simulate adding a Gotcha - write deviation to gotcha_refs
        manifest = service.get_task("auth_module")
        index_path = tmp_path / "tasks" / "auth_module" / "index.md"
        from mem0ress.storage.parser import SubstrateParser
        from mem0ress.core.schema import TaskManifest

        updated_manifest = TaskManifest(
            id=manifest.id,
            type=manifest.type,
            status=manifest.status,
            cognitive_triad=manifest.cognitive_triad,
            gotcha_refs=["偏离：发现密码使用 MD5 散列"],
            todos=manifest.todos,
        )
        content = SubstrateParser.serialize_manifest(updated_manifest, index_path)
        from mem0ress.storage.fs import get_file_hash
        expected_hash = get_file_hash(index_path)
        from mem0ress.storage.fs import safe_write
        safe_write(index_path, content, expected_hash)

        # === Phase 6: Create batch noise tasks (task_000 ~ task_009) ===
        for i in range(10):
            service.create_task(f"task_{i:03d}", f"噪声任务 {i}")

        # === Phase 7: Modify api_gateway further (more interference) ===
        service.update_cognitive_triad(
            "api_gateway",
            picture="API 网关 v2",
            requirements=["支持 GraphQL", "支持 REST", "支持 gRPC"],
            constraints=["必须使用 HTTP/3"],
        )

        # === Phase 8: Return to auth_module, verify cognition ===
        final_manifest = service.get_task("auth_module")

        # --- Picture 验证 ---
        assert final_manifest.cognitive_triad.picture == "用户顺畅登录"

        # --- Requirements 验证 ---
        assert len(final_manifest.cognitive_triad.requirements) == 2
        assert "响应 < 100ms" in final_manifest.cognitive_triad.requirements
        assert "支持 OAuth2" in final_manifest.cognitive_triad.requirements

        # --- Constraints 验证 ---
        constraints = final_manifest.cognitive_triad.constraints
        assert len(constraints) == 3, f"Expected 3 constraints, got {len(constraints)}: {constraints}"
        assert "不可明文存储密码" in constraints
        assert "必须加密传输" in constraints
        assert "必须支持 refresh token" in constraints

        # --- Todos 验证 ---
        assert len(final_manifest.todos) == 2
        assert final_manifest.todos[0].text == "梳理具体执行步骤"  # 默认初始 todo
        assert final_manifest.todos[0].done is True  # 我们更新了它
        assert final_manifest.todos[1].text == "编写 Auth 中间件"
        assert final_manifest.todos[1].done is False

        # --- Gotcha 验证 ---
        assert len(final_manifest.gotcha_refs) == 1
        assert "偏离" in final_manifest.gotcha_refs[0]
        assert "MD5" in final_manifest.gotcha_refs[0]

        # === Phase 9: Run Harness verification ===
        results = runner.verify_task(final_manifest)

        tier1 = results[0]
        assert tier1.passed is False, "Tier 1 should fail due to incomplete todo"
        assert "编写 Auth 中间件" in tier1.message

        tier2 = results[1]
        assert tier2.passed is True  # No requirements to run

        tier3 = results[2]
        assert tier3.passed is True  # Judge placeholder

        # === Phase 10: Status plane verification ===
        assembler = PlaneAssembler(substrate_root=tmp_path)
        plane = assembler.compile_status_plane().render()

        # New format: ■ {id} [{todo_progress}] {STATUS}
        # Picture/requirements/constraints are goals, not state - they don't appear
        assert "■ auth_module [1/2] CREATED" in plane
        assert "■ api_gateway [0/1] CREATED" in plane
        assert "■ task_000 [0/1] CREATED" in plane

    def test_task_cognition_isolation_between_tasks(self, tmp_path):
        """Test that modifying one task doesn't affect another's cognition."""
        service = TaskServiceImpl(substrate_root=tmp_path)

        # Create two tasks with distinct cognition
        service.create_task("task_a", "任务 A 的 picture")
        service.update_cognitive_triad(
            "task_a",
            picture="任务 A 的 picture",
            requirements=["A 的需求"],
            constraints=["A 的约束"],
        )

        service.create_task("task_b", "任务 B 的 picture")
        service.update_cognitive_triad(
            "task_b",
            picture="任务 B 的 picture",
            requirements=["B 的需求"],
            constraints=["B 的约束"],
        )

        # Modify task_a significantly
        service.update_cognitive_triad(
            "task_a",
            picture="A 被大幅修改后的 picture",
            requirements=["A 的新需求1", "A 的新需求2"],
            constraints=["A 的新约束1", "A 的新约束2", "A 的新约束3"],
        )

        # Verify task_b is unchanged
        manifest_b = service.get_task("task_b")
        assert manifest_b.cognitive_triad.picture == "任务 B 的 picture"
        assert len(manifest_b.cognitive_triad.requirements) == 1
        assert manifest_b.cognitive_triad.requirements[0] == "B 的需求"
        assert len(manifest_b.cognitive_triad.constraints) == 1
        assert manifest_b.cognitive_triad.constraints[0] == "B 的约束"