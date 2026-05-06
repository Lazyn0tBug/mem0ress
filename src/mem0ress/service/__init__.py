"""Service layer - TaskService Protocol and implementation."""

from mem0ress.service.impl.task_service import TaskServiceImpl
from mem0ress.service.protocol import TaskServiceProtocol

__all__ = ["TaskServiceProtocol", "TaskServiceImpl"]