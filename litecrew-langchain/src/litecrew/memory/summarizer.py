"""
Memory summarization for LiteCrew.
"""

from typing import List, Dict, Any, Optional
from litecrew.memory.conversation import ConversationMemory


class MemorySummarizer:
    """
    Summarizes conversation memory to reduce size while retaining information.
    """

    def __init__(self, compression_ratio: float = 0.3):
        """
        Initialize memory summarizer.

        Args:
            compression_ratio: Target compression ratio (0.3 = 30% of original size)
        """
        self.compression_ratio = compression_ratio

    def summarize(self, memory: ConversationMemory, focus: Optional[str] = None) -> str:
        """
        Summarize conversation memory.

        Args:
            memory: Conversation memory to summarize
            focus: Optional focus area for summarization

        Returns:
            Summary string
        """
        turns = memory.get_turns()

        if not turns:
            return ""

        # Simple rule-based summarization for now
        # In production, this would use an LLM
        summary_parts = []

        # Extract key information
        topics = self._extract_topics(turns)
        if topics:
            summary_parts.append(f"Topics discussed: {', '.join(topics)}")

        # Extract key facts
        facts = self._extract_facts(turns)
        if facts:
            summary_parts.append(f"Key information: {'; '.join(facts)}")

        # Extract actions/decisions
        actions = self._extract_actions(turns)
        if actions:
            summary_parts.append(f"Actions/decisions: {'; '.join(actions)}")

        # If focus provided, emphasize it
        if focus:
            focused_info = self._extract_focused_info(turns, focus)
            if focused_info:
                summary_parts.insert(0, f"Regarding {focus}: {focused_info}")

        summary = " ".join(summary_parts)

        # Ensure summary is compressed
        target_length = int(
            self._calculate_total_length(turns) * self.compression_ratio
        )
        if len(summary) > target_length:
            summary = summary[:target_length].rsplit(" ", 1)[0] + "..."

        return summary

    def incremental_summarize(
        self, existing_summary: str, new_turns: List[Dict[str, Any]]
    ) -> str:
        """
        Update existing summary with new turns.

        Args:
            existing_summary: Current summary
            new_turns: New conversation turns

        Returns:
            Updated summary
        """
        if not new_turns:
            return existing_summary

        # Extract new information
        new_info = []

        new_topics = self._extract_topics(new_turns)
        if new_topics:
            new_info.append(f"New topics: {', '.join(new_topics)}")

        new_facts = self._extract_facts(new_turns)
        if new_facts:
            new_info.append(f"Additional info: {'; '.join(new_facts)}")

        if not new_info:
            return existing_summary

        # Combine with existing summary
        if existing_summary:
            updated = f"{existing_summary} {' '.join(new_info)}"
        else:
            updated = " ".join(new_info)

        return updated

    def _extract_topics(self, turns: List[Dict[str, Any]]) -> List[str]:
        """Extract main topics from conversation."""
        topics = []

        # Simple keyword extraction
        keywords = ["about", "regarding", "concerning", "discuss", "tell me about"]

        for turn in turns:
            if turn["role"] == "user":
                content_lower = turn["content"].lower()
                for keyword in keywords:
                    if keyword in content_lower:
                        # Extract next few words as topic
                        idx = content_lower.find(keyword)
                        topic_part = turn["content"][idx + len(keyword) :].strip()
                        topic_words = topic_part.split()[:3]
                        if topic_words:
                            topic = " ".join(topic_words).rstrip("?.,!;:")
                            if len(topic) > 2:
                                topics.append(topic)

        # Deduplicate
        return list(dict.fromkeys(topics))[:5]  # Max 5 topics

    def _extract_facts(self, turns: List[Dict[str, Any]]) -> List[str]:
        """Extract key facts from conversation."""
        facts = []

        # Look for factual patterns
        fact_patterns = [
            "is",
            "are",
            "was",
            "were",
            "equals",
            "means",
            "defined as",
            "known as",
            "called",
        ]

        for turn in turns:
            if turn["role"] == "assistant":
                sentences = turn["content"].split(". ")
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    if any(pattern in sentence_lower for pattern in fact_patterns):
                        if 10 < len(sentence) < 100:  # Reasonable fact length
                            facts.append(sentence.strip())

        return facts[:5]  # Max 5 facts

    def _extract_actions(self, turns: List[Dict[str, Any]]) -> List[str]:
        """Extract actions or decisions from conversation."""
        actions = []

        # Look for action patterns
        action_patterns = [
            "will",
            "should",
            "must",
            "need to",
            "going to",
            "let's",
            "decide",
            "agreed",
            "plan to",
        ]

        for turn in turns:
            content_lower = turn["content"].lower()
            if any(pattern in content_lower for pattern in action_patterns):
                # Extract sentence containing action
                sentences = turn["content"].split(". ")
                for sentence in sentences:
                    if any(pattern in sentence.lower() for pattern in action_patterns):
                        if len(sentence) < 100:
                            actions.append(sentence.strip())

        return actions[:3]  # Max 3 actions

    def _extract_focused_info(self, turns: List[Dict[str, Any]], focus: str) -> str:
        """Extract information related to specific focus."""
        focus_lower = focus.lower()
        relevant_parts = []

        for turn in turns:
            if focus_lower in turn["content"].lower():
                # Extract sentence containing focus
                sentences = turn["content"].split(". ")
                for sentence in sentences:
                    if focus_lower in sentence.lower():
                        relevant_parts.append(sentence.strip())

        if relevant_parts:
            return "; ".join(relevant_parts[:3])
        return ""

    def _calculate_total_length(self, turns: List[Dict[str, Any]]) -> int:
        """Calculate total length of all turns."""
        return sum(len(turn["content"]) for turn in turns)

    def estimate_summary_quality(
        self, summary: str, original_turns: List[Dict[str, Any]]
    ) -> float:
        """
        Estimate quality of summary (0-1 score).

        Args:
            summary: Generated summary
            original_turns: Original conversation turns

        Returns:
            Quality score between 0 and 1
        """
        if not summary or not original_turns:
            return 0.0

        # Calculate information retention
        summary_lower = summary.lower()
        retained_info = 0
        total_info = 0

        # Check topic retention
        topics = self._extract_topics(original_turns)
        for topic in topics:
            total_info += 1
            if topic.lower() in summary_lower:
                retained_info += 1

        # Check fact retention
        facts = self._extract_facts(original_turns)
        for fact in facts:
            total_info += 1
            # Check if key words from fact are in summary
            key_words = [w for w in fact.split() if len(w) > 4][:3]
            if any(word.lower() in summary_lower for word in key_words):
                retained_info += 1

        if total_info == 0:
            return 1.0  # No extractable info, any summary is fine

        return retained_info / total_info
