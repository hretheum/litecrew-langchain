"""
State migration functionality for version upgrades.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class StateMigration:
    """Represents a migration between state versions."""

    from_version: str
    to_version: str
    migration_func: Callable[[Dict[str, Any]], Dict[str, Any]]
    description: str = ""

    def apply(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply migration to state."""
        return self.migration_func(state)

    def is_applicable(self, current_version: str) -> bool:
        """Check if migration is applicable for given version."""
        return current_version == self.from_version


class MigrationChain:
    """Manages a chain of migrations."""

    def __init__(self):
        self.migrations: List[StateMigration] = []

    def add_migration(self, migration: StateMigration) -> None:
        """Add migration to chain."""
        self.migrations.append(migration)

    def find_migration_path(
        self, from_version: str, to_version: str
    ) -> List[StateMigration]:
        """Find migration path between versions."""
        path = []
        current_version = from_version

        while current_version != to_version:
            migration = self._find_next_migration(current_version)
            if migration is None:
                raise ValueError(
                    f"No migration path from {from_version} to {to_version}"
                )

            path.append(migration)
            current_version = migration.to_version

        return path

    def _find_next_migration(self, from_version: str) -> Optional[StateMigration]:
        """Find next migration from given version."""
        for migration in self.migrations:
            if migration.from_version == from_version:
                return migration
        return None

    def apply_migrations(
        self, state: Dict[str, Any], from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """Apply all migrations in path."""
        path = self.find_migration_path(from_version, to_version)

        current_state = state
        for migration in path:
            current_state = migration.apply(current_state)

        return current_state


# Predefined migrations for common upgrades
BUILTIN_MIGRATIONS = MigrationChain()

# Example: Migration from v1.0 to v2.0 - Convert string agents/tasks to dicts
BUILTIN_MIGRATIONS.add_migration(
    StateMigration(
        from_version="1.0",
        to_version="2.0",
        description="Convert string agents/tasks to dictionary format",
        migration_func=lambda state: {
            **state,
            "agents": [
                {"role": a} if isinstance(a, str) else a
                for a in state.get("agents", [])
            ],
            "tasks": [
                {"description": t} if isinstance(t, str) else t
                for t in state.get("tasks", [])
            ],
        },
    )
)

# Example: Migration from v2.0 to v2.1 - Add task states if missing
BUILTIN_MIGRATIONS.add_migration(
    StateMigration(
        from_version="2.0",
        to_version="2.1",
        description="Add task states if missing",
        migration_func=lambda state: {
            **state,
            "task_states": state.get(
                "task_states",
                [
                    {
                        "status": "pending",
                        "output": None,
                        "error": None,
                        "start_time": None,
                        "end_time": None,
                        "attempts": 0,
                    }
                    for _ in state.get("tasks", [])
                ],
            ),
        },
    )
)
