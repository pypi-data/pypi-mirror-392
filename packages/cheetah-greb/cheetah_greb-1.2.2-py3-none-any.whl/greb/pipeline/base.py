"""
Base data structures and utilities for the Greb pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


@dataclass
class FileSpan:
    """Represents a text span within a file."""
    path: str
    start_line: int
    end_line: int
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "text": self.text
        }


@dataclass
class CandidateMatch:
    """Represents a candidate match from grep/glob operations."""
    path: str
    line_number: int
    matched_text: str
    context_before: str = ""
    context_after: str = ""

    def to_span(self, window_size: int = 10) -> FileSpan:
        """Convert to a FileSpan with context window."""
        # This would be implemented in the read tool
        return FileSpan(
            path=self.path,
            start_line=max(1, self.line_number - window_size),
            end_line=self.line_number + window_size,
            text=self.context_before + self.matched_text + self.context_after
        )


class RankedResult(BaseModel):
    """Represents a ranked result after LLM re-ranking with enhanced information."""
    path: str
    score: float
    highlights: List[Dict[str, Any]]
    summary: Optional[str] = None
    file_info: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None

    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }


class PipelineConfig(BaseModel):
    """Configuration for the Greb pipeline."""
    # Tool execution limits
    max_grep_results: int = 10000
    max_glob_results: int = 10
    context_window_size: int = 5

    # Read tool configuration
    read_max_file_size: int = 5048576  # 5MB
    read_window_size: int = 10
    read_max_spans: int = 500
    read_max_lines_per_file: int = 100
    read_context_lines: int = 10
    read_binary_sample_size: int = 1024
    read_generic_window_size: int = 10

    # Cerebras configuration
    cerebras_api_key: str
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    cerebras_model: str = "gpt-oss-120b"
    reasoning_effort: str = "low"  # "low", "medium", or "high" - only for gpt-oss-120b

    # Re-ranking configuration
    top_k_results: int = 10
    rerank_temperature: float = 0.0

    class Config:
        extra = "allow"


class ExtractedKeywords(BaseModel):
    """Model for extracted keywords from natural language query."""
    primary_terms: List[str]  # Main technical terms to search for
    file_patterns: List[str]  # File patterns to limit search
    search_terms: List[str]   # All terms to use in grep search
    intent: str              # User's intent summary


class QueryRequest(BaseModel):
    """Represents a query request from the OpenAI-compatible API."""
    query: str
    max_results: Optional[int] = None
    tools: Optional[List[str]] = None  # ["grep", "glob", "read"]


class QueryResponse(BaseModel):
    """Represents an enhanced query response with detailed information."""
    results: List[RankedResult]
    total_candidates: int
    query: str
    execution_time_ms: Optional[float] = None
    extracted_keywords: Optional[Dict[str, Any]] = None
    tools_used: Optional[List[str]] = None
    overall_reasoning: Optional[str] = None
    token_usage: Optional[Dict[str, Any]] = None