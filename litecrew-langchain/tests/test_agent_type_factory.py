"""Tests for AgentTypeFactory to improve coverage."""

import pytest
from unittest.mock import Mock, patch
from litecrew.agent_types.factory import AgentTypeFactory
from litecrew.agent_types.base import AgentType, AgentTypeConfig


class TestAgentTypeFactory:
    """Tests for AgentTypeFactory."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Save original registry state
        self.original_registry = AgentTypeFactory._registry.copy()
        self.original_configs = AgentTypeFactory._default_configs.copy()
    
    def teardown_method(self):
        """Clean up after tests."""
        # Restore original registry state
        AgentTypeFactory._registry = self.original_registry
        AgentTypeFactory._default_configs = self.original_configs
    
    def test_register_type_basic(self):
        """Test basic type registration."""
        # Create a mock agent type class
        mock_agent_class = Mock(spec=AgentType)
        
        # Register the type
        AgentTypeFactory.register_type("test_agent", mock_agent_class)
        
        # Check if it was registered
        assert "test_agent" in AgentTypeFactory._registry
        assert AgentTypeFactory._registry["test_agent"] == mock_agent_class
    
    def test_register_type_with_default_config(self):
        """Test type registration with default config."""
        # Create a mock agent type class and config
        mock_agent_class = Mock(spec=AgentType)
        mock_config = AgentTypeConfig(
            name="test_agent",
            description="Test agent",
            system_prompt_template="Test prompt"
        )
        
        # Register the type with config
        AgentTypeFactory.register_type("test_agent", mock_agent_class, mock_config)
        
        # Check if both were registered
        assert "test_agent" in AgentTypeFactory._registry
        assert "test_agent" in AgentTypeFactory._default_configs
        assert AgentTypeFactory._default_configs["test_agent"] == mock_config
    
    def test_register_type_lowercase_conversion(self):
        """Test that type names are converted to lowercase."""
        mock_agent_class = Mock(spec=AgentType)
        
        # Register with uppercase name
        AgentTypeFactory.register_type("TEST_AGENT", mock_agent_class)
        
        # Should be stored in lowercase
        assert "test_agent" in AgentTypeFactory._registry
        assert "TEST_AGENT" not in AgentTypeFactory._registry
    
    def test_create_known_type(self):
        """Test creating a known agent type."""
        # Register a mock type
        mock_agent_class = Mock(spec=AgentType)
        mock_instance = Mock()
        mock_agent_class.return_value = mock_instance
        
        AgentTypeFactory.register_type("test_agent", mock_agent_class)
        
        # Create instance
        result = AgentTypeFactory.create("test_agent")
        
        # Should call the constructor and return instance
        mock_agent_class.assert_called_once()
        assert result == mock_instance
    
    def test_create_unknown_type(self):
        """Test creating an unknown agent type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown agent type: unknown_type"):
            AgentTypeFactory.create("unknown_type")
    
    def test_create_with_default_config(self):
        """Test creating agent with default config."""
        # Create mock agent class and config
        mock_agent_class = Mock(spec=AgentType)
        mock_instance = Mock()
        mock_agent_class.return_value = mock_instance
        
        default_config = AgentTypeConfig(
            name="test_agent",
            description="Test agent",
            system_prompt_template="Default prompt"
        )
        
        # Register type with default config
        AgentTypeFactory.register_type("test_agent", mock_agent_class, default_config)
        
        # Create instance
        result = AgentTypeFactory.create("test_agent")
        
        # Should use default config
        mock_agent_class.assert_called_once_with(default_config)
        assert result == mock_instance
    
    def test_create_with_config_override(self):
        """Test creating agent with config override."""
        # Create mock agent class
        mock_agent_class = Mock(spec=AgentType)
        mock_instance = Mock()
        mock_agent_class.return_value = mock_instance
        
        # Create default config
        default_config = AgentTypeConfig(
            name="test_agent",
            description="Default description",
            system_prompt_template="Default prompt"
        )
        
        # Register type with default config
        AgentTypeFactory.register_type("test_agent", mock_agent_class, default_config)
        
        # Create with override
        override_config = {"description": "Override description"}
        result = AgentTypeFactory.create("test_agent", override_config)
        
        # Should modify the default config
        mock_agent_class.assert_called_once()
        used_config = mock_agent_class.call_args[0][0]
        assert used_config.description == "Override description"
        assert used_config.system_prompt_template == "Default prompt"  # Unchanged
    
    def test_create_with_config_override_invalid_attr(self):
        """Test config override with invalid attribute."""
        # Create mock agent class
        mock_agent_class = Mock(spec=AgentType)
        mock_instance = Mock()
        mock_agent_class.return_value = mock_instance
        
        # Create default config
        default_config = AgentTypeConfig(
            name="test_agent",
            description="Test",
            system_prompt_template="Test"
        )
        
        # Register type
        AgentTypeFactory.register_type("test_agent", mock_agent_class, default_config)
        
        # Create with invalid override
        override_config = {"invalid_attr": "value", "description": "Valid override"}
        result = AgentTypeFactory.create("test_agent", override_config)
        
        # Should ignore invalid attribute, apply valid one
        mock_agent_class.assert_called_once()
        used_config = mock_agent_class.call_args[0][0]
        assert used_config.description == "Valid override"
        assert not hasattr(used_config, "invalid_attr")
    
    def test_create_without_default_config_with_get_default_config(self):
        """Test creating agent without default config but with get_default_config method."""
        # Create mock agent class with get_default_config
        mock_agent_class = Mock()
        mock_instance = Mock()
        mock_agent_class.return_value = mock_instance
        
        # Mock get_default_config method
        mock_config = AgentTypeConfig(
            name="test_agent",
            description="From get_default_config",
            system_prompt_template="Method prompt"
        )
        mock_agent_class.get_default_config = Mock(return_value=mock_config)
        
        # Register type without default config
        AgentTypeFactory.register_type("test_agent", mock_agent_class)
        
        # Create instance
        result = AgentTypeFactory.create("test_agent")
        
        # Should call get_default_config and use returned config
        mock_agent_class.get_default_config.assert_called_once()
        mock_agent_class.assert_called_once_with(mock_config)
    
    def test_create_without_default_config_fallback(self):
        """Test creating agent without default config and without get_default_config."""
        # Create mock agent class without get_default_config
        mock_agent_class = Mock(spec=AgentType)
        mock_instance = Mock()
        mock_agent_class.return_value = mock_instance
        
        # Make sure get_default_config doesn't exist
        if hasattr(mock_agent_class, 'get_default_config'):
            delattr(mock_agent_class, 'get_default_config')
        
        # Register type without default config
        AgentTypeFactory.register_type("test_agent", mock_agent_class)
        
        # Create instance
        result = AgentTypeFactory.create("test_agent")
        
        # Should use fallback config
        mock_agent_class.assert_called_once()
        used_config = mock_agent_class.call_args[0][0]
        assert isinstance(used_config, AgentTypeConfig)
        assert used_config.name == "test_agent"
        assert "Default test_agent agent" in used_config.description
    
    def test_create_with_config_override_no_default(self):
        """Test creating agent with config override when no default config."""
        # Create mock agent class
        mock_agent_class = Mock()
        mock_instance = Mock()
        mock_agent_class.return_value = mock_instance
        
        # Mock get_default_config
        default_config = AgentTypeConfig(
            name="test_agent",
            description="Method default",
            system_prompt_template="Method prompt"
        )
        mock_agent_class.get_default_config = Mock(return_value=default_config)
        
        # Register type without default config
        AgentTypeFactory.register_type("test_agent", mock_agent_class)
        
        # Create with config override
        override_config = {"description": "Override description"}
        result = AgentTypeFactory.create("test_agent", override_config)
        
        # Should apply override to method-generated config
        mock_agent_class.assert_called_once()
        used_config = mock_agent_class.call_args[0][0]
        assert used_config.description == "Override description"
        assert used_config.system_prompt_template == "Method prompt"
    
    def test_list_types(self):
        """Test listing available types."""
        # Clear registry for clean test
        AgentTypeFactory._registry.clear()
        
        # Add some types
        mock_class1 = Mock(spec=AgentType)
        mock_class2 = Mock(spec=AgentType)
        
        AgentTypeFactory.register_type("type1", mock_class1)
        AgentTypeFactory.register_type("type2", mock_class2)
        
        # Get list
        types = AgentTypeFactory.list_types()
        
        # Should contain both types
        assert "type1" in types
        assert "type2" in types
        assert len(types) == 2
    
    def test_get_type_info_known_type(self):
        """Test getting info for known type."""
        # Create mock agent class with get_default_config
        mock_agent_class = Mock()
        mock_config = AgentTypeConfig(
            name="test_agent",
            description="Test agent description",
            system_prompt_template="Test prompt {role}"
        )
        mock_agent_class.get_default_config = Mock(return_value=mock_config)
        
        # Register type
        AgentTypeFactory.register_type("test_agent", mock_agent_class)
        
        # Get info
        info = AgentTypeFactory.get_type_info("test_agent")
        
        # Check info structure
        assert info["name"] == "test_agent"
        assert info["description"] == "Test agent description"
        assert "configurable_options" in info
        assert "default_config" in info
        assert isinstance(info["configurable_options"], list)
        assert isinstance(info["default_config"], dict)
    
    def test_get_type_info_unknown_type(self):
        """Test getting info for unknown type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown agent type: unknown_type"):
            AgentTypeFactory.get_type_info("unknown_type")
    
    def test_get_type_info_without_get_default_config(self):
        """Test getting info for type without get_default_config method."""
        # Create mock agent class without get_default_config
        mock_agent_class = Mock(spec=AgentType)
        if hasattr(mock_agent_class, 'get_default_config'):
            delattr(mock_agent_class, 'get_default_config')
        
        # Register type
        AgentTypeFactory.register_type("test_agent", mock_agent_class)
        
        # Get info
        info = AgentTypeFactory.get_type_info("test_agent")
        
        # Should use fallback config
        assert info["name"] == "test_agent"
        assert "Default test_agent agent" in info["description"]
        assert "configurable_options" in info
        assert "default_config" in info
    
    def test_case_insensitive_operations(self):
        """Test that operations are case insensitive."""
        # Register with lowercase
        mock_agent_class = Mock(spec=AgentType)
        mock_instance = Mock()
        mock_agent_class.return_value = mock_instance
        
        AgentTypeFactory.register_type("test_agent", mock_agent_class)
        
        # Create with different cases
        result1 = AgentTypeFactory.create("TEST_AGENT")
        result2 = AgentTypeFactory.create("Test_Agent")
        result3 = AgentTypeFactory.create("test_agent")
        
        # All should work
        assert mock_agent_class.call_count == 3
    
    def test_default_types_available(self):
        """Test that default agent types are available."""
        # Default types should be registered
        types = AgentTypeFactory.list_types()
        
        expected_types = ["conversational", "thinking", "moderator", "critic"]
        for expected_type in expected_types:
            assert expected_type in types
    
    def test_create_default_conversational_agent(self):
        """Test creating default conversational agent."""
        # Should be able to create without error
        agent = AgentTypeFactory.create("conversational")
        
        # Should be an instance of AgentType
        assert isinstance(agent, AgentType)
    
    def test_create_default_thinking_agent(self):
        """Test creating default thinking agent."""
        # Should be able to create without error
        agent = AgentTypeFactory.create("thinking")
        
        # Should be an instance of AgentType
        assert isinstance(agent, AgentType)