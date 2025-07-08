"""Comprehensive tests for Agent class to boost coverage to 80%."""

import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from litecrew.agent import Agent, LiteAgent
from litecrew.events import EventEmitter, LifecycleCallbacks
from litecrew.llm import LLMConfig, LLMProvider


class MockTool:
    """Mock tool for testing."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def run(self, input_text: str) -> str:
        return f"Mock result for {input_text}"


class MockLLM:
    """Mock LLM for testing - simplified version that works with LangChain."""

    def __init__(self):
        self.model_name = "mock-llm"

    def _generate(self, prompts, **kwargs):
        from langchain_core.outputs import Generation, LLMResult

        return LLMResult(generations=[[Generation(text="Mock response")]])

    @property
    def _llm_type(self) -> str:
        return "mock"
    
    def invoke(self, input, **kwargs):
        """Support invoke method."""
        return "Mock response"
    
    async def ainvoke(self, input, **kwargs):
        """Support async invoke method."""
        return "Mock response"
    
    def bind(self, **kwargs):
        """Support bind method."""
        return self


class TestLiteAgent:
    """Test the base LiteAgent class."""

    def test_lite_agent_init(self):
        """Test LiteAgent initialization with any arguments."""
        agent = LiteAgent()
        assert agent is not None

        # Should accept any arguments
        agent = LiteAgent("test", goal="test", role="test", random_arg=123)
        assert agent is not None


class TestAgentInitialization:
    """Test Agent initialization with various configurations."""

    def test_basic_agent_creation(self):
        """Test basic agent creation with minimal parameters."""
        agent = Agent(role="Test Agent", goal="Test goal", backstory="Test backstory")

        assert agent.role == "Test Agent"
        assert agent.goal == "Test goal"
        assert agent.backstory == "Test backstory"
        assert agent.tools == []
        assert agent.verbose is False
        assert agent.max_iter == 5
        assert agent.allow_delegation is True
        assert agent.cache_responses is True
        assert agent.streaming is False
        assert agent.async_execution is True

    def test_agent_with_tools(self):
        """Test agent creation with tools."""
        tool1 = MockTool("search", "Search for information")
        tool2 = MockTool("calculator", "Perform calculations")

        agent = Agent(
            role="Researcher",
            goal="Research topics",
            backstory="Expert researcher",
            tools=[tool1, tool2],
        )

        assert len(agent.tools) == 2
        assert agent.tools[0] == tool1
        assert agent.tools[1] == tool2

    def test_agent_with_custom_llm(self):
        """Test agent creation with custom LLM."""
        from langchain_core.language_models import BaseLLM
        from langchain_core.outputs import LLMResult, Generation
        
        class TestLLM(BaseLLM):
            def _generate(self, prompts, **kwargs):
                return LLMResult(generations=[[Generation(text="Mock response")]])
            
            @property
            def _llm_type(self) -> str:
                return "test"
        
        mock_llm = TestLLM()

        agent = Agent(
            role="Writer",
            goal="Write content",
            backstory="Professional writer",
            llm=mock_llm,
        )

        assert agent.llm == mock_llm

    def test_agent_with_memory_disabled(self):
        """Test agent creation with memory disabled."""
        agent = Agent(
            role="Analyst", goal="Analyze data", backstory="Data analyst", memory=False
        )

        assert agent._memory_enabled is False
        assert agent._memory is None
        assert agent._conversation_memory is None

    def test_agent_with_custom_config(self):
        """Test agent creation with custom configuration."""
        agent = Agent(
            role="Manager",
            goal="Manage team",
            backstory="Team manager",
            verbose=True,
            max_iter=10,
            allow_delegation=False,
            max_execution_time=300,
            streaming=True,
        )

        assert agent.verbose is True
        assert agent.max_iter == 10
        assert agent.allow_delegation is False
        assert agent.max_execution_time == 300
        assert agent.streaming is True

    def test_agent_with_rate_limiting(self):
        """Test agent creation with rate limiting configuration."""
        agent = Agent(
            role="API Agent",
            goal="Make API calls",
            backstory="API specialist",
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
        """Test agent creation with structured output configuration."""
        from dataclasses import dataclass

        @dataclass
        class TestOutput:
            result: str
            confidence: float

        agent = Agent(
            role="Structured Agent",
            goal="Generate structured output",
            backstory="Output specialist",
            output_dataclass=TestOutput,
            output_schema={
                "type": "object",
                "properties": {"test": {"type": "string"}},
            },
            save_outputs=True,
            auto_fix_outputs=True,
        )

        assert agent._output_parser is not None
        assert agent._output_validator is not None
        assert agent.auto_fix_outputs is True
        assert agent.save_outputs is True

    def test_agent_with_output_directory(self):
        """Test agent creation with output directory."""
        output_dir = Path("/tmp/test_outputs")

        agent = Agent(
            role="File Agent",
            goal="Generate files",
            backstory="File specialist",
            output_dir=output_dir,
            save_outputs=True,
        )

        assert agent._file_handler is not None

    def test_agent_with_event_system(self):
        """Test agent creation with event system."""
        event_emitter = EventEmitter()
        lifecycle_callbacks = LifecycleCallbacks()

        agent = Agent(
            role="Event Agent",
            goal="Handle events",
            backstory="Event specialist",
            event_emitter=event_emitter,
            lifecycle_callbacks=lifecycle_callbacks,
        )

        assert agent.event_emitter == event_emitter
        assert agent.lifecycle_callbacks == lifecycle_callbacks

    @patch("litecrew.agent_types.AgentTypeFactory")
    def test_agent_with_type_system(self, mock_factory):
        """Test agent creation with agent type system."""
        mock_agent_type = Mock()
        mock_agent_type.get_system_prompt.return_value = "Custom system prompt"
        mock_factory.create.return_value = mock_agent_type
        mock_factory.list_types.return_value = ["thinking", "conversational"]

        with patch("litecrew.agent.Agent._validate_agent_type", return_value=True):
            agent = Agent(
                role="Thinking Agent",
                goal="Think deeply",
                backstory="Deep thinker",
                type="thinking",
                type_config={"depth": "high"},
            )

            assert agent.type == "thinking"
            assert agent.type_config == {"depth": "high"}
            assert agent._agent_type == mock_agent_type

    @patch("litecrew.agent_types.AgentTypeFactory")
    def test_agent_with_invalid_type(self, mock_factory):
        """Test agent creation with invalid type."""
        mock_factory.list_types.return_value = ["thinking", "conversational"]

        with pytest.raises(ValueError, match="Invalid agent type"):
            Agent(
                role="Invalid Agent", goal="Test", backstory="Test", type="invalid_type"
            )


class TestAgentMethods:
    """Test Agent methods and functionality."""

    @pytest.fixture
    def basic_agent(self):
        """Create a basic agent for testing."""
        return Agent(role="Test Agent", goal="Test goal", backstory="Test backstory")

    def test_build_system_message(self, basic_agent):
        """Test system message building."""
        message = basic_agent._build_system_message()

        assert "You are Test Agent" in message
        assert "Test goal" in message
        assert "Test backstory" in message
        assert "tools" in message
        assert "Final Answer" in message

    def test_convert_tools_langchain(self, basic_agent):
        """Test converting LangChain tools."""
        from langchain.tools import Tool

        lc_tool = Tool(
            name="test_tool", description="Test tool", func=lambda x: "result"
        )

        converted = basic_agent._convert_tools([lc_tool])
        assert len(converted) == 1
        assert converted[0] == lc_tool

    def test_convert_tools_crewai_style(self, basic_agent):
        """Test converting CrewAI-style tools."""
        mock_tool = MockTool("search", "Search tool")

        converted = basic_agent._convert_tools([mock_tool])
        assert len(converted) == 1
        assert converted[0].name == "search"
        assert converted[0].description == "Search tool"

    def test_convert_tools_callable(self, basic_agent):
        """Test converting callable tools."""

        def test_function(input_text: str) -> str:
            return f"Processed: {input_text}"

        converted = basic_agent._convert_tools([test_function])
        assert len(converted) == 1
        assert converted[0].name == "test_function"
        assert "test_function" in converted[0].description

    def test_parse_providers_string(self, basic_agent):
        """Test parsing provider strings."""
        providers = basic_agent._parse_providers(["openai", "anthropic"])
        assert len(providers) == 2
        assert LLMProvider.OPENAI in providers
        assert LLMProvider.ANTHROPIC in providers

    def test_parse_providers_enum(self, basic_agent):
        """Test parsing provider enums."""
        providers = basic_agent._parse_providers([LLMProvider.OPENAI])
        assert len(providers) == 1
        assert providers[0] == LLMProvider.OPENAI

    def test_parse_providers_invalid(self, basic_agent):
        """Test parsing invalid providers."""
        # Should handle invalid providers gracefully
        providers = basic_agent._parse_providers(["invalid_provider"])
        assert len(providers) == 0

    def test_get_model_name(self, basic_agent):
        """Test getting model name."""
        # Mock the LLM to have a model_name attribute
        basic_agent.llm = Mock()
        basic_agent.llm.model_name = "test-model"

        name = basic_agent._get_model_name()
        assert name == "test-model"

    def test_get_model_name_fallback(self, basic_agent):
        """Test getting model name with fallback."""
        # Mock LLM without model_name or model attribute
        basic_agent.llm = Mock()
        basic_agent.llm.model_name = None
        basic_agent.llm.model = None
        
        # Remove the attributes to test hasattr fallback
        if hasattr(basic_agent.llm, 'model_name'):
            delattr(basic_agent.llm, 'model_name')
        if hasattr(basic_agent.llm, 'model'):
            delattr(basic_agent.llm, 'model')

        name = basic_agent._get_model_name()
        assert name == "gpt-3.5-turbo"  # Default fallback

    def test_repr(self, basic_agent):
        """Test string representation."""
        repr_str = repr(basic_agent)
        assert "Agent" in repr_str
        assert "Test Agent" in repr_str
        assert "Test goal" in repr_str

    def test_clear_memory(self, basic_agent):
        """Test clearing memory."""
        # Should not raise error even if memory is None
        basic_agent.clear_memory()

        # Test with actual memory
        basic_agent._conversation_memory = Mock()
        basic_agent.clear_memory()
        basic_agent._conversation_memory.clear.assert_called_once()

    def test_search_memory_no_memory(self, basic_agent):
        """Test searching memory when no memory exists."""
        results = basic_agent.search_memory("test query")
        assert results == []

    def test_search_memory_with_memory(self, basic_agent):
        """Test searching memory with actual memory."""
        mock_memory = Mock()
        mock_memory.search.return_value = [{"content": "test"}]
        basic_agent._conversation_memory = mock_memory

        results = basic_agent.search_memory("test query")
        assert len(results) == 1
        assert results[0]["content"] == "test"

    def test_metrics(self, basic_agent):
        """Test getting metrics."""
        metrics = basic_agent.metrics

        assert "execution_count" in metrics
        assert "creation_time_ms" in metrics
        assert "memory_enabled" in metrics
        assert metrics["execution_count"] == 0
        assert metrics["memory_enabled"] is True
        assert isinstance(metrics["creation_time_ms"], float)

    def test_get_metrics_alias(self, basic_agent):
        """Test get_metrics method (alias for metrics)."""
        metrics1 = basic_agent.metrics
        metrics2 = basic_agent.get_metrics()

        # Metrics may have slight differences in timing, check key fields
        assert metrics1["execution_count"] == metrics2["execution_count"]
        assert metrics1["memory_enabled"] == metrics2["memory_enabled"]
        assert "creation_time_ms" in metrics1
        assert "creation_time_ms" in metrics2

    def test_switch_llm_provider(self, basic_agent):
        """Test switching LLM provider."""
        with patch.object(basic_agent, "_initialize_llm") as mock_init:
            mock_llm = Mock()
            mock_init.return_value = mock_llm

            basic_agent.switch_llm_provider(LLMProvider.ANTHROPIC)

            mock_init.assert_called_once_with(LLMProvider.ANTHROPIC, None)
            assert basic_agent.llm == mock_llm

    def test_budget_alert_handler(self, basic_agent):
        """Test budget alert handler."""
        # Should not raise error
        basic_agent._budget_alert_handler("Test alert", 50.0, 100.0)

        # Test with verbose mode
        basic_agent.verbose = True
        with patch("builtins.print") as mock_print:
            basic_agent._budget_alert_handler("Test alert", 75.0, 100.0)
            mock_print.assert_called()

    def test_validate_agent_type_valid(self, basic_agent):
        """Test validating valid agent type."""
        with patch("litecrew.agent_types.AgentTypeFactory.list_types") as mock_list:
            mock_list.return_value = ["thinking", "conversational"]

            assert basic_agent._validate_agent_type("thinking") is True

    def test_validate_agent_type_invalid(self, basic_agent):
        """Test validating invalid agent type."""
        with patch("litecrew.agent_types.AgentTypeFactory.list_types") as mock_list:
            mock_list.return_value = ["thinking", "conversational"]

            assert basic_agent._validate_agent_type("invalid") is False

    def test_get_type_info_no_type(self, basic_agent):
        """Test getting type info when no type is set."""
        info = basic_agent.get_type_info()

        assert info["type"] is None
        assert info["description"] is not None
        assert isinstance(info, dict)

    @patch("litecrew.agent_types.AgentTypeFactory")
    def test_get_type_info_with_type(self, mock_factory):
        """Test getting type info when type is set."""
        mock_agent_type = Mock()
        mock_agent_type.description = "Test type description"
        mock_agent_type.capabilities = ["thinking", "reasoning"]
        mock_factory.create.return_value = mock_agent_type
        mock_factory.list_types.return_value = ["thinking"]

        with patch("litecrew.agent.Agent._validate_agent_type", return_value=True):
            agent = Agent(
                role="Test",
                goal="Test",
                backstory="Test",
                type="thinking",
                type_config={"level": "high"},
            )

            info = agent.get_type_info()

            assert info["type"] == "thinking"
            assert info["config"] == {"level": "high"}
            assert info["description"] == "Test type description"

    def test_validate_type_config_no_type(self, basic_agent):
        """Test validating type config when no type is set."""
        assert basic_agent.validate_type_config() is True

    @patch("litecrew.agent_types.AgentTypeFactory")
    def test_validate_type_config_with_type(self, mock_factory):
        """Test validating type config when type is set."""
        mock_agent_type = Mock()
        mock_agent_type.validate_config.return_value = True
        mock_factory.create.return_value = mock_agent_type
        mock_factory.list_types.return_value = ["thinking"]

        with patch("litecrew.agent.Agent._validate_agent_type", return_value=True):
            agent = Agent(role="Test", goal="Test", backstory="Test", type="thinking")

            assert agent.validate_type_config() is True
            mock_agent_type.validate_config.assert_called_once()


class TestAgentExecution:
    """Test agent execution methods."""

    @pytest.fixture
    def agent_with_mock_executor(self):
        """Create agent with mocked executor."""
        agent = Agent(role="Test Agent", goal="Test", backstory="Test")
        agent._agent_executor = Mock()
        return agent

    def test_execute_basic(self, agent_with_mock_executor):
        """Test basic task execution."""
        agent_with_mock_executor._agent_executor.invoke.return_value = {
            "output": "Test result"
        }

        result = agent_with_mock_executor.execute("Test task")
        assert result == "Test result"
        agent_with_mock_executor._agent_executor.invoke.assert_called_once()

    def test_execute_with_context(self, agent_with_mock_executor):
        """Test execution with context."""
        agent_with_mock_executor._agent_executor.invoke.return_value = {
            "output": "Result with context"
        }

        result = agent_with_mock_executor.execute("Test task", "Context info")
        assert result == "Result with context"

    def test_execute_with_rate_limiting(self):
        """Test execution with rate limiting."""
        agent = Agent(
            role="Rate Limited Agent", goal="Test", backstory="Test", max_rpm=60
        )

        # Mock the rate limiter
        agent._rate_limiter = Mock()
        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": "Rate limited result"}

        result = agent.execute("Test task")

        # Should call rate limiter
        agent._rate_limiter.wait_if_needed.assert_called_once()
        assert result == "Rate limited result"

    def test_execute_with_token_tracking(self):
        """Test execution with token tracking."""
        agent = Agent(
            role="Token Tracked Agent", goal="Test", backstory="Test", track_tokens=True
        )

        # Mock components
        agent._token_counter = Mock()
        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": "Token tracked result"}

        with patch("litecrew.llm.utils.estimate_tokens", return_value=100):
            result = agent.execute("Test task")

        # Should track tokens
        agent._token_counter.add_tokens.assert_called()
        assert result == "Token tracked result"

    def test_execute_with_budget_management(self):
        """Test execution with budget management."""
        agent = Agent(
            role="Budget Managed Agent",
            goal="Test",
            backstory="Test",
            budget_limit=100.0,
            track_tokens=True,
        )

        # Mock components
        agent._budget_manager = Mock()
        agent._budget_manager.can_afford.return_value = True
        agent._token_counter = Mock()
        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": "Budget managed result"}

        with patch("litecrew.llm.utils.estimate_tokens", return_value=50):
            result = agent.execute("Test task")

        # Should check budget
        agent._budget_manager.can_afford.assert_called()
        assert result == "Budget managed result"

    def test_execute_budget_exceeded(self):
        """Test execution when budget is exceeded."""
        agent = Agent(
            role="Budget Exceeded Agent",
            goal="Test",
            backstory="Test",
            budget_limit=100.0,
            track_tokens=True,
        )

        # Mock budget manager to deny request
        agent._budget_manager = Mock()
        agent._budget_manager.can_afford.return_value = False
        agent._token_counter = Mock()

        with patch("litecrew.llm.utils.estimate_tokens", return_value=150):
            result = agent.execute("Test task")

        # Should return budget error message
        assert "budget limit exceeded" in result.lower()

    def test_execute_with_memory_storage(self, agent_with_mock_executor):
        """Test execution with memory storage."""
        # Setup memory
        agent_with_mock_executor._conversation_memory = Mock()
        agent_with_mock_executor._agent_executor.invoke.return_value = {
            "output": "Memory stored result"
        }

        result = agent_with_mock_executor.execute("Test task")

        # Should store in memory
        agent_with_mock_executor._conversation_memory.add_interaction.assert_called()
        assert result == "Memory stored result"

    def test_execute_with_event_emission(self, agent_with_mock_executor):
        """Test execution with event emission."""
        # Setup event emitter
        agent_with_mock_executor.event_emitter = Mock()
        agent_with_mock_executor._agent_executor.invoke.return_value = {
            "output": "Event emitted result"
        }

        result = agent_with_mock_executor.execute("Test task")

        # Should emit events
        assert (
            agent_with_mock_executor.event_emitter.emit.call_count >= 2
        )  # Start and complete
        assert result == "Event emitted result"

    def test_execute_with_lifecycle_callbacks(self, agent_with_mock_executor):
        """Test execution with lifecycle callbacks."""
        # Setup lifecycle callbacks
        agent_with_mock_executor.lifecycle_callbacks = Mock()
        agent_with_mock_executor._agent_executor.invoke.return_value = {
            "output": "Callback triggered result"
        }

        result = agent_with_mock_executor.execute("Test task")

        # Should trigger callbacks
        assert agent_with_mock_executor.lifecycle_callbacks.trigger.call_count >= 2
        assert result == "Callback triggered result"

    def test_execute_with_structured_output(self):
        """Test execution with structured output parsing."""
        from dataclasses import dataclass

        @dataclass
        class TestOutput:
            result: str
            confidence: float

        agent = Agent(
            role="Structured Agent",
            goal="Test",
            backstory="Test",
            output_dataclass=TestOutput,
        )

        # Mock executor and parser
        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {
            "output": '{"result": "test", "confidence": 0.9}'
        }
        agent._output_parser = Mock()
        agent._output_parser.parse.return_value = TestOutput("test", 0.9)

        result = agent.execute("Test task")

        # Should parse structured output
        agent._output_parser.parse.assert_called_once()
        assert isinstance(result, TestOutput)

    def test_execute_with_output_validation(self):
        """Test execution with output validation."""
        agent = Agent(
            role="Validated Agent",
            goal="Test",
            backstory="Test",
            output_schema={
                "type": "object",
                "properties": {"test": {"type": "string"}},
            },
        )

        # Mock executor and validator
        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": '{"test": "value"}'}
        agent._output_validator = Mock()
        agent._output_validator.validate.return_value = True

        result = agent.execute("Test task")

        # Should validate output
        agent._output_validator.validate.assert_called_once()
        assert result == '{"test": "value"}'

    def test_execute_with_file_output(self):
        """Test execution with file output saving."""
        agent = Agent(
            role="File Agent",
            goal="Test",
            backstory="Test",
            output_dir="/tmp/test",
            save_outputs=True,
        )

        # Mock executor and file handler
        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": "File content"}
        agent._file_handler = Mock()
        agent._file_handler.save.return_value = "/tmp/test/output.txt"

        result = agent.execute("Test task")

        # Should save to file
        agent._file_handler.save.assert_called_once()
        assert result == "File content"

    def test_execute_error_handling(self, agent_with_mock_executor):
        """Test execution error handling."""
        # Make executor raise an exception
        agent_with_mock_executor._agent_executor.invoke.side_effect = Exception(
            "Test error"
        )

        result = agent_with_mock_executor.execute("Test task")

        # Should handle error gracefully
        assert "error" in result.lower()
        assert "test error" in result.lower()


class TestAgentPerformance:
    """Test agent performance metrics and monitoring."""

    def test_creation_time_tracking(self):
        """Test that creation time is tracked."""
        start_time = time.perf_counter()
        agent = Agent(role="Test", goal="Test", backstory="Test")
        end_time = time.perf_counter()

        assert agent._creation_time >= start_time
        assert agent._creation_time <= end_time

    def test_execution_count_tracking(self):
        """Test that execution count is tracked."""
        agent = Agent(role="Test", goal="Test", backstory="Test")
        agent._agent_executor = Mock()
        agent._agent_executor.invoke.return_value = {"output": "result"}

        assert agent._execution_count == 0

        agent.execute("Task 1")
        assert agent._execution_count == 1

        agent.execute("Task 2")
        assert agent._execution_count == 2

    def test_metrics_completeness(self):
        """Test that metrics include all expected fields."""
        agent = Agent(
            role="Metrics Agent",
            goal="Track metrics",
            backstory="Metrics specialist",
            max_rpm=60,
            track_tokens=True,
            budget_limit=100.0,
        )

        metrics = agent.metrics()

        expected_fields = [
            "role",
            "goal",
            "backstory",
            "execution_count",
            "creation_time",
            "memory_enabled",
            "max_iterations",
            "allow_delegation",
            "cache_responses",
            "streaming",
            "async_execution",
        ]

        for field in expected_fields:
            assert field in metrics

        # Check rate limiting metrics
        if agent._rate_limiter:
            assert "rate_limiter" in metrics

        # Check token tracking metrics
        if agent._token_counter:
            assert "token_counter" in metrics

        # Check budget metrics
        if agent._budget_manager:
            assert "budget_manager" in metrics


class TestAgentLLMIntegration:
    """Test agent LLM integration and management."""

    def test_initialize_llm_with_provider(self):
        """Test LLM initialization with provider."""
        with patch("litecrew.llm.LLMManager.create_llm") as mock_create:
            mock_llm = Mock()
            mock_create.return_value = mock_llm

            agent = Agent(
                role="LLM Agent",
                goal="Test LLM",
                backstory="LLM specialist",
                llm_provider=LLMProvider.OPENAI,
            )

            mock_create.assert_called_once()
            assert agent.llm == mock_llm

    def test_initialize_llm_with_config(self):
        """Test LLM initialization with configuration."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-sonnet",
            temperature=0.7,
            max_tokens=1000,
        )

        with patch("litecrew.llm.LLMManager.create_llm") as mock_create:
            mock_llm = Mock()
            mock_create.return_value = mock_llm

            agent = Agent(
                role="Config Agent",
                goal="Test config",
                backstory="Config specialist",
                llm_config=config,
            )

            mock_create.assert_called_once()
            assert agent.llm == mock_llm

    def test_llm_fallback_providers(self):
        """Test LLM with fallback providers."""
        fallback_providers = [LLMProvider.ANTHROPIC, LLMProvider.OPENAI]

        agent = Agent(
            role="Fallback Agent",
            goal="Test fallbacks",
            backstory="Fallback specialist",
            fallback_providers=fallback_providers,
        )

        assert len(agent._fallback_providers) == 2
        assert LLMProvider.ANTHROPIC in agent._fallback_providers
        assert LLMProvider.OPENAI in agent._fallback_providers

    def test_response_caching(self):
        """Test response caching functionality."""
        agent = Agent(
            role="Cache Agent",
            goal="Test caching",
            backstory="Cache specialist",
            cache_responses=True,
        )

        assert agent._response_cache is not None
        assert agent.cache_responses is True

    def test_response_caching_disabled(self):
        """Test disabled response caching."""
        agent = Agent(
            role="No Cache Agent",
            goal="Test no caching",
            backstory="No cache specialist",
            cache_responses=False,
        )

        assert agent._response_cache is None
        assert agent.cache_responses is False
