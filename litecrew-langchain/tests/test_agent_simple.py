"""Simple focused tests for Agent class to boost coverage."""

from unittest.mock import Mock, patch

from litecrew.agent import Agent, LiteAgent


class TestAgentSimple:
    """Simple tests to boost Agent coverage."""

    def test_lite_agent_compatibility(self):
        """Test LiteAgent base class."""
        agent = LiteAgent()
        agent2 = LiteAgent("any", "args", key="value")
        assert agent is not None
        assert agent2 is not None

    def test_basic_agent_properties(self):
        """Test basic agent properties."""
        agent = Agent(role="Test Agent", goal="Test goal", backstory="Test backstory")

        assert agent.role == "Test Agent"
        assert agent.goal == "Test goal"
        assert agent.backstory == "Test backstory"
        assert agent.tools == []
        assert agent.verbose is False
        assert agent.max_iter == 5
        assert agent.allow_delegation is True
        assert agent.streaming is False
        assert agent.async_execution is True
        assert agent.cache_responses is True
        assert agent._memory_enabled is True

    def test_agent_with_config(self):
        """Test agent with configuration options."""
        agent = Agent(
            role="Config Agent",
            goal="Test config",
            backstory="Test config",
            verbose=True,
            max_iter=10,
            allow_delegation=False,
            memory=False,
            streaming=True,
            cache_responses=False,
        )

        assert agent.verbose is True
        assert agent.max_iter == 10
        assert agent.allow_delegation is False
        assert agent._memory_enabled is False
        assert agent.streaming is True
        assert agent.cache_responses is False

    def test_agent_build_system_message(self):
        """Test system message building."""
        agent = Agent(
            role="System Agent", goal="System goal", backstory="System backstory"
        )

        message = agent._build_system_message()
        assert "You are System Agent" in message
        assert "System goal" in message
        assert "System backstory" in message
        assert "tools" in message
        assert "Final Answer" in message

    def test_agent_convert_tools(self):
        """Test tool conversion."""
        agent = Agent(role="Tool Agent", goal="Test", backstory="Test")

        # Test with empty tools
        converted = agent._convert_tools([])
        assert len(converted) == 0

        # Test with callable function
        def test_func(x):
            return f"result: {x}"

        converted = agent._convert_tools([test_func])
        assert len(converted) == 1
        assert converted[0].name == "test_func"

    def test_agent_parse_providers(self):
        """Test provider parsing."""
        agent = Agent(role="Provider Agent", goal="Test", backstory="Test")

        # Test with empty list
        providers = agent._parse_providers([])
        assert len(providers) == 0

        # Test with invalid provider (should be handled gracefully)
        agent.verbose = False  # Suppress output
        providers = agent._parse_providers(["invalid_provider"])
        assert len(providers) == 0

    def test_agent_get_model_name(self):
        """Test getting model name."""
        agent = Agent(role="Model Agent", goal="Test", backstory="Test")

        # Mock LLM with model_name
        agent.llm = Mock()
        agent.llm.model_name = "test-model"

        name = agent._get_model_name()
        assert name == "test-model"

        # Test fallback to _llm_type
        delattr(agent.llm, "model_name")
        agent.llm._llm_type = "test_type"

        name = agent._get_model_name()
        assert name == "test_type"

        # Test fallback to class name
        delattr(agent.llm, "_llm_type")
        agent.llm.__class__.__name__ = "TestLLM"

        name = agent._get_model_name()
        assert name == "TestLLM"

    def test_agent_repr(self):
        """Test agent string representation."""
        agent = Agent(role="Repr Agent", goal="Test repr", backstory="Test repr")

        repr_str = repr(agent)
        assert "Agent" in repr_str
        assert "Repr Agent" in repr_str
        assert "Test repr" in repr_str

    def test_agent_clear_memory(self):
        """Test memory clearing."""
        agent = Agent(role="Memory Agent", goal="Test", backstory="Test")

        # Should not raise error
        agent.clear_memory()

        # Test with mock memory
        agent._conversation_memory = Mock()
        agent.clear_memory()
        agent._conversation_memory.clear.assert_called_once()

    def test_agent_search_memory_no_memory(self):
        """Test memory search without memory."""
        agent = Agent(
            role="Search Agent",
            goal="Test search",
            backstory="Test search",
            memory=False,
        )

        results = agent.search_memory("test query")
        assert results == []

    def test_agent_search_memory_with_memory(self):
        """Test memory search with memory."""
        agent = Agent(role="Memory Agent", goal="Test", backstory="Test")

        # Mock memory search
        with patch("litecrew.memory.MemorySearch") as mock_search_class:
            mock_search = Mock()
            mock_search.search.return_value = [{"content": "test"}]
            mock_search_class.return_value = mock_search

            agent._conversation_memory = Mock()

            results = agent.search_memory("test query")
            assert len(results) == 1
            assert results[0]["content"] == "test"

    def test_agent_metrics(self):
        """Test agent metrics."""
        agent = Agent(role="Metrics Agent", goal="Test", backstory="Test")

        metrics = agent.metrics()
        assert isinstance(metrics, dict)
        assert "creation_time_ms" in metrics
        assert "execution_count" in metrics
        assert "memory_enabled" in metrics
        assert "tools_count" in metrics
        assert "cache_enabled" in metrics

        # Test execution count
        assert metrics["execution_count"] == 0
        assert metrics["memory_enabled"] is True
        assert metrics["cache_enabled"] is True

    def test_agent_get_metrics(self):
        """Test get_metrics method."""
        agent = Agent(role="Get Metrics Agent", goal="Test", backstory="Test")

        # get_metrics should return the metrics method, not call it
        result = agent.get_metrics()
        assert callable(result)  # It returns the method itself

        # Call it to get actual metrics
        metrics = result()
        assert isinstance(metrics, dict)

    def test_agent_switch_llm_provider(self):
        """Test switching LLM provider."""
        agent = Agent(role="Switch Agent", goal="Test", backstory="Test")

        original_llm = agent.llm

        with patch.object(agent, "_initialize_llm") as mock_init:
            mock_llm = Mock()
            mock_init.return_value = mock_llm

            from litecrew.llm import LLMProvider

            agent.switch_llm_provider(LLMProvider.OPENAI)

            mock_init.assert_called_once()
            assert agent.llm == mock_llm

    def test_agent_budget_alert_handler(self):
        """Test budget alert handler."""
        agent = Agent(role="Budget Agent", goal="Test", backstory="Test")

        # Should not raise error
        agent._budget_alert_handler("Test alert", 50.0, 100.0)

        # Test with verbose mode
        agent.verbose = True
        with patch("builtins.print") as mock_print:
            agent._budget_alert_handler("Budget alert", 75.0, 100.0)
            mock_print.assert_called()

    def test_agent_validate_agent_type(self):
        """Test agent type validation."""
        agent = Agent(role="Type Agent", goal="Test", backstory="Test")

        with patch("litecrew.agent_types.AgentTypeFactory.list_types") as mock_list:
            mock_list.return_value = ["thinking", "conversational", "critic"]

            assert agent._validate_agent_type("thinking") is True
            assert agent._validate_agent_type("invalid") is False

    def test_agent_get_type_info_no_type(self):
        """Test get_type_info when no type is set."""
        agent = Agent(role="Info Agent", goal="Test", backstory="Test")

        with patch("litecrew.agent_types.AgentTypeFactory.list_types") as mock_list:
            mock_list.return_value = ["thinking", "conversational"]

            info = agent.get_type_info()

            assert info["type"] is None
            assert info["config"] == {}
            assert info["available_types"] == ["thinking", "conversational"]

    def test_agent_validate_type_config_no_type(self):
        """Test validating type config when no type is set."""
        agent = Agent(role="Config Agent", goal="Test", backstory="Test")

        # Should return True when no type is set
        assert agent.validate_type_config() is True

    def test_agent_with_rate_limiting(self):
        """Test agent with rate limiting."""
        agent = Agent(
            role="Rate Agent",
            goal="Test rate limiting",
            backstory="Test rate limiting",
            max_rpm=60,
            track_tokens=True,
            budget_limit=100.0,
        )

        assert agent.max_rpm == 60
        assert agent.track_tokens is True
        assert agent._rate_limiter is not None
        assert agent._token_counter is not None
        assert agent._budget_manager is not None

    def test_agent_with_structured_outputs(self):
        """Test agent with structured outputs."""
        from dataclasses import dataclass

        @dataclass
        class TestOutput:
            result: str

        agent = Agent(
            role="Structured Agent",
            goal="Test structured outputs",
            backstory="Test structured outputs",
            output_dataclass=TestOutput,
            output_schema={"type": "object"},
            save_outputs=True,
            auto_fix_outputs=True,
        )

        assert agent._output_parser is not None
        assert agent._output_validator is not None
        assert agent.save_outputs is True
        assert agent.auto_fix_outputs is True

    def test_agent_with_file_handler(self):
        """Test agent with file output handler."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            agent = Agent(
                role="File Agent",
                goal="Test file outputs",
                backstory="Test file outputs",
                output_dir=temp_dir,
                save_outputs=True,
            )

            assert agent._file_handler is not None

    def test_agent_with_event_system(self):
        """Test agent with event system."""
        from litecrew.events import EventEmitter, LifecycleCallbacks

        event_emitter = EventEmitter()
        lifecycle_callbacks = LifecycleCallbacks()

        agent = Agent(
            role="Event Agent",
            goal="Test events",
            backstory="Test events",
            event_emitter=event_emitter,
            lifecycle_callbacks=lifecycle_callbacks,
        )

        assert agent.event_emitter == event_emitter
        assert agent.lifecycle_callbacks == lifecycle_callbacks

    def test_agent_execution_basic(self):
        """Test basic agent execution."""
        agent = Agent(role="Exec Agent", goal="Test", backstory="Test")

        # Mock the agent executor
        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": "Test result"}

        result = agent.execute("Test task")
        assert result == "Test result"
        assert agent._execution_count == 1

    def test_agent_execution_with_context(self):
        """Test agent execution with context."""
        agent = Agent(role="Context Agent", goal="Test", backstory="Test")

        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": "Context result"}

        result = agent.execute("Test task", "Test context")
        assert result == "Context result"

    def test_agent_execution_error_handling(self):
        """Test agent execution error handling."""
        agent = Agent(role="Error Agent", goal="Test", backstory="Test")

        agent._agent_executor = Mock()
        agent._agent_executor.invoke.side_effect = Exception("Test error")

        result = agent.execute("Test task")
        assert "error" in result.lower()
        assert "test error" in result.lower()

    def test_agent_with_memory_interactions(self):
        """Test agent memory interactions during execution."""
        agent = Agent(role="Memory Agent", goal="Test", backstory="Test")

        # Mock components
        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": "Memory result"}
        agent._conversation_memory = Mock()

        result = agent.execute("Test task")

        # Should store in memory
        agent._conversation_memory.add_interaction.assert_called_once()
        assert result == "Memory result"

    def test_agent_with_events_during_execution(self):
        """Test agent event emission during execution."""

        event_emitter = Mock()
        agent = Agent(
            role="Event Agent",
            goal="Test",
            backstory="Test",
            event_emitter=event_emitter,
        )

        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": "Event result"}

        result = agent.execute("Test task")

        # Should emit events
        assert event_emitter.emit.call_count >= 2  # Start and complete events
        assert result == "Event result"
