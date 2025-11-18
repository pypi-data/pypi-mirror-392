"""
Greb: AI-powered code search and analysis service

Available as:
1. Python package - pip install cheetah-greb
2. MCP Server - For Claude Desktop, Cline, Cursor, Windsurf
3. API Service - Usage-based billing with API keys

Usage:
    from greb import GrebClient
    
    client = GrebClient(api_key="grb_your_api_key")
    results = client.search(
        query="Find authentication middleware",
        directory="./src",
        file_patterns=["*.py", "*.js"]
    )
"""

__version__ = "1.2.2"

# Only expose search-based client (chat/completions removed)
from .client import (
    GrebClient,
    AsyncGrebClient,
    SearchRequest,
    SearchResponse,
    SearchResult,
    ClientConfig,
)

__all__ = [
    "GrebClient",
    "AsyncGrebClient",
    "SearchRequest",
    "SearchResponse",
    "SearchResult",
    "ClientConfig",
    "__version__",
]
