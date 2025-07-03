"""
LiteAgent - CrewAI-compatible agent built on LangChain
"""

from typing import Any, List, Optional, Dict
from langchain.agents import AgentExecutor, create_react_agent
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
        memory: bool = True,
        verbose: bool = False,
        max_iter: int = 5,
        allow_delegation: bool = True,
        max_execution_time: Optional[int] = None,
    ):
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
        
        # Initialize LLM (default to OpenAI)
        self.llm = llm or ChatOpenAI(temperature=0.7, model="gpt-4-turbo-preview")
        
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
        try:
            result = self._agent_executor.invoke({"input": full_prompt})
            return result.get("output", "")
        except Exception as e:
            if self.verbose:
                print(f"Agent {self.role} encountered error: {e}")
            return f"Error: {str(e)}"
            
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