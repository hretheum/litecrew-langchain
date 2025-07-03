"""
Context Size Limiter

Manages context size limits, compression, and smart truncation to ensure
efficient memory usage while preserving important information.
"""

import re
import zlib
import json
from typing import Tuple, Optional, Dict, Any
from enum import Enum

from .context_config import ContextConfig, ContextCompressionType


class ContextSizeLimiter:
    """
    Manages context size limits and applies compression strategies.
    
    Ensures context stays within memory limits while preserving
    the most important information through intelligent compression.
    """
    
    def __init__(self, config: Optional[ContextConfig] = None):
        """
        Initialize context size limiter.
        
        Args:
            config: Context configuration, uses defaults if None
        """
        self.config = config or ContextConfig()
        self.config.validate()
        
        # Compression stats
        self._compression_stats = {
            'total_compressions': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'average_compression_ratio': 0.0
        }
    
    def enforce_limits(self, context: str, max_size: Optional[int] = None) -> str:
        """
        Enforce size limits on context string.
        
        Args:
            context: Context string to limit
            max_size: Optional override for max size, uses config default if None
            
        Returns:
            Size-limited context string
        """
        if not context:
            return context
        
        target_size = max_size or self.config.max_size_per_task
        current_size = len(context.encode('utf-8'))
        
        # Return as-is if within limits
        if current_size <= target_size:
            return context
        
        # Apply compression based on configuration
        if self.config.enable_compression:
            compressed_context, ratio = self.compress_if_needed(context, target_size)
            
            # Update compression stats
            self._update_compression_stats(current_size, len(compressed_context.encode('utf-8')), ratio)
            
            return compressed_context
        else:
            # Simple truncation if compression disabled
            return self.truncate_smart(context, target_size)
    
    def compress_if_needed(self, context: str, target_size: int) -> Tuple[str, float]:
        """
        Compress context if it exceeds size threshold.
        
        Args:
            context: Context string to potentially compress
            target_size: Target size in bytes
            
        Returns:
            Tuple of (compressed_context, compression_ratio)
        """
        current_size = len(context.encode('utf-8'))
        
        # Check if compression is needed
        threshold_size = int(target_size * self.config.compression_threshold)
        if current_size <= threshold_size:
            return context, 1.0
        
        # Apply compression based on type
        if self.config.compression_type == ContextCompressionType.TRUNCATE:
            compressed = self.truncate_smart(context, target_size)
            
        elif self.config.compression_type == ContextCompressionType.SLIDING_WINDOW:
            compressed = self.sliding_window_compress(context, target_size)
            
        elif self.config.compression_type == ContextCompressionType.SMART_SUMMARY:
            compressed = self.smart_summary_compress(context, target_size)
            
        else:  # NONE
            compressed = context
        
        # Calculate compression ratio
        compressed_size = len(compressed.encode('utf-8'))
        ratio = compressed_size / current_size if current_size > 0 else 1.0
        
        return compressed, ratio
    
    def truncate_smart(self, context: str, target_size: int) -> str:
        """
        Smart truncation that preserves beginning and end.
        
        Args:
            context: Context to truncate
            target_size: Target size in bytes
            
        Returns:
            Truncated context string
        """
        if len(context.encode('utf-8')) <= target_size:
            return context
        
        # Split into paragraphs or sections
        sections = self._split_into_sections(context)
        
        if len(sections) <= 2:
            # Simple truncation for short contexts
            max_chars = target_size // 2  # Rough estimate
            if len(context) <= max_chars:
                return context
            
            # Keep beginning and end
            keep_size = max_chars // 3
            beginning = context[:keep_size]
            end = context[-keep_size:]
            
            return f"{beginning}\n\n... [content truncated] ...\n\n{end}"
        
        # For longer contexts, keep first few and last few sections
        preserved_sections = []
        current_size = 0
        
        # Calculate how many sections we can keep
        section_sizes = [len(s.encode('utf-8')) for s in sections]
        total_sections = len(sections)
        
        # Always try to keep first and last sections
        keep_first = min(2, total_sections // 3)
        keep_last = min(2, total_sections // 3)
        
        # Add first sections
        for i in range(keep_first):
            if current_size + section_sizes[i] < target_size * 0.8:
                preserved_sections.append(sections[i])
                current_size += section_sizes[i]
        
        # Add truncation marker
        if total_sections > keep_first + keep_last:
            preserved_sections.append("\n... [middle content summarized] ...\n")
            current_size += 50  # Estimated marker size
        
        # Add last sections
        for i in range(max(0, total_sections - keep_last), total_sections):
            if current_size + section_sizes[i] < target_size:
                preserved_sections.append(sections[i])
                current_size += section_sizes[i]
        
        return "\n\n".join(preserved_sections)
    
    def sliding_window_compress(self, context: str, target_size: int) -> str:
        """
        Sliding window compression keeping recent content.
        
        Args:
            context: Context to compress
            target_size: Target size in bytes
            
        Returns:
            Compressed context using sliding window
        """
        sections = self._split_into_sections(context)
        
        # Work backwards to keep most recent content
        selected_sections = []
        current_size = 0
        
        for section in reversed(sections):
            section_size = len(section.encode('utf-8'))
            if current_size + section_size <= target_size * 0.9:
                selected_sections.insert(0, section)
                current_size += section_size
            else:
                break
        
        # Add indicator if content was truncated
        if len(selected_sections) < len(sections):
            truncated_count = len(sections) - len(selected_sections)
            indicator = f"\n[{truncated_count} earlier sections truncated]\n"
            selected_sections.insert(0, indicator)
        
        return "\n\n".join(selected_sections)
    
    def smart_summary_compress(self, context: str, target_size: int) -> str:
        """
        Smart summarization compression (placeholder for future LLM integration).
        
        Args:
            context: Context to compress
            target_size: Target size in bytes
            
        Returns:
            Compressed context with summarization
        """
        # For now, use sliding window as fallback
        # Future: Integrate with LLM for intelligent summarization
        
        sections = self._split_into_sections(context)
        
        if len(sections) <= 3:
            return self.sliding_window_compress(context, target_size)
        
        # Keep first and last sections, summarize middle
        first_section = sections[0]
        last_section = sections[-1]
        middle_sections = sections[1:-1]
        
        # Calculate sizes
        first_size = len(first_section.encode('utf-8'))
        last_size = len(last_section.encode('utf-8'))
        available_for_middle = target_size - first_size - last_size - 200  # Buffer for summary
        
        if available_for_middle <= 0:
            # Not enough space, use sliding window
            return self.sliding_window_compress(context, target_size)
        
        # Create simple summary of middle sections
        middle_summary = self._create_simple_summary(middle_sections)
        summary_size = len(middle_summary.encode('utf-8'))
        
        if summary_size <= available_for_middle:
            return f"{first_section}\n\n{middle_summary}\n\n{last_section}"
        else:
            # Summary too long, truncate middle sections
            return f"{first_section}\n\n[{len(middle_sections)} sections summarized]\n\n{last_section}"
    
    def _split_into_sections(self, context: str) -> list[str]:
        """Split context into logical sections."""
        # Try to split on common separators
        if '\n\n---\n\n' in context:
            sections = context.split('\n\n---\n\n')
        elif '\n\n' in context:
            sections = context.split('\n\n')
        elif '\n' in context and len(context.split('\n')) > 10:
            lines = context.split('\n')
            sections = []
            current_section = []
            
            for line in lines:
                current_section.append(line)
                # Group every 5 lines or at obvious breaks
                if len(current_section) >= 5 or line.strip() == '' or line.startswith('['):
                    if current_section:
                        sections.append('\n'.join(current_section))
                        current_section = []
            
            if current_section:
                sections.append('\n'.join(current_section))
        else:
            # Split into chunks if no natural breaks
            chunk_size = len(context) // 5
            sections = [context[i:i+chunk_size] for i in range(0, len(context), chunk_size)]
        
        return [s for s in sections if s.strip()]
    
    def _create_simple_summary(self, sections: list[str]) -> str:
        """Create a simple summary of sections."""
        # Extract key information from each section
        summary_parts = []
        
        for i, section in enumerate(sections):
            # Extract first line or sentence as summary
            lines = section.strip().split('\n')
            if lines:
                first_line = lines[0].strip()
                
                # Try to find timestamp or agent markers
                timestamp_match = re.search(r'\[([\d:]+)\]', first_line)
                agent_match = re.search(r'\[([^\]]+)\]', first_line)
                
                if timestamp_match or agent_match:
                    summary_parts.append(first_line)
                else:
                    # Take first meaningful sentence
                    sentences = section.split('.')
                    if sentences and len(sentences[0]) < 100:
                        summary_parts.append(sentences[0].strip() + '.')
                    else:
                        summary_parts.append(first_line[:50] + '...')
        
        summary = f"[Summary of {len(sections)} sections]:\n" + '\n'.join(summary_parts)
        return summary
    
    def _update_compression_stats(self, original_size: int, compressed_size: int, ratio: float):
        """Update compression statistics."""
        self._compression_stats['total_compressions'] += 1
        self._compression_stats['total_original_size'] += original_size
        self._compression_stats['total_compressed_size'] += compressed_size
        
        # Calculate running average
        total_compressions = self._compression_stats['total_compressions']
        if total_compressions > 0:
            overall_ratio = (
                self._compression_stats['total_compressed_size'] / 
                self._compression_stats['total_original_size']
            )
            self._compression_stats['average_compression_ratio'] = overall_ratio
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        stats = self._compression_stats.copy()
        
        if stats['total_compressions'] > 0:
            stats['average_original_size'] = stats['total_original_size'] / stats['total_compressions']
            stats['average_compressed_size'] = stats['total_compressed_size'] / stats['total_compressions']
        else:
            stats['average_original_size'] = 0
            stats['average_compressed_size'] = 0
        
        return stats
    
    def reset_stats(self):
        """Reset compression statistics."""
        self._compression_stats = {
            'total_compressions': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'average_compression_ratio': 0.0
        }
    
    def estimate_compression_ratio(self, context: str) -> float:
        """
        Estimate compression ratio for given context.
        
        Args:
            context: Context to estimate compression for
            
        Returns:
            Estimated compression ratio (0.0 to 1.0)
        """
        if not context:
            return 1.0
        
        # Use simple heuristics based on content type
        sections = self._split_into_sections(context)
        
        # More repetitive content compresses better
        unique_words = len(set(context.lower().split()))
        total_words = len(context.split())
        
        if total_words > 0:
            repetition_factor = 1.0 - (unique_words / total_words)
        else:
            repetition_factor = 0.0
        
        # Base compression based on content structure
        if len(sections) > 5:
            base_ratio = self.config.compression_ratio
        else:
            base_ratio = 0.8  # Less aggressive for short content
        
        # Adjust based on repetition
        estimated_ratio = base_ratio + (repetition_factor * 0.3)
        
        return min(1.0, max(0.1, estimated_ratio))