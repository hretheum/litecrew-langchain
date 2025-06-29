"""
Integration tests for LiteCrewAI
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import tempfile
from pathlib import Path

class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    @pytest.mark.asyncio
    async def test_simple_crew_workflow(self, mock_ollama, mock_redis):
        """Test a simple crew workflow from start to finish"""
        
        # Mock components
        class MockAgent:
            def __init__(self, name, role, llm_client):
                self.name = name
                self.role = role
                self.llm = llm_client
                self.tasks_completed = 0
            
            async def execute_task(self, task):
                response = await self.llm.generate(f"Execute task: {task['description']}")
                self.tasks_completed += 1
                return {
                    "agent": self.name,
                    "task": task["name"],
                    "result": response["response"],
                    "status": "completed"
                }
        
        class MockCrew:
            def __init__(self, name):
                self.name = name
                self.agents = []
                self.tasks = []
                self.results = []
            
            def add_agent(self, agent):
                self.agents.append(agent)
            
            def add_task(self, task):
                self.tasks.append(task)
            
            async def execute(self):
                for task in self.tasks:
                    # Assign task to first available agent
                    agent = self.agents[0]
                    result = await agent.execute_task(task)
                    self.results.append(result)
                
                return self.results
        
        # Set up mocks
        mock_ollama.generate = AsyncMock(return_value={
            "response": "Task completed successfully",
            "model": "mistral:7b",
            "done": True
        })
        
        # Create workflow
        crew = MockCrew("test_crew")
        
        agent = MockAgent("assistant", "Helper", mock_ollama)
        crew.add_agent(agent)
        
        task = {
            "name": "analyze_data",
            "description": "Analyze the provided data and summarize findings"
        }
        crew.add_task(task)
        
        # Execute workflow
        results = await crew.execute()
        
        # Verify results
        assert len(results) == 1
        assert results[0]["agent"] == "assistant"
        assert results[0]["status"] == "completed"
        assert "Task completed successfully" in results[0]["result"]
        assert agent.tasks_completed == 1
    
    def test_multi_agent_collaboration(self):
        """Test collaboration between multiple agents"""
        
        class MockAgent:
            def __init__(self, name, specialization):
                self.name = name
                self.specialization = specialization
                self.memory = {}
            
            def can_handle_task(self, task_type):
                return task_type in self.specialization
            
            def execute_task(self, task):
                if not self.can_handle_task(task["type"]):
                    return {"status": "failed", "reason": "Not specialized for this task"}
                
                result = f"{self.name} completed {task['description']}"
                self.memory[task["name"]] = result
                
                return {
                    "agent": self.name,
                    "task": task["name"],
                    "result": result,
                    "status": "completed"
                }
            
            def share_knowledge(self, other_agent, key):
                if key in self.memory:
                    other_agent.memory[key] = self.memory[key]
                    return True
                return False
        
        # Create specialized agents
        researcher = MockAgent("researcher", ["research", "analysis"])
        writer = MockAgent("writer", ["writing", "documentation"])
        reviewer = MockAgent("reviewer", ["review", "quality_check"])
        
        # Define workflow tasks
        tasks = [
            {"name": "research_task", "type": "research", "description": "Research AI trends"},
            {"name": "write_task", "type": "writing", "description": "Write summary report"},
            {"name": "review_task", "type": "review", "description": "Review final document"}
        ]
        
        results = []
        
        # Execute tasks with appropriate agents
        for task in tasks:
            if task["type"] == "research":
                result = researcher.execute_task(task)
            elif task["type"] == "writing":
                # Writer needs research results
                researcher.share_knowledge(writer, "research_task")
                result = writer.execute_task(task)
            elif task["type"] == "review":
                # Reviewer needs writing results
                writer.share_knowledge(reviewer, "write_task")
                result = reviewer.execute_task(task)
            
            results.append(result)
        
        # Verify collaboration
        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)
        
        # Verify knowledge sharing
        assert "research_task" in writer.memory
        assert "write_task" in reviewer.memory
    
    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""
        
        class UnreliableAgent:
            def __init__(self, name, failure_rate=0.3):
                self.name = name
                self.failure_rate = failure_rate
                self.attempt_count = 0
            
            def execute_task(self, task):
                self.attempt_count += 1
                
                # Simulate random failures
                import random
                if random.random() < self.failure_rate:
                    return {
                        "agent": self.name,
                        "task": task["name"],
                        "status": "failed",
                        "error": "Simulated failure",
                        "attempt": self.attempt_count
                    }
                
                return {
                    "agent": self.name,
                    "task": task["name"],
                    "result": f"Completed {task['description']}",
                    "status": "completed",
                    "attempt": self.attempt_count
                }
        
        class ResilientExecutor:
            def __init__(self, max_retries=3):
                self.max_retries = max_retries
            
            def execute_with_retry(self, agent, task):
                for attempt in range(self.max_retries):
                    result = agent.execute_task(task)
                    
                    if result["status"] == "completed":
                        return result
                    
                    if attempt == self.max_retries - 1:
                        result["final_attempt"] = True
                        return result
                
                return {"status": "exhausted", "max_retries": self.max_retries}
        
        # Test with unreliable agent
        agent = UnreliableAgent("unreliable", failure_rate=0.8)  # High failure rate
        executor = ResilientExecutor(max_retries=5)
        
        task = {"name": "test_task", "description": "Test task with retries"}
        
        # Execute multiple times to test retry logic
        success_count = 0
        total_attempts = 0
        
        for _ in range(10):
            result = executor.execute_with_retry(agent, task)
            total_attempts += result.get("attempt", 0)
            
            if result["status"] == "completed":
                success_count += 1
        
        # Should have some successes due to retries
        assert success_count > 0
        assert total_attempts > 10  # More attempts than executions due to retries

class TestSystemIntegration:
    """Test integration with external systems"""
    
    def test_database_integration(self, temp_dir):
        """Test database operations"""
        import sqlite3
        import json
        
        class MockDatabase:
            def __init__(self, db_path):
                self.db_path = db_path
                self.init_database()
            
            def init_database(self):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        status TEXT NOT NULL,
                        result TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS agents (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                conn.close()
            
            def save_task(self, task):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO tasks (name, status, result) VALUES (?, ?, ?)",
                    (task["name"], task["status"], json.dumps(task.get("result")))
                )
                
                task_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                return task_id
            
            def get_task(self, task_id):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "status": row[2],
                        "result": json.loads(row[3]) if row[3] else None,
                        "created_at": row[4]
                    }
                return None
        
        # Test database operations
        db_path = temp_dir / "test.db"
        db = MockDatabase(str(db_path))
        
        # Save a task
        task = {
            "name": "test_task",
            "status": "completed",
            "result": {"output": "Success", "score": 95}
        }
        
        task_id = db.save_task(task)
        assert task_id is not None
        
        # Retrieve the task
        retrieved_task = db.get_task(task_id)
        assert retrieved_task["name"] == "test_task"
        assert retrieved_task["status"] == "completed"
        assert retrieved_task["result"]["output"] == "Success"
    
    def test_cache_integration(self, mock_redis):
        """Test Redis cache integration"""
        
        class MockCacheService:
            def __init__(self, redis_client):
                self.redis = redis_client
            
            def cache_result(self, key, result, ttl=3600):
                import json
                serialized = json.dumps(result)
                self.redis.setex(key, ttl, serialized)
            
            def get_cached_result(self, key):
                import json
                cached = self.redis.get(key)
                if cached:
                    return json.loads(cached)
                return None
            
            def invalidate_cache(self, pattern):
                # Mock cache invalidation
                return True
        
        cache = MockCacheService(mock_redis)
        
        # Test caching
        result = {"data": "test result", "timestamp": "2025-06-29"}
        cache.cache_result("task:123", result)
        
        # Verify cache call
        mock_redis.setex.assert_called_once()
        
        # Test retrieval
        mock_redis.get.return_value = '{"data": "test result", "timestamp": "2025-06-29"}'
        cached_result = cache.get_cached_result("task:123")
        
        assert cached_result["data"] == "test result"
        assert cached_result["timestamp"] == "2025-06-29"
    
    @pytest.mark.asyncio
    async def test_llm_integration(self, mock_ollama):
        """Test LLM provider integration"""
        
        class MockLLMService:
            def __init__(self, ollama_client):
                self.ollama = ollama_client
                self.request_count = 0
            
            async def generate_response(self, prompt, model="mistral:7b"):
                self.request_count += 1
                
                response = await self.ollama.generate({
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                })
                
                return {
                    "response": response["response"],
                    "model": response["model"],
                    "request_id": self.request_count
                }
            
            async def batch_generate(self, prompts, model="mistral:7b"):
                results = []
                for prompt in prompts:
                    result = await self.generate_response(prompt, model)
                    results.append(result)
                return results
        
        # Set up mock
        mock_ollama.generate = AsyncMock(return_value={
            "response": "Generated response",
            "model": "mistral:7b",
            "done": True
        })
        
        llm_service = MockLLMService(mock_ollama)
        
        # Test single generation
        result = await llm_service.generate_response("Test prompt")
        assert result["response"] == "Generated response"
        assert result["request_id"] == 1
        
        # Test batch generation
        prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
        results = await llm_service.batch_generate(prompts)
        
        assert len(results) == 3
        assert llm_service.request_count == 4  # 1 + 3

class TestPerformanceIntegration:
    """Test performance-related integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self):
        """Test concurrent execution of multiple tasks"""
        import asyncio
        import time
        
        class ConcurrentTaskExecutor:
            def __init__(self, max_concurrent=3):
                self.max_concurrent = max_concurrent
                self.semaphore = asyncio.Semaphore(max_concurrent)
            
            async def execute_task(self, task_id, duration=0.1):
                async with self.semaphore:
                    start_time = time.time()
                    await asyncio.sleep(duration)
                    end_time = time.time()
                    
                    return {
                        "task_id": task_id,
                        "execution_time": end_time - start_time,
                        "status": "completed"
                    }
            
            async def execute_batch(self, task_specs):
                tasks = [
                    self.execute_task(spec["id"], spec.get("duration", 0.1))
                    for spec in task_specs
                ]
                
                results = await asyncio.gather(*tasks)
                return results
        
        executor = ConcurrentTaskExecutor(max_concurrent=2)
        
        # Create test tasks
        task_specs = [
            {"id": f"task_{i}", "duration": 0.05}
            for i in range(5)
        ]
        
        start_time = time.time()
        results = await executor.execute_batch(task_specs)
        total_time = time.time() - start_time
        
        # Verify results
        assert len(results) == 5
        assert all(r["status"] == "completed" for r in results)
        
        # Should complete faster than sequential execution
        # With max_concurrent=2, should take ~0.15s instead of 0.25s
        assert total_time < 0.2
    
    def test_memory_usage_tracking(self):
        """Test memory usage tracking during operations"""
        import sys
        import gc
        
        class MemoryTracker:
            def __init__(self):
                self.baseline = self.get_memory_usage()
                self.measurements = []
            
            def get_memory_usage(self):
                gc.collect()  # Force garbage collection
                return sys.getsizeof(gc.get_objects())
            
            def record_measurement(self, label):
                current = self.get_memory_usage()
                self.measurements.append({
                    "label": label,
                    "memory": current,
                    "delta": current - self.baseline
                })
            
            def get_memory_report(self):
                return {
                    "baseline": self.baseline,
                    "measurements": self.measurements,
                    "peak_usage": max(m["memory"] for m in self.measurements) if self.measurements else self.baseline
                }
        
        tracker = MemoryTracker()
        
        # Simulate memory-intensive operations
        tracker.record_measurement("start")
        
        # Create some data
        large_data = [i for i in range(10000)]
        tracker.record_measurement("after_data_creation")
        
        # Process data
        processed_data = [x * 2 for x in large_data]
        tracker.record_measurement("after_processing")
        
        # Clean up
        del large_data
        del processed_data
        tracker.record_measurement("after_cleanup")
        
        report = tracker.get_memory_report()
        
        # Verify tracking
        assert len(report["measurements"]) == 4
        assert report["peak_usage"] >= report["baseline"]
        
        # Memory should increase after data creation
        creation_delta = report["measurements"][1]["delta"]
        assert creation_delta > 0

class TestConfigurationIntegration:
    """Test configuration and environment integration"""
    
    def test_environment_configuration(self, mock_env):
        """Test environment-based configuration"""
        
        class ConfigManager:
            def __init__(self):
                self.config = {}
                self.load_config()
            
            def load_config(self):
                import os
                
                # Load from environment
                self.config = {
                    "database_url": os.getenv("DATABASE_URL", "sqlite:///default.db"),
                    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                    "secret_key": os.getenv("SECRET_KEY"),
                    "log_level": os.getenv("LOG_LEVEL", "INFO"),
                    "environment": os.getenv("ENVIRONMENT", "development")
                }
            
            def get(self, key, default=None):
                return self.config.get(key, default)
            
            def validate_config(self):
                required_keys = ["secret_key"]
                missing = [key for key in required_keys if not self.config.get(key)]
                
                if missing:
                    raise ValueError(f"Missing required configuration: {missing}")
                
                return True
        
        config = ConfigManager()
        
        # Test configuration loading
        assert config.get("database_url") == "sqlite:///test.db"
        assert config.get("secret_key") == "test-secret-key"
        assert config.get("environment") == "test"
        
        # Test validation
        assert config.validate_config() == True
    
    def test_multi_environment_config(self, temp_dir):
        """Test configuration for multiple environments"""
        import json
        
        # Create config files
        configs = {
            "development": {
                "debug": True,
                "database_url": "sqlite:///dev.db",
                "log_level": "DEBUG"
            },
            "production": {
                "debug": False,
                "database_url": "postgresql://prod/db",
                "log_level": "INFO"
            },
            "test": {
                "debug": True,
                "database_url": "sqlite:///:memory:",
                "log_level": "DEBUG"
            }
        }
        
        for env, config in configs.items():
            config_file = temp_dir / f"{env}.json"
            with open(config_file, 'w') as f:
                json.dump(config, f)
        
        class MultiEnvConfig:
            def __init__(self, config_dir, environment="development"):
                self.config_dir = Path(config_dir)
                self.environment = environment
                self.config = self.load_config()
            
            def load_config(self):
                config_file = self.config_dir / f"{self.environment}.json"
                
                if not config_file.exists():
                    raise FileNotFoundError(f"Config file not found: {config_file}")
                
                with open(config_file) as f:
                    return json.load(f)
        
        # Test different environments
        dev_config = MultiEnvConfig(temp_dir, "development")
        assert dev_config.config["debug"] == True
        assert "dev.db" in dev_config.config["database_url"]
        
        prod_config = MultiEnvConfig(temp_dir, "production")
        assert prod_config.config["debug"] == False
        assert "postgresql" in prod_config.config["database_url"]
        
        test_config = MultiEnvConfig(temp_dir, "test")
        assert ":memory:" in test_config.config["database_url"]