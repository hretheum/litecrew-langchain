"""
Human-in-the-loop interaction system for LiteCrew.

Provides approval flows, feedback collection, and human intervention capabilities.
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from litecrew.agent import Agent as LiteAgent
from litecrew.task import LiteTask, TaskOutput


class ApprovalStatus(Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    TIMEOUT = "timeout"


class InterventionType(Enum):
    """Types of human intervention."""
    APPROVAL = "approval"
    FEEDBACK = "feedback"
    CORRECTION = "correction"
    GUIDANCE = "guidance"
    REVIEW = "review"


@dataclass
class ApprovalRequest:
    """A request for human approval."""
    
    id: str
    request_type: InterventionType
    component: str  # Agent or task requesting approval
    content: str  # What needs approval
    context: Dict[str, Any] = field(default_factory=dict)
    options: List[str] = field(default_factory=list)
    timeout: Optional[float] = None
    
    # Response tracking
    status: ApprovalStatus = ApprovalStatus.PENDING
    response: Optional[str] = None
    response_time: Optional[float] = None
    responder: Optional[str] = None
    
    def approve(self, responder: str = "human") -> None:
        """Approve the request."""
        self.status = ApprovalStatus.APPROVED
        self.response = "Approved"
        self.response_time = time.time()
        self.responder = responder
    
    def reject(self, reason: str, responder: str = "human") -> None:
        """Reject the request."""
        self.status = ApprovalStatus.REJECTED
        self.response = reason
        self.response_time = time.time()
        self.responder = responder
    
    def modify(self, new_content: str, responder: str = "human") -> None:
        """Modify the request content."""
        self.status = ApprovalStatus.MODIFIED
        self.response = new_content
        self.response_time = time.time()
        self.responder = responder


@dataclass
class HumanFeedback:
    """Human feedback on agent/task performance."""
    
    id: str
    component: str
    feedback_type: str  # "quality", "accuracy", "helpfulness", etc.
    rating: Optional[float] = None  # 0-1 scale
    comment: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "component": self.component,
            "feedback_type": self.feedback_type,
            "rating": self.rating,
            "comment": self.comment,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp
        }


class HumanInterface:
    """Interface for human interaction with crews."""
    
    def __init__(
        self,
        approval_handler: Optional[Callable] = None,
        feedback_handler: Optional[Callable] = None,
        auto_approve: bool = False,
        default_timeout: float = 300.0  # 5 minutes
    ):
        """Initialize human interface.
        
        Args:
            approval_handler: Custom approval handler function
            feedback_handler: Custom feedback handler function
            auto_approve: Automatically approve all requests
            default_timeout: Default timeout for approvals
        """
        self.approval_handler = approval_handler or self._default_approval_handler
        self.feedback_handler = feedback_handler or self._default_feedback_handler
        self.auto_approve = auto_approve
        self.default_timeout = default_timeout
        
        # Request tracking
        self._pending_approvals: Dict[str, ApprovalRequest] = {}
        self._approval_history: List[ApprovalRequest] = []
        self._feedback_history: List[HumanFeedback] = []
        
        # Async support
        self._approval_queue: asyncio.Queue = None
        self._response_futures: Dict[str, asyncio.Future] = {}
    
    def request_approval(
        self,
        component: str,
        content: str,
        request_type: InterventionType = InterventionType.APPROVAL,
        context: Optional[Dict[str, Any]] = None,
        options: Optional[List[str]] = None,
        timeout: Optional[float] = None
    ) -> ApprovalRequest:
        """Request human approval.
        
        Args:
            component: Component requesting approval
            content: Content to approve
            request_type: Type of intervention needed
            context: Additional context
            options: Available options for response
            timeout: Timeout for approval
            
        Returns:
            ApprovalRequest object
        """
        import uuid
        
        request = ApprovalRequest(
            id=str(uuid.uuid4()),
            request_type=request_type,
            component=component,
            content=content,
            context=context or {},
            options=options or ["approve", "reject", "modify"],
            timeout=timeout or self.default_timeout
        )
        
        # Add to pending
        self._pending_approvals[request.id] = request
        
        # Handle auto-approval
        if self.auto_approve:
            request.approve("auto")
            self._complete_approval(request)
            return request
        
        # Process approval
        self._process_approval(request)
        
        return request
    
    def wait_for_approval(
        self,
        request: ApprovalRequest,
        timeout: Optional[float] = None
    ) -> ApprovalRequest:
        """Wait for approval response.
        
        Args:
            request: Approval request to wait for
            timeout: Maximum wait time
            
        Returns:
            Updated approval request
        """
        timeout = timeout or request.timeout or self.default_timeout
        start_time = time.time()
        
        while request.status == ApprovalStatus.PENDING:
            if time.time() - start_time > timeout:
                request.status = ApprovalStatus.TIMEOUT
                self._complete_approval(request)
                break
            
            time.sleep(0.1)  # Poll interval
        
        return request
    
    async def request_approval_async(
        self,
        component: str,
        content: str,
        **kwargs
    ) -> ApprovalRequest:
        """Request approval asynchronously.
        
        Args:
            component: Component requesting approval
            content: Content to approve
            **kwargs: Additional arguments for request_approval
            
        Returns:
            ApprovalRequest object
        """
        # Initialize async queue if needed
        if self._approval_queue is None:
            self._approval_queue = asyncio.Queue()
        
        # Create request
        request = self.request_approval(component, content, **kwargs)
        
        # Create future for response
        future = asyncio.Future()
        self._response_futures[request.id] = future
        
        # Wait for response
        await future
        
        return request
    
    def provide_feedback(
        self,
        component: str,
        feedback_type: str,
        rating: Optional[float] = None,
        comment: Optional[str] = None,
        suggestions: Optional[List[str]] = None
    ) -> HumanFeedback:
        """Provide feedback on component performance.
        
        Args:
            component: Component to provide feedback for
            feedback_type: Type of feedback
            rating: Rating (0-1 scale)
            comment: Text comment
            suggestions: List of suggestions
            
        Returns:
            HumanFeedback object
        """
        import uuid
        
        feedback = HumanFeedback(
            id=str(uuid.uuid4()),
            component=component,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            suggestions=suggestions or []
        )
        
        # Store feedback
        self._feedback_history.append(feedback)
        
        # Process feedback
        self.feedback_handler(feedback)
        
        return feedback
    
    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        return [
            req for req in self._pending_approvals.values()
            if req.status == ApprovalStatus.PENDING
        ]
    
    def respond_to_approval(
        self,
        request_id: str,
        action: str,
        response: Optional[str] = None,
        responder: str = "human"
    ) -> bool:
        """Respond to an approval request.
        
        Args:
            request_id: ID of the request
            action: Action to take ("approve", "reject", "modify")
            response: Response content (for reject/modify)
            responder: Who is responding
            
        Returns:
            True if successful
        """
        request = self._pending_approvals.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        
        if action == "approve":
            request.approve(responder)
        elif action == "reject":
            request.reject(response or "Rejected", responder)
        elif action == "modify":
            request.modify(response or request.content, responder)
        else:
            return False
        
        self._complete_approval(request)
        return True
    
    def get_approval_history(
        self,
        component: Optional[str] = None,
        status: Optional[ApprovalStatus] = None,
        limit: int = 100
    ) -> List[ApprovalRequest]:
        """Get approval history.
        
        Args:
            component: Filter by component
            status: Filter by status
            limit: Maximum results
            
        Returns:
            List of approval requests
        """
        history = self._approval_history
        
        if component:
            history = [r for r in history if r.component == component]
        
        if status:
            history = [r for r in history if r.status == status]
        
        return history[-limit:]
    
    def get_feedback_history(
        self,
        component: Optional[str] = None,
        feedback_type: Optional[str] = None,
        limit: int = 100
    ) -> List[HumanFeedback]:
        """Get feedback history.
        
        Args:
            component: Filter by component
            feedback_type: Filter by type
            limit: Maximum results
            
        Returns:
            List of feedback entries
        """
        history = self._feedback_history
        
        if component:
            history = [f for f in history if f.component == component]
        
        if feedback_type:
            history = [f for f in history if f.feedback_type == feedback_type]
        
        return history[-limit:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get human interaction metrics."""
        total_approvals = len(self._approval_history)
        
        if total_approvals == 0:
            return {
                "total_approvals": 0,
                "approval_rate": 0,
                "avg_response_time": 0,
                "total_feedback": len(self._feedback_history)
            }
        
        # Calculate metrics
        approved = sum(1 for r in self._approval_history if r.status == ApprovalStatus.APPROVED)
        response_times = [
            r.response_time - r.context.get("request_time", r.response_time)
            for r in self._approval_history
            if r.response_time and r.status != ApprovalStatus.TIMEOUT
        ]
        
        return {
            "total_approvals": total_approvals,
            "approval_rate": approved / total_approvals,
            "rejection_rate": sum(1 for r in self._approval_history if r.status == ApprovalStatus.REJECTED) / total_approvals,
            "timeout_rate": sum(1 for r in self._approval_history if r.status == ApprovalStatus.TIMEOUT) / total_approvals,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "total_feedback": len(self._feedback_history),
            "avg_rating": sum(f.rating for f in self._feedback_history if f.rating) / len([f for f in self._feedback_history if f.rating]) if any(f.rating for f in self._feedback_history) else 0
        }
    
    def _process_approval(self, request: ApprovalRequest) -> None:
        """Process an approval request."""
        # Add request timestamp
        request.context["request_time"] = time.time()
        
        # Call approval handler
        self.approval_handler(request)
    
    def _complete_approval(self, request: ApprovalRequest) -> None:
        """Complete an approval request."""
        # Move to history
        if request.id in self._pending_approvals:
            del self._pending_approvals[request.id]
        self._approval_history.append(request)
        
        # Complete async future if exists
        if request.id in self._response_futures:
            future = self._response_futures.pop(request.id)
            if not future.done():
                future.set_result(request)
    
    def _default_approval_handler(self, request: ApprovalRequest) -> None:
        """Default approval handler (console-based)."""
        print(f"\n{'='*60}")
        print(f"APPROVAL REQUEST: {request.request_type.value}")
        print(f"{'='*60}")
        print(f"Component: {request.component}")
        print(f"Content: {request.content}")
        
        if request.context:
            print(f"Context: {json.dumps(request.context, indent=2)}")
        
        if request.options:
            print(f"Options: {', '.join(request.options)}")
        
        print(f"{'='*60}")
        print(f"Request ID: {request.id}")
        print("Use respond_to_approval() to respond")
    
    def _default_feedback_handler(self, feedback: HumanFeedback) -> None:
        """Default feedback handler."""
        # Just store feedback, no additional processing
        pass


class HumanAgent(LiteAgent):
    """Special agent that requires human input for tasks."""
    
    def __init__(
        self,
        interface: HumanInterface,
        role: str = "Human Expert",
        goal: str = "Provide human expertise and judgment",
        backstory: str = "A human expert providing guidance and decisions",
        **kwargs
    ):
        """Initialize human agent.
        
        Args:
            interface: Human interface for interactions
            role: Agent role
            goal: Agent goal
            backstory: Agent backstory
            **kwargs: Additional agent parameters
        """
        super().__init__(role=role, goal=goal, backstory=backstory, **kwargs)
        self.interface = interface
    
    def execute_task(self, task: LiteTask, context: str) -> TaskOutput:
        """Execute task with human input.
        
        Args:
            task: Task to execute
            context: Execution context
            
        Returns:
            Task output
        """
        # Request human input
        request = self.interface.request_approval(
            component=f"agent_{self.role}",
            content=f"Task: {task.description}\nExpected Output: {task.expected_output}\nContext: {context}",
            request_type=InterventionType.GUIDANCE,
            context={
                "task_id": getattr(task, "id", "unknown"),
                "task_description": task.description
            }
        )
        
        # Wait for response
        request = self.interface.wait_for_approval(request)
        
        # Generate output based on response
        if request.status == ApprovalStatus.APPROVED:
            output = task.expected_output
        elif request.status == ApprovalStatus.MODIFIED:
            output = request.response
        elif request.status == ApprovalStatus.REJECTED:
            output = f"Task rejected: {request.response}"
        else:
            output = "No human response received"
        
        # Request feedback on output
        self.interface.provide_feedback(
            component=f"agent_{self.role}",
            feedback_type="task_completion",
            comment=f"Task completed with status: {request.status.value}"
        )
        
        return TaskOutput(
            raw=output,
            task_id=getattr(task, "id", "unknown")
        )


# Decorators for human approval
def requires_approval(
    interface: HumanInterface,
    request_type: InterventionType = InterventionType.APPROVAL
):
    """Decorator to require human approval for a function.
    
    Args:
        interface: Human interface for approval
        request_type: Type of intervention
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create approval request
            request = interface.request_approval(
                component=func.__name__,
                content=f"Execute function: {func.__name__}",
                request_type=request_type,
                context={
                    "args": str(args)[:100],
                    "kwargs": str(kwargs)[:100]
                }
            )
            
            # Wait for approval
            request = interface.wait_for_approval(request)
            
            if request.status == ApprovalStatus.APPROVED:
                return func(*args, **kwargs)
            else:
                raise RuntimeError(f"Function execution not approved: {request.response}")
        
        return wrapper
    return decorator