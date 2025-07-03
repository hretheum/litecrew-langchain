"""
Context Merging Strategies

Implements different strategies for merging and combining context data
from multiple sources while maintaining efficiency and relevance.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import re

from .shared_context import ContextMetadata


class ContextMergeStrategy(Enum):
    """Available context merging strategies."""
    CONCATENATE = "concatenate"        # Simple string joining
    SUMMARY = "summary"                # LLM-based summarization (future)
    PRIORITY = "priority"              # Keep only high-priority items
    SLIDING_WINDOW = "sliding_window"  # Keep only recent N items
    RELEVANCE = "relevance"            # Keep most relevant items
    HIERARCHICAL = "hierarchical"      # Organize by agent/task hierarchy


@dataclass
class ContextItem:
    """Context item with value and metadata."""
    key: str
    value: Any
    metadata: ContextMetadata
    
    def __str__(self) -> str:
        return str(self.value)
    
    @property
    def size_bytes(self) -> int:
        return self.metadata.size_bytes
    
    @property
    def timestamp(self) -> datetime:
        return self.metadata.timestamp
    
    @property
    def priority(self) -> int:
        return self.metadata.priority


class MergeStrategy(ABC):
    """Abstract base class for context merge strategies."""
    
    @abstractmethod
    def merge(self, contexts: List[ContextItem], max_size: Optional[int] = None) -> str:
        """
        Merge context items into a single string.
        
        Args:
            contexts: List of context items to merge
            max_size: Optional maximum size limit in bytes
            
        Returns:
            Merged context string
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass


class ConcatenateMergeStrategy(MergeStrategy):
    """
    Simple concatenation merge strategy.
    
    Joins all context items with separators in chronological order.
    """
    
    def __init__(self, separator: str = "\n\n---\n\n"):
        self.separator = separator
    
    def merge(self, contexts: List[ContextItem], max_size: Optional[int] = None) -> str:
        """Concatenate all contexts with separators."""
        if not contexts:
            return ""
        
        # Sort by timestamp
        sorted_contexts = sorted(contexts, key=lambda x: x.timestamp)
        
        # Build merged string
        parts = []
        current_size = 0
        
        for item in sorted_contexts:
            item_str = str(item.value)
            
            # Add header with metadata
            if item.metadata.agent_role:
                header = f"[{item.metadata.agent_role}] "
            else:
                header = "[Context] "
            
            if item.metadata.task_description:
                header += f"{item.metadata.task_description}"
            
            if header.strip() != "[Context]":
                item_str = f"{header}:\n{item_str}"
            
            # Check size limit
            if max_size and current_size + len(item_str) > max_size:
                break
            
            parts.append(item_str)
            current_size += len(item_str)
        
        return self.separator.join(parts)
    
    def get_strategy_name(self) -> str:
        return "concatenate"


class PriorityMergeStrategy(MergeStrategy):
    """
    Priority-based merge strategy.
    
    Keeps only high-priority context items, then fills with recent items.
    """
    
    def __init__(self, min_priority: int = 2):
        self.min_priority = min_priority
    
    def merge(self, contexts: List[ContextItem], max_size: Optional[int] = None) -> str:
        """Merge contexts by priority, then recency."""
        if not contexts:
            return ""
        
        # Separate by priority
        high_priority = [c for c in contexts if c.priority >= self.min_priority]
        low_priority = [c for c in contexts if c.priority < self.min_priority]
        
        # Sort each group by timestamp (newest first)
        high_priority.sort(key=lambda x: x.timestamp, reverse=True)
        low_priority.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Select items within size limit
        selected_items = []
        current_size = 0
        
        # Add high priority items first
        for item in high_priority:
            item_size = len(str(item.value))
            if max_size and current_size + item_size > max_size:
                break
            selected_items.append(item)
            current_size += item_size
        
        # Fill remaining space with recent low priority items
        for item in low_priority:
            item_size = len(str(item.value))
            if max_size and current_size + item_size > max_size:
                break
            selected_items.append(item)
            current_size += item_size
        
        # Sort final selection by timestamp for coherent flow
        selected_items.sort(key=lambda x: x.timestamp)
        
        # Format output
        parts = []
        for item in selected_items:
            priority_marker = "🔴" if item.priority >= 3 else "🟡" if item.priority >= 2 else "⚪"
            timestamp = item.timestamp.strftime("%H:%M")
            
            if item.metadata.agent_role:
                header = f"{priority_marker} [{timestamp}] {item.metadata.agent_role}"
            else:
                header = f"{priority_marker} [{timestamp}] Context"
            
            parts.append(f"{header}:\n{str(item.value)}")
        
        return "\n\n".join(parts)
    
    def get_strategy_name(self) -> str:
        return "priority"


class SlidingWindowMergeStrategy(MergeStrategy):
    """
    Sliding window merge strategy.
    
    Keeps only the most recent N items or items within a time window.
    """
    
    def __init__(self, window_size: int = 10, time_window_minutes: Optional[int] = None):
        self.window_size = window_size
        self.time_window_minutes = time_window_minutes
    
    def merge(self, contexts: List[ContextItem], max_size: Optional[int] = None) -> str:
        """Merge contexts using sliding window approach."""
        if not contexts:
            return ""
        
        # Sort by timestamp (newest first)
        sorted_contexts = sorted(contexts, key=lambda x: x.timestamp, reverse=True)
        
        # Apply time window filter if specified
        if self.time_window_minutes:
            cutoff_time = datetime.now() - timedelta(minutes=self.time_window_minutes)
            sorted_contexts = [c for c in sorted_contexts if c.timestamp >= cutoff_time]
        
        # Apply size window
        windowed_contexts = sorted_contexts[:self.window_size]
        
        # Apply size limit
        if max_size:
            selected_contexts = []
            current_size = 0
            
            for item in windowed_contexts:
                item_size = len(str(item.value))
                if current_size + item_size > max_size:
                    break
                selected_contexts.append(item)
                current_size += item_size
        else:
            selected_contexts = windowed_contexts
        
        # Sort back to chronological order for output
        selected_contexts.sort(key=lambda x: x.timestamp)
        
        # Format output
        parts = []
        for item in selected_contexts:
            timestamp = item.timestamp.strftime("%H:%M:%S")
            
            if item.metadata.agent_role:
                header = f"[{timestamp}] {item.metadata.agent_role}"
            else:
                header = f"[{timestamp}] Context"
            
            parts.append(f"{header}:\n{str(item.value)}")
        
        return "\n\n".join(parts)
    
    def get_strategy_name(self) -> str:
        return "sliding_window"


class RelevanceMergeStrategy(MergeStrategy):
    """
    Relevance-based merge strategy.
    
    Selects context items most relevant to a query or recent patterns.
    """
    
    def __init__(self, query: Optional[str] = None):
        self.query = query
    
    def merge(self, contexts: List[ContextItem], max_size: Optional[int] = None) -> str:
        """Merge contexts by relevance scoring."""
        if not contexts:
            return ""
        
        # Calculate relevance scores
        scored_contexts = []
        for item in contexts:
            score = self._calculate_relevance_score(item)
            scored_contexts.append((score, item))
        
        # Sort by relevance score (highest first)
        scored_contexts.sort(key=lambda x: x[0], reverse=True)
        
        # Select items within size limit
        selected_items = []
        current_size = 0
        
        for score, item in scored_contexts:
            item_size = len(str(item.value))
            if max_size and current_size + item_size > max_size:
                break
            selected_items.append((score, item))
            current_size += item_size
        
        # Sort by timestamp for coherent flow
        selected_items.sort(key=lambda x: x[1].timestamp)
        
        # Format output with relevance indicators
        parts = []
        for score, item in selected_items:
            relevance_marker = "🔥" if score >= 10 else "⭐" if score >= 5 else "💡"
            timestamp = item.timestamp.strftime("%H:%M")
            
            if item.metadata.agent_role:
                header = f"{relevance_marker} [{timestamp}] {item.metadata.agent_role}"
            else:
                header = f"{relevance_marker} [{timestamp}] Context"
            
            parts.append(f"{header}:\n{str(item.value)}")
        
        return "\n\n".join(parts)
    
    def _calculate_relevance_score(self, item: ContextItem) -> float:
        """Calculate relevance score for context item."""
        score = 0.0
        
        # Base score from priority
        score += item.priority * 2
        
        # Recent items get higher scores
        age_minutes = (datetime.now() - item.timestamp).total_seconds() / 60
        if age_minutes < 5:
            score += 5
        elif age_minutes < 30:
            score += 3
        elif age_minutes < 60:
            score += 1
        
        # Access frequency
        score += min(item.metadata.access_count / 5, 3)
        
        # Query relevance if provided
        if self.query:
            value_str = str(item.value).lower()
            query_lower = self.query.lower()
            
            # Simple keyword matching
            for term in query_lower.split():
                if term in value_str:
                    score += 2
            
            # Task description relevance
            if item.metadata.task_description:
                task_lower = item.metadata.task_description.lower()
                for term in query_lower.split():
                    if term in task_lower:
                        score += 1
        
        return score
    
    def get_strategy_name(self) -> str:
        return "relevance"


class HierarchicalMergeStrategy(MergeStrategy):
    """
    Hierarchical merge strategy.
    
    Organizes context by agent roles and task hierarchy.
    """
    
    def merge(self, contexts: List[ContextItem], max_size: Optional[int] = None) -> str:
        """Merge contexts in hierarchical structure."""
        if not contexts:
            return ""
        
        # Group by agent role
        agent_groups: Dict[str, List[ContextItem]] = {}
        ungrouped = []
        
        for item in contexts:
            if item.metadata.agent_role:
                if item.metadata.agent_role not in agent_groups:
                    agent_groups[item.metadata.agent_role] = []
                agent_groups[item.metadata.agent_role].append(item)
            else:
                ungrouped.append(item)
        
        # Sort within each group by timestamp
        for agent_role in agent_groups:
            agent_groups[agent_role].sort(key=lambda x: x.timestamp)
        
        ungrouped.sort(key=lambda x: x.timestamp)
        
        # Build hierarchical output
        sections = []
        current_size = 0
        
        # Add agent sections
        for agent_role, items in agent_groups.items():
            section_parts = [f"## {agent_role}"]
            section_size = len(section_parts[0])
            
            for item in items:
                timestamp = item.timestamp.strftime("%H:%M:%S")
                task_info = f" - {item.metadata.task_description}" if item.metadata.task_description else ""
                
                item_text = f"[{timestamp}]{task_info}:\n{str(item.value)}"
                item_size = len(item_text)
                
                if max_size and current_size + section_size + item_size > max_size:
                    break
                
                section_parts.append(item_text)
                section_size += item_size
            
            if len(section_parts) > 1:  # Only add if has content beyond header
                sections.append("\n\n".join(section_parts))
                current_size += section_size
        
        # Add ungrouped items
        if ungrouped and (not max_size or current_size < max_size):
            ungrouped_parts = ["## General Context"]
            section_size = len(ungrouped_parts[0])
            
            for item in ungrouped:
                timestamp = item.timestamp.strftime("%H:%M:%S")
                item_text = f"[{timestamp}]:\n{str(item.value)}"
                item_size = len(item_text)
                
                if max_size and current_size + section_size + item_size > max_size:
                    break
                
                ungrouped_parts.append(item_text)
                section_size += item_size
            
            if len(ungrouped_parts) > 1:
                sections.append("\n\n".join(ungrouped_parts))
        
        return "\n\n\n".join(sections)
    
    def get_strategy_name(self) -> str:
        return "hierarchical"


class ContextMerger:
    """
    Main context merger that applies different merging strategies.
    """
    
    def __init__(self):
        self.strategies = {
            ContextMergeStrategy.CONCATENATE: ConcatenateMergeStrategy(),
            ContextMergeStrategy.PRIORITY: PriorityMergeStrategy(),
            ContextMergeStrategy.SLIDING_WINDOW: SlidingWindowMergeStrategy(),
            ContextMergeStrategy.RELEVANCE: RelevanceMergeStrategy(),
            ContextMergeStrategy.HIERARCHICAL: HierarchicalMergeStrategy(),
        }
    
    def merge(self, 
              contexts: List[ContextItem], 
              strategy: ContextMergeStrategy,
              max_size: Optional[int] = None,
              **strategy_kwargs) -> str:
        """
        Merge contexts using specified strategy.
        
        Args:
            contexts: List of context items to merge
            strategy: Merge strategy to use
            max_size: Optional maximum size in bytes
            **strategy_kwargs: Additional arguments for strategy
            
        Returns:
            Merged context string
        """
        if not contexts:
            return ""
        
        # Get strategy instance
        if strategy in self.strategies:
            merger = self.strategies[strategy]
        else:
            # Fallback to concatenate
            merger = self.strategies[ContextMergeStrategy.CONCATENATE]
        
        # Apply strategy-specific configuration
        if strategy_kwargs:
            if strategy == ContextMergeStrategy.RELEVANCE and 'query' in strategy_kwargs:
                merger = RelevanceMergeStrategy(query=strategy_kwargs['query'])
            elif strategy == ContextMergeStrategy.SLIDING_WINDOW:
                window_size = strategy_kwargs.get('window_size', 10)
                time_window = strategy_kwargs.get('time_window_minutes')
                merger = SlidingWindowMergeStrategy(window_size, time_window)
        
        return merger.merge(contexts, max_size)
    
    def estimate_merged_size(self, contexts: List[ContextItem]) -> int:
        """Estimate size of merged context."""
        total_size = 0
        for item in contexts:
            total_size += len(str(item.value))
            # Add overhead for formatting
            total_size += 50  # Estimated header/separator overhead
        
        return total_size
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available merge strategy names."""
        return [strategy.value for strategy in ContextMergeStrategy]