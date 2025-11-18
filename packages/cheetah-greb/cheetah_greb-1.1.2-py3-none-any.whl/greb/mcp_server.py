"""
Greb MCP Server using FastMCP for AI-powered code search.
Provides tools for code search, file reading, and usage statistics.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("greb")

# Configuration
API_BASE = os.getenv("GREB_API_URL", "http://localhost:8000")
USER_AGENT = "greb-mcp/1.0"


async def make_greb_request(method: str, url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Make a request to the Greb API with proper error handling."""
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=json_data, timeout=30.0)
            else:
                return None

            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request error: {e}", file=sys.stderr)
            return None


@mcp.tool()
async def code_search(query: str, directory: str = ".", file_patterns: List[str] = None, max_results: int = 10) -> str:
    """Search code using natural language queries powered by AI.

    Args:
        query: Natural language description of what to find
        directory: FULL ABSOLUTE PATH to directory to search in (required for MCP, optional, default: current directory)
        file_patterns: File patterns to filter (optional)
        max_results: Maximum number of results (optional, default: 10)

    IMPORTANT FOR MCP: Always provide the full absolute path to the directory.
    Examples:
        - Windows: "D:\\greb_website\\backend" or "C:\\myproject\\src"
        - Linux/Mac: "/home/user/myproject/backend" or "/Users/username/project/src"
        - Do NOT use relative paths like "backend" or "src" - they will not work correctly.
    """
    # Get API key from environment
    api_key = os.getenv("GREB_API_KEY")
    if not api_key:
        return "Error: GREB_API_KEY environment variable is required"

    # Directory validation - MCP requires absolute paths
    if directory and not os.path.isabs(directory):
        return f"Error: MCP requires absolute paths for directory. Got '{directory}'. Please use full path (Windows: D:\\project\\backend, Linux/Mac: /home/user/project/backend) instead of relative paths."

    if directory == ".":
        directory = os.getcwd()  # Use current working directory

    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json"
    }

    # Step 1: Call server to extract keywords using Cerebras
    keyword_url = f"{API_BASE}/v1/extract-keywords"
    keyword_data = await make_greb_request("POST", keyword_url, headers, json_data={"query": query})
    
    if not keyword_data:
        return "Failed to extract keywords from API."
    
    keywords = keyword_data.get("search_terms", []) or keyword_data.get("primary_terms", [])
    if not keywords:
        return f"Server failed to extract keywords from query: {query}"
    
    # Step 2: Run full orchestrator pipeline LOCALLY
    from .pipeline.orchestrator import PipelineOrchestrator
    from .pipeline.base import PipelineConfig, ExtractedKeywords
    from concurrent.futures import ThreadPoolExecutor
    
    print(f"MCP: Running local search pipeline in {directory}", file=sys.stderr)
    
    # Create local orchestrator config (no Cerebras key needed for local operations)
    local_config = PipelineConfig(
        cerebras_api_key="",  # Not used locally
        max_grep_results=int(os.getenv("MAX_GREP_RESULTS", "1500")),
        max_glob_results=int(os.getenv("MAX_GLOB_RESULTS", "50")),
        top_k_results=max_results or int(os.getenv("TOP_K_RESULTS", "10"))
    )
    
    local_orchestrator = PipelineOrchestrator(local_config)
    
    # Prepare extracted keywords
    extracted_keywords = ExtractedKeywords(
        primary_terms=keyword_data.get("primary_terms", []),
        search_terms=keywords,
        file_patterns=file_patterns or keyword_data.get("file_patterns", []),
        intent=keyword_data.get("intent", query)
    )
    
    # Execute parallel grep searches with orchestrator logic
    all_spans = []
    MAX_PARALLEL_SEARCHES = 8
    
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_SEARCHES) as executor:
        futures = []
        search_terms = extracted_keywords.search_terms[:MAX_PARALLEL_SEARCHES]
        
        for term in search_terms:
            future = executor.submit(
                local_orchestrator.grep_tool.grep,
                pattern=term,
                path=directory,
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
                print(f"MCP: Grep failed for '{term}': {e}", file=sys.stderr)
    
    # Deduplicate candidates
    unique_candidates = {}
    for span in all_spans:
        key = (span["path"], span["line_number"])
        if key not in unique_candidates:
            unique_candidates[key] = span
    candidates = list(unique_candidates.values())
    
    if not candidates:
        return f"No matches found locally for query: '{query}'"
    
    # Step 3: Send candidates to API for Cerebras reranking
    rerank_request = {
        "query": query,
        "candidates": candidates,
        "max_results": max_results
    }

    # Make POST request to rerank API
    rerank_url = f"{API_BASE}/v1/rerank"
    data = await make_greb_request("POST", rerank_url, headers, json_data=rerank_request)

    if not data:
        return "Failed to fetch reranked results from API."

    # Format results for better readability
    results = data.get("results", [])
    if not results:
        return f"No results found for query: '{query}'"

    formatted_results = [f"## Found {len(results)} results for: {query}\n"]

    for i, result in enumerate(results, 1):
        path = result.get('path', 'Unknown')
        score = result.get('score', 0)
        summary = result.get('summary', '')
        highlights = result.get('highlights', [])

        formatted_result = f"\n### {i}. {path}\n"
        formatted_result += f"**Relevance Score:** {score:.3f}\n"

        if summary:
            # Clean up Unicode in summary
            try:
                safe_summary = summary.encode('ascii', 'ignore').decode('ascii').strip()
                formatted_result += f"**Summary:** {safe_summary}\n"
            except:
                formatted_result += f"**Summary:** (Summary unavailable)\n"

        if highlights:
            formatted_result += "**Key Highlights:**\n"
            for highlight in highlights[:3]:  # Show top 3 highlights
                if isinstance(highlight, dict):
                    # Use the full span information with line numbers and code
                    span = highlight.get('span', {})
                    reason = highlight.get('reason', 'Code found here')
                    line_start = span.get('start_line', 1)
                    line_end = span.get('end_line', line_start)
                    code_text = span.get('text', '')

                    # Clean up Unicode characters in reason and code
                    try:
                        safe_reason = reason.encode('ascii', 'ignore').decode('ascii').strip()
                    except:
                        safe_reason = "Code found here"

                    try:
                        safe_code_text = code_text.encode('ascii', 'ignore').decode('ascii')
                    except:
                        safe_code_text = ""

                    formatted_result += f"- **Lines {line_start}-{line_end}:** {safe_reason}\n"
                    if safe_code_text and safe_code_text.strip():
                        # Format code snippet nicely
                        code_lines = safe_code_text.strip().split('\n')
                        for line in code_lines:
                            formatted_result += f"  ```{line}```\n"
                        formatted_result += "\n"
                    else:
                        # Add a note when no code is available
                        formatted_result += f"  *(No code snippet available)*\n\n"
                elif isinstance(highlight, str):
                    # Clean up Unicode in string highlights
                    try:
                        safe_highlight = highlight.encode('ascii', 'ignore').decode('ascii').strip()
                        formatted_result += f"- {safe_highlight}\n"
                    except:
                        formatted_result += f"- (Highlight text unavailable)\n"

        formatted_results.append(formatted_result)

    # Add execution info if available
    if data.get("execution_time_ms"):
        formatted_results.append(f"\n**Search completed in:** {data['execution_time_ms']:.2f}ms")

    if data.get("extracted_keywords"):
        keywords = data["extracted_keywords"]
        if isinstance(keywords, dict):
            # Detailed keyword breakdown
            formatted_results.append(f"\n**Search Analysis:**")
            if keywords.get("primary_terms"):
                formatted_results.append(f"- **Primary Terms:** {', '.join(keywords['primary_terms'])}")
            if keywords.get("search_terms"):
                formatted_results.append(f"- **Search Terms:** {', '.join(keywords['search_terms'])}")
            if keywords.get("intent"):
                formatted_results.append(f"- **Intent:** {keywords['intent']}")
        elif isinstance(keywords, list):
            formatted_results.append(f"\n**Extracted Keywords:** {', '.join(keywords)}")

    # Add overall reasoning if available
    if data.get("overall_reasoning"):
        reasoning = data["overall_reasoning"]
        # Clean up Unicode in reasoning
        try:
            safe_reasoning = reasoning.encode('ascii', 'ignore').decode('ascii').strip()
            formatted_results.append(f"\n**Summary:**\n{safe_reasoning}")
        except:
            formatted_results.append(f"\n**Summary:**\n(Reasoning unavailable due to encoding issues)")

    # Handle Unicode characters properly for Windows
    try:
        return "\n".join(formatted_results)
    except UnicodeEncodeError:
        # Fallback: replace problematic Unicode characters
        safe_results = []
        for line in formatted_results:
            safe_line = line.encode('ascii', 'ignore').decode('ascii')
            safe_results.append(safe_line)
        return "\n".join(safe_results)


# REMOVED: read_file tool - MCP client should use its own file reading capabilities
# The code_search tool now returns file paths and relevant snippets for the client to read

# REMOVED: get_usage_stats tool - Usage statistics not yet fully implemented


def main():
    """Initialize and run the server exactly like in official docs."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()