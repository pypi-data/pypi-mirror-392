"""
Pipeline orchestrator that coordinates all Greb tools.
"""
from __future__ import annotations
import time
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import FileSpan, CandidateMatch, PipelineConfig, QueryResponse, RankedResult
from .grep import GrepTool
from .glob import GlobTool
from .read import ReadTool
from .rerank import RerankTool
from .keyword_extractor import KeywordExtractor
from .token_tracker import token_tracker
class PipelineOrchestrator:
    """Orchestrates the complete Greb pipeline."""
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.grep_tool = GrepTool(max_results=config.max_grep_results)
        self.glob_tool = GlobTool(max_results=config.max_glob_results)
        self.read_tool = ReadTool(max_file_size=config.read_max_file_size)
        self.rerank_tool = RerankTool(config)
        self.keyword_extractor = KeywordExtractor(config)
    def search(
        self,
        query: str,
        directory: Optional[str] = None,
        file_patterns: Optional[List[str]] = None,
        max_results: Optional[int] = None,
        server_client=None
    ) -> QueryResponse:
        """
        Execute the complete search pipeline.
        Args:
            query: Natural language search query
            directory: Directory to search in (default: current)
            file_patterns: File patterns to constrain search
            max_results: Override default max results
        Returns:
            QueryResponse with ranked results
        """
        start_time = time.time()
        # Reset token tracker for this request
        token_tracker.reset()
        # Set defaults
        max_results = max_results or self.config.top_k_results
        directory = directory or "."
        # Smart tool selection: Auto-detect directory size and choose optimal tools
        import os as os_module
        # Quick file count (only counts, doesn't read)
        file_count = 0
        if os_module.path.exists(directory):
            # Fast estimation: count top-level files + sample subdirectories
            for root, dirs, files in os_module.walk(directory):
                file_count += len(files)
                # Stop counting after threshold to save time
                if file_count > 10000:
                    break
        # Choose tools based on directory size
            # Always use only fast tools - glob is too slow (113 seconds for 10k files)
        tools = ["grep", "read"]
        # 1. Extract keywords using Python server
        if not server_client:
            raise ValueError("server_client is required for keyword extraction")

        keyword_response = server_client.post(
            "/v1/extract-keywords",
            json={"query": query}
        )
        keyword_response.raise_for_status()
        keyword_data = keyword_response.json()

        from .base import ExtractedKeywords
        extracted_keywords = ExtractedKeywords(
            primary_terms=keyword_data.get("primary_terms", []),
            search_terms=keyword_data.get("search_terms", []),
            file_patterns=keyword_data.get("file_patterns", []),
            intent=keyword_data.get("intent", query)
        )
        # Use extracted file patterns if none provided
        if file_patterns is None:
            file_patterns = extracted_keywords.file_patterns

        # Multi-turn parallel search (optimized for speed)
        # Dynamic scaling based on system resources
        import os
        cpu_count = os.cpu_count() or 4
        MAX_TURNS = int(os.getenv("MAX_TURNS", "2"))  # Single turn for max speed
        # Scale parallel searches to match system capacity (8x CPU cores for I/O-bound grep)
        optimal_parallel = min(cpu_count * 8, int(os.getenv('MAX_PARALLEL_SEARCHES', '128')))
        MAX_PARALLEL_SEARCHES = optimal_parallel
        all_candidates: List[CandidateMatch] = []
        for turn in range(1, MAX_TURNS):
            turn_start = time.time()
            # Determine which search terms to use for this turn
            # Turn 1: Primary terms, Turn 2: Secondary terms
            if turn == 1:
                search_terms = extracted_keywords.primary_terms[:MAX_PARALLEL_SEARCHES]
            else:
                # Turn 2: Secondary terms + remaining primary terms
                search_terms = extracted_keywords.search_terms[:MAX_PARALLEL_SEARCHES]
            # Execute parallel searches within this turn
            turn_candidates = []
            with ThreadPoolExecutor(max_workers=MAX_PARALLEL_SEARCHES) as executor:
                futures = []
                # Submit up to 8 parallel grep searches
                for i, term in enumerate(search_terms):
                    if "grep" in tools:
                        future = executor.submit(
                            self.grep_tool.search,
                            query=term,
                            directory=directory,
                            file_patterns=file_patterns,
                            case_sensitive=False,
                            context_lines=2
                        )
                        futures.append(('grep', term, future))
                # Execute glob search in parallel if enabled
                if "glob" in tools and turn == 1:
                    future = executor.submit(
                        self.glob_tool.find_files,
                        patterns=file_patterns or ["*"],
                        directory=directory,
                        recursive=True
                    )
                    futures.append(('glob', 'pattern_search', future))
                # Wait for all parallel searches to complete
                for tool_name, search_term, future in futures:
                    try:
                        if tool_name == 'grep':
                            results = future.result()
                            turn_candidates.extend(results)
                        elif tool_name == 'glob':
                            files = future.result()
                            glob_candidates = self.glob_tool.create_candidates_from_files(files, directory)
                            turn_candidates.extend(glob_candidates)
                    except Exception as e:
                        print(f"     [WARNING]  Search failed for '{search_term}': {e}")
            turn_time = (time.time() - turn_start) * 1000
            all_candidates.extend(turn_candidates)
        # 5. Remove duplicates and limit candidates
        dedup_start = time.time()
        unique_candidates = self._deduplicate_candidates(all_candidates)
        unique_candidates = unique_candidates[:self.config.max_grep_results]
        dedup_time = (time.time() - dedup_start) * 1000
        # 6. Read file contents - use environment variables directly from read tool
        read_start = time.time()
        spans = self.read_tool.read_spans_from_candidates(
            unique_candidates,
            max_spans=self.config.max_grep_results
        )
        read_time = (time.time() - read_start) * 1000
        # 7. Re-rank using Python server (passing spans with context to /v1/rerank)
        rerank_start = time.time()

        # Convert spans (with full context) to format expected by rerank API
        rerank_candidates = []
        for span in spans:
            rerank_candidates.append({
                "path": span.path,
                "start_line": span.start_line,
                "end_line": span.end_line,
                "content": span.text,  # This contains full context: lines 15-25
                "score": 0.0
            })

        # Send candidates to Python server for reranking
        rerank_response = server_client.post(
            "/v1/rerank",
            json={
                "query": query,
                "candidates": rerank_candidates,
                "max_results": max_results
            }
        )
        rerank_response.raise_for_status()
        rerank_data = rerank_response.json()
        rerank_time = (time.time() - rerank_start) * 1000
        # Convert server response to RankedResult objects
        ranked_results = []
        for result in rerank_data.get('results', []):
            ranked_results.append(RankedResult(
                path=result.get('path', ''),
                score=result.get('score', 0.0),
                highlights=result.get('highlights', []),
                summary=result.get('summary'),
                file_info=result.get('file_info'),
                reasoning=result.get('reasoning')
            ))
        # 8. Generate overall reasoning and create response
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        # Use server reasoning response instead of direct Cerebras call
        overall_reasoning = None
        # Results are already enhanced from rerank tool, no need for additional processing
        enhanced_results = ranked_results
        # Get reasoning and token usage from server response
        overall_reasoning = rerank_data.get('overall_reasoning')
        token_usage = rerank_data.get('token_usage')
        return QueryResponse(
            results=ranked_results,
            total_candidates=len(unique_candidates),
            query=query,
            overall_reasoning=overall_reasoning,
            token_usage=token_usage
        )
    def _execute_grep_search_with_keywords(
        self,
        keywords,
        directory: str,
        file_patterns: Optional[List[str]]
    ) -> List[CandidateMatch]:
        """Execute grep search using Cerebras-extracted keywords."""
        candidates = []
        for term in keywords.search_terms:
            matches = self.grep_tool.search(
                query=term,
                directory=directory,
                file_patterns=file_patterns,
                case_sensitive=False,
                context_lines=2
            )
            candidates.extend(matches)
        return candidates
    def _execute_glob_search_with_keywords(
        self,
        keywords,
        directory: str,
        file_patterns: Optional[List[str]]
    ) -> List[CandidateMatch]:
        """Execute glob search using extracted keywords."""
        # Use keywords file patterns if none provided
        if file_patterns is None:
            file_patterns = keywords.file_patterns
        files = self.glob_tool.find_files(
            patterns=file_patterns,
            directory=directory,
            recursive=True
        )
        return self.glob_tool.create_candidates_from_files(files, directory)
    def _deduplicate_candidates(self, candidates: List[CandidateMatch]) -> List[CandidateMatch]:
        """Remove duplicate candidates based on path and line number."""
        seen = set()
        unique = []
        for candidate in candidates:
            key = (candidate.path, candidate.line_number)
            if key not in seen:
                seen.add(key)
                unique.append(candidate)
        return unique
    def get_file_content(self, file_path: str, line_range: Optional[tuple] = None) -> FileSpan:
        """
        Get content for a specific file.
        Args:
            file_path: Path to the file
            line_range: Optional (start, end) tuple for specific lines
        Returns:
            FileSpan with the requested content
        """
        if line_range:
            return self.read_tool.read_file(
                file_path=file_path,
                start_line=line_range[0],
                end_line=line_range[1]
            )
        else:
            return self.read_tool.read_file(file_path=file_path)
    def search_in_file(
        self,
        file_path: str,
        query: str,
        context_lines: int = 5
    ) -> List[FileSpan]:
        """
        Search within a specific file.
        Args:
            file_path: Path to the file
            query: Natural language search query
            context_lines: Number of context lines
        Returns:
            List of matching FileSpans
        """
        # Extract keywords from natural language query
        extracted_keywords = self.keyword_extractor.extract_keywords(query)
        return self.read_tool.search_and_read(
            file_path=file_path,
            search_terms=extracted_keywords.search_terms,
            context_lines=context_lines
        )