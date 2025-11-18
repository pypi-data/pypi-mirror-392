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
        max_results: Optional[int] = None
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
        if file_count > 10000:
            # Large codebase: Use only fast tools (grep uses ripgrep with exclusions)
            tools = ["grep", "read"]
            print(f"[DIR] Large directory detected ({file_count}+ files) - using fast tools: grep + read")
        else:
            # Small codebase: Use all tools for better quality
            tools = ["grep", "glob", "read"]
            print(f"[DIR] Small directory detected ({file_count} files) - using all tools for better quality")

        # 1. Extract keywords using Cerebras
        extracted_keywords = self.keyword_extractor.extract_keywords(query)

        # Use extracted file patterns if none provided
        if file_patterns is None:
            file_patterns = extracted_keywords.file_patterns

        # Multi-turn parallel search (inspired by SWE-grep)
        # Max 4 turns: 3 exploration turns + 1 final answer
        MAX_TURNS = 4
        MAX_PARALLEL_SEARCHES = 8
        
        all_candidates: List[CandidateMatch] = []
        
        for turn in range(1, MAX_TURNS):
            print(f"[SEARCH] Turn {turn}/{MAX_TURNS - 1}: Running parallel searches...")
            turn_start = time.time()
            
            # Determine which search terms to use for this turn
            # Turn 1: Primary terms, Turn 2: Secondary terms, Turn 3: Broader search
            if turn == 1:
                search_terms = extracted_keywords.primary_terms[:MAX_PARALLEL_SEARCHES]
            elif turn == 2:
                search_terms = extracted_keywords.search_terms[:MAX_PARALLEL_SEARCHES]
            else:
                # Turn 3: Mix of all terms
                search_terms = (extracted_keywords.primary_terms + extracted_keywords.search_terms)[:MAX_PARALLEL_SEARCHES]
            
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
                        print(f"  [WARNING]  Search failed for '{search_term}': {e}")
            
            turn_time = (time.time() - turn_start) * 1000
            print(f"  ⏱️  Turn {turn}: {len(turn_candidates)} candidates in {turn_time:.2f}ms")
            
            all_candidates.extend(turn_candidates)

        # 5. Remove duplicates and limit candidates
        dedup_start = time.time()
        unique_candidates = self._deduplicate_candidates(all_candidates)
        unique_candidates = unique_candidates[:self.config.max_grep_results]
        dedup_time = (time.time() - dedup_start) * 1000
        print(f"  ⏱️  Deduplication: {len(unique_candidates)} unique from {len(all_candidates)} total in {dedup_time:.2f}ms")

        # 6. Read file contents - use environment variables directly from read tool
        read_start = time.time()
        spans = self.read_tool.read_spans_from_candidates(
            unique_candidates,
            max_spans=self.config.max_grep_results
        )
        read_time = (time.time() - read_start) * 1000
        print(f"  ⏱️  Read spans: {len(spans)} spans in {read_time:.2f}ms")

        # 7. Re-rank with Cerebras (passing original natural query)
        rerank_start = time.time()
        ranked_results = self.rerank_tool.rerank_spans_with_context(
            natural_query=query,
            extracted_keywords=extracted_keywords,
            spans=spans,
            top_k=max_results
        )
        rerank_time = (time.time() - rerank_start) * 1000
        print(f"  ⏱️  Reranking: {len(ranked_results)} results in {rerank_time:.2f}ms")

        # 8. Generate overall reasoning and create response
        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # Generate overall reasoning using Cerebras
        overall_reasoning = None
        if ranked_results:
            reasoning_messages = [
                {
                    "role": "system",
                    "content": "You are a code search assistant. Provide a brief summary of how these results address the user's query."
                },
                {
                    "role": "user",
                    "content": f"""User Query: "{query}"
User Intent: {extracted_keywords.intent}

Top Results:
{chr(10).join([f"- {r.path} (score: {r.score:.2f}){chr(10)}  {r.highlights[0].get('summary', 'No summary') if r.highlights else 'No summary'}" for r in ranked_results[:3]])}

Provide a brief summary of how these results help solve the user's problem."""
                }
            ]

            reasoning_response = self.rerank_tool.client.chat.completions.create(
                model=self.config.cerebras_model,
                messages=reasoning_messages,
                temperature=0,
                max_tokens=300
            )

            # Track token usage from overall reasoning with messages
            token_tracker.track_reasoning(reasoning_response, reasoning_messages)

            overall_reasoning = reasoning_response.choices[0].message.content

        # Results are already enhanced from rerank tool, no need for additional processing
        enhanced_results = ranked_results

        # Get token usage from tracker
        token_usage = token_tracker.get_summary_dict()

        return QueryResponse(
            results=enhanced_results,
            total_candidates=len(unique_candidates),
            query=query,
            execution_time_ms=execution_time,
            extracted_keywords={
                "primary_terms": extracted_keywords.primary_terms,
                "search_terms": extracted_keywords.search_terms,
                "intent": extracted_keywords.intent,
                "file_patterns": extracted_keywords.file_patterns
            },
            tools_used=tools,
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