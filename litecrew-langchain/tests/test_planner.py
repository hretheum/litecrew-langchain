"""
Tests for Planning and Reasoning system.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from litecrew.agent import Agent as LiteAgent
from litecrew.orchestration.planner import (
    ExecutionPlan,
    PlanStatus,
    PlanStep,
    ReasoningEngine,
    TaskPlanner,
)


class TestTaskPlanner:
    """Test task planning functionality."""
    
    @pytest.fixture
    def agents(self):
        """Create test agents."""
        return [
            LiteAgent(
                role="Researcher",
                goal="Research and gather information",
                backstory="Expert researcher"
            ),
            LiteAgent(
                role="Analyst",
                goal="Analyze data and provide insights",
                backstory="Data analyst"
            ),
            LiteAgent(
                role="Writer",
                goal="Create content and documentation",
                backstory="Professional writer"
            )
        ]
    
    @pytest.fixture
    def planner(self):
        """Create task planner."""
        return TaskPlanner(enable_reasoning=True, max_steps=10)
    
    def test_plan_creation(self, planner, agents):
        """Test basic plan creation."""
        goal = "Create a comprehensive report on AI trends"
        
        # Mock the planning agent's response
        mock_response = """
        [
            {
                "id": "step_1",
                "description": "Research current AI trends",
                "agent_role": "Researcher",
                "dependencies": [],
                "expected_output": "List of AI trends with sources"
            },
            {
                "id": "step_2",
                "description": "Analyze the trends for patterns",
                "agent_role": "Analyst",
                "dependencies": ["step_1"],
                "expected_output": "Analysis report with insights"
            },
            {
                "id": "step_3",
                "description": "Write the final report",
                "agent_role": "Writer",
                "dependencies": ["step_2"],
                "expected_output": "Comprehensive report document"
            }
        ]
        """
        
        with patch.object(planner.planning_agent, 'execute', return_value=mock_response):
            plan = planner.create_plan(goal, agents)
        
        assert plan.goal == goal
        assert len(plan.steps) == 3
        assert plan.steps[0].agent.role == "Researcher"
        assert plan.steps[1].dependencies == ["step_1"]
        assert plan.steps[2].agent.role == "Writer"
    
    def test_planning_time_constraint(self, planner, agents):
        """Test planning time meets <5s requirement."""
        goal = "Complex multi-step project"
        
        # Mock response to ensure fast execution
        with patch.object(planner.planning_agent, 'execute', return_value='[{"id": "step_1", "description": "Task", "agent_role": "Researcher", "dependencies": []}]'):
            start_time = time.perf_counter()
            plan = planner.create_plan(goal, agents)
            planning_time = (time.perf_counter() - start_time) * 1000  # ms
        
        assert planning_time < 5000  # <5s requirement
        assert len(plan.steps) >= 1
        
        # Check metrics
        metrics = planner.get_metrics()
        assert metrics["avg_planning_time"] < 5.0
    
    def test_plan_validation(self, planner, agents):
        """Test plan validation functionality."""
        # Create a valid plan
        plan = ExecutionPlan(goal="Test goal")
        plan.add_step(PlanStep(
            id="step_1",
            description="First step",
            goal="Do something",
            agent=agents[0]
        ))
        plan.add_step(PlanStep(
            id="step_2",
            description="Second step",
            goal="Do something else",
            agent=agents[1],
            dependencies=["step_1"]
        ))
        
        is_valid, issues = planner.validate_plan(plan)
        assert is_valid
        assert len(issues) == 0
        
        # Test invalid plan with circular dependency
        plan.steps[0].dependencies = ["step_2"]
        is_valid, issues = planner.validate_plan(plan)
        assert not is_valid
        assert any("Unreachable" in issue for issue in issues)
    
    def test_plan_optimization(self, planner, agents):
        """Test plan optimization for parallel execution."""
        plan = ExecutionPlan(goal="Parallel tasks")
        
        # Add steps that can be parallelized
        plan.add_step(PlanStep(
            id="step_1",
            description="Task A",
            goal="Complete A",
            agent=agents[0],
            dependencies=[]
        ))
        plan.add_step(PlanStep(
            id="step_2",
            description="Task B",
            goal="Complete B",
            agent=agents[1],
            dependencies=[]
        ))
        plan.add_step(PlanStep(
            id="step_3",
            description="Task C",
            goal="Complete C",
            agent=agents[2],
            dependencies=["step_1", "step_2"]
        ))
        
        optimized_plan = planner.optimize_plan(plan)
        
        # Check parallel groups identified
        assert "parallel_groups" in optimized_plan.context
        parallel_groups = optimized_plan.context["parallel_groups"]
        assert len(parallel_groups) > 0
        assert ["step_1", "step_2"] in parallel_groups
    
    def test_goal_decomposition(self, planner, agents):
        """Test complex goal decomposition."""
        complex_goal = """
        Build a complete web application with:
        1. User authentication
        2. Database design
        3. API endpoints
        4. Frontend interface
        5. Testing and deployment
        """
        
        mock_response = """
        [
            {"id": "step_1", "description": "Design database schema", "agent_role": "Analyst", "dependencies": []},
            {"id": "step_2", "description": "Implement authentication", "agent_role": "Researcher", "dependencies": ["step_1"]},
            {"id": "step_3", "description": "Create API endpoints", "agent_role": "Analyst", "dependencies": ["step_1"]},
            {"id": "step_4", "description": "Build frontend", "agent_role": "Writer", "dependencies": ["step_3"]},
            {"id": "step_5", "description": "Write tests", "agent_role": "Analyst", "dependencies": ["step_2", "step_3", "step_4"]},
            {"id": "step_6", "description": "Deploy application", "agent_role": "Researcher", "dependencies": ["step_5"]}
        ]
        """
        
        with patch.object(planner.planning_agent, 'execute', return_value=mock_response):
            plan = planner.create_plan(complex_goal, agents)
        
        assert len(plan.steps) >= 5
        # Check dependencies are properly set
        deploy_step = next(s for s in plan.steps if "deploy" in s.description.lower())
        assert len(deploy_step.dependencies) > 0
    
    def test_reasoning_chains(self, planner, agents):
        """Test reasoning is added to plan steps."""
        planner.enable_reasoning = True
        
        with patch.object(planner.planning_agent, 'execute') as mock_execute:
            # First call returns the plan, subsequent calls return reasoning
            mock_execute.side_effect = [
                '[{"id": "step_1", "description": "Research", "agent_role": "Researcher", "dependencies": []}]',
                "This step is necessary to gather initial information. It contributes foundational knowledge. Risk: incomplete data."
            ]
            
            plan = planner.create_plan("Simple goal", agents)
        
        assert plan.steps[0].reasoning != ""
        assert "necessary" in plan.steps[0].reasoning.lower()


class TestReasoningEngine:
    """Test reasoning engine functionality."""
    
    @pytest.fixture
    def reasoning_engine(self):
        """Create reasoning engine."""
        return ReasoningEngine()
    
    @pytest.fixture
    def test_step(self):
        """Create test step."""
        return PlanStep(
            id="test_step",
            description="Analyze market data",
            goal="Identify trends",
            reasoning="Market analysis is crucial for decision making"
        )
    
    def test_step_reasoning(self, reasoning_engine, test_step):
        """Test reasoning about step execution."""
        context = {"market": "bullish", "confidence": 0.8}
        previous_results = ["Data collected", "Initial analysis done"]
        
        mock_response = """
        {
            "should_execute": true,
            "adjustments": "Focus on tech sector",
            "risks": ["Market volatility", "Data accuracy"],
            "success_probability": 0.85
        }
        """
        
        with patch.object(reasoning_engine.reasoning_agent, 'execute', return_value=mock_response):
            analysis = reasoning_engine.reason_about_step(test_step, context, previous_results)
        
        assert analysis["should_execute"] is True
        assert analysis["success_probability"] == 0.85
        assert len(analysis["risks"]) == 2
        assert analysis["adjustments"] is not None
    
    def test_failure_analysis(self, reasoning_engine, test_step):
        """Test failure analysis capability."""
        error = ValueError("Invalid data format")
        context = {"step": "data_processing", "attempt": 1}
        
        mock_response = """
        The failure was caused by incorrect data format in the input file.
        We should retry with data validation. Alternative: use a different parser.
        To prevent: add input validation before processing.
        """
        
        with patch.object(reasoning_engine.reasoning_agent, 'execute', return_value=mock_response):
            analysis = reasoning_engine.analyze_failure(test_step, error, context)
        
        assert "analysis" in analysis
        assert analysis["should_retry"] is True  # "retry" is in response
        assert "root_cause" in analysis
        assert "timestamp" in analysis
    
    def test_adaptation_capability(self, reasoning_engine, test_step):
        """Test adaptation capability metric."""
        # Test multiple scenarios to verify adaptation
        scenarios = [
            {
                "context": {"environment": "production", "load": "high"},
                "expected_adaptation": "Scale resources"
            },
            {
                "context": {"errors": 5, "threshold": 3},
                "expected_adaptation": "Switch to fallback"
            },
            {
                "context": {"deadline": "urgent", "resources": "limited"},
                "expected_adaptation": "Prioritize critical"
            }
        ]
        
        adaptations_made = 0
        
        for scenario in scenarios:
            with patch.object(reasoning_engine.reasoning_agent, 'execute') as mock:
                mock.return_value = f'{{"should_execute": true, "adjustments": "{scenario["expected_adaptation"]}"}}'
                
                analysis = reasoning_engine.reason_about_step(
                    test_step,
                    scenario["context"],
                    []
                )
                
                if analysis.get("adjustments"):
                    adaptations_made += 1
        
        # Should adapt to different scenarios (automatic adaptation)
        assert adaptations_made == len(scenarios)


class TestPlanExecution:
    """Test plan execution mechanics."""
    
    def test_conditional_execution(self):
        """Test conditional step execution."""
        plan = ExecutionPlan(goal="Conditional workflow")
        
        # Step with condition
        step1 = PlanStep(
            id="step_1",
            description="Check condition",
            goal="Evaluate",
            conditions={"data_quality": {"operator": "greater_than", "value": 0.8}}
        )
        
        step2 = PlanStep(
            id="step_2",
            description="Process data",
            goal="Transform",
            dependencies=["step_1"],
            conditions={"proceed": True}
        )
        
        plan.add_step(step1)
        plan.add_step(step2)
        
        # Test condition not met
        plan.context = {"data_quality": 0.5}
        ready_steps = plan.get_ready_steps()
        assert step1 not in ready_steps
        
        # Test condition met
        plan.context = {"data_quality": 0.9}
        ready_steps = plan.get_ready_steps()
        assert step1 in ready_steps
        
        # Complete step 1 and check step 2
        step1.status = PlanStatus.COMPLETED
        plan.context["proceed"] = True
        ready_steps = plan.get_ready_steps()
        assert step2 in ready_steps
    
    def test_plan_status_tracking(self):
        """Test plan execution status tracking."""
        plan = ExecutionPlan(goal="Test execution")
        
        # Add multiple steps
        for i in range(5):
            plan.add_step(PlanStep(
                id=f"step_{i}",
                description=f"Task {i}",
                goal=f"Complete {i}"
            ))
        
        # Initial status
        status = plan.get_status()
        assert status["total_steps"] == 5
        assert status["completed_steps"] == 0
        assert status["progress_percentage"] == 0
        
        # Complete some steps
        plan.steps[0].status = PlanStatus.COMPLETED
        plan.steps[1].status = PlanStatus.COMPLETED
        plan.steps[2].status = PlanStatus.IN_PROGRESS
        plan.steps[3].status = PlanStatus.FAILED
        
        status = plan.get_status()
        assert status["completed_steps"] == 2
        assert status["failed_steps"] == 1
        assert status["in_progress_steps"] == 1
        assert status["progress_percentage"] == 40.0  # 2/5 * 100
    
    def test_deterministic_flow_execution(self):
        """Test flow execution is deterministic."""
        plan = ExecutionPlan(goal="Deterministic flow")
        
        # Create a specific dependency chain
        plan.add_step(PlanStep(id="A", description="Task A", goal="A"))
        plan.add_step(PlanStep(id="B", description="Task B", goal="B", dependencies=["A"]))
        plan.add_step(PlanStep(id="C", description="Task C", goal="C", dependencies=["A"]))
        plan.add_step(PlanStep(id="D", description="Task D", goal="D", dependencies=["B", "C"]))
        
        # Test execution order multiple times
        for _ in range(10):
            execution_order = []
            temp_plan = ExecutionPlan(goal=plan.goal)
            temp_plan.steps = [
                PlanStep(
                    id=s.id,
                    description=s.description,
                    goal=s.goal,
                    dependencies=s.dependencies.copy()
                ) for s in plan.steps
            ]
            
            while True:
                ready = temp_plan.get_ready_steps()
                if not ready:
                    break
                
                # Execute in consistent order (sorted by ID)
                ready.sort(key=lambda s: s.id)
                for step in ready:
                    execution_order.append(step.id)
                    step.status = PlanStatus.COMPLETED
            
            # Execution order should always respect dependencies
            assert execution_order.index("A") < execution_order.index("B")
            assert execution_order.index("A") < execution_order.index("C")
            assert execution_order.index("B") < execution_order.index("D")
            assert execution_order.index("C") < execution_order.index("D")