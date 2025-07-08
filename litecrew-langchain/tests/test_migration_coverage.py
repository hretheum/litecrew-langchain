"""Tests for migration to improve coverage."""

from litecrew.state.migration import StateMigration, MigrationChain


class TestStateMigrationCoverage:
    """Tests for StateMigration to improve coverage."""
    
    def test_apply_migration(self):
        """Test applying a migration to state."""
        def transform_state(state):
            state["new_field"] = "added"
            return state
        
        migration = StateMigration(
            from_version="1.0",
            to_version="1.1",
            migration_func=transform_state,
            description="Add new field"
        )
        
        initial_state = {"old_field": "value"}
        result = migration.apply(initial_state)
        
        assert result["old_field"] == "value"
        assert result["new_field"] == "added"
    
    def test_is_applicable_true(self):
        """Test is_applicable returns True for matching version."""
        migration = StateMigration(
            from_version="1.0",
            to_version="1.1",
            migration_func=lambda x: x
        )
        
        assert migration.is_applicable("1.0") is True
    
    def test_is_applicable_false(self):
        """Test is_applicable returns False for non-matching version."""
        migration = StateMigration(
            from_version="1.0",
            to_version="1.1",
            migration_func=lambda x: x
        )
        
        assert migration.is_applicable("2.0") is False
    
    def test_migration_chain_init(self):
        """Test MigrationChain initialization."""
        chain = MigrationChain()
        assert chain.migrations == []
    
    def test_add_migration_to_chain(self):
        """Test adding migration to chain."""
        chain = MigrationChain()
        migration = StateMigration(
            from_version="1.0",
            to_version="1.1",
            migration_func=lambda x: x
        )
        
        chain.add_migration(migration)
        assert len(chain.migrations) == 1
        assert chain.migrations[0] == migration
    
    def test_find_migration_path_empty_chain(self):
        """Test finding migration path with empty chain raises ValueError."""
        chain = MigrationChain()
        
        import pytest
        with pytest.raises(ValueError, match="No migration path from 1.0 to 2.0"):
            chain.find_migration_path("1.0", "2.0")
    
    def test_migration_default_description(self):
        """Test default description for migration."""
        migration = StateMigration(
            from_version="1.0",
            to_version="1.1",
            migration_func=lambda x: x
        )
        
        assert migration.description == ""