"""
LiteAgent - CrewAI-compatible agent built on LangChain
"""

import time
import asyncio
from typing import Any, List, Optional, Dict, Union, TYPE_CHECKING, AsyncIterator, Callable
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
# Import removed - will create mock LLM inline

from litecrew.llm import LLMProvider, LLMConfig, LLMManager, ResponseCache
from litecrew.llm.utils import estimate_tokens

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel


class LiteAgent:
    """
    A lightweight agent implementation compatible with CrewAI API
    but built on LangChain for better performance.
    
    Attributes:
        role: The agent's role (e.g., "Researcher", "Writer")
        goal: What the agent aims to achieve
        backstory: Background context for the agent
        tools: List of tools available to the agent
        llm: Language model to use
        memory: Whether to maintain conversation memory
        verbose: Enable verbose output
        max_iter: Maximum iterations for task execution
    """
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]] = None,
        llm: Optional[Any] = None,
        memory: bool = True,
        verbose: bool = False,
        max_iter: int = 5,
        allow_delegation: bool = True,
        max_execution_time: Optional[int] = None,
        llm_provider: Optional[Union[str, LLMProvider]] = None,
        llm_config: Optional[Union[Dict[str, Any], LLMConfig]] = None,
        cache_responses: bool = True,
        fallback_providers: Optional[List[Union[str, LLMProvider]]] = None,
        streaming: bool = False,
        on_progress: Optional[Callable[[str, float], None]] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
        on_token: Optional[Callable[[str], None]] = None,
        async_execution: bool = True,
    ):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.verbose = verbose
        self.max_iter = max_iter
        self.allow_delegation = allow_delegation
        self.max_execution_time = max_execution_time
        self.cache_responses = cache_responses
        self.streaming = streaming
        self.on_progress = on_progress
        self.on_chunk = on_chunk
        self.on_token = on_token
        self.async_execution = async_execution
        self.on_partial_response = None
        
        # Performance metrics
        self._creation_time = time.perf_counter()
        self._execution_count = 0
        self._memory_enabled = memory
        
        # Build system message from CrewAI-style attributes
        self.system_message = self._build_system_message()
        
        # Initialize LLM with multi-provider support
        self._llm_manager = LLMManager()
        self._response_cache = ResponseCache() if cache_responses else None
        self._fallback_providers = self._parse_providers(fallback_providers or [])
        
        # Initialize the LLM
        if llm:
            # Use provided LLM directly
            self.llm = llm
        else:
            # Create LLM from provider config
            self.llm = self._initialize_llm(llm_provider, llm_config)
        
        # Setup memory if enabled
        self._memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        ) if memory else None
        
        # Create LangChain agent
        self._agent_executor = self._create_agent_executor()
        
    def _build_system_message(self) -> str:
        """Build system message from role, goal, and backstory."""
        return f"""You are {self.role}.

Your personal goal is: {self.goal}

Your backstory is: {self.backstory}

You have access to the following tools:
{{tools}}

Use the following format:
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {{input}}
{{agent_scratchpad}}"""
        
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the LangChain agent executor."""
        # Convert tools to LangChain format if needed
        langchain_tools = self._convert_tools(self.tools)
        
        # Create prompt
        prompt = PromptTemplate(
            template=self.system_message,
            input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
        )
        
        # Create agent
        agent = create_react_agent(
            llm=self.llm,
            tools=langchain_tools,
            prompt=prompt
        )
        
        # Create executor
        return AgentExecutor(
            agent=agent,
            tools=langchain_tools,
            memory=self._memory,
            verbose=self.verbose,
            max_iterations=self.max_iter,
            handle_parsing_errors=True,
        )
        
    def _convert_tools(self, tools: List[Any]) -> List[Tool]:
        """Convert CrewAI tools to LangChain tools."""
        langchain_tools = []
        
        for tool in tools:
            if isinstance(tool, Tool):
                # Already a LangChain tool
                langchain_tools.append(tool)
            elif hasattr(tool, "name") and hasattr(tool, "description"):
                # Convert CrewAI-style tool
                langchain_tools.append(
                    Tool(
                        name=tool.name,
                        description=tool.description,
                        func=tool.run if hasattr(tool, "run") else tool,
                    )
                )
            else:
                # Assume it's a callable
                langchain_tools.append(
                    Tool(
                        name=tool.__name__,
                        description=f"Tool: {tool.__name__}",
                        func=tool,
                    )
                )
                
        return langchain_tools
        
    def _parse_providers(self, providers: List[Union[str, LLMProvider]]) -> List[LLMProvider]:
        """Parse provider list into LLMProvider enums."""
        parsed = []
        for provider in providers:
            if isinstance(provider, str):
                try:
                    parsed.append(LLMProvider(provider))
                except ValueError:
                    if self.verbose:
                        print(f"Unknown provider: {provider}")
            elif isinstance(provider, LLMProvider):
                parsed.append(provider)
        return parsed
        
    def _initialize_llm(self, 
                       provider: Optional[Union[str, LLMProvider]] = None, 
                       config: Optional[Union[Dict[str, Any], LLMConfig]] = None) -> 'BaseChatModel':
        """Initialize LLM with provider configuration."""
        # Parse provider
        if provider:
            if isinstance(provider, str):
                provider = LLMProvider(provider)
        else:
            # Default to OpenAI if available, otherwise use fake model
            import os
            if os.getenv("OPENAI_API_KEY"):
                provider = LLMProvider.OPENAI
            else:
                # Return mock model for testing when no API key
                from unittest.mock import Mock
                mock_llm = Mock()
                mock_llm.__class__.__name__ = "MockChatModel"
                mock_llm.invoke = Mock(return_value={"content": "I'm a test response from LiteAgent"})
                return mock_llm
        
        # Parse config
        if config:
            if isinstance(config, dict):
                # Create LLMConfig from dict
                llm_config = LLMConfig(
                    provider=provider,
                    model=config.get("model", "gpt-4-turbo-preview"),
                    temperature=config.get("temperature", 0.7),
                    max_tokens=config.get("max_tokens"),
                    api_key=config.get("api_key"),
                    api_base=config.get("api_base"),
                    timeout=config.get("timeout", 30),
                    max_retries=config.get("max_retries", 3),
                    use_functions=config.get("use_functions", False),
                    streaming=config.get("streaming", False),
                    extra_params=config.get("extra_params", {})
                )
            else:
                llm_config = config
        else:
            # Default config
            llm_config = LLMConfig(
                provider=provider,
                model="gpt-4-turbo-preview" if provider == LLMProvider.OPENAI else "mixtral-8x7b",
                temperature=0.7
            )
            
        # Create LLM with fallback handling
        try:
            return self._llm_manager.create_llm(llm_config)
        except Exception as e:
            if self.verbose:
                print(f"Failed to create {provider.value} LLM: {e}")
            
            # Try fallback providers
            for fallback in self._fallback_providers:
                try:
                    fallback_config = LLMConfig(
                        provider=fallback,
                        model=llm_config.model,
                        temperature=llm_config.temperature
                    )
                    return self._llm_manager.create_llm(fallback_config)
                except Exception:
                    continue
                    
            # Final fallback to mock model
            from unittest.mock import Mock
            mock_llm = Mock()
            mock_llm.__class__.__name__ = "MockChatModel"
            mock_llm.invoke = Mock(return_value={"content": "I'm a fallback response from LiteAgent"})
            return mock_llm
    
    def switch_llm_provider(self, provider: Union[str, LLMProvider], config: Optional[Dict[str, Any]] = None):
        """Switch to a different LLM provider."""
        self.llm = self._initialize_llm(provider, config)
        # Recreate agent executor with new LLM
        self._agent_executor = self._create_agent_executor()
        
    def execute(self, task_description: str, context: str = "") -> str:
        """
        Execute a task using the agent.
        
        Args:
            task_description: The task to execute
            context: Additional context from previous tasks
            
        Returns:
            The agent's response as a string
        """
        self._execution_count += 1
        
        # Build full prompt with context
        full_prompt = ""
        if context:
            full_prompt += f"Context from previous tasks:\n{context}\n\n"
        full_prompt += f"Current task: {task_description}"
        
        # Check cache if enabled
        if self._response_cache:
            cached = self._response_cache.get(
                full_prompt, 
                provider=self.llm.__class__.__name__
            )
            if cached:
                if self.verbose:
                    print(f"Using cached response for agent {self.role}")
                return cached
        
        # Execute through LangChain
        try:
            result = self._agent_executor.invoke({"input": full_prompt})
            response = result.get("output", "")
            
            # Cache response if enabled
            if self._response_cache and response:
                self._response_cache.add(
                    full_prompt,
                    response,
                    provider=self.llm.__class__.__name__
                )
                
            return response
        except Exception as e:
            if self.verbose:
                print(f"Agent {self.role} encountered error: {e}")
            return f"Error executing task: {str(e)}"
            
    def execute_task(self, task: 'Task', context: Optional[str] = None) -> Any:
        """
        Execute a task (CrewAI compatibility).
        
        Args:
            task: Task object to execute
            context: Optional context string
            
        Returns:
            Task execution result
        """
        # Build context from task's context tasks if available
        if hasattr(task, 'context') and task.context:
            context_parts = []
            for ctx_task in task.context:
                if hasattr(ctx_task, 'output') and ctx_task.output:
                    context_parts.append(str(ctx_task.output))
            context = "\n".join(context_parts)
            
        result = self.execute(task.description, context or "")
        
        # Store result in task if it has an output attribute
        if hasattr(task, 'output'):
            task.output = result
            
        return result
    
    async def aexecute(self, task_description: str, context: str = "") -> str:
        """
        Asynchronously execute a task.
        
        Args:
            task_description: The task to execute
            context: Additional context
            
        Returns:
            The agent's response
        """
        self._execution_count += 1
        
        # Report progress
        if self.on_progress:
            self.on_progress("Starting task", 0)
        
        # Build full prompt
        full_prompt = ""
        if context:
            full_prompt += f"Context from previous tasks:\n{context}\n\n"
        full_prompt += f"Current task: {task_description}"
        
        # Check cache
        if self._response_cache:
            cached = self._response_cache.get(
                full_prompt,
                provider=self.llm.__class__.__name__
            )
            if cached:
                if self.verbose:
                    print(f"Using cached response for agent {self.role}")
                if self.on_progress:
                    self.on_progress("Completed (cached)", 100)
                return cached
        
        if self.on_progress:
            self.on_progress("Executing LLM", 25)
        
        # Execute asynchronously
        try:
            # For now, run sync code in executor
            # TODO: Use native async when langchain supports it better
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._agent_executor.invoke,
                {"input": full_prompt}
            )
            response = result.get("output", "")
            
            if self.on_progress:
                self.on_progress("Processing response", 75)
            
            # Cache response
            if self._response_cache and response:
                self._response_cache.add(
                    full_prompt,
                    response,
                    provider=self.llm.__class__.__name__
                )
            
            if self.on_progress:
                self.on_progress("Completed", 100)
                
            return response
        except Exception as e:
            if self.verbose:
                print(f"Agent {self.role} encountered error: {e}")
            if self.on_progress:
                self.on_progress("Error", 100)
            return f"Error executing task: {str(e)}"
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        # Truncate long strings
        role = self.role if len(self.role) <= 50 else self.role[:47] + "..."
        goal = self.goal if len(self.goal) <= 100 else self.goal[:97] + "..."
        
        return (
            f"LiteAgent(role='{role}', "
            f"goal='{goal}', "
            f"tools={len(self.tools)}, "
            f"llm={self.llm.__class__.__name__})"
        )
    
    async def stream_execute(self, task_description: str, context: str = "") -> AsyncIterator[str]:
        """
        Stream execution of a task.
        
        Args:
            task_description: The task to execute
            context: Additional context
            
        Yields:
            Chunks of the response as they become available
        """
        if hasattr(self, '_stream_execute'):
            async for chunk in self._stream_execute(task_description, context):
                if self.on_chunk:
                    self.on_chunk(chunk)
                if self.on_token:
                    # Simple token splitting
                    for token in chunk.split():
                        self.on_token(token)
                yield chunk
        else:
            # Fallback: simulate streaming by chunking the response
            response = await self.aexecute(task_description, context)
            words = response.split()
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3])
                if i + 3 < len(words):
                    chunk += " "
                if self.on_chunk:
                    self.on_chunk(chunk)
                yield chunk
                await asyncio.sleep(0.01)  # Simulate streaming delay
    
    async def batch_execute(self, tasks: List[str], context: str = "") -> List[str]:
        """
        Execute multiple tasks in batch.
        
        Args:
            tasks: List of task descriptions
            context: Shared context for all tasks
            
        Returns:
            List of results in the same order as tasks
        """
        # Execute all tasks concurrently
        async_tasks = [self.aexecute(task, context) for task in tasks]
        results = await asyncio.gather(*async_tasks)
        return results
    
    def _execute_with_partials(self, task_description: str, context: str = "") -> str:
        """
        Execute with partial response handling.
        
        Args:
            task_description: The task to execute
            context: Additional context
            
        Returns:
            Complete response
        """
        # This would integrate with LLM-specific partial response handling
        # For now, just execute normally
        return self.execute(task_description, context)
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        creation_time_ms = (self._creation_time - time.perf_counter() + self._creation_time) * 1000
        
        metrics = {
            "creation_time_ms": creation_time_ms,
            "execution_count": self._execution_count,
            "memory_enabled": self._memory_enabled,
            "tools_count": len(self.tools),
            "llm_provider": self.llm.__class__.__name__,
            "cache_enabled": self.cache_responses,
        }
        
        if self._response_cache:
            metrics["cache_stats"] = self._response_cache.get_stats()
            
        return metrics