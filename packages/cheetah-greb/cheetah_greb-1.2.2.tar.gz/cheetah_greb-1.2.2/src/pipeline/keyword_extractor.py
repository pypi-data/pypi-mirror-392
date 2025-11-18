"""
Keyword extraction service using Cerebras for intelligent query parsing.
"""

from __future__ import annotations

import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from openai import OpenAI

from .base import PipelineConfig, ExtractedKeywords
from .token_tracker import token_tracker


class KeywordExtractor:
    """Extracts relevant keywords from natural language queries using Cerebras."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.cerebras_api_key,
            base_url=config.cerebras_base_url
        )

    def extract_keywords(self, query: str) -> ExtractedKeywords:
        """
        Extract relevant keywords from a natural language query using Cerebras.

        Args:
            query: Natural language search query

        Returns:
            ExtractedKeywords object with search terms and patterns

        Raises:
            RuntimeError: If Cerebras API call fails
        """
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            },
            {
                "role": "user",
                "content": self._get_user_prompt(query)
            }
        ]

        # Build API call parameters
        api_params = {
            "model": self.config.cerebras_model,
            "messages": messages,
            "temperature": 0.0,  # Low temperature for consistent extraction
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "keyword_extraction",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "primary_terms": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Main technical terms, function names, class names, variables that the user is looking for"
                            },
                            "file_patterns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "File patterns to search (e.g., *.py, *.js, **/auth/**)"
                            },
                            "search_terms": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "All terms that should be used in grep search, including variations"
                            },
                            "intent": {
                                "type": "string",
                                "description": "Brief summary of what the user wants to find or fix"
                            }
                        },
                        "required": ["primary_terms", "file_patterns", "search_terms", "intent"]
                    }
                }
            }
        }

        # Add reasoning_effort parameter only for gpt-oss-120b model
        if self.config.cerebras_model == "gpt-oss-120b":
            api_params["reasoning_effort"] = self.config.reasoning_effort

        response = self.client.chat.completions.create(**api_params)

        # Track token usage from keyword extraction with messages
        token_tracker.track_keyword_extraction(response, messages)

        result_data = json.loads(response.choices[0].message.content)
        return ExtractedKeywords(**result_data)

    def _get_system_prompt(self) -> str:
        """Get system prompt for keyword extraction."""
        return """You are an expert code search assistant specializing in focused keyword extraction. Your task is to analyze natural language queries and extract RELEVANT search terms without excessive variation.

Analyze the user's query and extract:
1. Primary terms: 3-5 main technical terms, function names, class names, variable names
2. File patterns: All relevant file patterns (e.g., *.py, *.js, **/auth/**, config/*)
3. Search terms: FOCUSED list of 8-12 essential terms including exact matches and key variations
4. Intent: Brief summary of what the user wants to find

**RULE #1: ALWAYS INCLUDE EXACT LITERAL TERMS FROM THE QUERY FIRST**
- If query mentions "readFile", include "readFile" exactly as-is
- If query mentions "handleUserAuth", include "handleUserAuth" exactly
- If query mentions "ComponentName", include "ComponentName" exactly
- THEN add a few key variations (readFile -> read_file, ReadFile)
- Do NOT skip literal terms from the query - they are the MOST important

CRITICAL: Generate exactly 8-12 HIGH-QUALITY search terms:
- **START with exact literal terms from query** (word-for-word matches)
- Include ONLY the most common naming conventions: camelCase, snake_case, PascalCase
- Include 2-3 key related concepts or synonyms
- Include 1-2 common prefixes/suffixes if relevant
- Focus on terms most likely to appear in actual code
- Avoid excessive variations that would create noise

Examples:
Query: "fix auth it is not working"
-> primary_terms: ["auth", "authentication", "login"]
-> search_terms: ["auth", "authenticate", "authentication", "login", "signin", "authHandler", "authService", "isAuthenticated", "authError", "loginError", "validateAuth", "authMiddleware"]
-> file_patterns: ["**/auth/**", "**/login/**", "*.js", "*.ts", "*.py"]
-> intent: "Find and fix authentication issues"

Query: "database connection fails in mysql"
-> primary_terms: ["database", "mysql", "connection", "db"]
-> search_terms: ["database", "db", "mysql", "connection", "connect", "dbConnection", "connectionString", "mysqlConnection", "connectionError", "dbConfig", "createConnection", "getConnection"]
-> file_patterns: ["**/db/**", "**/database/**", "**/mysql/**", "*.py", "*.js", "*.sql"]
-> intent: "Debug database connection issues"
"""

    def _get_user_prompt(self, query: str) -> str:
        """Get user prompt for keyword extraction."""
        return f"""Extract search keywords from this query: "{query}"

CRITICAL INSTRUCTIONS:
1. **FIRST**: Extract and include ALL literal technical terms EXACTLY as they appear in the query
   - If query says "readFile", include "readFile" in search_terms
   - If query says "handleAuth", include "handleAuth" in search_terms
   - If query says "UserController", include "UserController" in search_terms

2. **THEN**: Generate exactly 8-12 focused variations including:
   - Only the most common naming conventions (camelCase, snake_case, PascalCase)
   - 2-3 key related concepts or synonyms
   - 1-2 relevant prefixes/suffixes if applicable

FOCUS on quality over quantity - include terms most likely to appear in actual code.
DO NOT skip or modify literal terms from the query - they are the MOST IMPORTANT keywords to include."""