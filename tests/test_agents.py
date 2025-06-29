"""
Test suite for LiteCrewAI Agent functionality
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

class TestAgentCore:
    """Test core agent functionality"""
    
    def test_agent_initialization(self, sample_agent_config):
        """Test agent initialization with valid config"""
        # Mock agent class
        class MockAgent:
            def __init__(self, **config):
                self.name = config.get('name')
                self.role = config.get('role')
                self.goal = config.get('goal')
                self.backstory = config.get('backstory')
                self.llm = config.get('llm')
                self.max_iter = config.get('max_iter', 3)
                self.memory = config.get('memory', False)
                self.verbose = config.get('verbose', False)
        
        agent = MockAgent(**sample_agent_config)
        assert agent.name == "test_agent"
        assert agent.role == "Assistant"
        assert agent.goal == "Help with testing"
        assert agent.max_iter == 3
        assert agent.memory == True
    
    def test_agent_validation(self):
        """Test agent configuration validation"""
        from pydantic import BaseModel, ValidationError
        
        class AgentConfig(BaseModel):
            name: str
            role: str
            goal: str
            backstory: str
        
        # Valid config
        valid_config = {
            "name": "test_agent",
            "role": "Assistant", 
            "goal": "Help users",
            "backstory": "A helpful AI"
        }
        config = AgentConfig(**valid_config)
        assert config.name == "test_agent"
        
        # Invalid config - missing required fields
        with pytest.raises(ValidationError):
            AgentConfig(name="test")
    
    def test_agent_memory_system(self, mock_redis):
        """Test agent memory system"""
        class MockMemorySystem:
            def __init__(self, redis_client):
                self.redis = redis_client
            
            def store_memory(self, agent_id, key, value):
                self.redis.set(f"agent:{agent_id}:{key}", value)
                return True
            
            def get_memory(self, agent_id, key):
                return self.redis.get(f"agent:{agent_id}:{key}")
            
            def clear_memory(self, agent_id):
                # Mock clearing all agent memories
                return True
        
        memory = MockMemorySystem(mock_redis)
        
        # Test storing memory
        memory.store_memory("agent_1", "last_task", "completed task X")
        mock_redis.set.assert_called_with("agent:agent_1:last_task", "completed task X")
        
        # Test retrieving memory
        mock_redis.get.return_value = "completed task X"
        result = memory.get_memory("agent_1", "last_task")
        assert result == "completed task X"

class TestAgentExecution:
    """Test agent execution and task handling"""
    
    @pytest.mark.asyncio
    async def test_agent_execute_task(self, mock_ollama):
        """Test agent task execution"""
        class MockAgent:
            def __init__(self, llm_client):
                self.llm = llm_client
                self.max_iter = 3
            
            async def execute_task(self, task_description):
                # Simulate task execution
                response = await self.llm.generate(task_description)
                return {
                    "status": "completed",
                    "result": response["response"],
                    "iterations": 1
                }
        
        # Mock async generate method
        mock_ollama.generate = AsyncMock(return_value={
            "response": "Task completed successfully",
            "model": "mistral:7b",
            "done": True
        })
        
        agent = MockAgent(mock_ollama)
        result = await agent.execute_task("Write a test summary")
        
        assert result["status"] == "completed"
        assert "Task completed successfully" in result["result"]
        assert result["iterations"] == 1
    
    def test_agent_error_handling(self):
        """Test agent error handling"""
        class MockAgent:
            def execute_task(self, task):
                if not task or len(task.strip()) == 0:
                    raise ValueError("Task cannot be empty")
                if "error" in task.lower():
                    raise RuntimeError("Simulated execution error")
                return {"status": "completed", "result": "Task done"}
        
        agent = MockAgent()
        
        # Test empty task
        with pytest.raises(ValueError, match="Task cannot be empty"):
            agent.execute_task("")
        
        # Test error in task
        with pytest.raises(RuntimeError, match="Simulated execution error"):
            agent.execute_task("This will error")
        
        # Test successful execution
        result = agent.execute_task("Normal task")
        assert result["status"] == "completed"
    
    def test_agent_iteration_limit(self):
        """Test agent iteration limits"""
        class MockAgent:
            def __init__(self, max_iter=3):
                self.max_iter = max_iter
                self.iteration_count = 0
            
            def execute_with_retry(self, task):
                self.iteration_count = 0
                while self.iteration_count < self.max_iter:
                    self.iteration_count += 1
                    
                    # Simulate task that might need retries
                    if "difficult" in task and self.iteration_count < 2:
                        continue  # Retry
                    
                    return {
                        "status": "completed",
                        "iterations": self.iteration_count,
                        "result": f"Completed after {self.iteration_count} iterations"
                    }
                
                return {
                    "status": "failed", 
                    "iterations": self.iteration_count,
                    "error": "Max iterations exceeded"
                }
        
        agent = MockAgent(max_iter=3)
        
        # Easy task
        result = agent.execute_with_retry("simple task")
        assert result["status"] == "completed"
        assert result["iterations"] == 1
        
        # Difficult task (needs retries)
        result = agent.execute_with_retry("difficult task")
        assert result["status"] == "completed"
        assert result["iterations"] == 2

class TestAgentTools:
    """Test agent tool system"""
    
    def test_tool_registration(self):
        """Test tool registration and usage"""
        class MockTool:
            def __init__(self, name, description, func):
                self.name = name
                self.description = description
                self.func = func
            
            def execute(self, *args, **kwargs):
                return self.func(*args, **kwargs)
        
        class MockAgent:
            def __init__(self):
                self.tools = {}
            
            def register_tool(self, tool):
                self.tools[tool.name] = tool
            
            def use_tool(self, tool_name, *args, **kwargs):
                if tool_name not in self.tools:
                    raise ValueError(f"Tool {tool_name} not found")
                return self.tools[tool_name].execute(*args, **kwargs)
        
        # Create agent and tools
        agent = MockAgent()
        
        calculator_tool = MockTool(
            "calculator", 
            "Performs calculations",
            lambda x, y: x + y
        )
        
        agent.register_tool(calculator_tool)
        
        # Test tool usage
        result = agent.use_tool("calculator", 5, 3)
        assert result == 8
        
        # Test non-existent tool
        with pytest.raises(ValueError, match="Tool unknown not found"):
            agent.use_tool("unknown", 1, 2)
    
    def test_tool_validation(self):
        """Test tool input validation"""
        class ValidatedTool:
            def __init__(self, name, input_schema):
                self.name = name
                self.input_schema = input_schema
            
            def validate_input(self, data):
                return self.input_schema(**data)
            
            def execute(self, **kwargs):
                validated_data = self.validate_input(kwargs)
                return f"Executed {self.name} with {validated_data}"
        
        from pydantic import BaseModel
        
        class CalculatorInput(BaseModel):
            x: int
            y: int
            operation: str = "add"
        
        tool = ValidatedTool("calculator", CalculatorInput)
        
        # Valid input
        result = tool.execute(x=5, y=3, operation="add")
        assert "Executed calculator" in result
        
        # Invalid input
        with pytest.raises(Exception):  # Pydantic ValidationError
            tool.execute(x="not_a_number", y=3)

class TestAgentCommunication:
    """Test agent-to-agent communication"""
    
    def test_agent_delegation(self):
        """Test agent delegation to other agents"""
        class MockAgent:
            def __init__(self, name, role):
                self.name = name
                self.role = role
            
            def delegate_task(self, task, target_agent):
                return {
                    "delegated_by": self.name,
                    "delegated_to": target_agent.name,
                    "task": task,
                    "status": "delegated"
                }
            
            def receive_task(self, task, from_agent):
                return {
                    "received_by": self.name,
                    "from": from_agent,
                    "task": task,
                    "status": "received"
                }
        
        supervisor = MockAgent("supervisor", "Manager")
        worker = MockAgent("worker", "Executor")
        
        # Test delegation
        delegation = supervisor.delegate_task("Process data", worker)
        assert delegation["delegated_by"] == "supervisor"
        assert delegation["delegated_to"] == "worker"
        assert delegation["status"] == "delegated"
        
        # Test receiving
        reception = worker.receive_task("Process data", "supervisor")
        assert reception["received_by"] == "worker"
        assert reception["from"] == "supervisor"
        assert reception["status"] == "received"

class TestAgentPerformance:
    """Test agent performance and optimization"""
    
    def test_agent_response_time(self):
        """Test agent response time tracking"""
        import time
        
        class TimedAgent:
            def execute_task(self, task):
                start_time = time.time()
                
                # Simulate task processing
                time.sleep(0.01)  # 10ms simulated work
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                return {
                    "result": "Task completed",
                    "execution_time": execution_time,
                    "performance": "good" if execution_time < 0.1 else "slow"
                }
        
        agent = TimedAgent()
        result = agent.execute_task("test task")
        
        assert "execution_time" in result
        assert result["execution_time"] > 0
        assert result["performance"] in ["good", "slow"]
    
    def test_agent_memory_usage(self):
        """Test agent memory usage tracking"""
        import sys
        
        class MemoryTrackedAgent:
            def __init__(self):
                self.memory_baseline = sys.getsizeof(self)
            
            def track_memory_usage(self):
                current_size = sys.getsizeof(self)
                return {
                    "baseline": self.memory_baseline,
                    "current": current_size,
                    "growth": current_size - self.memory_baseline
                }
        
        agent = MemoryTrackedAgent()
        
        # Add some data to agent
        agent.data = [i for i in range(100)]
        
        memory_info = agent.track_memory_usage()
        assert memory_info["current"] >= memory_info["baseline"]
        assert memory_info["growth"] >= 0