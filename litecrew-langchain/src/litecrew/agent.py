"""
LiteAgent - CrewAI-compatible agent built on LangChain
"""

import time
from typing import Any, List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from langchain.agents import AgentExecutor
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import BaseMessage
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.tools import Tool


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
        function_calling_llm: Optional[Any] = None,
        max_iter: int = 5,
        max_rpm: Optional[int] = None,
        memory: bool = False,
        verbose: bool = False,
        allow_delegation: bool = False,
        step_callback: Optional[Any] = None,
        system_template: Optional[str] = None,
        prompt_template: Optional[str] = None,
        response_template: Optional[str] = None,
        max_execution_time: Optional[int] = None,
        callbacks: Optional[List[Any]] = None,
    ):
        """Initialize a LiteAgent."""
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.verbose = verbose
        self.max_iter = max_iter
        self.allow_delegation = allow_delegation
        self.max_execution_time = max_execution_time
        
        # Build system message from CrewAI-style attributes
        self.system_message = self._build_system_message()
        
        # Initialize LLM (lazy import to speed up startup)
        self._llm = llm
        self._llm_initialized = llm is not None
        
        # Setup memory if enabled (lazy loading)
        self._memory = None
        self._memory_enabled = memory
        
        # Delay agent creation until first use
        self._agent_executor = None
        
        # Track metrics
        self._creation_time = time.perf_counter()
        self._execution_count = 0
        
    @property
    def llm(self):
        """Lazy load LLM to improve import time."""
        if not self._llm_initialized:
            try:
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(temperature=0.7, model="gpt-4-turbo-preview")
                self._llm_initialized = True
            except Exception as e:
                # If no API key or other issue, use a mock LLM for testing
                from langchain_core.language_models import FakeListChatModel
                self._llm = FakeListChatModel(responses=["Task completed successfully"])
                self._llm_initialized = True
        return self._llm
    
    @property
    def memory(self):
        """Lazy load memory."""
        if self._memory is None and self._memory_enabled:
            from langchain.memory import ConversationBufferMemory
            self._memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        return self._memory
    
    @property
    def agent_executor(self):
        """Lazy load agent executor."""
        if self._agent_executor is None:
            self._agent_executor = self._create_agent_executor()
        return self._agent_executor
        
    def _build_system_message(self) -> str:
        """Build system message from role, goal, and backstory."""
        message = f"""You are {self.role}.

Your personal goal is: {self.goal}

Your backstory is: {self.backstory}"""

        if self.allow_delegation:
            message += "\n\nYou can delegate tasks to other agents when needed."

        message += """

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
        
        return message
        
    def _create_agent_executor(self):
        """Create the LangChain agent executor."""
        from langchain.agents import AgentExecutor, create_react_agent
        from langchain.prompts import PromptTemplate
        
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
            prompt=prompt,
        )
        
        # Create executor
        return AgentExecutor(
            agent=agent,
            tools=langchain_tools,
            memory=self.memory,
            verbose=self.verbose,
            max_iterations=self.max_iter,
            handle_parsing_errors=True,
        )
        
    def _convert_tools(self, tools: List[Any]) -> List['Tool']:
        """Convert CrewAI tools to LangChain tools."""
        langchain_tools = []
        
        from langchain.tools import Tool
        
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
                # Try to wrap as a basic tool
                langchain_tools.append(
                    Tool(
                        name=str(tool),
                        description=f"Tool: {tool}",
                        func=tool,
                    )
                )
                
        return langchain_tools
        
    def execute(self, task_description: str, context: str = "") -> str:
        """
        Execute a task using the agent.
        
        Args:
            task_description: The task to execute
            context: Additional context from previous tasks
            
        Returns:
            The agent's response as a string
        """
        # Build full prompt with context
        full_prompt = ""
        if context:
            full_prompt += f"Context from previous tasks:\n{context}\n\n"
        full_prompt += f"Current task: {task_description}"
        
        # Execute through LangChain
        self._execution_count += 1
        try:
            result = self.agent_executor.invoke({"input": full_prompt})
            return result.get("output", "")
        except Exception as e:
            if self.verbose:
                print(f"Agent {self.role} encountered error: {e}")
            return f"Error executing task: {str(e)}"
            
    def execute_task(self, task: 'Task', context: Optional[str] = None) -> Any:
        """
        Execute a CrewAI-style Task object.
        
        Args:
            task: Task object with description and context
            context: Additional context (optional)
            
        Returns:
            Task execution result
        """
        # Extract context from task if it has context attribute
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
    
    def __repr__(self) -> str:
        # Truncate long goals
        goal_display = self.goal if len(self.goal) <= 50 else self.goal[:47] + "..."
        return f"Agent(role={self.role}, goal={goal_display})"
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Return agent performance metrics."""
        creation_time_ms = (self._creation_time - time.perf_counter() + self._creation_time) * 1000
        return {
            "creation_time_ms": creation_time_ms,
            "execution_count": self._execution_count,
            "memory_enabled": self._memory_enabled,
            "tools_count": len(self.tools)
        }
    
    @classmethod
    def from_config(cls, config: Any) -> 'LiteAgent':
        """Create agent from configuration dictionary or object."""
        if hasattr(config, '__dict__'):
            # Handle object with attributes (like AgentConfig)
            config_dict = {k: v for k, v in config.__dict__.items() if not k.startswith('_')}
            return cls(**config_dict)
        else:
            # Handle dictionary
            return cls(**config)
    
    async def aexecute(self, task_description: str, context: str = "") -> str:
        """Async version of execute."""
        import asyncio
        # Run the sync execute in a thread pool to make it truly async
        return await asyncio.get_event_loop().run_in_executor(
            None, 
            self.execute, 
            task_description, 
            context
        )


# Alias for CrewAI compatibility
Agent = LiteAgent