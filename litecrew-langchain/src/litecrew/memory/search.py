"""
Memory search functionality for LiteCrew.
"""

import re
from collections import Counter
from typing import Any, Dict, List, Optional

from litecrew.memory.conversation import ConversationMemory


class MemorySearch:
    """
    Search functionality for conversation memory with relevance scoring.
    """

    def __init__(self) -> None:
        """Initialize memory search."""
        self._stop_words = {
            "the",
            "is",
            "at",
            "which",
            "on",
            "and",
            "a",
            "an",
            "as",
            "are",
            "was",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "shall",
            "to",
            "of",
            "in",
            "for",
            "with",
            "by",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "up",
            "down",
            "out",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "both",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "but",
            "if",
            "or",
            "because",
            "from",
            "here",
            "there",
            "these",
            "those",
            "this",
            "that",
            "it",
            "its",
            "you",
            "your",
            "i",
            "me",
            "my",
            "we",
            "our",
            "they",
            "them",
        }

    def search(
        self,
        memory: ConversationMemory,
        query: str,
        top_k: Optional[int] = None,
        min_score: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """
        Search memory for relevant turns.

        Args:
            memory: Conversation memory to search
            query: Search query
            top_k: Return only top K results
            min_score: Minimum relevance score

        Returns:
            List of matching turns with relevance scores
        """
        if not query:
            return []

        # Tokenize and clean query
        query_tokens = self._tokenize(query.lower())
        query_tokens = [t for t in query_tokens if t not in self._stop_words]

        if not query_tokens:
            return []

        # Score each turn
        scored_turns = []
        turns = memory.get_turns()

        for i, turn in enumerate(turns):
            score = self._score_turn(turn, query_tokens)
            if score >= min_score:
                result = turn.copy()
                result["relevance_score"] = score
                result["turn_index"] = i
                scored_turns.append(result)

        # Sort by relevance score
        scored_turns.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Return top K if specified
        if top_k:
            return scored_turns[:top_k]

        return scored_turns

    def semantic_search(
        self, memory: ConversationMemory, query: str, context_window: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Semantic search with context awareness.

        Args:
            memory: Conversation memory to search
            query: Search query
            context_window: Number of turns before/after to include

        Returns:
            List of matching turns with context
        """
        # First do regular search
        initial_results = self.search(memory, query)

        if not initial_results:
            return []

        # Expand results with context
        turns = memory.get_turns()
        expanded_results = []
        used_indices = set()

        for result in initial_results:
            turn_idx = result["turn_index"]

            # Get context window
            start_idx = max(0, turn_idx - context_window)
            end_idx = min(len(turns), turn_idx + context_window + 1)

            # Create context group
            context_group = {
                "matched_turn": result,
                "context_turns": [],
                "relevance_score": result["relevance_score"],
            }

            # Add context turns
            for i in range(start_idx, end_idx):
                if i != turn_idx and i not in used_indices:
                    context_turn = turns[i].copy()
                    context_turn["is_context"] = True
                    context_turn["distance_from_match"] = abs(i - turn_idx)
                    context_group["context_turns"].append(context_turn)
                    used_indices.add(i)

            used_indices.add(turn_idx)
            expanded_results.append(context_group)

        return expanded_results

    def find_related_turns(
        self, memory: ConversationMemory, turn_index: int, max_related: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find turns related to a specific turn.

        Args:
            memory: Conversation memory
            turn_index: Index of turn to find relations for
            max_related: Maximum related turns to return

        Returns:
            List of related turns
        """
        turns = memory.get_turns()

        if turn_index >= len(turns):
            return []

        target_turn = turns[turn_index]

        # Extract keywords from target turn
        target_tokens = self._tokenize(target_turn["content"].lower())
        target_tokens = [t for t in target_tokens if t not in self._stop_words]

        if not target_tokens:
            return []

        # Score other turns
        related = []

        for i, turn in enumerate(turns):
            if i == turn_index:
                continue

            score = self._score_turn(turn, target_tokens)
            if score > 0:
                result = turn.copy()
                result["relevance_score"] = score
                result["turn_index"] = i
                result["relation_type"] = self._determine_relation_type(
                    target_turn, turn
                )
                related.append(result)

        # Sort by relevance
        related.sort(key=lambda x: x["relevance_score"], reverse=True)

        return related[:max_related]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Simple tokenization - could be improved with NLTK or spaCy
        text = re.sub(r"[^\w\s]", " ", text)
        tokens = text.split()
        return [t for t in tokens if len(t) > 1]

    def _score_turn(self, turn: Dict[str, Any], query_tokens: List[str]) -> float:
        """
        Score a turn's relevance to query tokens.

        Args:
            turn: Conversation turn
            query_tokens: Tokenized query

        Returns:
            Relevance score (0-1)
        """
        # Tokenize turn content
        turn_tokens = self._tokenize(turn["content"].lower())

        if not turn_tokens:
            return 0.0

        # Calculate different similarity metrics

        # 1. Exact token matches
        exact_matches = sum(1 for token in query_tokens if token in turn_tokens)
        exact_score = exact_matches / len(query_tokens) if query_tokens else 0

        # 2. Partial matches (substring)
        partial_matches = 0.0
        for query_token in query_tokens:
            for turn_token in turn_tokens:
                if len(query_token) > 3 and query_token in turn_token:
                    partial_matches += 0.5
                    break
        partial_score = partial_matches / len(query_tokens) if query_tokens else 0

        # 3. Term frequency
        turn_counter = Counter(turn_tokens)
        tf_sum = sum(turn_counter.get(token, 0) for token in query_tokens)
        tf_score = min(float(tf_sum) / (len(turn_tokens) * 0.1), 1.0)  # Normalize

        # 4. Role weight (user queries might be more important)
        role_weight: float = 1.2 if turn["role"] == "user" else 1.0

        # Combine scores
        final_score = (
            exact_score * 0.5 + partial_score * 0.3 + tf_score * 0.2
        ) * role_weight

        return min(final_score, 1.0)

    def _determine_relation_type(
        self, turn1: Dict[str, Any], turn2: Dict[str, Any]
    ) -> str:
        """
        Determine relationship type between turns.

        Args:
            turn1: First turn
            turn2: Second turn

        Returns:
            Relation type string
        """
        # Simple heuristic-based relation detection

        # Check if it's a question-answer pair
        if turn1["role"] == "user" and turn2["role"] == "assistant":
            if "?" in turn1["content"]:
                return "answer"
        elif turn1["role"] == "assistant" and turn2["role"] == "user":
            if "?" in turn2["content"]:
                return "follow_up_question"

        # Check for topic continuation
        tokens1 = set(self._tokenize(turn1["content"].lower()))
        tokens2 = set(self._tokenize(turn2["content"].lower()))

        # Remove stop words
        tokens1 = tokens1 - self._stop_words
        tokens2 = tokens2 - self._stop_words

        # Calculate overlap
        if tokens1 and tokens2:
            overlap = len(tokens1 & tokens2) / min(len(tokens1), len(tokens2))
            if overlap > 0.3:
                return "topic_continuation"

        return "related"

    def get_search_stats(self) -> Dict[str, Any]:
        """
        Get search statistics.

        Returns:
            Dictionary with search stats
        """
        return {
            "stop_words_count": len(self._stop_words),
            "search_algorithm": "TF-based scoring with role weighting",
            "features": [
                "exact_match",
                "partial_match",
                "term_frequency",
                "role_weighting",
                "semantic_search",
                "context_awareness",
            ],
        }
