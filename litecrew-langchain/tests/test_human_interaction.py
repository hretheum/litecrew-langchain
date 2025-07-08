"""
Tests for Human-in-the-loop interaction system.
"""

import asyncio
import time
from unittest.mock import MagicMock, patch

import pytest

from litecrew.task import LiteTask, TaskOutput
from litecrew.human.interaction import (
    ApprovalRequest,
    ApprovalStatus,
    HumanAgent,
    HumanFeedback,
    HumanInterface,
    InterventionType,
    requires_approval,
)


class TestApprovalRequest:
    """Test ApprovalRequest functionality."""
    
    def test_approval_request_creation(self):
        """Test creating approval requests."""
        request = ApprovalRequest(
            id="test-123",
            request_type=InterventionType.APPROVAL,
            component="test_agent",
            content="Please approve this action",
            context={"task": "important_task"},
            options=["approve", "reject"],
            timeout=60.0
        )
        
        assert request.status == ApprovalStatus.PENDING
        assert request.component == "test_agent"
        assert "task" in request.context
    
    def test_approval_actions(self):
        """Test approval request actions."""
        request = ApprovalRequest(
            id="test-456",
            request_type=InterventionType.REVIEW,
            component="reviewer",
            content="Review this output"
        )
        
        # Test approve
        request.approve("john")
        assert request.status == ApprovalStatus.APPROVED
        assert request.response == "Approved"
        assert request.responder == "john"
        assert request.response_time is not None
        
        # Reset and test reject
        request.status = ApprovalStatus.PENDING
        request.reject("Not ready", "jane")
        assert request.status == ApprovalStatus.REJECTED
        assert request.response == "Not ready"
        assert request.responder == "jane"
        
        # Reset and test modify
        request.status = ApprovalStatus.PENDING
        request.modify("Modified content", "admin")
        assert request.status == ApprovalStatus.MODIFIED
        assert request.response == "Modified content"
        assert request.responder == "admin"


class TestHumanInterface:
    """Test HumanInterface functionality."""
    
    @pytest.fixture
    def interface(self):
        """Create test interface."""
        return HumanInterface(auto_approve=False, default_timeout=1.0)
    
    @pytest.fixture
    def auto_interface(self):
        """Create auto-approving interface."""
        return HumanInterface(auto_approve=True)
    
    def test_request_approval(self, interface):
        """Test basic approval request."""
        request = interface.request_approval(
            component="test_component",
            content="Test approval needed",
            request_type=InterventionType.APPROVAL,
            context={"priority": "high"}
        )
        
        assert request.id in interface._pending_approvals
        assert request.status == ApprovalStatus.PENDING
        assert len(interface.get_pending_approvals()) == 1
    
    def test_auto_approval(self, auto_interface):
        """Test automatic approval."""
        request = auto_interface.request_approval(
            component="test",
            content="Auto approve this"
        )
        
        assert request.status == ApprovalStatus.APPROVED
        assert request.responder == "auto"
        assert len(auto_interface._approval_history) == 1
        assert len(auto_interface.get_pending_approvals()) == 0
    
    def test_respond_to_approval(self, interface):
        """Test responding to approvals."""
        request = interface.request_approval(
            component="test",
            content="Approve me"
        )
        
        # Test approve
        success = interface.respond_to_approval(
            request.id,
            "approve",
            responder="tester"
        )
        
        assert success
        assert request.status == ApprovalStatus.APPROVED
        assert len(interface._approval_history) == 1
        
        # Test invalid response
        success = interface.respond_to_approval(
            "invalid-id",
            "approve"
        )
        assert not success
    
    def test_approval_timeout(self, interface):
        """Test approval timeout."""
        request = interface.request_approval(
            component="test",
            content="Will timeout",
            timeout=0.1
        )
        
        # Wait for timeout
        request = interface.wait_for_approval(request, timeout=0.2)
        
        assert request.status == ApprovalStatus.TIMEOUT
        assert len(interface._approval_history) == 1
    
    def test_provide_feedback(self, interface):
        """Test feedback provision."""
        feedback = interface.provide_feedback(
            component="test_agent",
            feedback_type="quality",
            rating=0.9,
            comment="Excellent work",
            suggestions=["Keep it up"]
        )
        
        assert feedback.component == "test_agent"
        assert feedback.rating == 0.9
        assert len(interface._feedback_history) == 1
    
    def test_approval_history(self, interface):
        """Test approval history retrieval."""
        # Create multiple requests
        for i in range(5):
            req = interface.request_approval(
                component=f"component_{i % 2}",
                content=f"Request {i}"
            )
            if i < 3:
                interface.respond_to_approval(req.id, "approve")
            else:
                interface.respond_to_approval(req.id, "reject")
        
        # Test filtering
        all_history = interface.get_approval_history()
        assert len(all_history) == 5
        
        component_history = interface.get_approval_history(component="component_0")
        assert len(component_history) == 3
        
        approved_history = interface.get_approval_history(status=ApprovalStatus.APPROVED)
        assert len(approved_history) == 3
    
    def test_metrics(self, interface):
        """Test metrics calculation."""
        # Create some approval history
        for i in range(10):
            req = interface.request_approval(
                component="test",
                content=f"Request {i}"
            )
            
            if i < 6:
                interface.respond_to_approval(req.id, "approve")
            elif i < 8:
                interface.respond_to_approval(req.id, "reject")
            # else: let timeout
        
        # Add feedback
        for i in range(5):
            interface.provide_feedback(
                component="test",
                feedback_type="quality",
                rating=0.8 + i * 0.05
            )
        
        metrics = interface.get_metrics()
        
        assert metrics["total_approvals"] == 10
        assert metrics["approval_rate"] == 0.6
        assert metrics["rejection_rate"] == 0.2
        assert metrics["timeout_rate"] == 0.2
        assert metrics["total_feedback"] == 5
        assert 0.9 <= metrics["avg_rating"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_async_approval(self, interface):
        """Test asynchronous approval request."""
        # Start approval request
        request_task = asyncio.create_task(
            interface.request_approval_async(
                component="async_test",
                content="Async approval"
            )
        )
        
        # Give it time to register
        await asyncio.sleep(0.1)
        
        # Respond to approval
        pending = interface.get_pending_approvals()
        assert len(pending) == 1
        
        interface.respond_to_approval(
            pending[0].id,
            "approve"
        )
        
        # Wait for completion
        request = await request_task
        assert request.status == ApprovalStatus.APPROVED


class TestHumanAgent:
    """Test HumanAgent functionality."""
    
    @pytest.fixture
    def human_agent(self):
        """Create human agent with auto-approve interface."""
        interface = HumanInterface(auto_approve=True)
        return HumanAgent(interface=interface)
    
    def test_human_agent_creation(self, human_agent):
        """Test human agent initialization."""
        assert human_agent.role == "Human Expert"
        assert human_agent.interface is not None
        assert human_agent.interface.auto_approve
    
    def test_human_agent_task_execution(self, human_agent):
        """Test task execution with human input."""
        task = LiteTask(
            description="Review this document",
            agent=human_agent,
            expected_output="Document reviewed"
        )
        
        # Execute task (auto-approved)
        output = human_agent.execute_task(task, "Test context")
        
        assert isinstance(output, TaskOutput)
        assert output.raw == "Document reviewed"
        
        # Check feedback was provided
        feedback_history = human_agent.interface.get_feedback_history()
        assert len(feedback_history) == 1
        assert feedback_history[0].feedback_type == "task_completion"
    
    def test_human_agent_rejection(self):
        """Test human agent with rejection."""
        # Create interface with custom handler
        def reject_handler(request):
            # Immediately reject
            request.reject("Not approved", "test")
        
        interface = HumanInterface(
            approval_handler=reject_handler,
            auto_approve=False
        )
        agent = HumanAgent(interface=interface)
        
        task = LiteTask(
            description="Do something",
            agent=agent,
            expected_output="Done"
        )
        
        output = agent.execute_task(task, "context")
        assert "rejected" in output.raw.lower()
    
    def test_human_agent_modification(self):
        """Test human agent with modification."""
        # Create interface with custom handler
        def modify_handler(request):
            # Modify the response
            request.modify("Modified output", "test")
        
        interface = HumanInterface(
            approval_handler=modify_handler,
            auto_approve=False
        )
        agent = HumanAgent(interface=interface)
        
        task = LiteTask(
            description="Generate text",
            agent=agent,
            expected_output="Original output"
        )
        
        output = agent.execute_task(task, "context")
        assert output.raw == "Modified output"


class TestRequiresApprovalDecorator:
    """Test requires_approval decorator."""
    
    def test_decorator_approval(self):
        """Test decorator with approval."""
        interface = HumanInterface(auto_approve=True)
        
        @requires_approval(interface)
        def sensitive_function(x, y):
            return x + y
        
        result = sensitive_function(2, 3)
        assert result == 5
        
        # Check approval was requested
        history = interface.get_approval_history()
        assert len(history) == 1
        assert history[0].component == "sensitive_function"
    
    def test_decorator_rejection(self):
        """Test decorator with rejection."""
        interface = HumanInterface(auto_approve=False)
        
        # Set up rejection
        @requires_approval(interface, InterventionType.REVIEW)
        def protected_function():
            return "Should not execute"
        
        # Mock rejection
        def reject_all(request):
            interface.respond_to_approval(request.id, "reject", "Denied")
        
        interface.approval_handler = reject_all
        
        # Should raise error
        with pytest.raises(RuntimeError, match="not approved"):
            protected_function()
    
    def test_decorator_with_args(self):
        """Test decorator preserves function arguments."""
        interface = HumanInterface(auto_approve=True)
        
        @requires_approval(interface)
        def function_with_args(name, value=10, **kwargs):
            return f"{name}: {value}, extra: {kwargs}"
        
        result = function_with_args("test", value=20, extra="data")
        assert "test: 20" in result
        assert "extra: {'extra': 'data'}" in result