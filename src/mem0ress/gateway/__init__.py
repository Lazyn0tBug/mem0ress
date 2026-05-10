"""Gateway - cognitive gateway modules.

Exports:
- PlaneAssembler: compile_status_plane (read-only status projection)
- TaskServiceImpl: task management implementation (create, update, complete, abandon)
- CognitiveContext: context manager for host lifecycle hooks (before/after turn)
- snapshot_session: append a session snapshot to session.md
"""

from mem0ress.gateway.actions import TaskServiceImpl
from mem0ress.gateway.intercept import CognitiveContext, snapshot_session
from mem0ress.gateway.plane import PlaneAssembler

__all__ = ["PlaneAssembler", "TaskServiceImpl", "CognitiveContext", "snapshot_session"]
