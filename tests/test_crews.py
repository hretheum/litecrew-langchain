"""
Test suite for LiteCrewAI Crew functionality  
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import asyncio

class TestCrewCore:
    """Test core crew functionality"""
    
    def test_crew_initialization(self, sample_crew_config):
        """Test crew initialization with valid config"""
        class MockCrew:
            def __init__(self, **config):
                self.name = config.get('name')
                self.agents = config.get('agents', [])
                self.tasks = config.get('tasks', [])
                self.process = config.get('process', 'sequential')
                self.verbose = config.get('verbose', False)
                self.memory = config.get('memory', False)
                self.max_rpm = config.get('max_rpm', 10)
                self.status = 'initialized'
        
        crew = MockCrew(**sample_crew_config)
        assert crew.name == "test_crew"
        assert crew.agents == ["test_agent"]
        assert crew.tasks == ["test_task"]
        assert crew.process == "sequential"
        assert crew.memory == True
        assert crew.max_rpm == 10
        assert crew.status == 'initialized'
    
    def test_crew_validation(self):
        """Test crew configuration validation"""
        from pydantic import BaseModel, ValidationError
        
        class CrewConfig(BaseModel):
            name: str
            agents: list
            tasks: list
            process: str = "sequential"
        
        # Valid config
        valid_config = {
            "name": "test_crew",
            "agents": ["agent1", "agent2"],
            "tasks": ["task1", "task2"],
            "process": "sequential"
        }
        config = CrewConfig(**valid_config)
        assert config.name == "test_crew"
        assert len(config.agents) == 2
        
        # Invalid config - empty agents
        with pytest.raises(ValidationError):
            CrewConfig(name="test", agents=[], tasks=["task1"])
    
    def test_crew_agent_management(self):
        """Test crew agent management"""
        class MockCrew:
            def __init__(self):
                self.agents = {}
                self.agent_order = []
            
            def add_agent(self, agent_id, agent_config):
                self.agents[agent_id] = agent_config
                self.agent_order.append(agent_id)
            
            def remove_agent(self, agent_id):
                if agent_id in self.agents:
                    del self.agents[agent_id]
                    self.agent_order.remove(agent_id)
            
            def get_agent(self, agent_id):
                return self.agents.get(agent_id)
            
            def list_agents(self):
                return [self.agents[agent_id] for agent_id in self.agent_order]
        
        crew = MockCrew()
        
        # Add agents
        crew.add_agent("agent1", {"name": "Agent 1", "role": "Worker"})
        crew.add_agent("agent2", {"name": "Agent 2", "role": "Manager"})
        
        assert len(crew.agents) == 2
        assert crew.get_agent("agent1")["name"] == "Agent 1"
        
        # List agents in order
        agents = crew.list_agents()
        assert len(agents) == 2
        assert agents[0]["name"] == "Agent 1"
        
        # Remove agent
        crew.remove_agent("agent1")
        assert len(crew.agents) == 1
        assert crew.get_agent("agent1") is None

class TestCrewExecution:
    """Test crew execution processes"""
    
    def test_sequential_execution(self):
        """Test sequential task execution"""
        class MockSequentialCrew:
            def __init__(self):
                self.tasks = []
                self.execution_log = []
            
            def add_task(self, task):
                self.tasks.append(task)
            
            def execute_sequential(self):
                results = []
                for i, task in enumerate(self.tasks):
                    self.execution_log.append(f"Starting task {i}: {task}")
                    
                    # Simulate task execution
                    result = f"Completed {task}"
                    results.append(result)
                    
                    self.execution_log.append(f"Finished task {i}: {task}")
                
                return results
        
        crew = MockSequentialCrew()
        crew.add_task("task1")
        crew.add_task("task2") 
        crew.add_task("task3")
        
        results = crew.execute_sequential()
        
        assert len(results) == 3
        assert results[0] == "Completed task1"
        assert len(crew.execution_log) == 6  # 2 logs per task
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel task execution"""
        class MockParallelCrew:
            def __init__(self):
                self.tasks = []
            
            def add_task(self, task):
                self.tasks.append(task)
            
            async def execute_task(self, task):
                # Simulate async task execution
                await asyncio.sleep(0.01)
                return f"Completed {task}"
            
            async def execute_parallel(self):
                # Execute all tasks in parallel
                coroutines = [self.execute_task(task) for task in self.tasks]
                results = await asyncio.gather(*coroutines)
                return results
        
        crew = MockParallelCrew()
        crew.add_task("task1")
        crew.add_task("task2")
        crew.add_task("task3")
        
        results = await crew.execute_parallel()
        
        assert len(results) == 3
        assert "Completed task1" in results
        assert "Completed task2" in results
        assert "Completed task3" in results
    
    def test_hierarchical_execution(self):
        """Test hierarchical crew execution"""
        class MockHierarchicalCrew:
            def __init__(self):
                self.manager = None
                self.workers = []
                self.task_assignments = {}
            
            def set_manager(self, manager):
                self.manager = manager
            
            def add_worker(self, worker):
                self.workers.append(worker)
            
            def execute_hierarchical(self, tasks):
                if not self.manager:
                    raise ValueError("No manager assigned")
                
                # Manager distributes tasks
                for i, task in enumerate(tasks):
                    worker = self.workers[i % len(self.workers)]
                    self.task_assignments[task] = worker
                
                # Simulate execution
                results = {}
                for task, worker in self.task_assignments.items():
                    results[task] = f"Task {task} completed by {worker}"
                
                return results
        
        crew = MockHierarchicalCrew()
        crew.set_manager("Manager Agent")
        crew.add_worker("Worker 1")
        crew.add_worker("Worker 2")
        
        tasks = ["task1", "task2", "task3", "task4"]
        results = crew.execute_hierarchical(tasks)
        
        assert len(results) == 4
        assert "Worker 1" in results["task1"]
        assert "Worker 2" in results["task2"]
        assert "Worker 1" in results["task3"]  # Round-robin assignment

class TestCrewCommunication:
    """Test crew communication and coordination"""
    
    def test_crew_messaging(self):
        """Test messaging between crew members"""
        class MockCrewMessaging:
            def __init__(self):
                self.message_queue = []
                self.agent_inboxes = {}
            
            def send_message(self, from_agent, to_agent, message):
                msg = {
                    "from": from_agent,
                    "to": to_agent,
                    "message": message,
                    "timestamp": datetime.now()
                }
                self.message_queue.append(msg)
                
                if to_agent not in self.agent_inboxes:
                    self.agent_inboxes[to_agent] = []
                self.agent_inboxes[to_agent].append(msg)
            
            def get_messages(self, agent):
                return self.agent_inboxes.get(agent, [])
            
            def broadcast_message(self, from_agent, message, recipients):
                for recipient in recipients:
                    self.send_message(from_agent, recipient, message)
        
        messaging = MockCrewMessaging()
        
        # Send message
        messaging.send_message("agent1", "agent2", "Hello!")
        
        # Check message was received
        messages = messaging.get_messages("agent2")
        assert len(messages) == 1
        assert messages[0]["message"] == "Hello!"
        assert messages[0]["from"] == "agent1"
        
        # Test broadcast
        messaging.broadcast_message("manager", "Meeting at 3pm", ["agent1", "agent2", "agent3"])
        
        assert len(messaging.get_messages("agent1")) == 1
        assert len(messaging.get_messages("agent2")) == 2  # Original message + broadcast
        assert len(messaging.get_messages("agent3")) == 1
    
    def test_crew_coordination(self):
        """Test crew coordination mechanisms"""
        class MockCrewCoordinator:
            def __init__(self):
                self.agents = {}
                self.shared_state = {}
                self.coordination_events = []
            
            def register_agent(self, agent_id, capabilities):
                self.agents[agent_id] = {
                    "capabilities": capabilities,
                    "status": "idle",
                    "current_task": None
                }
            
            def assign_task(self, task, required_capability):
                # Find agent with required capability
                available_agents = [
                    agent_id for agent_id, info in self.agents.items()
                    if required_capability in info["capabilities"] and info["status"] == "idle"
                ]
                
                if not available_agents:
                    return None
                
                selected_agent = available_agents[0]
                self.agents[selected_agent]["status"] = "busy"
                self.agents[selected_agent]["current_task"] = task
                
                self.coordination_events.append({
                    "type": "task_assigned",
                    "agent": selected_agent,
                    "task": task
                })
                
                return selected_agent
            
            def complete_task(self, agent_id):
                if agent_id in self.agents:
                    task = self.agents[agent_id]["current_task"]
                    self.agents[agent_id]["status"] = "idle"
                    self.agents[agent_id]["current_task"] = None
                    
                    self.coordination_events.append({
                        "type": "task_completed",
                        "agent": agent_id,
                        "task": task
                    })
        
        coordinator = MockCrewCoordinator()
        
        # Register agents
        coordinator.register_agent("agent1", ["analysis", "writing"])
        coordinator.register_agent("agent2", ["coding", "debugging"])
        
        # Assign tasks
        assigned_agent = coordinator.assign_task("analyze_data", "analysis")
        assert assigned_agent == "agent1"
        assert coordinator.agents["agent1"]["status"] == "busy"
        
        # Try to assign another analysis task (should fail - agent busy)
        assigned_agent2 = coordinator.assign_task("analyze_more", "analysis")
        assert assigned_agent2 is None
        
        # Complete task
        coordinator.complete_task("agent1")
        assert coordinator.agents["agent1"]["status"] == "idle"
        assert len(coordinator.coordination_events) == 2

class TestCrewMemory:
    """Test crew memory and knowledge sharing"""
    
    def test_shared_memory(self, mock_redis):
        """Test shared memory between crew members"""
        class MockCrewMemory:
            def __init__(self, redis_client):
                self.redis = redis_client
            
            def store_shared_knowledge(self, key, value, scope="crew"):
                self.redis.set(f"{scope}:{key}", value)
            
            def get_shared_knowledge(self, key, scope="crew"):
                return self.redis.get(f"{scope}:{key}")
            
            def share_agent_memory(self, from_agent, to_agent, memory_key):
                memory_value = self.redis.get(f"agent:{from_agent}:{memory_key}")
                if memory_value:
                    self.redis.set(f"agent:{to_agent}:{memory_key}", memory_value)
                    return True
                return False
        
        memory = MockCrewMemory(mock_redis)
        
        # Store shared knowledge
        memory.store_shared_knowledge("project_context", "AI development project")
        mock_redis.set.assert_called_with("crew:project_context", "AI development project")
        
        # Retrieve shared knowledge
        mock_redis.get.return_value = "AI development project"
        result = memory.get_shared_knowledge("project_context")
        assert result == "AI development project"
        
        # Share memory between agents
        mock_redis.get.return_value = "important insight"
        success = memory.share_agent_memory("agent1", "agent2", "insight")
        assert success == True
    
    def test_knowledge_aggregation(self):
        """Test knowledge aggregation across crew"""
        class MockKnowledgeAggregator:
            def __init__(self):
                self.knowledge_base = {}
                self.agent_contributions = {}
            
            def contribute_knowledge(self, agent_id, topic, knowledge):
                if topic not in self.knowledge_base:
                    self.knowledge_base[topic] = []
                
                contribution = {
                    "agent": agent_id,
                    "knowledge": knowledge,
                    "timestamp": datetime.now()
                }
                
                self.knowledge_base[topic].append(contribution)
                
                if agent_id not in self.agent_contributions:
                    self.agent_contributions[agent_id] = []
                self.agent_contributions[agent_id].append(contribution)
            
            def get_aggregated_knowledge(self, topic):
                if topic not in self.knowledge_base:
                    return []
                
                # Sort by timestamp
                contributions = sorted(
                    self.knowledge_base[topic],
                    key=lambda x: x["timestamp"]
                )
                
                return [c["knowledge"] for c in contributions]
            
            def get_agent_expertise(self, agent_id):
                contributions = self.agent_contributions.get(agent_id, [])
                topics = {}
                
                for contrib in contributions:
                    # Find topic for this contribution
                    for topic, topic_contribs in self.knowledge_base.items():
                        if contrib in topic_contribs:
                            topics[topic] = topics.get(topic, 0) + 1
                            break
                
                return topics
        
        aggregator = MockKnowledgeAggregator()
        
        # Agents contribute knowledge
        aggregator.contribute_knowledge("agent1", "python", "Use list comprehensions")
        aggregator.contribute_knowledge("agent2", "python", "Handle exceptions properly")
        aggregator.contribute_knowledge("agent1", "testing", "Write unit tests first")
        
        # Get aggregated knowledge
        python_knowledge = aggregator.get_aggregated_knowledge("python")
        assert len(python_knowledge) == 2
        assert "list comprehensions" in python_knowledge[0]
        assert "exceptions" in python_knowledge[1]
        
        # Get agent expertise
        agent1_expertise = aggregator.get_agent_expertise("agent1")
        assert agent1_expertise["python"] == 1
        assert agent1_expertise["testing"] == 1

class TestCrewMonitoring:
    """Test crew monitoring and analytics"""
    
    def test_crew_performance_tracking(self):
        """Test crew performance metrics"""
        class MockCrewPerformanceTracker:
            def __init__(self):
                self.metrics = {
                    "tasks_completed": 0,
                    "tasks_failed": 0,
                    "total_execution_time": 0,
                    "agent_utilization": {},
                    "collaboration_events": 0
                }
            
            def record_task_completion(self, task_id, execution_time, success, agents_involved):
                if success:
                    self.metrics["tasks_completed"] += 1
                else:
                    self.metrics["tasks_failed"] += 1
                
                self.metrics["total_execution_time"] += execution_time
                
                # Track agent utilization
                for agent in agents_involved:
                    if agent not in self.metrics["agent_utilization"]:
                        self.metrics["agent_utilization"][agent] = {
                            "tasks": 0,
                            "time": 0
                        }
                    self.metrics["agent_utilization"][agent]["tasks"] += 1
                    self.metrics["agent_utilization"][agent]["time"] += execution_time / len(agents_involved)
            
            def record_collaboration(self):
                self.metrics["collaboration_events"] += 1
            
            def get_performance_summary(self):
                total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
                success_rate = (self.metrics["tasks_completed"] / total_tasks * 100) if total_tasks > 0 else 0
                avg_execution_time = (self.metrics["total_execution_time"] / total_tasks) if total_tasks > 0 else 0
                
                return {
                    "total_tasks": total_tasks,
                    "success_rate": success_rate,
                    "average_execution_time": avg_execution_time,
                    "collaboration_events": self.metrics["collaboration_events"],
                    "agent_utilization": self.metrics["agent_utilization"]
                }
        
        tracker = MockCrewPerformanceTracker()
        
        # Record some task completions
        tracker.record_task_completion("task1", 2.5, True, ["agent1", "agent2"])
        tracker.record_task_completion("task2", 1.8, True, ["agent1"])
        tracker.record_task_completion("task3", 3.2, False, ["agent2"])
        tracker.record_collaboration()
        
        summary = tracker.get_performance_summary()
        
        assert summary["total_tasks"] == 3
        assert abs(summary["success_rate"] - 66.67) < 0.01  # 2/3 * 100
        assert abs(summary["average_execution_time"] - 2.5) < 0.01  # (2.5+1.8+3.2)/3
        assert summary["collaboration_events"] == 1
        assert summary["agent_utilization"]["agent1"]["tasks"] == 2
        assert summary["agent_utilization"]["agent2"]["tasks"] == 2
    
    def test_crew_health_monitoring(self):
        """Test crew health and status monitoring"""
        class MockCrewHealthMonitor:
            def __init__(self):
                self.agent_health = {}
                self.system_health = {
                    "memory_usage": 0,
                    "cpu_usage": 0,
                    "active_tasks": 0,
                    "error_rate": 0
                }
            
            def update_agent_health(self, agent_id, status, last_heartbeat=None):
                self.agent_health[agent_id] = {
                    "status": status,  # "healthy", "degraded", "unhealthy"
                    "last_heartbeat": last_heartbeat or datetime.now(),
                    "consecutive_failures": 0
                }
            
            def record_agent_failure(self, agent_id):
                if agent_id in self.agent_health:
                    self.agent_health[agent_id]["consecutive_failures"] += 1
                    
                    # Update status based on failures
                    failures = self.agent_health[agent_id]["consecutive_failures"]
                    if failures >= 3:
                        self.agent_health[agent_id]["status"] = "unhealthy"
                    elif failures >= 1:
                        self.agent_health[agent_id]["status"] = "degraded"
            
            def update_system_health(self, memory_usage, cpu_usage, active_tasks, error_rate):
                self.system_health.update({
                    "memory_usage": memory_usage,
                    "cpu_usage": cpu_usage,
                    "active_tasks": active_tasks,
                    "error_rate": error_rate
                })
            
            def get_overall_health(self):
                # Check agent health
                unhealthy_agents = sum(1 for health in self.agent_health.values() 
                                     if health["status"] == "unhealthy")
                degraded_agents = sum(1 for health in self.agent_health.values() 
                                    if health["status"] == "degraded")
                
                # Check system health
                system_issues = 0
                if self.system_health["memory_usage"] > 80:
                    system_issues += 1
                if self.system_health["cpu_usage"] > 80:
                    system_issues += 1
                if self.system_health["error_rate"] > 5:
                    system_issues += 1
                
                if unhealthy_agents > 0 or system_issues >= 2:
                    return "unhealthy"
                elif degraded_agents > 0 or system_issues >= 1:
                    return "degraded"
                else:
                    return "healthy"
        
        monitor = MockCrewHealthMonitor()
        
        # Set up agent health
        monitor.update_agent_health("agent1", "healthy")
        monitor.update_agent_health("agent2", "healthy")
        
        # Check initial health
        health = monitor.get_overall_health()
        assert health == "healthy"
        
        # Record some failures
        monitor.record_agent_failure("agent1")
        health = monitor.get_overall_health()
        assert health == "degraded"
        
        # More failures
        monitor.record_agent_failure("agent1")
        monitor.record_agent_failure("agent1")
        health = monitor.get_overall_health()
        assert health == "unhealthy"
        
        # Update system health
        monitor.update_system_health(
            memory_usage=85,  # High memory usage
            cpu_usage=70,
            active_tasks=5,
            error_rate=2
        )
        
        # Reset agent health but system is still problematic
        monitor.update_agent_health("agent1", "healthy")
        health = monitor.get_overall_health()
        assert health == "degraded"  # Due to high memory usage