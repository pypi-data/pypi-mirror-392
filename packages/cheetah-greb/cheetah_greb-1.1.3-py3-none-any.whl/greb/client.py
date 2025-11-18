"""
Greb Python Client SDK
This allows users to integrate Greb into their own applications and AI agents.

The client runs grep/glob searches LOCALLY on user's machine, then sends
candidates to the API server for AI-powered reranking and billing.
"""

from __future__ import annotations

import os
import time
from typing import Optional, List, Dict, Any, Iterator
from dataclasses import dataclass

import httpx
from pydantic import BaseModel

# Import local search tools
from .pipeline.grep import GrepTool
from .pipeline.glob import GlobTool
from .pipeline.read import ReadTool
from .pipeline.keyword_extractor import KeywordExtractor
from .pipeline.base import PipelineConfig, CandidateMatch


class SearchRequest(BaseModel):
    """Request model for code search - sends pre-searched candidates to server."""
    query: str
    candidates: List[Dict[str, Any]]  # Pre-searched matches from local grep
    max_results: Optional[int] = None


class SearchResult(BaseModel):
    """Individual search result."""
    path: str
    score: float
    highlights: List[Dict[str, Any]]
    summary: Optional[str] = None


class SearchResponse(BaseModel):
    """Response from code search."""
    results: List[SearchResult]
    total_candidates: int
    query: str
    execution_time_ms: float
    extracted_keywords: Optional[Dict[str, Any]] = None
    tools_used: Optional[List[str]] = None
    overall_reasoning: Optional[str] = None


@dataclass
class ClientConfig:
    """Configuration for the Greb client."""
    api_key: str
    base_url: str
    timeout: int = 60
    max_retries: int = 3


class GrebClient:
    """
    Python client for Greb API.
    
    Usage:
        ```python
        from greb import GrebClient
        
        # Initialize with API key
        client = GrebClient(api_key="grb_your_api_key_here")
        
        # Search for code
        results = client.search(
            query="Find all database connection functions",
            directory="./src",
            file_patterns=["*.py", "*.js"]
        )
        
        for result in results.results:
            print(f"{result.path}: {result.summary}")
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3,
        max_grep_results: int = None
    ):
        """
        Initialize the Greb client.
        
        Args:
            api_key: Your Greb API key (required or set GREB_API_KEY env var)
            base_url: API base URL (required or set GREB_API_URL env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            max_grep_results: Max results from local grep (default: 1500)
        """
        self.api_key = api_key or os.getenv("GREB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Set GREB_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.base_url = base_url or os.getenv("GREB_API_URL")
        if not self.base_url:
            raise ValueError(
                "API base URL is required. Set GREB_API_URL environment variable "
                "or pass base_url parameter."
            )
        
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize LOCAL search tools (run on user's machine)
        max_grep = max_grep_results or int(os.getenv("MAX_GREP_RESULTS", "1500"))
        max_glob = int(os.getenv("MAX_GLOB_RESULTS", "50"))
        read_max_size = int(os.getenv("READ_MAX_FILE_SIZE", "5048576"))
        self.grep_tool = GrepTool(max_results=max_grep)
        self.glob_tool = GlobTool(max_results=max_glob)
        self.read_tool = ReadTool(max_file_size=read_max_size)
        
        # HTTP client for API requests
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "greb-python/1.0.1"
            },
        )
    
    def search(
        self,
        query: str,
        directory: Optional[str] = None,
        file_patterns: Optional[List[str]] = None,
        max_results: Optional[int] = None
    ) -> SearchResponse:
        """
        Search for code using natural language query.
        
        This method:
        1. Runs grep/glob searches LOCALLY on your machine
        2. Collects candidate matches
        3. Sends candidates to API for AI-powered reranking
        4. Returns ranked results with billing tracked
        
        Args:
            query: Natural language description of what you're looking for
            directory: Directory to search in (absolute or relative path)
            file_patterns: File patterns to filter (e.g., ["*.py", "*.js"])
            max_results: Maximum number of results to return
            
        Returns:
            SearchResponse containing ranked results
            
        Example:
            ```python
            results = client.search(
                query="authentication middleware functions",
                directory="./backend/src",
                file_patterns=["*.py", "*.js"],
                max_results=10
            )
            ```
        """
        # Step 1: Call server to extract keywords using Cerebras
        keyword_response = self.client.post(
            "/v1/extract-keywords",
            json={"query": query}
        )
        keyword_response.raise_for_status()
        keyword_data = keyword_response.json()
        
        keywords = keyword_data.get("search_terms", []) or keyword_data.get("primary_terms", [])
        if not keywords:
            raise ValueError(f"Server failed to extract keywords from query: {query}")
        
        # Step 2: Run full orchestrator pipeline LOCALLY on user's machine
        # This includes parallel grep, glob (for <10K files), read tool, turn logic, etc.
        from .pipeline.orchestrator import PipelineOrchestrator
        from .pipeline.base import PipelineConfig
        
        # Create local orchestrator config (no Cerebras key needed for local search)
        local_config = PipelineConfig(
            cerebras_api_key="",  # Not used locally
            max_grep_results=self.grep_tool.max_results,
            max_glob_results=self.glob_tool.max_results,
            top_k_results=max_results or 10
        )
        
        local_orchestrator = PipelineOrchestrator(local_config)
        
        # Run LOCAL search with full pipeline (parallel grep, turn logic, glob, read)
        # But only up to candidate collection - don't rerank locally
        search_dir = os.path.abspath(directory) if directory else os.getcwd()
        
        print(f"Running local search pipeline in {search_dir}")
        
        # Use orchestrator's internal methods for local search
        # This gives us all the parallel grep, turn logic, file counting, etc.
        from .pipeline.base import ExtractedKeywords
        extracted_keywords = ExtractedKeywords(
            primary_terms=keyword_data.get("primary_terms", []),
            search_terms=keywords,
            file_patterns=file_patterns or keyword_data.get("file_patterns", []),
            intent=keyword_data.get("intent", query)
        )
        
        # Run local parallel searches with orchestrator logic
        all_spans = []
        search_dir_path = search_dir
        
        # Count files for strategy
        file_count = sum(1 for _ in os.walk(search_dir))
        use_glob = file_count < 10000
        
        # Execute parallel grep searches (from orchestrator)
        from concurrent.futures import ThreadPoolExecutor, as_completed
        MAX_PARALLEL_SEARCHES = 8
        
        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_SEARCHES) as executor:
            futures = []
            search_terms = extracted_keywords.search_terms[:MAX_PARALLEL_SEARCHES]
            
            for term in search_terms:
                future = executor.submit(
                    local_orchestrator.grep_tool.search,
                    pattern=term,
                    path=search_dir_path,
                    file_pattern=file_patterns[0] if file_patterns else "*",
                    context_lines=3,
                    case_sensitive=False
                )
                futures.append((term, future))
            
            # Collect results
            for term, future in futures:
                try:
                    result = future.result(timeout=30)
                    if result and result.get("matches"):
                        for match in result["matches"]:
                            all_spans.append({
                                "path": match.get("path", ""),
                                "line_number": match.get("line_number", 0),
                                "content": match.get("line", ""),
                                "context": match.get("context", []),
                                "score": 0.0
                            })
                except Exception as e:
                    print(f"Grep failed for '{term}': {e}")
        
        # Deduplicate
        unique_candidates = {}
        for span in all_spans:
            key = (span["path"], span["line_number"])
            if key not in unique_candidates:
                unique_candidates[key] = span
        
        candidates = list(unique_candidates.values())
        
        # Step 3: Send candidates to API for Cerebras reranking
        rerank_request = {
            "query": query,
            "candidates": candidates,
            "max_results": max_results
        }
        
        response = self.client.post(
            "/v1/rerank",
            json=rerank_request
        )
        response.raise_for_status()
        
        return SearchResponse(**response.json())
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        directory: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any] | Iterator[Dict[str, Any]]:
        """
        Use OpenAI-compatible chat completions with code search tools.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            directory: Working directory for code operations
            stream: Whether to stream the response
            
        Returns:
            Chat completion response or iterator if streaming
            
        Example:
            ```python
            response = client.chat(
                messages=[
                    {"role": "user", "content": "Find all API endpoints in the backend"}
                ],
                directory="./backend"
            )
            ```
        """
        payload = {
            "model": "greb",
            "messages": messages,
            "stream": stream
        }
        
        if directory:
            payload["metadata"] = {"directory": directory}
        
        if stream:
            return self._stream_chat(payload)
        else:
            response = self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()
    
    def _stream_chat(self, payload: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Stream chat completion responses."""
        with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data.strip() != "[DONE]":
                        yield eval(data)  # Parse JSON
    
    def get_file(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get file content with optional line range.
        
        Args:
            file_path: Path to the file
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (inclusive)
            
        Returns:
            File content and metadata
        """
        params = {"file_path": file_path}
        if start_line is not None:
            params["start_line"] = start_line
        if end_line is not None:
            params["end_line"] = end_line
        
        response = self.client.get("/file", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_usage(self) -> Dict[str, Any]:
        """
        Get current API usage statistics.
        
        Returns:
            Usage statistics including requests, tokens, and credits
        """
        response = self.client.get("/usage")
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = self.client.get("/health")
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncGrebClient:
    """
    Async Python client for Greb API.
    
    Usage:
        ```python
        from greb import AsyncGrebClient
        
        async with AsyncGrebClient(api_key="grb_your_key") as client:
            results = await client.search(
                query="Find authentication logic",
                directory="./src"
            )
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ):
        self.api_key = api_key or os.getenv("GREB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Set GREB_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.base_url = base_url or os.getenv("GREB_API_URL")
        if not self.base_url:
            raise ValueError(
                "API base URL is required. Set GREB_API_URL environment variable "
                "or pass base_url parameter."
            )
        
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "swe-grep-python/1.0.0"
            }
        )
    
    async def search(
        self,
        query: str,
        directory: Optional[str] = None,
        file_patterns: Optional[List[str]] = None,
        max_results: Optional[int] = None
    ) -> SearchResponse:
        """Async version of search."""
        request = SearchRequest(
            query=query,
            directory=directory,
            file_patterns=file_patterns,
            max_results=max_results
        )
        
        response = await self.client.post(
            "/search",
            json=request.model_dump(exclude_none=True)
        )
        response.raise_for_status()
        
        return SearchResponse(**response.json())
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        directory: Optional[str] = None,
        stream: bool = False
    ):
        """Async version of chat."""
        payload = {
            "model": "greb",
            "messages": messages,
            "stream": stream
        }
        
        if directory:
            payload["metadata"] = {"directory": directory}
        
        if stream:
            return self._stream_chat(payload)
        else:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()
    
    async def _stream_chat(self, payload: Dict[str, Any]):
        """Stream chat completion responses asynchronously."""
        async with self.client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() != "[DONE]":
                        yield eval(data)
    
    async def get_file(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> Dict[str, Any]:
        """Async version of get_file."""
        params = {"file_path": file_path}
        if start_line is not None:
            params["start_line"] = start_line
        if end_line is not None:
            params["end_line"] = end_line
        
        response = await self.client.get("/file", params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_usage(self) -> Dict[str, Any]:
        """Async version of get_usage."""
        response = await self.client.get("/usage")
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Async version of health_check."""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the async HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Convenience exports
__all__ = [
    "GrebClient",
    "AsyncGrebClient",
    "SearchRequest",
    "SearchResponse",
    "SearchResult",
    "ClientConfig",
]
