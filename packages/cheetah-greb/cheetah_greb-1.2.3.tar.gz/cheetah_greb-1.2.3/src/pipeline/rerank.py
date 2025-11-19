"""
Rerank tool implementation using Cerebras GPT-OSS for intelligent result ranking.
"""

from __future__ import annotations

import json
import os
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from openai import OpenAI
import httpx

from .base import FileSpan, RankedResult, PipelineConfig
from .token_tracker import token_tracker


class RerankRequest(BaseModel):
    """Request model for reranking."""
    query: str
    spans: List[Dict[str, Any]]
    top_k: int = 5


class RerankResponse(BaseModel):
    """Response model for reranking results."""
    results: List[RankedResult]
    reasoning: Optional[str] = None


class RerankTool:
    """Implements intelligent result re-ranking using Cerebras GPT-OSS."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        
        # Configure connection pooling for better performance
        # Use persistent connections and connection pooling to reduce overhead
        http_client = httpx.Client(
            limits=httpx.Limits(
                max_connections=10,  # Maximum number of connections in the pool
                max_keepalive_connections=5,  # Keep connections alive for reuse
                keepalive_expiry=30.0  # Keep connections alive for 30 seconds
            ),
            timeout=httpx.Timeout(
                connect=5.0,  # Connection timeout
                read=self.config.rerank_timeout,  # Read timeout from config
                write=5.0,  # Write timeout
                pool=5.0  # Pool timeout
            ),
            transport=httpx.HTTPTransport(retries=2)  # Retry transient failures
        )
        
        self.client = OpenAI(
            api_key=config.cerebras_api_key,
            base_url=config.cerebras_base_url,
            http_client=http_client
        )

    def _call_api_with_retry(self, api_params: Dict[str, Any], max_retries: int = 3):
        """
        Call the Cerebras API with retry logic for transient failures.
        
        Args:
            api_params: Parameters for the API call
            max_retries: Maximum number of retry attempts
            
        Returns:
            API response
            
        Raises:
            RuntimeError: If all retry attempts fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(**api_params)
                return response
            except (httpx.TimeoutException, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Exponential backoff: 0.5s, 1s, 2s
                    wait_time = 0.5 * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                raise RuntimeError(f"API timeout after {max_retries} attempts: {e}")
            except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 0.5 * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                raise RuntimeError(f"Connection error after {max_retries} attempts: {e}")
            except Exception as e:
                # Don't retry on other errors (e.g., authentication, validation)
                raise RuntimeError(f"Cerebras API call failed: {e}")
        
        raise RuntimeError(f"API call failed after {max_retries} attempts: {last_error}")

    def rerank_spans(
        self,
        query: str,
        spans: List[FileSpan],
        top_k: Optional[int] = None
    ) -> List[RankedResult]:
        """
        Re-rank file spans based on relevance to the query.

        Args:
            query: The original search query
            spans: List of FileSpan objects to rank
            top_k: Number of top results to return (overrides config)

        Returns:
            List of RankedResult objects
        """
        if not spans:
            return []

        top_k = top_k or self.config.top_k_results

        # Limit batch size to avoid token limit issues
        if len(spans) > self.config.rerank_max_batch_size:
            spans = spans[:self.config.rerank_max_batch_size]

        # Prepare spans for the model
        span_data = []
        for i, span in enumerate(spans):
            # Truncate very long spans to avoid token limits
            text = span.text
            if len(text) > 2000:
                text = text[:2000] + "..."

            span_data.append({
                "id": i,
                "path": span.path,
                "start_line": span.start_line,
                "end_line": span.end_line,
                "text": text
            })

        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            },
            {
                "role": "user",
                "content": self._get_user_prompt(query, span_data, top_k)
            }
        ]

        try:
            # Build API call parameters
            api_params = {
                "model": self.config.cerebras_model,
                "messages": messages,
                "temperature": self.config.rerank_temperature,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "rerank_results",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "results": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "span_id": {"type": "integer"},
                                            "score": {"type": "number"},
                                            "reason": {"type": "string"},
                                            "highlights": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "line_start": {"type": "integer"},
                                                        "line_end": {"type": "integer"},
                                                        "reason": {"type": "string"}
                                                    },
                                                    "required": ["line_start", "line_end", "reason"]
                                                }
                                            }
                                        },
                                        "required": ["span_id", "score", "reason", "highlights"]
                                    }
                                },
                                "reasoning": {"type": "string"}
                            },
                            "required": ["results"]
                        }
                    }
                }
            }

            # Add reasoning_effort parameter only for gpt-oss-120b model
            if self.config.cerebras_model == "gpt-oss-120b":
                api_params["reasoning_effort"] = self.config.reasoning_effort

            # Add timeout to prevent hanging
            api_params["timeout"] = self.config.rerank_timeout

            # Call API with retry logic for transient failures
            response = self._call_api_with_retry(api_params)

            # Track token usage from reranking with messages and span data
            token_tracker.track_reranking(response, messages, span_data)

            # Parse the structured response
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    result_data = json.loads(response.choices[0].message.content)
                    return self._convert_to_ranked_results(result_data, spans)
                except json.JSONDecodeError:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(1)

        except Exception as e:
            raise RuntimeError(f"Cerebras reranking failed: {e}")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for reranking."""
        return """You are an expert code search assistant. Analyze and rank code snippets based on their relevance to the search query.

For each code snippet, provide:
1. A relevance score from 0.0 to 1.0 (where 1.0 is most relevant)
2. A brief reason for the score
3. Specific highlights within the code that are most relevant

Use your intelligence to determine relevance based on semantic meaning, context, and the user's apparent intent."""

    def _get_user_prompt(self, query: str, span_data: List[Dict], top_k: int) -> str:
        """Get the user prompt for reranking."""
        spans_text = json.dumps(span_data, separators=(',', ':'))

        return f"""Search Query: "{query}"

Analyze and rank these code snippets by relevance. Return the top {top_k} results.

Code Snippets:
{spans_text}

Rank based on what would most help solve the user's actual problem."""

    def _convert_to_ranked_results(
        self,
        result_data: Dict[str, Any],
        original_spans: List[FileSpan]
    ) -> List[RankedResult]:
        """Convert the model response to RankedResult objects."""
        results = []

        for item in result_data.get("results", []):
            span_id = item.get("span_id")
            if span_id is not None and 0 <= span_id < len(original_spans):
                span = original_spans[span_id]

                # Convert highlights to the expected format
                highlights = []
                for hl in item.get("highlights", []):
                    # Create a sub-span for this specific highlight
                    start_line = hl.get("line_start", span.start_line)
                    end_line = hl.get("line_end", span.end_line)

                    highlights.append({
                        "line_start": start_line,
                        "line_end": end_line,
                        "reason": hl.get("reason", ""),
                        "span": {
                            "start_line": start_line,
                            "end_line": end_line,
                            "text": self._extract_span_text(span.text, start_line, end_line, span.start_line)
                        }
                    })

                result = RankedResult(
                    path=span.path,
                    score=item.get("score", 0.0),
                    highlights=highlights
                )
                results.append(result)

        return results

    def _extract_span_text(self, full_text: str, target_start: int, target_end: int, span_start: int) -> str:
        """Extract the specific text for a highlight within a span."""
        if not full_text:
            return ""

        lines = full_text.split('\n')

        # Calculate the relative line positions within the span
        relative_start = target_start - span_start
        relative_end = target_end - span_start + 1

        # Ensure bounds are valid
        if relative_start < 0:
            relative_start = 0
        if relative_end > len(lines):
            relative_end = len(lines)

        # Extract the relevant lines
        highlight_lines = lines[relative_start:relative_end]
        return '\n'.join(highlight_lines)

    def rerank_spans_with_context(
        self,
        natural_query: str,
        extracted_keywords,
        spans: List[FileSpan],
        top_k: Optional[int] = None
    ) -> List[RankedResult]:
        """
        Re-rank file spans using natural language query context and extracted keywords.

        Args:
            natural_query: Original natural language query from user
            extracted_keywords: Keywords extracted by Cerebras
            spans: List of FileSpan objects to rank
            top_k: Number of top results to return

        Returns:
            List of RankedResult objects with enhanced context
        """
        if not spans:
            return []

        top_k = top_k or self.config.top_k_results

        # Limit batch size to avoid token limit issues
        if len(spans) > self.config.rerank_max_batch_size:
            spans = spans[:self.config.rerank_max_batch_size]

        # Prepare enhanced span data with file information
        span_data = []
        for i, span in enumerate(spans):
            # Truncate very long spans to avoid token limits
            text = span.text
            if len(text) > 2000:
                text = text[:2000] + "..."

            # Extract file name and extension
            file_name = span.path.split('/')[-1] if '/' in span.path else span.path.split('\\')[-1]
            file_ext = file_name.split('.')[-1] if '.' in file_name else 'unknown'

            span_data.append({
                "id": i,
                "path": span.path,
                "file_name": file_name,
                "file_extension": file_ext,
                "start_line": span.start_line,
                "end_line": span.end_line,
                "text": text
            })

        messages = [
            {
                "role": "system",
                "content": self._get_enhanced_system_prompt()
            },
            {
                "role": "user",
                "content": self._get_enhanced_user_prompt(natural_query, extracted_keywords, span_data, top_k)
            }
        ]

        try:
            # Build API call parameters
            api_params = {
                "model": self.config.cerebras_model,
                "messages": messages,
                "temperature": self.config.rerank_temperature,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "enhanced_rerank_results",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "results": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "span_id": {"type": "integer"},
                                            "score": {"type": "number"},
                                            "reason": {"type": "string"},
                                            "summary": {"type": "string"},
                                            "highlights": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "line_start": {"type": "integer"},
                                                        "line_end": {"type": "integer"},
                                                        "reason": {"type": "string"}
                                                    },
                                                    "required": ["line_start", "line_end", "reason"]
                                                }
                                            }
                                        },
                                        "required": ["span_id", "score", "reason", "summary", "highlights"]
                                    }
                                },
                                "reasoning": {"type": "string"}
                            },
                            "required": ["results", "reasoning"]
                        }
                    }
                }
            }

            # Add reasoning_effort parameter only for gpt-oss-120b model
            if self.config.cerebras_model == "gpt-oss-120b":
                api_params["reasoning_effort"] = self.config.reasoning_effort

            # Add timeout to prevent hanging
            api_params["timeout"] = self.config.rerank_timeout

            # Call API with retry logic for transient failures
            response = self._call_api_with_retry(api_params)

            # Track token usage from enhanced reranking with messages and span data
            token_tracker.track_enhanced_reranking(response, messages, span_data)

            # Parse the structured response
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    result_data = json.loads(response.choices[0].message.content)
                    return self._convert_to_enhanced_ranked_results(result_data, spans)
                except json.JSONDecodeError:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(1)

        except Exception as e:
            raise RuntimeError(f"Cerebras enhanced reranking failed: {e}")

    def _get_enhanced_system_prompt(self) -> str:
        """Get enhanced system prompt for reranking with natural language context."""
        return """You are an expert code search assistant. Rank code snippets based on their relevance to the user's original query.

You will receive:
1. The ORIGINAL USER QUERY (exactly as typed by the user)
2. Extracted keywords and analysis
3. Code snippets found in the codebase

IMPORTANT: Pay special attention to the ORIGINAL USER QUERY - this is exactly what the user wants. Use the keywords as supporting information, but prioritize the user's original wording and intent.

For each snippet, provide:
1. Relevance score (0.0-1.0) based on how well it matches the original query
2. Reason for the score (explain why it matches the user's request)
3. Code summary
4. Relevant highlights

Prioritize results that best solve the user's actual problem as expressed in their ORIGINAL USER QUERY."""

    def _get_enhanced_user_prompt(self, natural_query: str, keywords, span_data: List[Dict], top_k: int) -> str:
        """Get enhanced user prompt for reranking with full context."""
        return f"""ORIGINAL USER QUERY: "{natural_query}"

This is the exact query the user typed. Use this as the primary guide for understanding what the user wants.

Keywords:
- Primary: {keywords.primary_terms}
- Search: {keywords.search_terms}
- Intent: {keywords.intent}
- Patterns: {keywords.file_patterns}

Analyze and rank these code snippets based on the ORIGINAL USER QUERY above.
Focus on the user's actual intent and what they're trying to accomplish.

Return the top {top_k} results that best address the user's original request.

Code Snippets:
{json.dumps(span_data, separators=(',', ':'))}"""

    def _convert_to_enhanced_ranked_results(
        self,
        result_data: Dict[str, Any],
        original_spans: List[FileSpan]
    ) -> List[RankedResult]:
        """Convert the enhanced model response to RankedResult objects with summaries."""
        results = []

        for item in result_data.get("results", []):
            span_id = item.get("span_id")
            if span_id is not None and 0 <= span_id < len(original_spans):
                span = original_spans[span_id]

                # Convert highlights to the expected format (without summary/file_info)
                highlights = []
                for hl in item.get("highlights", []):
                    start_line = hl.get("line_start", span.start_line)
                    end_line = hl.get("line_end", span.end_line)

                    highlights.append({
                        "line_start": start_line,
                        "line_end": end_line,
                        "reason": hl.get("reason", ""),
                        "span": {
                            "start_line": start_line,
                            "end_line": end_line,
                            "text": self._extract_span_text(span.text, start_line, end_line, span.start_line)
                        }
                    })

                # Create file info at the result level
                file_info = {
                    "path": span.path,
                    "file_name": span.path.split('/')[-1] if '/' in span.path else span.path.split('\\')[-1],
                    "start_line": span.start_line,
                    "end_line": span.end_line
                }

                result = RankedResult(
                    path=span.path,
                    score=item.get("score", 0.0),
                    highlights=highlights,
                    summary=item.get("summary", ""),
                    file_info=file_info,
                    reasoning=item.get("reason", "")
                )
                results.append(result)

        return results

    def search_and_rerank(
        self,
        query: str,
        spans: List[FileSpan],
        context: Optional[str] = None
    ) -> RerankResponse:
        """
        Full search and rerank pipeline with optional context.

        Args:
            query: Search query
            spans: List of FileSpan objects to rank
            context: Optional additional context for the search

        Returns:
            RerankResponse with ranked results and reasoning
        """
        if context:
            # Enhance the query with context
            enhanced_query = f"Query: {query}\nContext: {context}"
        else:
            enhanced_query = query

        ranked_results = self.rerank_spans(enhanced_query, spans)

        # Generate overall reasoning using Cerebras
        reasoning_messages = [
            {
                "role": "system",
                "content": "You are a code search assistant. Briefly explain why these results are relevant to the query."
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nTop results found in:\n" +
                         "\n".join([f"- {r.path} (score: {r.score:.2f})" for r in ranked_results[:3]])
            }
        ]

        # Build API call parameters for reasoning
        reasoning_params = {
            "model": self.config.cerebras_model,
            "messages": reasoning_messages,
            "temperature": 0,
            "max_tokens": 200
        }

        # Add reasoning_effort parameter only for gpt-oss-120b model
        if self.config.cerebras_model == "gpt-oss-120b":
            reasoning_params["reasoning_effort"] = self.config.reasoning_effort

        # Add timeout to prevent hanging
        reasoning_params["timeout"] = self.config.rerank_timeout

        # Call API with retry logic for transient failures
        reasoning_response = self._call_api_with_retry(reasoning_params)

        # Track token usage from reasoning with messages
        token_tracker.track_reasoning(reasoning_response, reasoning_messages)

        reasoning = reasoning_response.choices[0].message.content

        return RerankResponse(
            results=ranked_results,
            reasoning=reasoning
        )