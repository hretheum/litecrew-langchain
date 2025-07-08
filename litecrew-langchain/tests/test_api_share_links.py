"""Tests for share links functionality."""

import base64
import json

import pytest

from litecrew.api.share_links import ShareLinkManager, get_share_manager


class TestShareLinkManager:
    """Test share link manager functionality."""

    @pytest.fixture
    def manager(self):
        """Create a share link manager instance."""
        return ShareLinkManager()

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "process_type": "debate",
            "agents": [
                {"role": "Debater 1", "goal": "Argue for"},
                {"role": "Debater 2", "goal": "Argue against"},
            ],
            "topic": "AI Safety",
            "max_rounds": 5,
        }

    def test_create_share_link(self, manager, sample_config):
        """Test creating a share link."""
        base_url = "https://example.com"
        link = manager.create_share_link(sample_config, base_url)

        # Check link format
        assert link.startswith(f"{base_url}/#/shared/")

        # Extract link ID
        link_id = link.split("/")[-1]
        assert len(link_id) == 8  # UUID first 8 chars

        # Check link was stored
        assert link_id in manager.links
        assert manager.links[link_id]["config"] == sample_config
        assert manager.links[link_id]["uses"] == 0

    def test_create_share_link_no_base_url(self, manager, sample_config):
        """Test creating share link without base URL."""
        link = manager.create_share_link(sample_config)
        assert link.startswith("/#/shared/")

    def test_create_embedded_link(self, manager, sample_config):
        """Test creating embedded link."""
        base_url = "https://example.com"
        link = manager.create_embedded_link(sample_config, base_url)

        # Check link format
        assert link.startswith(f"{base_url}/#/config/")

        # Extract and decode config
        encoded_part = link.split("/")[-1]
        decoded_json = base64.urlsafe_b64decode(encoded_part.encode()).decode()
        decoded_config = json.loads(decoded_json)

        assert decoded_config == sample_config

    def test_create_embedded_link_compact_json(self, manager):
        """Test that embedded link uses compact JSON."""
        config = {"key": "value", "nested": {"a": 1, "b": 2}}
        link = manager.create_embedded_link(config)

        # Extract encoded part
        encoded_part = link.split("/")[-1]
        decoded_json = base64.urlsafe_b64decode(encoded_part.encode()).decode()

        # Should not have spaces after separators
        assert ": " not in decoded_json
        assert ", " not in decoded_json

    def test_get_config_from_link(self, manager, sample_config):
        """Test retrieving config from share link."""
        # Create link
        link = manager.create_share_link(sample_config)
        link_id = link.split("/")[-1]

        # Get config
        retrieved_config = manager.get_config_from_link(link_id)
        assert retrieved_config == sample_config

        # Check usage was incremented
        assert manager.links[link_id]["uses"] == 1

        # Get again
        retrieved_config = manager.get_config_from_link(link_id)
        assert retrieved_config == sample_config
        assert manager.links[link_id]["uses"] == 2

    def test_get_config_from_link_not_found(self, manager):
        """Test retrieving config with invalid link ID."""
        config = manager.get_config_from_link("nonexistent")
        assert config is None

    def test_get_config_from_embedded(self, manager, sample_config):
        """Test retrieving config from embedded link."""
        # Create embedded link
        link = manager.create_embedded_link(sample_config)
        encoded_part = link.split("/")[-1]

        # Get config
        retrieved_config = manager.get_config_from_embedded(encoded_part)
        assert retrieved_config == sample_config

    def test_get_config_from_embedded_invalid(self, manager):
        """Test retrieving config from invalid embedded data."""
        # Invalid base64
        config = manager.get_config_from_embedded("not-base64!")
        assert config is None

        # Valid base64 but invalid JSON
        invalid_json = base64.urlsafe_b64encode(b"not json").decode()
        config = manager.get_config_from_embedded(invalid_json)
        assert config is None

    def test_list_shared_links(self, manager, sample_config):
        """Test listing all shared links."""
        # Initially empty
        assert manager.list_shared_links() == {}

        # Create some links
        link1 = manager.create_share_link(sample_config)
        link2 = manager.create_share_link({"different": "config"})

        links = manager.list_shared_links()
        assert len(links) == 2

        # Check structure
        for link_id, link_data in links.items():
            assert "config" in link_data
            assert "created_at" in link_data
            assert "uses" in link_data

    def test_delete_link(self, manager, sample_config):
        """Test deleting a shared link."""
        # Create link
        link = manager.create_share_link(sample_config)
        link_id = link.split("/")[-1]

        # Delete it
        result = manager.delete_link(link_id)
        assert result is True
        assert link_id not in manager.links

        # Try to get it
        config = manager.get_config_from_link(link_id)
        assert config is None

        # Delete non-existent
        result = manager.delete_link("nonexistent")
        assert result is False

    def test_multiple_links_same_config(self, manager, sample_config):
        """Test creating multiple links for same config."""
        links = []
        for _ in range(3):
            link = manager.create_share_link(sample_config)
            links.append(link)

        # All should be different
        assert len(set(links)) == 3

        # All should work
        for link in links:
            link_id = link.split("/")[-1]
            config = manager.get_config_from_link(link_id)
            assert config == sample_config

    def test_special_characters_in_config(self, manager):
        """Test handling special characters in configuration."""
        config = {
            "text": "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "unicode": "Unicode: 你好 مرحبا שלום",
            "escaped": "Escaped: \n\t\r\\",
        }

        # Test embedded link
        link = manager.create_embedded_link(config)
        encoded_part = link.split("/")[-1]
        retrieved = manager.get_config_from_embedded(encoded_part)
        assert retrieved == config

        # Test share link
        share_link = manager.create_share_link(config)
        link_id = share_link.split("/")[-1]
        retrieved = manager.get_config_from_link(link_id)
        assert retrieved == config

    def test_large_config(self, manager):
        """Test handling large configurations."""
        # Create a large config
        large_config = {
            f"key_{i}": {
                "data": f"value_{i}" * 100,
                "nested": {f"sub_{j}": j for j in range(10)},
            }
            for i in range(50)
        }

        # Should handle large embedded link
        link = manager.create_embedded_link(large_config)
        encoded_part = link.split("/")[-1]
        retrieved = manager.get_config_from_embedded(encoded_part)
        assert retrieved == large_config

    def test_link_id_uniqueness(self, manager, sample_config):
        """Test that link IDs are unique."""
        link_ids = set()

        # Create many links
        for _ in range(100):
            link = manager.create_share_link(sample_config)
            link_id = link.split("/")[-1]
            link_ids.add(link_id)

        # All should be unique
        assert len(link_ids) == 100


class TestShareManagerSingleton:
    """Test share manager singleton pattern."""

    def test_get_share_manager_returns_singleton(self):
        """Test that get_share_manager returns same instance."""
        manager1 = get_share_manager()
        manager2 = get_share_manager()
        assert manager1 is manager2

    def test_singleton_preserves_state(self):
        """Test that singleton preserves state between calls."""
        manager1 = get_share_manager()
        config = {"test": "config"}

        # Create link with first reference
        link = manager1.create_share_link(config)
        link_id = link.split("/")[-1]

        # Get second reference and check state
        manager2 = get_share_manager()
        retrieved = manager2.get_config_from_link(link_id)
        assert retrieved == config
