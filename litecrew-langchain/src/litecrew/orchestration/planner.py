"""
Planning and Reasoning system for advanced orchestration.
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask, TaskOutput


class PlanStatus(Enum):
    """Status of a plan or plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """A single step in an execution plan."""
    
    id: str
    description: str
    goal: str
    agent: Optional[LiteAgent] = None
    dependencies: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    expected_output: str = ""
    status: PlanStatus = PlanStatus.PENDING
    result: Optional[Any] = None
    reasoning: str = ""
    execution_time: float = 0.0
    
    def is_ready(self, completed_steps: List[str]) -> bool:
        """Check if this step is ready to execute."""
        # Check all dependencies are completed
        return all(dep in completed_steps for dep in self.dependencies)
    
    def should_execute(self, context: Dict[str, Any]) -> bool:
        """Check if conditions are met for execution."""
        if not self.conditions:
            return True
        
        # Evaluate conditions
        for key, expected_value in self.conditions.items():
            if key not in context:
                return False
            
            actual_value = context[key]
            
            # Handle different condition types
            if isinstance(expected_value, dict):
                # Complex condition
                if "operator" in expected_value:
                    op = expected_value["operator"]
                    value = expected_value["value"]
                    
                    if op == "equals":
                        if actual_value != value:
                            return False
                    elif op == "contains":
                        if value not in str(actual_value):
                            return False
                    elif op == "greater_than":
                        if actual_value <= value:
                            return False
                    elif op == "less_than":
                        if actual_value >= value:
                            return False
            else:
                # Simple equality check
                if actual_value != expected_value:
                    return False
        
        return True


@dataclass
class ExecutionPlan:
    """A complete execution plan with multiple steps."""
    
    goal: str
    steps: List[PlanStep] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    total_steps: int = 0
    completed_steps: int = 0
    
    def add_step(self, step: PlanStep) -> None:
        """Add a step to the plan."""
        self.steps.append(step)
        self.total_steps = len(self.steps)
    
    def get_ready_steps(self) -> List[PlanStep]:
        """Get all steps ready for execution."""
        completed_ids = [
            step.id for step in self.steps 
            if step.status == PlanStatus.COMPLETED
        ]
        
        ready_steps = []
        for step in self.steps:
            if (step.status == PlanStatus.PENDING and 
                step.is_ready(completed_ids) and
                step.should_execute(self.context)):
                ready_steps.append(step)
        
        return ready_steps
    
    def update_context(self, key: str, value: Any) -> None:
        """Update execution context."""
        self.context[key] = value
    
    def get_status(self) -> Dict[str, Any]:
        """Get plan execution status."""
        status_counts = {status: 0 for status in PlanStatus}
        for step in self.steps:
            status_counts[step.status] += 1
        
        return {
            "goal": self.goal,
            "total_steps": self.total_steps,
            "completed_steps": status_counts[PlanStatus.COMPLETED],
            "failed_steps": status_counts[PlanStatus.FAILED],
            "pending_steps": status_counts[PlanStatus.PENDING],
            "in_progress_steps": status_counts[PlanStatus.IN_PROGRESS],
            "skipped_steps": status_counts[PlanStatus.SKIPPED],
            "progress_percentage": (
                status_counts[PlanStatus.COMPLETED] / self.total_steps * 100
                if self.total_steps > 0 else 0
            )
        }


class TaskPlanner:
    """Dynamic task planning system with goal decomposition."""
    
    def __init__(
        self,
        planning_agent: Optional[LiteAgent] = None,
        max_planning_time: float = 5.0,
        enable_reasoning: bool = True,
        max_steps: int = 20
    ):
        """Initialize task planner.
        
        Args:
            planning_agent: Agent to use for planning (creates default if None)
            max_planning_time: Maximum time for planning in seconds
            enable_reasoning: Enable reasoning chains
            max_steps: Maximum steps in a plan
        """
        self.planning_agent = planning_agent or self._create_default_planner()
        self.max_planning_time = max_planning_time
        self.enable_reasoning = enable_reasoning
        self.max_steps = max_steps
        
        # Planning metrics
        self._planning_times = []
        self._plan_success_rate = []
    
    def _create_default_planner(self) -> LiteAgent:
        """Create default planning agent."""
        return LiteAgent(
            role="Strategic Planner",
            goal="Create detailed execution plans for complex goals",
            backstory="""Expert in breaking down complex goals into actionable steps. 
            Skilled at identifying dependencies, prerequisites, and optimal execution order.""",
            verbose=False
        )
    
    def create_plan(
        self,
        goal: str,
        available_agents: List[LiteAgent],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """Create an execution plan for a goal.
        
        Args:
            goal: The goal to achieve
            available_agents: List of available agents
            context: Initial context
            
        Returns:
            ExecutionPlan with steps
        """
        start_time = time.perf_counter()
        
        # Create planning prompt
        agent_descriptions = "\n".join([
            f"- {agent.role}: {agent.goal}"
            for agent in available_agents
        ])
        
        planning_prompt = f"""
        Goal: {goal}
        
        Available agents:
        {agent_descriptions}
        
        Create a detailed step-by-step plan to achieve this goal.
        For each step, specify:
        1. A clear description of what needs to be done
        2. Which agent should perform it
        3. Any dependencies on previous steps
        4. Expected output
        
        Format your response as a JSON array of steps:
        [
            {{
                "id": "step_1",
                "description": "Research the topic",
                "agent_role": "Researcher",
                "dependencies": [],
                "expected_output": "Comprehensive research findings"
            }},
            ...
        ]
        
        Keep the plan focused and efficient. Maximum {self.max_steps} steps.
        """
        
        # Get plan from planning agent
        response = self.planning_agent.execute(planning_prompt)
        
        # Parse plan
        plan = ExecutionPlan(goal=goal, context=context or {})
        
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                steps_data = json.loads(json_match.group())
            else:
                # Fallback: create a simple plan
                steps_data = [
                    {
                        "id": "step_1",
                        "description": goal,
                        "agent_role": available_agents[0].role if available_agents else "Agent",
                        "dependencies": [],
                        "expected_output": "Task completed"
                    }
                ]
            
            # Create plan steps
            agent_map = {agent.role: agent for agent in available_agents}
            
            for step_data in steps_data[:self.max_steps]:
                step = PlanStep(
                    id=step_data.get("id", f"step_{len(plan.steps) + 1}"),
                    description=step_data.get("description", ""),
                    goal=step_data.get("goal", step_data.get("description", "")),
                    agent=agent_map.get(step_data.get("agent_role")),
                    dependencies=step_data.get("dependencies", []),
                    expected_output=step_data.get("expected_output", ""),
                    reasoning=step_data.get("reasoning", "")
                )
                plan.add_step(step)
                
        except (json.JSONDecodeError, KeyError) as e:
            # Create fallback single-step plan
            step = PlanStep(
                id="step_1",
                description=goal,
                goal=goal,
                agent=available_agents[0] if available_agents else None,
                expected_output="Goal achieved"
            )
            plan.add_step(step)
        
        # Add reasoning if enabled
        if self.enable_reasoning:
            self._add_reasoning_to_plan(plan)
        
        # Track planning time
        planning_time = time.perf_counter() - start_time
        self._planning_times.append(planning_time)
        
        return plan
    
    def _add_reasoning_to_plan(self, plan: ExecutionPlan) -> None:
        """Add reasoning chains to plan steps."""
        for i, step in enumerate(plan.steps):
            if not step.reasoning:
                # Generate reasoning for the step
                reasoning_prompt = f"""
                For the following step in a plan to achieve "{plan.goal}":
                
                Step: {step.description}
                Dependencies: {step.dependencies}
                
                Provide a brief reasoning for:
                1. Why this step is necessary
                2. What it contributes to the overall goal
                3. Any risks or considerations
                
                Keep it concise (2-3 sentences).
                """
                
                reasoning = self.planning_agent.execute(reasoning_prompt)
                step.reasoning = reasoning.strip()
    
    def validate_plan(self, plan: ExecutionPlan) -> Tuple[bool, List[str]]:
        """Validate a plan for correctness.
        
        Args:
            plan: Plan to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for circular dependencies
        for step in plan.steps:
            if step.id in step.dependencies:
                issues.append(f"Step {step.id} depends on itself")
            
            # Check dependencies exist
            step_ids = [s.id for s in plan.steps]
            for dep in step.dependencies:
                if dep not in step_ids:
                    issues.append(f"Step {step.id} depends on non-existent step {dep}")
        
        # Check for unreachable steps
        completed = set()
        changed = True
        while changed:
            changed = False
            for step in plan.steps:
                if step.id not in completed and step.is_ready(list(completed)):
                    completed.add(step.id)
                    changed = True
        
        unreachable = [s.id for s in plan.steps if s.id not in completed]
        if unreachable:
            issues.append(f"Unreachable steps: {unreachable}")
        
        # Check agent assignments
        for step in plan.steps:
            if step.agent is None:
                issues.append(f"Step {step.id} has no assigned agent")
        
        return len(issues) == 0, issues
    
    def optimize_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize a plan for better execution.
        
        Args:
            plan: Plan to optimize
            
        Returns:
            Optimized plan
        """
        # Identify steps that can be parallelized
        parallel_groups = []
        processed = set()
        
        for step in plan.steps:
            if step.id in processed:
                continue
            
            # Find all steps with same dependencies
            group = [step]
            for other in plan.steps:
                if (other.id != step.id and 
                    other.id not in processed and
                    set(other.dependencies) == set(step.dependencies)):
                    group.append(other)
                    processed.add(other.id)
            
            processed.add(step.id)
            if len(group) > 1:
                parallel_groups.append(group)
        
        # Add parallel execution hints to context
        if parallel_groups:
            plan.context["parallel_groups"] = [
                [s.id for s in group] for group in parallel_groups
            ]
        
        return plan
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get planner metrics."""
        if not self._planning_times:
            return {
                "avg_planning_time": 0,
                "total_plans_created": 0,
                "success_rate": 0
            }
        
        return {
            "avg_planning_time": sum(self._planning_times) / len(self._planning_times),
            "max_planning_time": max(self._planning_times),
            "min_planning_time": min(self._planning_times),
            "total_plans_created": len(self._planning_times),
            "success_rate": (
                sum(self._plan_success_rate) / len(self._plan_success_rate)
                if self._plan_success_rate else 0
            )
        }


class ReasoningEngine:
    """Reasoning system for complex decision making."""
    
    def __init__(self, reasoning_agent: Optional[LiteAgent] = None):
        """Initialize reasoning engine.
        
        Args:
            reasoning_agent: Agent for reasoning (creates default if None)
        """
        self.reasoning_agent = reasoning_agent or self._create_default_reasoner()
    
    def _create_default_reasoner(self) -> LiteAgent:
        """Create default reasoning agent."""
        return LiteAgent(
            role="Reasoning Specialist",
            goal="Analyze situations and provide logical reasoning",
            backstory="Expert in logical analysis, critical thinking, and decision making.",
            verbose=False
        )
    
    def reason_about_step(
        self,
        step: PlanStep,
        context: Dict[str, Any],
        previous_results: List[Any]
    ) -> Dict[str, Any]:
        """Reason about a specific step execution.
        
        Args:
            step: Step to reason about
            context: Current context
            previous_results: Results from previous steps
            
        Returns:
            Reasoning analysis
        """
        reasoning_prompt = f"""
        Analyze the following step:
        
        Step: {step.description}
        Goal: {step.goal}
        Context: {json.dumps(context, indent=2)}
        Previous results: {previous_results[-3:] if previous_results else "None"}
        
        Provide:
        1. Should this step be executed? (yes/no)
        2. Any adjustments needed to the approach?
        3. Potential risks or issues
        4. Expected success probability (0-1)
        
        Format as JSON.
        """
        
        response = self.reasoning_agent.execute(reasoning_prompt)
        
        try:
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Default reasoning
        return {
            "should_execute": True,
            "adjustments": None,
            "risks": [],
            "success_probability": 0.8
        }
    
    def analyze_failure(
        self,
        step: PlanStep,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze why a step failed.
        
        Args:
            step: Failed step
            error: Exception that occurred
            context: Execution context
            
        Returns:
            Failure analysis
        """
        analysis_prompt = f"""
        A step failed during execution:
        
        Step: {step.description}
        Error: {str(error)}
        Context: {json.dumps(context, indent=2)}
        
        Analyze:
        1. Root cause of failure
        2. Whether to retry (yes/no)
        3. Alternative approaches
        4. How to prevent this in future
        
        Be concise and actionable.
        """
        
        response = self.reasoning_agent.execute(analysis_prompt)
        
        return {
            "root_cause": "Analysis provided by reasoning agent",
            "analysis": response,
            "should_retry": "retry" in response.lower(),
            "timestamp": time.time()
        }