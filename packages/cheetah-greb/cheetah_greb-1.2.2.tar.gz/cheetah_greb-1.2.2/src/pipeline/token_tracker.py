"""
Token usage tracking utilities for Cerebras API calls.
Handles proper token counting based on Cerebras API responses.
Internal server-side implementation only.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import threading
import tiktoken


@dataclass
class TokenUsage:
    """Token usage information from Cerebras API calls."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __add__(self, other: 'TokenUsage') -> 'TokenUsage':
        """Combine two TokenUsage objects."""
        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens
        )


@dataclass
class CerebrasCallStats:
    """Statistics for tracking Cerebras API calls and token usage."""
    keyword_extraction: TokenUsage = field(default_factory=TokenUsage)
    reranking: TokenUsage = field(default_factory=TokenUsage)
    reasoning: TokenUsage = field(default_factory=TokenUsage)
    total: TokenUsage = field(default_factory=TokenUsage)

    def add_keyword_extraction(self, usage: TokenUsage) -> None:
        """Add token usage from keyword extraction."""
        self.keyword_extraction += usage
        self.total += usage

    def add_reranking(self, usage: TokenUsage) -> None:
        """Add token usage from re-ranking."""
        self.reranking += usage
        self.total += usage

    def add_reasoning(self, usage: TokenUsage) -> None:
        """Add token usage from reasoning calls."""
        self.reasoning += usage
        self.total += usage


class TokenTracker:
    """Thread-safe token usage tracking for Cerebras API calls."""

    def __init__(self):
        self._lock = threading.Lock()
        self._current_request_stats = CerebrasCallStats()
        # Initialize tokenizer for accurate token counting
        try:
            # Use GPT-4 tokenizer as closest approximation for Cerebras models
            self._tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            print(f"WARNING: Failed to initialize tokenizer: {e}")
            self._tokenizer = None

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken tokenizer.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if not text:
            return 0

        if self._tokenizer:
            try:
                return len(self._tokenizer.encode(text))
            except Exception as e:
                print(f"WARNING: Token counting failed: {e}")

        # If tokenizer fails, return 0 (will use API tokens)
        return 0

    def count_messages_tokens(self, messages: list) -> int:
        """
        Count total tokens in a list of messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'

        Returns:
            Total number of tokens in all messages
        """
        total_tokens = 0
        for message in messages:
            if isinstance(message, dict):
                content = message.get('content', '')
                total_tokens += self.count_tokens(content)
        return total_tokens

    def extract_usage_from_response(self, response: Any, calculated_input_tokens: int = 0) -> TokenUsage:
        """
        Extract token usage from Cerebras API response with calculated input tokens.

        Args:
            response: Cerebras API response object
            calculated_input_tokens: Pre-calculated input tokens for verification

        Returns:
            TokenUsage object with token counts
        """
        try:
            # Usage statistics are available in response.usage
            if hasattr(response, 'usage') and response.usage:
                api_prompt_tokens = getattr(response.usage, 'prompt_tokens', 0)
                api_completion_tokens = getattr(response.usage, 'completion_tokens', 0)
                api_total_tokens = getattr(response.usage, 'total_tokens', 0)

                # Use Cerebras API tokens (they use different tokenization than tiktoken)
                # Removed token comparison as Cerebras uses different tokenization than OpenAI's tiktoken
  

                return TokenUsage(
                    prompt_tokens=api_prompt_tokens,
                    completion_tokens=api_completion_tokens,
                    total_tokens=api_total_tokens
                )
        except Exception as e:
            print(f"[WARNING]  Failed to extract token usage from response: {e}")

        # Fallback: return zero usage if extraction fails
        return TokenUsage()

    def track_keyword_extraction(self, response: Any, messages: list = None) -> TokenUsage:
        """
        Track token usage from keyword extraction API call.

        Args:
            response: Cerebras API response from keyword extraction
            messages: List of messages sent to API for token counting

        Returns:
            TokenUsage from this call
        """
        calculated_input = self.count_messages_tokens(messages) if messages else 0
        usage = self.extract_usage_from_response(response, calculated_input)

        print(f"Keyword Extraction: {usage.prompt_tokens} input + {usage.completion_tokens} output = {usage.total_tokens} tokens")
        if messages:
            print(f"   System prompt: {self.count_tokens(messages[0].get('content', ''))} tokens")
            print(f"   User prompt: {self.count_tokens(messages[1].get('content', ''))} tokens")

        with self._lock:
            self._current_request_stats.add_keyword_extraction(usage)

        return usage

    def track_reranking(self, response: Any, messages: list = None, span_data: list = None) -> TokenUsage:
        """
        Track token usage from re-ranking API call.

        Args:
            response: Cerebras API response from re-ranking
            messages: List of messages sent to API for token counting
            span_data: Code spans data sent to API

        Returns:
            TokenUsage from this call
        """
        calculated_input = self.count_messages_tokens(messages) if messages else 0

        # Add tokens from span_data (grep results sent for re-ranking)
        if span_data:
            span_text_tokens = sum(self.count_tokens(str(span.get('text', ''))) for span in span_data)
            calculated_input += span_text_tokens
            print(f"   Grep results for re-ranking: {len(span_data)} code spans sent to API")

        usage = self.extract_usage_from_response(response, calculated_input)

        print(f"Re-ranking: {usage.prompt_tokens} input + {usage.completion_tokens} output = {usage.total_tokens} tokens")
        if messages:
            print(f"   System prompt: {self.count_tokens(messages[0].get('content', ''))} tokens")
            # print(f"   User prompt + spans: {calculated_input - self.count_tokens(messages[0].get('content', ''))} tokens")

        with self._lock:
            self._current_request_stats.add_reranking(usage)

        return usage

    def track_enhanced_reranking(self, response: Any, messages: list = None, span_data: list = None) -> TokenUsage:
        """
        Track token usage from enhanced re-ranking API call.

        Args:
            response: Cerebras API response from enhanced re-ranking
            messages: List of messages sent to API for token counting
            span_data: Code spans data sent to API

        Returns:
            TokenUsage from this call
        """
        calculated_input = self.count_messages_tokens(messages) if messages else 0

        # Add tokens from span_data (grep results sent for re-ranking)
        if span_data:
            span_text_tokens = sum(self.count_tokens(str(span.get('text', ''))) for span in span_data)
            calculated_input += span_text_tokens
            print(f"   Grep results for enhanced re-ranking: {span_text_tokens} tokens from {len(span_data)} code spans")

        usage = self.extract_usage_from_response(response, calculated_input)

        print(f"Enhanced Re-ranking: {usage.prompt_tokens} input + {usage.completion_tokens} output = {usage.total_tokens} tokens")
        if messages:
            print(f"   System prompt: {self.count_tokens(messages[0].get('content', ''))} tokens")
            # print(f"   User prompt + spans: {calculated_input - self.count_tokens(messages[0].get('content', ''))} tokens")

        with self._lock:
            self._current_request_stats.add_reranking(usage)

        return usage

    def track_reasoning(self, response: Any, messages: list = None) -> TokenUsage:
        """
        Track token usage from reasoning API call.

        Args:
            response: Cerebras API response from reasoning
            messages: List of messages sent to API for token counting

        Returns:
            TokenUsage from this call
        """
        calculated_input = self.count_messages_tokens(messages) if messages else 0
        usage = self.extract_usage_from_response(response, calculated_input)

        print(f"Reasoning: {usage.prompt_tokens} input + {usage.completion_tokens} output = {usage.total_tokens} tokens")
        if messages:
            print(f"   System prompt: {self.count_tokens(messages[0].get('content', ''))} tokens")
            print(f"   User prompt: {self.count_tokens(messages[1].get('content', ''))} tokens")

        with self._lock:
            self._current_request_stats.add_reasoning(usage)

        return usage

    def get_current_stats(self) -> CerebrasCallStats:
        """
        Get current request statistics.

        Returns:
            Current request statistics
        """
        with self._lock:
            return self._current_request_stats

    def reset(self) -> None:
        """Reset current request statistics."""
        with self._lock:
            self._current_request_stats = CerebrasCallStats()

    def get_summary_dict(self) -> Dict[str, Any]:
        """
        Get summary of current token usage as dictionary.

        Returns:
            Dictionary with token usage breakdown
        """
        stats = self.get_current_stats()
        return {
            "keyword_extraction": {
                "prompt_tokens": stats.keyword_extraction.prompt_tokens,
                "completion_tokens": stats.keyword_extraction.completion_tokens,
                "total_tokens": stats.keyword_extraction.total_tokens
            },
            "reranking": {
                "prompt_tokens": stats.reranking.prompt_tokens,
                "completion_tokens": stats.reranking.completion_tokens,
                "total_tokens": stats.reranking.total_tokens
            },
            "reasoning": {
                "prompt_tokens": stats.reasoning.prompt_tokens,
                "completion_tokens": stats.reasoning.completion_tokens,
                "total_tokens": stats.reasoning.total_tokens
            },
            "total": {
                "prompt_tokens": stats.total.prompt_tokens,
                "completion_tokens": stats.total.completion_tokens,
                "total_tokens": stats.total.total_tokens
            }
        }


# Global instance for use across the pipeline
token_tracker = TokenTracker()