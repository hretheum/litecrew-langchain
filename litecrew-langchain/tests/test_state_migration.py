"""Comprehensive tests for state migration functionality."""

import pytest
from litecrew.state.migration import (
    StateMigration,
    MigrationChain,
    BUILTIN_MIGRATIONS
)


class TestStateMigration:
    """Test StateMigration class."""
    
    def test_migration_init(self):
        """Test migration initialization."""
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: {"version": "2.0", **state},
            description="Test migration"
        )
        
        assert migration.from_version == "1.0"
        assert migration.to_version == "2.0"
        assert migration.description == "Test migration"
        assert migration.migration_func is not None
        
    def test_migration_init_without_description(self):
        """Test migration initialization without description."""
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: state
        )
        
        assert migration.description == ""
        
    def test_migration_apply(self):
        """Test applying migration to state."""
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: {**state, "version": "2.0", "migrated": True}
        )
        
        original_state = {"version": "1.0", "data": "test"}
        new_state = migration.apply(original_state)
        
        assert new_state["version"] == "2.0"
        assert new_state["data"] == "test"
        assert new_state["migrated"] is True
        
    def test_migration_is_applicable_true(self):
        """Test migration is applicable for matching version."""
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: state
        )
        
        assert migration.is_applicable("1.0") is True
        
    def test_migration_is_applicable_false(self):
        """Test migration is not applicable for non-matching version."""
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: state
        )
        
        assert migration.is_applicable("2.0") is False
        assert migration.is_applicable("1.1") is False
        
    def test_migration_apply_with_complex_transformation(self):
        """Test migration with complex state transformation."""
        def transform_state(state):
            new_state = state.copy()
            if "users" in new_state:
                new_state["users"] = [
                    {"name": user, "active": True} if isinstance(user, str) else user
                    for user in new_state["users"]
                ]
            return new_state
            
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=transform_state
        )
        
        original_state = {
            "users": ["alice", "bob", {"name": "charlie", "active": False}],
            "version": "1.0"
        }
        
        new_state = migration.apply(original_state)
        
        assert len(new_state["users"]) == 3
        assert new_state["users"][0] == {"name": "alice", "active": True}
        assert new_state["users"][1] == {"name": "bob", "active": True}
        assert new_state["users"][2] == {"name": "charlie", "active": False}


class TestMigrationChain:
    """Test MigrationChain class."""
    
    def test_migration_chain_init(self):
        """Test migration chain initialization."""
        chain = MigrationChain()
        assert chain.migrations == []
        
    def test_add_migration(self):
        """Test adding migration to chain."""
        chain = MigrationChain()
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: state
        )
        
        chain.add_migration(migration)
        assert len(chain.migrations) == 1
        assert chain.migrations[0] == migration
        
    def test_add_multiple_migrations(self):
        """Test adding multiple migrations to chain."""
        chain = MigrationChain()
        
        migration1 = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: state
        )
        
        migration2 = StateMigration(
            from_version="2.0",
            to_version="3.0",
            migration_func=lambda state: state
        )
        
        chain.add_migration(migration1)
        chain.add_migration(migration2)
        
        assert len(chain.migrations) == 2
        assert chain.migrations[0] == migration1
        assert chain.migrations[1] == migration2
        
    def test_find_next_migration_exists(self):
        """Test finding next migration when it exists."""
        chain = MigrationChain()
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: state
        )
        
        chain.add_migration(migration)
        found = chain._find_next_migration("1.0")
        
        assert found == migration
        
    def test_find_next_migration_not_exists(self):
        """Test finding next migration when it doesn't exist."""
        chain = MigrationChain()
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: state
        )
        
        chain.add_migration(migration)
        found = chain._find_next_migration("2.0")
        
        assert found is None
        
    def test_find_migration_path_single_step(self):
        """Test finding migration path with single step."""
        chain = MigrationChain()
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: state
        )
        
        chain.add_migration(migration)
        path = chain.find_migration_path("1.0", "2.0")
        
        assert len(path) == 1
        assert path[0] == migration
        
    def test_find_migration_path_multi_step(self):
        """Test finding migration path with multiple steps."""
        chain = MigrationChain()
        
        migration1 = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: {"version": "2.0", **state}
        )
        
        migration2 = StateMigration(
            from_version="2.0",
            to_version="3.0",
            migration_func=lambda state: {"version": "3.0", **state}
        )
        
        chain.add_migration(migration1)
        chain.add_migration(migration2)
        
        path = chain.find_migration_path("1.0", "3.0")
        
        assert len(path) == 2
        assert path[0] == migration1
        assert path[1] == migration2
        
    def test_find_migration_path_same_version(self):
        """Test finding migration path when versions are the same."""
        chain = MigrationChain()
        path = chain.find_migration_path("1.0", "1.0")
        
        assert path == []
        
    def test_find_migration_path_no_path(self):
        """Test finding migration path when no path exists."""
        chain = MigrationChain()
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: state
        )
        
        chain.add_migration(migration)
        
        with pytest.raises(ValueError, match="No migration path from 1.0 to 3.0"):
            chain.find_migration_path("1.0", "3.0")
            
    def test_apply_migrations_single_step(self):
        """Test applying migrations with single step."""
        chain = MigrationChain()
        migration = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: {**state, "version": "2.0", "migrated": True}
        )
        
        chain.add_migration(migration)
        
        original_state = {"version": "1.0", "data": "test"}
        new_state = chain.apply_migrations(original_state, "1.0", "2.0")
        
        assert new_state["version"] == "2.0"
        assert new_state["data"] == "test"
        assert new_state["migrated"] is True
        
    def test_apply_migrations_multi_step(self):
        """Test applying migrations with multiple steps."""
        chain = MigrationChain()
        
        migration1 = StateMigration(
            from_version="1.0",
            to_version="2.0",
            migration_func=lambda state: {**state, "version": "2.0", "step1": True}
        )
        
        migration2 = StateMigration(
            from_version="2.0",
            to_version="3.0",
            migration_func=lambda state: {**state, "version": "3.0", "step2": True}
        )
        
        chain.add_migration(migration1)
        chain.add_migration(migration2)
        
        original_state = {"version": "1.0", "data": "test"}
        new_state = chain.apply_migrations(original_state, "1.0", "3.0")
        
        assert new_state["version"] == "3.0"
        assert new_state["data"] == "test"
        assert new_state["step1"] is True
        assert new_state["step2"] is True
        
    def test_apply_migrations_same_version(self):
        """Test applying migrations when versions are the same."""
        chain = MigrationChain()
        
        original_state = {"version": "1.0", "data": "test"}
        new_state = chain.apply_migrations(original_state, "1.0", "1.0")
        
        assert new_state == original_state
        
    def test_apply_migrations_no_path(self):
        """Test applying migrations when no path exists."""
        chain = MigrationChain()
        
        original_state = {"version": "1.0", "data": "test"}
        
        with pytest.raises(ValueError, match="No migration path from 1.0 to 3.0"):
            chain.apply_migrations(original_state, "1.0", "3.0")


class TestBuiltinMigrations:
    """Test builtin migrations."""
    
    def test_builtin_migrations_exists(self):
        """Test that builtin migrations exist."""
        assert BUILTIN_MIGRATIONS is not None
        assert isinstance(BUILTIN_MIGRATIONS, MigrationChain)
        assert len(BUILTIN_MIGRATIONS.migrations) > 0
        
    def test_v1_to_v2_migration(self):
        """Test migration from version 1.0 to 2.0."""
        state = {
            "version": "1.0",
            "agents": ["agent1", "agent2", {"role": "agent3"}],
            "tasks": ["task1", "task2", {"description": "task3"}]
        }
        
        migrated = BUILTIN_MIGRATIONS.apply_migrations(state, "1.0", "2.0")
        
        assert migrated["agents"] == [
            {"role": "agent1"},
            {"role": "agent2"},
            {"role": "agent3"}
        ]
        assert migrated["tasks"] == [
            {"description": "task1"},
            {"description": "task2"},
            {"description": "task3"}
        ]
        
    def test_v2_to_v2_1_migration(self):
        """Test migration from version 2.0 to 2.1."""
        state = {
            "version": "2.0",
            "agents": [{"role": "agent1"}],
            "tasks": [{"description": "task1"}, {"description": "task2"}]
        }
        
        migrated = BUILTIN_MIGRATIONS.apply_migrations(state, "2.0", "2.1")
        
        assert "task_states" in migrated
        assert len(migrated["task_states"]) == 2
        
        for task_state in migrated["task_states"]:
            assert task_state["status"] == "pending"
            assert task_state["output"] is None
            assert task_state["error"] is None
            assert task_state["start_time"] is None
            assert task_state["end_time"] is None
            assert task_state["attempts"] == 0
            
    def test_v2_to_v2_1_migration_existing_task_states(self):
        """Test migration from 2.0 to 2.1 with existing task states."""
        existing_task_states = [
            {"status": "completed", "output": "result", "error": None}
        ]
        
        state = {
            "version": "2.0",
            "agents": [{"role": "agent1"}],
            "tasks": [{"description": "task1"}],
            "task_states": existing_task_states
        }
        
        migrated = BUILTIN_MIGRATIONS.apply_migrations(state, "2.0", "2.1")
        
        assert migrated["task_states"] == existing_task_states
        
    def test_v1_to_v2_1_migration_chain(self):
        """Test migration chain from 1.0 to 2.1."""
        state = {
            "version": "1.0",
            "agents": ["agent1"],
            "tasks": ["task1", "task2"]
        }
        
        migrated = BUILTIN_MIGRATIONS.apply_migrations(state, "1.0", "2.1")
        
        # Check v1 to v2 migration
        assert migrated["agents"] == [{"role": "agent1"}]
        assert migrated["tasks"] == [
            {"description": "task1"},
            {"description": "task2"}
        ]
        
        # Check v2 to v2.1 migration
        assert "task_states" in migrated
        assert len(migrated["task_states"]) == 2
        
    def test_v1_to_v2_migration_empty_lists(self):
        """Test v1 to v2 migration with empty agents and tasks."""
        state = {
            "version": "1.0",
            "agents": [],
            "tasks": []
        }
        
        migrated = BUILTIN_MIGRATIONS.apply_migrations(state, "1.0", "2.0")
        
        assert migrated["agents"] == []
        assert migrated["tasks"] == []
        
    def test_v1_to_v2_migration_missing_lists(self):
        """Test v1 to v2 migration without agents and tasks."""
        state = {"version": "1.0"}
        
        migrated = BUILTIN_MIGRATIONS.apply_migrations(state, "1.0", "2.0")
        
        assert migrated["agents"] == []
        assert migrated["tasks"] == []
        
    def test_v2_to_v2_1_migration_no_tasks(self):
        """Test v2 to v2.1 migration without tasks."""
        state = {
            "version": "2.0",
            "agents": [{"role": "agent1"}]
        }
        
        migrated = BUILTIN_MIGRATIONS.apply_migrations(state, "2.0", "2.1")
        
        assert migrated["task_states"] == []