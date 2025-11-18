"""
Greb MCP Server using FastMCP for AI-powered code search.
Provides tools for code search, file reading, and usage statistics.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

class SyncHttpClientWrapper:
    """Wrapper to provide synchronous HTTP client for orchestrator."""

    def __init__(self, base_url: str, headers: dict):
        # Create a synchronous client using the same config as async client
        self.client = httpx.Client(
            base_url=base_url,
            timeout=30.0,
            headers=headers
        )

    def post(self, url: str, **kwargs):
        """Make synchronous post call."""
        return self.client.post(url, **kwargs)

    def get(self, url: str, **kwargs):
        """Make synchronous get call."""
        return self.client.get(url, **kwargs)

    def close(self):
        """Close the client."""
        self.client.close()

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

    # Use orchestrator pipeline - all custom logic removed
    from .pipeline.orchestrator import PipelineOrchestrator
    from .pipeline.base import PipelineConfig

  
    # Create orchestrator config - server handles all Cerebras calls
    orchestrator_config = PipelineConfig(
        cerebras_api_key="",  # Server handles Cerebras
        max_grep_results=int(os.getenv("MAX_GREP_RESULTS", "10000")),
        max_glob_results=int(os.getenv("MAX_GLOB_RESULTS", "10")),
        top_k_results=max_results or int(os.getenv("TOP_K_RESULTS", "10"))
    )

    orchestrator = PipelineOrchestrator(orchestrator_config)

    # Create synchronous HTTP client for orchestrator
    sync_client = SyncHttpClientWrapper(API_BASE, headers)

    try:
        # Use main search method - orchestrator handles keyword extraction and reranking via server
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: orchestrator.search(
                query=query,
                directory=directory,
                file_patterns=file_patterns,
                max_results=max_results,
                server_client=sync_client
            )
        )
    finally:
        # Clean up the synchronous client
        sync_client.close()

    # Format results for MCP output
    results = response.results
    if not results:
        return f"No results found for query: '{query}'"

    formatted_results = [f"## Found {len(results)} results for: {query}\n"]

    for i, result in enumerate(results, 1):
        path = result.path
        score = result.score
        summary = getattr(result, 'summary', '')
        highlights = getattr(result, 'highlights', [])

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
                        formatted_result += f"  *(No code snippet available)*\n\n"
                elif isinstance(highlight, str):
                    try:
                        safe_highlight = highlight.encode('ascii', 'ignore').decode('ascii').strip()
                        formatted_result += f"- {safe_highlight}\n"
                    except:
                        formatted_result += f"- (Highlight text unavailable)\n"

        formatted_results.append(formatted_result)

    
    # Add overall reasoning
    if response.overall_reasoning:
        reasoning = response.overall_reasoning
        try:
            safe_reasoning = reasoning.encode('ascii', 'ignore').decode('ascii').strip()
            formatted_results.append(f"\n**Summary:**\n{safe_reasoning}")
        except:
            formatted_results.append(f"\n**Summary:**\n(Reasoning unavailable due to encoding issues)")

    # Handle Unicode characters properly for Windows
    try:
        return "\n".join(formatted_results)
    except UnicodeEncodeError:
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