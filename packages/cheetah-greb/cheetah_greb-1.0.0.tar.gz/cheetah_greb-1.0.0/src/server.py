"""
Greb API Server for code search.

Token Counting Standard:
    - 1 token = 4 characters (standard for OpenAI/Cerebras APIs)
    - Input tokens: query text
    - Output tokens: results JSON serialized
    
Pricing:
    - Input: $0.45 per 1M tokens
    - Output: $0.85 per 1M tokens
    - 1 credit = $0.01 USD
    
Example: 
    - Query "find auth" (9 chars) + results (400 chars) = 2 input + 100 output tokens
    - Cost: (2/1M × $0.45) + (100/1M × $0.85) = $0.000085 ≈ 1 credit
"""

from __future__ import annotations

import os
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Union, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends, Response, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

from .pipeline.orchestrator import PipelineOrchestrator
from .pipeline.base import PipelineConfig, RankedResult
from .auth_middleware import get_current_user as _get_current_user, UsageTracker, APIKeyValidator


class ModelInfo(BaseModel):
    """Model information for /models endpoint."""
    id: str
    object: str = "model"
    created: int = int(time.time())
    owned_by: str = "greb"


class ModelsResponse(BaseModel):
    """Response for /models endpoint."""
    object: str = "list"
    data: List[ModelInfo]


# Load environment variables at module import time
load_dotenv()

# Global orchestrator instance
orchestrator: Optional[PipelineOrchestrator] = None

# Create security scheme and validator instance for dependency injection
security = HTTPBearer()
validator = APIKeyValidator()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """Wrapper for get_current_user without optional parameters."""
    return await _get_current_user(credentials, validator)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global orchestrator

    # Initialize the orchestrator on startup
    try:
        config = PipelineConfig(
            cerebras_api_key=os.getenv("CEREBRAS_API_KEY", ""),
            cerebras_base_url=os.getenv("CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1"),
            cerebras_model=os.getenv("CEREBRAS_MODEL", "gpt-oss-120b"),
            max_grep_results=int(os.getenv("MAX_GREP_RESULTS", "100")),
            max_glob_results=int(os.getenv("MAX_GLOB_RESULTS", "50")),
            context_window_size=int(os.getenv("CONTEXT_WINDOW_SIZE", "10")),
            top_k_results=int(os.getenv("TOP_K_RESULTS", "5")),
            rerank_temperature=float(os.getenv("RERANK_TEMPERATURE", "0.1")),
            # Read tool configuration
            read_max_file_size=int(os.getenv("READ_MAX_FILE_SIZE", "1048576")),
            read_window_size=int(os.getenv("READ_WINDOW_SIZE", "10")),
            read_max_spans=int(os.getenv("READ_MAX_SPANS", "50")),
            read_max_lines_per_file=int(os.getenv("READ_MAX_LINES_PER_FILE", "100")),
            read_context_lines=int(os.getenv("READ_CONTEXT_LINES", "5")),
            read_binary_sample_size=int(os.getenv("READ_BINARY_SAMPLE_SIZE", "1024")),
            read_generic_window_size=int(os.getenv("READ_GENERIC_WINDOW_SIZE", "10"))
        )

        if not config.cerebras_api_key:
            print("Warning: CEREBRAS_API_KEY not set, reranking will be disabled")

        orchestrator = PipelineOrchestrator(config)
        print("Greb pipeline initialized successfully")

    except Exception as e:
        print(f"Failed to initialize Greb pipeline: {e}")
        orchestrator = None

    yield

    # Cleanup on shutdown
    orchestrator = None


# Create FastAPI app
app = FastAPI(
    title="Greb API",
    description="OpenAI-compatible API for Greb code search",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Greb API Server",
        "version": "1.0.0",
        "endpoints": {
            "search": "/v1/search",
            "models": "/v1/models",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global orchestrator

    return {
        "status": "healthy" if orchestrator else "unhealthy",
        "pipeline_initialized": orchestrator is not None,
        "timestamp": time.time()
    }


@app.get("/v1/models", response_model=ModelsResponse)
async def list_models():
    """List available models."""
    return ModelsResponse(
        data=[
            ModelInfo(id="greb")
        ]
    )


@app.get("/v1/models/{model_id}")
async def get_model(model_id: str):
    """Get model information."""
    if model_id != "greb":
        raise HTTPException(status_code=404, detail="Model not found")

    return ModelInfo(id=model_id)


class SearchRequest(BaseModel):
    """Direct search request (non-chat format)."""
    query: str
    directory: Optional[str] = None
    file_patterns: Optional[List[str]] = None
    max_results: Optional[int] = None


@app.post("/v1/search")
async def search_code(
    request: SearchRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Direct code search endpoint (simpler than chat/completions).

    This is what the Python SDK uses.
    """
    global orchestrator

    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Greb pipeline not initialized. Check server logs."
        )
    
    # Initialize usage tracker
    tracker = UsageTracker()
    api_key = user.get("api_key")

    try:
        # Execute search pipeline - orchestrator handles all logic
        import time as time_module
        search_start = time_module.time()
        
        print(f"Searching for: {request.query}")
        print(f"Directory: {request.directory or 'current'}")
        print(f"Max results: {request.max_results or 'default (config.top_k_results)'}")
        
        # Count files in directory for debugging
        import os as os_module
        search_dir = request.directory or "."
        if os_module.path.exists(search_dir):
            file_count = sum(len(files) for _, _, files in os_module.walk(search_dir))
            print(f"Total files in directory: {file_count}")
        
        # Run blocking orchestrator.search() in thread pool to avoid blocking async event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,  # Use default ThreadPoolExecutor
            lambda: orchestrator.search(
                query=request.query,
                directory=request.directory,
                file_patterns=request.file_patterns,
                max_results=request.max_results
            )
        )
        
        search_time = (time_module.time() - search_start) * 1000
        print(f"Search completed: {len(response.results)} results in {search_time:.2f}ms (orchestrator: {response.execution_time_ms}ms)")

        # Get actual token usage from Cerebras API responses
        token_usage = response.token_usage or {}
        total_usage = token_usage.get('total', {})
        input_tokens = total_usage.get('prompt_tokens', 0)
        output_tokens = total_usage.get('completion_tokens', 0)
        total_tokens = total_usage.get('total_tokens', 0)

        # Calculate cost breakdown
        keyword_stats = token_usage.get('keyword_extraction', {})
        rerank_stats = token_usage.get('reranking', {})
        reasoning_stats = token_usage.get('reasoning', {})

        keyword_input = keyword_stats.get('prompt_tokens', 0)
        keyword_output = keyword_stats.get('completion_tokens', 0)
        keyword_total = keyword_stats.get('total_tokens', 0)

        rerank_input = rerank_stats.get('prompt_tokens', 0)
        rerank_output = rerank_stats.get('completion_tokens', 0)
        rerank_total = rerank_stats.get('total_tokens', 0)

        reasoning_input = reasoning_stats.get('prompt_tokens', 0)
        reasoning_output = reasoning_stats.get('completion_tokens', 0)
        reasoning_total = reasoning_stats.get('total_tokens', 0)

        # Track usage SYNCHRONOUSLY - wait for backend to confirm
        print(f"COMPLETE TOKEN BREAKDOWN:")
        print(f"   - Keyword Extraction: {keyword_input} input + {keyword_output} output = {keyword_total} tokens")
        print(f"   - Re-ranking: {rerank_input} input + {rerank_output} output = {rerank_total} tokens")
        print(f"     (Includes grep results sent for re-ranking)")
        print(f"   - Reasoning: {reasoning_input} input + {reasoning_output} output = {reasoning_total} tokens")
        print(f"   - TOTAL: {input_tokens} input + {output_tokens} output = {total_tokens} tokens")

        # Calculate costs using your pricing ($0.45/1M input, $0.85/1M output)
        input_cost = (input_tokens / 1000000) * 0.45
        output_cost = (output_tokens / 1000000) * 0.85
        total_cost = input_cost + output_cost
        print(f"COST CALCULATION: ${input_cost:.6f} input + ${output_cost:.6f} output = ${total_cost:.6f} total")

        try:
            tracking_success = await tracker.track(
                api_key=api_key,
                endpoint="/v1/search",
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            if tracking_success:
                print(f"Usage tracked successfully in backend")
            else:
                print(f"WARNING: Usage tracking returned false - backend may not have updated")
        except Exception as tracking_error:
            print(f"CRITICAL: Failed to track usage: {tracking_error}")
            # Still return results but log the error
            import traceback
            traceback.print_exc()

        # Return response directly from orchestrator
        return {
            "results": [
                {
                    "path": r.path,
                    "score": r.score,
                    "highlights": r.highlights,
                    "summary": r.highlights[0].get("summary") if r.highlights else None
                }
                for r in response.results
            ],
            "total_candidates": response.total_candidates,
            "query": response.query,
            "execution_time_ms": response.execution_time_ms
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")




@app.get("/file")
async def read_file(
    file_path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Read a file from the filesystem."""
    import os as os_module

    try:
        # Security: ensure file_path is within allowed directory
        base_dir = os_module.getcwd()
        full_path = os_module.path.abspath(os_module.path.join(base_dir, file_path))

        if not full_path.startswith(base_dir):
            raise HTTPException(status_code=403, detail="Access denied: Path outside allowed directory")

        if not os_module.path.exists(full_path):
            raise HTTPException(status_code=404, detail="File not found")

        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Apply line range if specified
        if start_line is not None or end_line is not None:
            start = (start_line - 1) if start_line is not None else 0
            end = end_line if end_line is not None else len(lines)
            lines = lines[start:end]

        content = ''.join(lines)

        return {
            "content": content,
            "file_path": file_path,
            "total_lines": len(content.split('\n')),
            "line_range": {
                "start": start_line or 1,
                "end": end_line or len(content.split('\n'))
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")




@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return {
        "error": {
            "message": str(exc),
            "type": type(exc).__name__,
            "code": "internal_error"
        }
    }


def main():
    """Run the server."""
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))

    print(f"Starting Greb API server on http://{host}:{port}")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /v1/models - List models")
    print("  POST /v1/search - Search code")
    print()
    print("Environment variables:")
    print("  CEREBRAS_API_KEY - Required for re-ranking")
    print("  CEREBRAS_BASE_URL - Cerebras API URL (default: https://api.cerebras.ai/v1)")
    print("  CEREBRAS_MODEL - Model name (default: gpt-oss-120b)")
    print("  HOST - Server host (default: 127.0.0.1)")
    print("  PORT - Server port (default: 8000)")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()