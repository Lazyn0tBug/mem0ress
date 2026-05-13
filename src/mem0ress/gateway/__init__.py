"""Gateway - cognitive gateway modules.

Exports:
- PlaneAssembler: compile_status_plane (read-only status projection)
- TaskServiceImpl: task management implementation (create, update, complete, abandon)
- snapshot_session: append a session snapshot to session.md

CognitiveContext is reserved for future Skill/host integration.
It is NOT used by the MVP CLI — the MVP runtime is the Hermes Skill layer.
"""

from mem0ress.gateway.actions import TaskServiceImpl
from mem0ress.gateway.intercept import CognitiveContext, snapshot_session
from mem0ress.gateway.plane import PlaneAssembler

__all__ = ["PlaneAssembler", "TaskServiceImpl", "snapshot_session", "CognitiveContext"]
