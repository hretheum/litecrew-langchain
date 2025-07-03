# LiteCrew Implementation Plan: LangChain + CrewAI Features

## Executive Summary

Based on benchmark results showing LangChain's 408x faster startup and 91% less memory overhead compared to CrewAI, we recommend building a lightweight layer on top of LangChain that implements CrewAI's best features without its performance penalties.

## Why This Approach?

### Benchmark Results:
- **LangChain**: 0.008s import, 17MB memory ✅
- **CrewAI**: 3.268s import, 208MB memory ❌
- **LiteCrew Fork**: Failed, increased size to 10.7MB ❌

### Key Insight:
Instead of forking CrewAI (which failed), we'll build a minimal wrapper around LangChain that provides CrewAI's multi-agent orchestration features.

## Implementation Plan

### Phase 1: Core Foundation (Week 1)

#### 1.1 Project Setup
```bash
# New structure
litecrew-langchain/
├── litecrew/
│   ├── __init__.py
│   ├── agent.py       # LiteAgent wrapper
│   ├── crew.py        # LiteCrew orchestrator
│   ├── task.py        # LiteTask with dependencies
│   └── process.py     # Sequential/Hierarchical execution
├── tests/
├── benchmarks/
└── pyproject.toml
```

#### 1.2 LiteAgent Implementation
```python
# litecrew/agent.py
from langchain.agents import create_react_agent
from langchain.memory import ConversationBufferMemory
from typing import List, Optional, Any

class LiteAgent:
    """CrewAI-compatible agent on LangChain foundation"""
    
    def __init__(
        self,
        role: str,
        goal: str, 
        backstory: str,
        tools: List[Any] = None,
        llm: Optional[Any] = None,
        memory: bool = True,
        verbose: bool = False,
        max_iter: int = 5
    ):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        
        # Build system prompt from CrewAI-style attributes
        self.system_prompt = f"""You are {role}.
Your goal: {goal}
Background: {backstory}"""
        
        # Create LangChain agent
        self._memory = ConversationBufferMemory() if memory else None
        self._agent = self._build_langchain_agent(llm)
        
    def execute(self, task_description: str, context: str = "") -> str:
        """Execute task using LangChain agent"""
        prompt = f"{context}\n\nTask: {task_description}"
        return self._agent.invoke({"input": prompt})
```

### Phase 2: Multi-Agent Orchestration (Week 2)

#### 2.1 Task System
```python
# litecrew/task.py
from typing import Optional, List, Any
from pydantic import BaseModel

class LiteTask(BaseModel):
    description: str
    agent: Optional['LiteAgent'] = None
    context: Optional[List['LiteTask']] = None
    expected_output: str = ""
    tools: List[Any] = []
    
    def execute(self, crew_context: dict = None) -> 'TaskOutput':
        """Execute task with context from previous tasks"""
        context_str = self._build_context()
        result = self.agent.execute(self.description, context_str)
        return TaskOutput(raw=result, task=self)
```

#### 2.2 Crew Orchestration
```python
# litecrew/crew.py
from typing import List, Dict, Any
import asyncio

class LiteCrew:
    """Lightweight multi-agent orchestration"""
    
    def __init__(
        self,
        agents: List[LiteAgent],
        tasks: List[LiteTask],
        process: str = "sequential",  # or "hierarchical"
        manager_agent: Optional[LiteAgent] = None
    ):
        self.agents = agents
        self.tasks = tasks
        self.process = process
        self.manager = manager_agent
        
    def kickoff(self, inputs: Dict = None) -> 'CrewOutput':
        """Execute crew tasks with minimal overhead"""
        if self.process == "sequential":
            return self._run_sequential(inputs)
        elif self.process == "hierarchical":
            return self._run_hierarchical(inputs)
            
    def _run_sequential(self, inputs: Dict) -> 'CrewOutput':
        """Run tasks one by one, passing context"""
        outputs = []
        for task in self.tasks:
            # Add previous outputs as context
            task.context = outputs[-3:] if outputs else []
            output = task.execute(inputs)
            outputs.append(output)
        return CrewOutput(raw=outputs[-1].raw, tasks_output=outputs)
```

### Phase 3: Advanced Features (Week 3)

#### 3.1 Agent Delegation
```python
# litecrew/tools/delegation.py
from langchain.tools import Tool

class DelegationTool(Tool):
    """Allow agents to delegate to each other"""
    
    def __init__(self, agents: List[LiteAgent]):
        self.agents = {a.role: a for a in agents}
        super().__init__(
            name="delegate_task",
            description="Delegate a task to another agent",
            func=self._delegate
        )
        
    def _delegate(self, query: str) -> str:
        # Parse: "Ask the Researcher to find information about X"
        role, task = self._parse_delegation(query)
        if role in self.agents:
            return self.agents[role].execute(task)
        return "Agent not found"
```

#### 3.2 Hierarchical Process
```python
# litecrew/process.py
class HierarchicalProcess:
    """Manager agent coordinates other agents"""
    
    def __init__(self, manager: LiteAgent, agents: List[LiteAgent]):
        self.manager = manager
        self.agents = agents
        
    def execute(self, tasks: List[LiteTask]) -> List[TaskOutput]:
        """Manager decides task assignment"""
        plan = self.manager.execute(
            f"Plan how to execute these tasks: {tasks}"
        )
        
        # Parse plan and assign tasks
        assignments = self._parse_assignments(plan)
        results = []
        
        for task, agent_role in assignments:
            agent = self._get_agent(agent_role)
            result = agent.execute(task.description)
            results.append(result)
            
        return results
```

### Phase 4: Performance Optimization (Week 4)

#### 4.1 Lazy Loading
```python
# Only import what's needed
def create_agent(*args, **kwargs):
    """Lazy load agent creation"""
    from langchain.agents import create_react_agent
    return LiteAgent(*args, **kwargs)
```

#### 4.2 Memory Management
```python
# Automatic cleanup after task execution
class LiteAgent:
    def __del__(self):
        """Clean up memory on deletion"""
        if hasattr(self, '_memory'):
            self._memory.clear()
```

### Phase 5: Testing & Benchmarking (Week 5)

#### 5.1 Performance Tests
```python
# benchmarks/test_performance.py
def test_import_time():
    start = time.perf_counter()
    import litecrew
    duration = time.perf_counter() - start
    assert duration < 0.1  # Target: <100ms
    
def test_memory_usage():
    before = psutil.Process().memory_info().rss
    crew = LiteCrew(agents=[...], tasks=[...])
    crew.kickoff()
    after = psutil.Process().memory_info().rss
    assert (after - before) / 1024 / 1024 < 30  # <30MB overhead
```

#### 5.2 Feature Parity Tests
```python
# Test CrewAI-compatible API
def test_crewai_compatibility():
    # Should work with CrewAI-style code
    agent = LiteAgent(
        role="Researcher",
        goal="Find information",
        backstory="Expert researcher"
    )
    crew = LiteCrew(
        agents=[agent],
        tasks=[LiteTask(description="Research AI frameworks")]
    )
    result = crew.kickoff()
    assert result.raw is not None
```

## Migration Guide

### From CrewAI to LiteCrew:
```python
# Before (CrewAI) - 208MB memory
from crewai import Agent, Crew, Task

agent = Agent(
    role="Researcher",
    goal="Research topics",
    backstory="Expert researcher"
)

# After (LiteCrew) - 17MB memory  
from litecrew import LiteAgent, LiteCrew, LiteTask

agent = LiteAgent(
    role="Researcher",
    goal="Research topics", 
    backstory="Expert researcher"
)
# Same API, 91% less memory!
```

## Success Metrics

1. **Performance**:
   - Import time: <0.05s (vs CrewAI's 3.3s)
   - Memory usage: <30MB (vs CrewAI's 208MB)
   - Startup time: <100ms

2. **Features**:
   - ✅ Multi-agent orchestration
   - ✅ Task dependencies
   - ✅ Sequential/Hierarchical execution
   - ✅ Agent delegation
   - ✅ CrewAI-compatible API

3. **Code Quality**:
   - 100% type hints
   - >80% test coverage
   - Zero dependencies beyond LangChain

## Timeline

- **Week 1**: Core foundation (Agent, Task, Crew)
- **Week 2**: Multi-agent orchestration
- **Week 3**: Advanced features (delegation, hierarchical)
- **Week 4**: Performance optimization
- **Week 5**: Testing, benchmarking, documentation

## Conclusion

By building on LangChain's efficient foundation and adding only the essential CrewAI features, we can achieve:
- **10x better performance** than CrewAI
- **Same developer experience** with compatible API
- **Production-ready** from day one

No more failed forks. Just clean, efficient code that works.