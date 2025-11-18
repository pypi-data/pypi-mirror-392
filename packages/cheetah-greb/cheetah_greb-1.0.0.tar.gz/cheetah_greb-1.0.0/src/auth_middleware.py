"""
Authentication and billing middleware for Greb API server.
Handles API key validation, usage tracking, and rate limiting.
"""

from __future__ import annotations

import os
import time
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import httpx


class UsageTier(BaseModel):
    """Usage tier configuration."""
    name: str
    requests_per_minute: int
    requests_per_day: Optional[int]
    requests_per_month: Optional[int]
    input_token_price: float  # Price per 1M input tokens
    output_token_price: float  # Price per 1M output tokens


# Define pricing plans based on Greb pricing model
PRICING_PLANS = {
    "free": UsageTier(
        name="Free Plan",
        requests_per_minute=10,
        requests_per_day=30,
        requests_per_month=1000,
        input_token_price=0.0,
        output_token_price=0.0
    ),
    "payAsYouGo": UsageTier(
        name="Pay as you go",
        requests_per_minute=1000,  # Very high rate limit
        requests_per_day=None,
        requests_per_month=None,
        input_token_price=0.45,  # $0.45 per 1M input tokens
        output_token_price=0.85   # $0.85 per 1M output tokens
    ),
    "enterprise": UsageTier(
        name="Enterprise",
        requests_per_minute=10000,  # Extremely high rate limit
        requests_per_day=None,
        requests_per_month=None,
        input_token_price=0.0,  # Custom pricing
        output_token_price=0.0   # Custom pricing
    )
}


class APIKeyValidator:
    """
    Validates API keys and tracks usage.
    Integrates with the existing backend User model.
    """
    
    def __init__(self, backend_url: Optional[str] = None):
        """
        Initialize API key validator.
        
        Args:
            backend_url: URL of the Greb backend API
        """
        self.backend_url = backend_url or os.getenv(
            "GREB_BACKEND_URL",
            "http://localhost:5000/api"
        )
        # Initialize without auth header - add per request if needed
        self.client = httpx.AsyncClient(base_url=self.backend_url, timeout=30.0)  # Increased timeout
        
        # In-memory cache for validated keys (1 minute TTL)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 60  # seconds
        
        print(f"APIKeyValidator initialized with backend: {self.backend_url}")
    
    async def validate_key(self, api_key: str) -> Dict[str, Any]:
        """
        Validate an API key and return user data.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Dict containing user info, tier, and usage data
            
        Raises:
            HTTPException if key is invalid
        """
        # Check cache first
        if api_key in self.cache:
            cached = self.cache[api_key]
            if time.time() - cached["cached_at"] < self.cache_ttl:
                return cached["data"]
        
        try:
            # Call backend API to validate key
            response = await self.client.post(
                "/usage/validate-api-key",
                json={"apiKey": api_key}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Cache the result
                self.cache[api_key] = {
                    "data": data,
                    "cached_at": time.time()
                }
                
                return data
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired API key"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service unavailable"
                )
        
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Cannot reach authentication service: {str(e)}"
            )
    
    async def track_usage(
        self,
        api_key: str,
        endpoint: str,
        input_tokens: int = 0,
        output_tokens: int = 0
    ) -> bool:
        """
        Track API usage for billing purposes.
        
        Args:
            api_key: The API key being used
            endpoint: The endpoint being called
            input_tokens: Number of input tokens consumed
            output_tokens: Number of output tokens consumed
            
        Returns:
            True if tracking succeeded
        """
        try:
            print(f"Tracking usage to backend: {self.backend_url}/usage/track")
            print(f"   API Key: {api_key[:20]}...")
            print(f"   Input tokens: {input_tokens}, Output tokens: {output_tokens}")
            
            response = await self.client.post(
                "/usage/track",
                json={
                    "apiKey": api_key,
                    "endpoint": endpoint,
                    "inputTokens": input_tokens,
                    "outputTokens": output_tokens,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timeout=30.0  # Increase timeout to 30 seconds
            )
            
            print(f"Backend response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"Usage tracked successfully!")
                print(f"   Response: {response_data}")
                return True
            else:
                print(f"Backend returned non-200 status: {response.status_code}")
                print(f"   Response body: {response.text}")
                return False

        except httpx.TimeoutException as e:
            print(f"Timeout connecting to backend: {e}")
            print(f"   Backend URL: {self.backend_url}")
            return False
        except httpx.RequestError as e:
            print(f"Network error tracking usage: {e}")
            print(f"   Backend URL: {self.backend_url}")
            print(f"   Make sure backend is running on port 5000")
            return False
        except Exception as e:
            print(f"Unexpected error tracking usage: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def check_rate_limit(
        self,
        api_key: str,
        user_plan: str
    ) -> bool:
        """
        Check if the user has exceeded their rate limit.
        
        Args:
            api_key: The API key being used
            user_plan: User's pricing plan (free/payAsYouGo/enterprise)
            
        Returns:
            True if within limits, raises HTTPException otherwise
        """
        plan = PRICING_PLANS.get(user_plan, PRICING_PLANS["free"])
        
        try:
            # Check rate limit via backend
            response = await self.client.get(
                f"/usage/rate-limit/{api_key}"
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("success"):
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Rate limit check failed. Please try again."
                    )
                    
                rate_data = data.get("data", {})
                requests_this_minute = rate_data.get("requestsThisMinute", 0)
                requests_today = rate_data.get("requestsToday", 0)
                
                if requests_this_minute >= plan.requests_per_minute:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded: {plan.requests_per_minute} requests per minute. Plan: {plan.name}"
                    )
                
                if plan.requests_per_day and requests_today >= plan.requests_per_day:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Daily quota exceeded: {plan.requests_per_day} requests per day. Plan: {plan.name}"
                    )
                
                return True
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Rate limit service returned status {response.status_code}"
                )
        
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Cannot reach rate limit service: {str(e)}"
            )


# FastAPI security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    validator: Optional[APIKeyValidator] = None
) -> Dict[str, Any]:
    """
    FastAPI dependency for authenticating requests.
    
    Usage:
        @app.get("/search")
        async def search(user: Dict = Depends(get_current_user)):
            # user contains authenticated user data
            pass
    """
    if validator is None:
        validator = APIKeyValidator()
    
    api_key = credentials.credentials
    
    # Validate the API key format
    if not api_key.startswith("grb_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format. Keys should start with 'grb_'"
        )
    
    # Validate with backend
    validation_result = await validator.validate_key(api_key)
    
    # Extract user data from response
    if not validation_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    user_data = validation_result.get("data", {})
    
    # Check rate limits
    user_plan = user_data.get("plan", "free")
    await validator.check_rate_limit(api_key, user_plan)
    
    return {
        **user_data,
        "api_key": api_key
    }


class UsageTracker:
    """Helper class for tracking usage within request handlers."""
    
    def __init__(self, validator: Optional[APIKeyValidator] = None):
        self.validator = validator or APIKeyValidator()
    
    async def track(
        self,
        api_key: str,
        endpoint: str,
        input_tokens: int = 0,
        output_tokens: int = 0
    ):
        """
        Track token usage for billing.

        Args:
            api_key: The API key being used
            endpoint: The endpoint being called
            input_tokens: Number of input tokens consumed
            output_tokens: Number of output tokens consumed
        """
        await self.validator.track_usage(
            api_key=api_key,
            endpoint=endpoint,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
