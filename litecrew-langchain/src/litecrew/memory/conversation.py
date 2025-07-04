"""
Conversation memory implementation for LiteCrew.
"""

from collections import deque
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class ConversationMemory:
    """
    Short-term conversation memory with size limits and persistence hooks.
    """

    def __init__(
        self,
        max_size: int = 100,
        summarize_after: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize conversation memory.

        Args:
            max_size: Maximum number of turns to keep
            summarize_after: Trigger summarization after this many turns
            metadata: Additional metadata to store
        """
        self.max_size = max_size
        self.summarize_after = summarize_after
        self._turns: deque = deque(maxlen=max_size)
        self._metadata = metadata or {}
        self._summary: Optional[str] = None
        self._save_hook: Optional[Callable] = None
        self._load_hook: Optional[Callable] = None

    def add_turn(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a conversation turn.

        Args:
            role: Speaker role (user, assistant, system)
            content: Message content
            metadata: Optional turn metadata
        """
        turn = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        self._turns.append(turn)

        # Check if summarization needed
        if self.summarize_after and len(self._turns) >= self.summarize_after:
            self._trigger_summarization()

    def get_turns(self, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation turns.

        Args:
            last_n: Return only last N turns

        Returns:
            List of conversation turns
        """
        turns = list(self._turns)
        if last_n:
            return turns[-last_n:]
        return turns

    def build_context(self, max_tokens: Optional[int] = None) -> str:
        """
        Build context string from memory.

        Args:
            max_tokens: Maximum tokens to include

        Returns:
            Context string
        """
        context_parts = []

        # Include summary if available
        if self._summary:
            context_parts.append(f"Previous conversation summary: {self._summary}")

        # Add recent turns
        for turn in self._turns:
            turn_text = f"{turn['role']}: {turn['content']}"
            context_parts.append(turn_text)

        context = "\n".join(context_parts)

        # Truncate if needed (simple character-based truncation)
        if max_tokens:
            # Rough estimate: 1 token ≈ 4 characters
            max_chars = max_tokens * 4
            if len(context) > max_chars:
                context = context[-max_chars:]
                # Find first complete turn
                first_newline = context.find("\n")
                if first_newline > 0:
                    context = context[first_newline + 1 :]

        return context

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search memory for relevant turns.

        Args:
            query: Search query

        Returns:
            List of matching turns
        """
        results = []
        query_lower = query.lower()

        for turn in self._turns:
            if query_lower in turn["content"].lower():
                results.append(turn)

        return results

    def clear(self):
        """Clear all memory."""
        self._turns.clear()
        self._summary = None

    def __len__(self) -> int:
        """Get number of turns in memory."""
        return len(self._turns)

    def set_save_hook(self, hook: Callable[[Dict[str, Any]], None]):
        """Set persistence save hook."""
        self._save_hook = hook

    def set_load_hook(self, hook: Callable[[], Dict[str, Any]]):
        """Set persistence load hook."""
        self._load_hook = hook

    def save(self):
        """Save memory using configured hook."""
        if self._save_hook:
            data = self.export()
            self._save_hook(data)

    def load(self):
        """Load memory using configured hook."""
        if self._load_hook:
            data = self._load_hook()
            if data:
                self.import_data(data)

    def export(self) -> Dict[str, Any]:
        """
        Export memory to dictionary.

        Returns:
            Serializable dictionary
        """
        return {
            "turns": list(self._turns),
            "metadata": self._metadata,
            "summary": self._summary,
            "max_size": self.max_size,
            "summarize_after": self.summarize_after,
        }

    def import_data(self, data: Dict[str, Any]):
        """
        Import memory from dictionary.

        Args:
            data: Memory data to import
        """
        self._turns = deque(data.get("turns", []), maxlen=self.max_size)
        self._metadata = data.get("metadata", {})
        self._summary = data.get("summary")

    def has_summary(self) -> bool:
        """Check if memory has a summary."""
        return self._summary is not None

    def get_summary(self) -> Optional[str]:
        """Get memory summary."""
        return self._summary

    def set_summary(self, summary: str):
        """Set memory summary."""
        self._summary = summary

    def _trigger_summarization(self):
        """Trigger automatic summarization."""
        # This would be implemented with actual summarization
        # For now, just mark that summarization is needed
        if not self._summary and len(self._turns) > self.summarize_after:
            # Take first half of turns as "summarized"
            summarized_count = len(self._turns) // 2
            self._summary = f"[Summary of first {summarized_count} turns]"

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Dictionary with memory stats
        """
        return {
            "turn_count": len(self._turns),
            "max_size": self.max_size,
            "has_summary": self.has_summary(),
            "oldest_turn": self._turns[0]["timestamp"] if self._turns else None,
            "newest_turn": self._turns[-1]["timestamp"] if self._turns else None,
            "metadata": self._metadata,
        }
