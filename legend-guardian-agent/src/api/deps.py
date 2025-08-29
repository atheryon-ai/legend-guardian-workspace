"""API dependencies and authentication."""

from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, Header, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.settings import Settings, get_settings

logger = structlog.get_logger()

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    """Verify API key from Bearer token."""
    if not credentials:
        logger.warning("Missing authentication credentials")
        raise HTTPException(status_code=401, detail="Missing authentication credentials")
    
    token = credentials.credentials
    if token not in settings.valid_api_keys:
        logger.warning("Invalid API key", key_prefix=token[:8] if len(token) > 8 else token)
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    logger.debug("API key verified", key_prefix=token[:8] if len(token) > 8 else token)
    return token


async def get_correlation_id(
    request: Request,
    x_correlation_id: Annotated[str | None, Header()] = None,
) -> str:
    """Get correlation ID from request."""
    return x_correlation_id or getattr(request.state, "correlation_id", "unknown")


async def get_project_id(
    project_id: str | None = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,
) -> str:
    """Get project ID from request or use default."""
    return project_id or settings.project_id


async def get_workspace_id(
    workspace_id: str | None = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,
) -> str:
    """Get workspace ID from request or use default."""
    return workspace_id or settings.workspace_id


class RateLimiter:
    """Simple rate limiter dependency."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter."""
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def __call__(self, request: Request, api_key: str = Depends(verify_api_key)):
        """Check rate limit."""
        import time
        
        now = time.time()
        
        # Clean old entries
        self.requests = {
            k: v for k, v in self.requests.items() 
            if now - v["timestamp"] < self.window_seconds
        }
        
        # Check rate limit
        if api_key in self.requests:
            entry = self.requests[api_key]
            if entry["count"] >= self.max_requests:
                logger.warning("Rate limit exceeded", api_key_prefix=api_key[:8])
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {self.max_requests} requests per {self.window_seconds} seconds"
                )
            entry["count"] += 1
        else:
            self.requests[api_key] = {"count": 1, "timestamp": now}
        
        return api_key


# Create rate limiter instance
rate_limiter = RateLimiter()


class PIIRedactor:
    """PII redaction middleware."""
    
    PATTERNS = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone number
    ]
    
    @classmethod
    def redact(cls, text: str) -> str:
        """Redact PII from text."""
        import re
        
        if not text:
            return text
        
        for pattern in cls.PATTERNS:
            text = re.sub(pattern, "[REDACTED]", text)
        
        return text


async def get_pii_redactor(
    settings: Annotated[Settings, Depends(get_settings)]
) -> PIIRedactor | None:
    """Get PII redactor if enabled."""
    return PIIRedactor() if settings.pii_redaction_enabled else None