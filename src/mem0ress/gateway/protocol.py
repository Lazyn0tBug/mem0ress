"""TaskService Protocol definition - interface for cognitive task management."""

from typing import Protocol

from mem0ress.core.schema import TaskManifest


class TaskServiceProtocol(Protocol):
    """Protocol for task service operations.

    All implementations must satisfy this interface.
    """

    def create_task(self, task_id: str, picture: str) -> TaskManifest:
        """Create a new task with given ID and picture.

        Args:
            task_id: Unique task identifier (directory name)
            picture: Goal picture for task completion

        Returns:
            Created TaskManifest

        Raises:
            TaskExistsError: If task_id already exists
        """
        ...

    def get_task(self, task_id: str) -> TaskManifest:
        """Get task by ID.

        Args:
            task_id: Task identifier

        Returns:
            TaskManifest for the task

        Raises:
            FileNotFoundError: If task does not exist
        """
        ...

    def update_todo(self, task_id: str, index: int, done: bool) -> TaskManifest:
        """Update todo completion status.

        Args:
            task_id: Task identifier
            index: Todo index (0-based)
            done: Completion status

        Returns:
            Updated TaskManifest

        Raises:
            FileNotFoundError: If task does not exist
            IndexError: If index is out of range
            ConflictError: If file was modified concurrently
        """
        ...

    def update_cognitive_triad(
        self,
        task_id: str,
        picture: str,
        requirements: list[str],
        constraints: list[str],
    ) -> TaskManifest:
        """Update the cognitive triad (picture, requirements, constraints).

        Args:
            task_id: Task identifier
            picture: New picture
            requirements: New requirements list
            constraints: New constraints list

        Returns:
            Updated TaskManifest

        Raises:
            FileNotFoundError: If task does not exist
            ConflictError: If file was modified concurrently
        """
        ...

    def get_all_tasks(self) -> list[TaskManifest]:
        """Get all tasks in the substrate.

        Returns:
            List of all TaskManifest objects
        """
        ...

    def delete_task(self, task_id: str) -> None:
        """Delete a task and all its files.

        Args:
            task_id: Task identifier

        Raises:
            FileNotFoundError: If task does not exist
        """
        ...

    def add_todo(self, task_id: str, text: str) -> TaskManifest:
        """Add a new todo to task.

        Args:
            task_id: Task identifier
            text: Todo text

        Returns:
            Updated TaskManifest

        Raises:
            FileNotFoundError: If task does not exist
            ConflictError: If file was modified concurrently
        """
        ...

    def remove_todo(self, task_id: str, index: int) -> TaskManifest:
        """Remove a todo from task.

        Args:
            task_id: Task identifier
            index: Todo index (0-based)

        Returns:
            Updated TaskManifest

        Raises:
            FileNotFoundError: If task does not exist
            IndexError: If index is out of range
            ConflictError: If file was modified concurrently
        """
        ...

    def complete_task(self, task_id: str) -> TaskManifest:
        """Mark a task as COMPLETED.

        Args:
            task_id: Task identifier

        Returns:
            Updated TaskManifest with status COMPLETED

        Raises:
            FileNotFoundError: If task does not exist
            ConflictError: If file was modified concurrently
        """
        ...

    def abandon_task(self, task_id: str) -> TaskManifest:
        """Mark a task as ABANDONED.

        Args:
            task_id: Task identifier

        Returns:
            Updated TaskManifest with status ABANDONED

        Raises:
            FileNotFoundError: If task does not exist
            ConflictError: If file was modified concurrently
        """
        ...