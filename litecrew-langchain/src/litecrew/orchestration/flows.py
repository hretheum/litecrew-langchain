"""
Conditional Flows system for advanced orchestration.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union, Tuple

from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask, TaskOutput


class FlowNodeType(Enum):
    """Types of flow nodes."""
    TASK = "task"
    CONDITION = "condition"
    LOOP = "loop"
    BRANCH = "branch"
    MERGE = "merge"
    START = "start"
    END = "end"


class ConditionOperator(Enum):
    """Condition operators."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class FlowCondition:
    """A condition for flow control."""
    
    left: Union[str, Any]  # Variable name or value
    operator: ConditionOperator
    right: Union[str, Any]  # Variable name or value
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate the condition against context."""
        # Resolve values
        left_value = self._resolve_value(self.left, context)
        right_value = self._resolve_value(self.right, context)
        
        # Evaluate based on operator
        if self.operator == ConditionOperator.EQUALS:
            return left_value == right_value
        elif self.operator == ConditionOperator.NOT_EQUALS:
            return left_value != right_value
        elif self.operator == ConditionOperator.GREATER_THAN:
            return left_value > right_value
        elif self.operator == ConditionOperator.LESS_THAN:
            return left_value < right_value
        elif self.operator == ConditionOperator.CONTAINS:
            return str(right_value) in str(left_value)
        elif self.operator == ConditionOperator.NOT_CONTAINS:
            return str(right_value) not in str(left_value)
        elif self.operator == ConditionOperator.IN:
            return left_value in right_value
        elif self.operator == ConditionOperator.NOT_IN:
            return left_value not in right_value
        else:
            return False
    
    def _resolve_value(self, value: Union[str, Any], context: Dict[str, Any]) -> Any:
        """Resolve a value from context if it's a variable reference."""
        if isinstance(value, str) and value.startswith("$"):
            # Variable reference
            var_name = value[1:]
            return context.get(var_name, None)
        return value


@dataclass
class FlowNode:
    """A node in the execution flow."""
    
    id: str
    type: FlowNodeType
    name: str = ""
    description: str = ""
    
    # For TASK nodes
    task: Optional[LiteTask] = None
    agent: Optional[LiteAgent] = None
    
    # For CONDITION nodes
    condition: Optional[FlowCondition] = None
    true_branch: Optional[str] = None  # Node ID
    false_branch: Optional[str] = None  # Node ID
    
    # For LOOP nodes
    loop_condition: Optional[FlowCondition] = None
    loop_body: List[str] = field(default_factory=list)  # Node IDs
    max_iterations: int = 100
    
    # For BRANCH nodes
    branches: Dict[str, str] = field(default_factory=dict)  # condition_value -> node_id
    
    # Execution tracking
    executed: bool = False
    result: Optional[Any] = None
    execution_count: int = 0
    
    def reset(self) -> None:
        """Reset execution state."""
        self.executed = False
        self.result = None
        self.execution_count = 0


@dataclass
class ExecutionFlow:
    """A complete execution flow with conditional logic."""
    
    name: str
    nodes: Dict[str, FlowNode] = field(default_factory=dict)
    start_node: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    execution_path: List[str] = field(default_factory=list)
    
    def add_node(self, node: FlowNode) -> None:
        """Add a node to the flow."""
        self.nodes[node.id] = node
        
        # Set start node if it's the first or explicitly a START node
        if not self.start_node or node.type == FlowNodeType.START:
            self.start_node = node.id
    
    def get_node(self, node_id: str) -> Optional[FlowNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the flow structure."""
        issues = []
        
        if not self.start_node:
            issues.append("No start node defined")
        
        # Check all referenced nodes exist
        for node in self.nodes.values():
            if node.type == FlowNodeType.CONDITION:
                if node.true_branch and node.true_branch not in self.nodes:
                    issues.append(f"Node {node.id}: true_branch references non-existent node {node.true_branch}")
                if node.false_branch and node.false_branch not in self.nodes:
                    issues.append(f"Node {node.id}: false_branch references non-existent node {node.false_branch}")
            
            elif node.type == FlowNodeType.LOOP:
                for body_node in node.loop_body:
                    if body_node not in self.nodes:
                        issues.append(f"Node {node.id}: loop body references non-existent node {body_node}")
            
            elif node.type == FlowNodeType.BRANCH:
                for _, target_node in node.branches.items():
                    if target_node not in self.nodes:
                        issues.append(f"Node {node.id}: branch references non-existent node {target_node}")
        
        # Check for loops in non-LOOP nodes
        visited = set()
        
        def check_cycles(node_id: str, path: List[str]) -> None:
            if node_id in path:
                issues.append(f"Cycle detected: {' -> '.join(path + [node_id])}")
                return
            
            if node_id in visited:
                return
            
            visited.add(node_id)
            node = self.nodes.get(node_id)
            if not node:
                return
            
            new_path = path + [node_id]
            
            if node.type == FlowNodeType.CONDITION:
                if node.true_branch:
                    check_cycles(node.true_branch, new_path)
                if node.false_branch:
                    check_cycles(node.false_branch, new_path)
            elif node.type == FlowNodeType.BRANCH:
                for _, target in node.branches.items():
                    check_cycles(target, new_path)
        
        if self.start_node:
            check_cycles(self.start_node, [])
        
        return len(issues) == 0, issues


class FlowExecutor:
    """Executor for conditional flows."""
    
    def __init__(
        self,
        max_execution_time: float = 300.0,  # 5 minutes
        enable_debugging: bool = False
    ):
        """Initialize flow executor.
        
        Args:
            max_execution_time: Maximum execution time in seconds
            enable_debugging: Enable debug output
        """
        self.max_execution_time = max_execution_time
        self.enable_debugging = enable_debugging
        self._execution_metrics = {
            "total_nodes_executed": 0,
            "branch_evaluations": 0,
            "loop_iterations": 0,
            "execution_times": []
        }
    
    def execute(
        self,
        flow: ExecutionFlow,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a flow.
        
        Args:
            flow: Flow to execute
            initial_context: Initial context values
            
        Returns:
            Final execution context
        """
        start_time = time.perf_counter()
        
        # Initialize context
        if initial_context:
            flow.context.update(initial_context)
        
        # Reset all nodes
        for node in flow.nodes.values():
            node.reset()
        
        # Clear execution path
        flow.execution_path.clear()
        
        # Execute from start node
        if not flow.start_node:
            raise ValueError("No start node defined")
        
        try:
            self._execute_node(flow, flow.start_node, start_time)
        except Exception as e:
            if self.enable_debugging:
                print(f"Flow execution error: {e}")
            raise
        
        # Record execution time
        execution_time = time.perf_counter() - start_time
        self._execution_metrics["execution_times"].append(execution_time)
        
        return flow.context
    
    def _execute_node(
        self,
        flow: ExecutionFlow,
        node_id: str,
        start_time: float
    ) -> Optional[str]:
        """Execute a single node and return next node ID.
        
        Args:
            flow: Flow being executed
            node_id: ID of node to execute
            start_time: Flow start time for timeout checking
            
        Returns:
            ID of next node to execute, or None
        """
        # Check timeout
        if time.perf_counter() - start_time > self.max_execution_time:
            raise TimeoutError(f"Flow execution exceeded {self.max_execution_time}s")
        
        node = flow.get_node(node_id)
        if not node:
            return None
        
        # Track execution
        flow.execution_path.append(node_id)
        node.execution_count += 1
        self._execution_metrics["total_nodes_executed"] += 1
        
        if self.enable_debugging:
            print(f"Executing node {node_id} ({node.type.value}): {node.name}")
        
        # Execute based on node type
        if node.type == FlowNodeType.TASK:
            return self._execute_task_node(flow, node)
        
        elif node.type == FlowNodeType.CONDITION:
            return self._execute_condition_node(flow, node)
        
        elif node.type == FlowNodeType.LOOP:
            return self._execute_loop_node(flow, node, start_time)
        
        elif node.type == FlowNodeType.BRANCH:
            return self._execute_branch_node(flow, node)
        
        elif node.type == FlowNodeType.START:
            # Start nodes typically have a single outgoing connection
            # For simplicity, we'll look for the first task or condition node
            for next_node in flow.nodes.values():
                if next_node.id != node_id and next_node.type in [FlowNodeType.TASK, FlowNodeType.CONDITION]:
                    return next_node.id
            return None
        
        elif node.type == FlowNodeType.END:
            return None
        
        return None
    
    def _execute_task_node(self, flow: ExecutionFlow, node: FlowNode) -> Optional[str]:
        """Execute a task node."""
        if node.task and node.agent:
            # Execute the task
            result = node.agent.execute_task(node.task, str(flow.context))
            node.result = result
            
            # Store result in context
            result_key = f"{node.id}_result"
            flow.context[result_key] = result
            
            # Update task output in context
            if hasattr(result, 'raw'):
                flow.context[f"{node.id}_output"] = result.raw
        
        node.executed = True
        
        # Find next node (simple sequential for now)
        # In a full implementation, this would follow edges
        return self._find_next_sequential_node(flow, node.id)
    
    def _execute_condition_node(self, flow: ExecutionFlow, node: FlowNode) -> Optional[str]:
        """Execute a condition node."""
        self._execution_metrics["branch_evaluations"] += 1
        
        if node.condition:
            result = node.condition.evaluate(flow.context)
            node.result = result
            
            if self.enable_debugging:
                print(f"Condition evaluated to: {result}")
            
            # Choose branch
            if result and node.true_branch:
                return node.true_branch
            elif not result and node.false_branch:
                return node.false_branch
        
        node.executed = True
        return None
    
    def _execute_loop_node(
        self,
        flow: ExecutionFlow,
        node: FlowNode,
        start_time: float
    ) -> Optional[str]:
        """Execute a loop node."""
        iteration = 0
        
        while iteration < node.max_iterations:
            # Check loop condition
            if node.loop_condition:
                if not node.loop_condition.evaluate(flow.context):
                    break
            
            # Execute loop body
            for body_node_id in node.loop_body:
                next_node = body_node_id
                while next_node and next_node in node.loop_body:
                    next_node = self._execute_node(flow, next_node, start_time)
            
            iteration += 1
            self._execution_metrics["loop_iterations"] += 1
            
            # Update loop counter in context
            flow.context[f"{node.id}_iteration"] = iteration
        
        node.executed = True
        node.result = {"iterations": iteration}
        
        # Continue after loop
        return self._find_next_sequential_node(flow, node.id)
    
    def _execute_branch_node(self, flow: ExecutionFlow, node: FlowNode) -> Optional[str]:
        """Execute a branch node."""
        self._execution_metrics["branch_evaluations"] += 1
        
        # Evaluate each branch condition
        for condition_key, target_node in node.branches.items():
            # Simple string matching for now
            # In full implementation, could support complex conditions
            if str(flow.context.get("branch_key", "")) == condition_key:
                node.result = {"selected_branch": condition_key}
                node.executed = True
                return target_node
        
        # Default branch (if exists)
        if "default" in node.branches:
            node.result = {"selected_branch": "default"}
            node.executed = True
            return node.branches["default"]
        
        node.executed = True
        return None
    
    def _find_next_sequential_node(self, flow: ExecutionFlow, current_id: str) -> Optional[str]:
        """Find the next node in sequential order."""
        # Simple implementation: find first unexecuted node after current
        node_ids = list(flow.nodes.keys())
        try:
            current_idx = node_ids.index(current_id)
            for next_id in node_ids[current_idx + 1:]:
                next_node = flow.nodes[next_id]
                if not next_node.executed and next_node.type != FlowNodeType.END:
                    return next_id
        except ValueError:
            pass
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics."""
        metrics = self._execution_metrics.copy()
        
        if metrics["execution_times"]:
            metrics["avg_execution_time"] = sum(metrics["execution_times"]) / len(metrics["execution_times"])
            metrics["max_execution_time"] = max(metrics["execution_times"])
            metrics["min_execution_time"] = min(metrics["execution_times"])
        
        return metrics


class FlowBuilder:
    """Builder for creating flows programmatically."""
    
    def __init__(self, name: str):
        """Initialize flow builder.
        
        Args:
            name: Flow name
        """
        self.flow = ExecutionFlow(name=name)
        self._node_counter = 0
    
    def add_task(
        self,
        task: LiteTask,
        agent: LiteAgent,
        node_id: Optional[str] = None
    ) -> str:
        """Add a task node.
        
        Args:
            task: Task to execute
            agent: Agent to execute task
            node_id: Optional node ID
            
        Returns:
            Node ID
        """
        if not node_id:
            node_id = f"task_{self._node_counter}"
            self._node_counter += 1
        
        node = FlowNode(
            id=node_id,
            type=FlowNodeType.TASK,
            name=task.description[:50],
            description=task.description,
            task=task,
            agent=agent
        )
        
        self.flow.add_node(node)
        return node_id
    
    def add_condition(
        self,
        condition: FlowCondition,
        true_branch: str,
        false_branch: Optional[str] = None,
        node_id: Optional[str] = None
    ) -> str:
        """Add a condition node.
        
        Args:
            condition: Condition to evaluate
            true_branch: Node ID for true branch
            false_branch: Node ID for false branch
            node_id: Optional node ID
            
        Returns:
            Node ID
        """
        if not node_id:
            node_id = f"condition_{self._node_counter}"
            self._node_counter += 1
        
        node = FlowNode(
            id=node_id,
            type=FlowNodeType.CONDITION,
            name=f"If {condition.left} {condition.operator.value} {condition.right}",
            condition=condition,
            true_branch=true_branch,
            false_branch=false_branch
        )
        
        self.flow.add_node(node)
        return node_id
    
    def add_loop(
        self,
        loop_condition: FlowCondition,
        loop_body: List[str],
        max_iterations: int = 100,
        node_id: Optional[str] = None
    ) -> str:
        """Add a loop node.
        
        Args:
            loop_condition: Condition for loop continuation
            loop_body: List of node IDs in loop body
            max_iterations: Maximum iterations
            node_id: Optional node ID
            
        Returns:
            Node ID
        """
        if not node_id:
            node_id = f"loop_{self._node_counter}"
            self._node_counter += 1
        
        node = FlowNode(
            id=node_id,
            type=FlowNodeType.LOOP,
            name=f"While {loop_condition.left} {loop_condition.operator.value} {loop_condition.right}",
            loop_condition=loop_condition,
            loop_body=loop_body,
            max_iterations=max_iterations
        )
        
        self.flow.add_node(node)
        return node_id
    
    def build(self) -> ExecutionFlow:
        """Build and return the flow."""
        # Validate before returning
        is_valid, issues = self.flow.validate()
        if not is_valid:
            raise ValueError(f"Flow validation failed: {issues}")
        
        return self.flow