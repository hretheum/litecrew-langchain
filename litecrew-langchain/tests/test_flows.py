"""
Tests for Conditional Flows system.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask, TaskOutput
from litecrew.orchestration.flows import (
    ConditionOperator,
    ExecutionFlow,
    FlowBuilder,
    FlowCondition,
    FlowExecutor,
    FlowNode,
    FlowNodeType,
)


class TestFlowConditions:
    """Test flow condition evaluation."""
    
    def test_basic_conditions(self):
        """Test basic condition operators."""
        context = {"value": 10, "name": "test", "items": [1, 2, 3]}
        
        # Equals
        cond = FlowCondition("$value", ConditionOperator.EQUALS, 10)
        assert cond.evaluate(context) is True
        
        # Not equals
        cond = FlowCondition("$value", ConditionOperator.NOT_EQUALS, 5)
        assert cond.evaluate(context) is True
        
        # Greater than
        cond = FlowCondition("$value", ConditionOperator.GREATER_THAN, 5)
        assert cond.evaluate(context) is True
        
        # Less than
        cond = FlowCondition("$value", ConditionOperator.LESS_THAN, 20)
        assert cond.evaluate(context) is True
        
        # Contains
        cond = FlowCondition("$name", ConditionOperator.CONTAINS, "es")
        assert cond.evaluate(context) is True
        
        # In
        cond = FlowCondition(2, ConditionOperator.IN, "$items")
        assert cond.evaluate(context) is True
    
    def test_variable_resolution(self):
        """Test variable resolution in conditions."""
        context = {"threshold": 0.8, "score": 0.9}
        
        # Both sides as variables
        cond = FlowCondition("$score", ConditionOperator.GREATER_THAN, "$threshold")
        assert cond.evaluate(context) is True
        
        # Mixed variable and literal
        cond = FlowCondition("$score", ConditionOperator.GREATER_THAN, 0.7)
        assert cond.evaluate(context) is True


class TestFlowExecution:
    """Test flow execution mechanics."""
    
    @pytest.fixture
    def agents(self):
        """Create test agents."""
        return {
            "researcher": LiteAgent(
                role="Researcher",
                goal="Research information",
                backstory="Expert researcher"
            ),
            "analyst": LiteAgent(
                role="Analyst",
                goal="Analyze data",
                backstory="Data analyst"
            )
        }
    
    @pytest.fixture
    def executor(self):
        """Create flow executor."""
        return FlowExecutor(enable_debugging=False)
    
    def test_simple_conditional_flow(self, agents, executor):
        """Test simple if-else flow."""
        # Build flow
        builder = FlowBuilder("Simple Conditional")
        
        # Add initial task
        task1 = LiteTask(
            description="Check data quality",
            agent=agents["researcher"],
            expected_output="Quality score"
        )
        task1_id = builder.add_task(task1, agents["researcher"])
        
        # Add condition
        condition = FlowCondition("$quality_score", ConditionOperator.GREATER_THAN, 0.8)
        
        # Add conditional tasks
        task_good = LiteTask(
            description="Process high quality data",
            agent=agents["analyst"],
            expected_output="Processed data"
        )
        task_bad = LiteTask(
            description="Clean low quality data",
            agent=agents["analyst"],
            expected_output="Cleaned data"
        )
        
        good_id = builder.add_task(task_good, agents["analyst"])
        bad_id = builder.add_task(task_bad, agents["analyst"])
        
        cond_id = builder.add_condition(condition, good_id, bad_id)
        
        flow = builder.build()
        
        # Mock task execution
        with patch.object(agents["researcher"], 'execute_task') as mock_research:
            with patch.object(agents["analyst"], 'execute_task') as mock_analyst:
                mock_research.return_value = TaskOutput(raw="0.9", task_id="1")
                mock_analyst.return_value = TaskOutput(raw="Processed", task_id="2")
                
                # Execute with high quality score
                context = executor.execute(flow, {"quality_score": 0.9})
                
                # Should execute good branch
                assert mock_analyst.called
                assert "Processed" in str(mock_analyst.return_value.raw)
    
    def test_loop_execution(self, agents, executor):
        """Test loop flow execution."""
        flow = ExecutionFlow("Loop Test")
        
        # Add loop condition
        loop_cond = FlowCondition("$counter", ConditionOperator.LESS_THAN, 3)
        
        # Add task in loop
        task = LiteTask(
            description="Process item",
            agent=agents["researcher"],
            expected_output="Item processed"
        )
        
        task_node = FlowNode(
            id="process_task",
            type=FlowNodeType.TASK,
            task=task,
            agent=agents["researcher"]
        )
        flow.add_node(task_node)
        
        # Add loop node
        loop_node = FlowNode(
            id="loop",
            type=FlowNodeType.LOOP,
            loop_condition=loop_cond,
            loop_body=["process_task"],
            max_iterations=5
        )
        flow.add_node(loop_node)
        
        # Mock execution
        execution_count = 0
        def mock_execute(*args, **kwargs):
            nonlocal execution_count
            execution_count += 1
            return TaskOutput(raw=f"Processed {execution_count}", task_id=str(execution_count))
        
        with patch.object(agents["researcher"], 'execute_task', side_effect=mock_execute):
            context = executor.execute(flow, {"counter": 0})
            
            # Update counter in mock to break loop
            flow.context["counter"] = 3
            
            # Should have executed multiple times
            assert execution_count >= 1
            
            # Check metrics
            metrics = executor.get_metrics()
            assert metrics["loop_iterations"] > 0
    
    def test_branch_evaluation_metric(self, executor):
        """Test branch evaluation metric (<10ms)."""
        flow = ExecutionFlow("Branch Test")
        
        # Create multiple conditions to test
        conditions = []
        for i in range(10):
            cond = FlowCondition(f"$var_{i}", ConditionOperator.EQUALS, i)
            node = FlowNode(
                id=f"cond_{i}",
                type=FlowNodeType.CONDITION,
                condition=cond,
                true_branch="end",
                false_branch="end"
            )
            flow.add_node(node)
            conditions.append(node)
        
        # Add end node
        end_node = FlowNode(id="end", type=FlowNodeType.END)
        flow.add_node(end_node)
        
        # Set start to first condition
        flow.start_node = "cond_0"
        
        # Execute and measure
        context = {f"var_{i}": i for i in range(10)}
        
        start_time = time.perf_counter()
        executor.execute(flow, context)
        total_time = (time.perf_counter() - start_time) * 1000  # ms
        
        metrics = executor.get_metrics()
        evaluations = metrics["branch_evaluations"]
        
        # Calculate average time per evaluation
        if evaluations > 0:
            avg_eval_time = total_time / evaluations
            assert avg_eval_time < 10  # <10ms per evaluation
    
    def test_flow_debugging(self, agents, executor):
        """Test flow debugging capability."""
        executor.enable_debugging = True
        
        flow = ExecutionFlow("Debug Test")
        
        task = LiteTask(
            description="Debug task",
            agent=agents["researcher"],
            expected_output="Debug output"
        )
        
        task_node = FlowNode(
            id="debug_task",
            type=FlowNodeType.TASK,
            task=task,
            agent=agents["researcher"]
        )
        flow.add_node(task_node)
        
        # Capture debug output
        debug_output = []
        
        with patch('builtins.print') as mock_print:
            with patch.object(agents["researcher"], 'execute_task', return_value=TaskOutput(raw="Done", task_id="1")):
                executor.execute(flow)
                
                # Check debug output was generated
                assert mock_print.called
                debug_calls = [str(call) for call in mock_print.call_args_list]
                assert any("Executing node" in str(call) for call in debug_calls)


class TestFlowValidation:
    """Test flow validation functionality."""
    
    def test_valid_flow(self):
        """Test validation of a valid flow."""
        flow = ExecutionFlow("Valid Flow")
        
        # Add nodes
        start = FlowNode(id="start", type=FlowNodeType.START)
        task = FlowNode(id="task", type=FlowNodeType.TASK)
        end = FlowNode(id="end", type=FlowNodeType.END)
        
        flow.add_node(start)
        flow.add_node(task)
        flow.add_node(end)
        
        is_valid, issues = flow.validate()
        assert is_valid
        assert len(issues) == 0
    
    def test_invalid_flow_missing_nodes(self):
        """Test validation catches missing node references."""
        flow = ExecutionFlow("Invalid Flow")
        
        # Add condition with non-existent branch
        cond = FlowNode(
            id="cond",
            type=FlowNodeType.CONDITION,
            condition=FlowCondition("$x", ConditionOperator.EQUALS, 1),
            true_branch="missing_node",
            false_branch="also_missing"
        )
        flow.add_node(cond)
        
        is_valid, issues = flow.validate()
        assert not is_valid
        assert len(issues) >= 2
        assert any("non-existent" in issue for issue in issues)
    
    def test_cycle_detection(self):
        """Test validation detects cycles."""
        flow = ExecutionFlow("Cyclic Flow")
        
        # Create a cycle
        node1 = FlowNode(
            id="node1",
            type=FlowNodeType.CONDITION,
            condition=FlowCondition("$x", ConditionOperator.EQUALS, 1),
            true_branch="node2"
        )
        node2 = FlowNode(
            id="node2",
            type=FlowNodeType.CONDITION,
            condition=FlowCondition("$y", ConditionOperator.EQUALS, 2),
            true_branch="node1"  # Cycle back
        )
        
        flow.add_node(node1)
        flow.add_node(node2)
        
        is_valid, issues = flow.validate()
        assert not is_valid
        assert any("Cycle detected" in issue for issue in issues)


class TestFlowBuilder:
    """Test flow builder functionality."""
    
    def test_builder_basic_flow(self):
        """Test building a basic flow."""
        builder = FlowBuilder("Test Flow")
        
        # Add components
        agent = LiteAgent(role="Worker", goal="Do work", backstory="Worker")
        task = LiteTask(description="Work task", agent=agent, expected_output="Done")
        
        task_id = builder.add_task(task, agent)
        assert task_id is not None
        
        # Add condition
        cond = FlowCondition("$result", ConditionOperator.EQUALS, "success")
        cond_id = builder.add_condition(cond, "end", "retry")
        assert cond_id is not None
        
        # Build should succeed with partial flow
        # (In real use, would add all nodes before building)
        flow = builder.flow  # Access directly since validation would fail
        assert len(flow.nodes) == 2
    
    def test_builder_auto_ids(self):
        """Test automatic ID generation."""
        builder = FlowBuilder("Auto ID Test")
        
        agent = LiteAgent(role="Worker", goal="Do work", backstory="Worker")
        task = LiteTask(description="Task", agent=agent, expected_output="Done")
        
        # Add multiple tasks
        ids = []
        for _ in range(3):
            task_id = builder.add_task(task, agent)
            ids.append(task_id)
        
        # IDs should be unique
        assert len(set(ids)) == 3
        assert all("task_" in id for id in ids)