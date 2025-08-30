
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from src.settings import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key in settings.VALID_API_KEYS:
        return api_key
    else:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )
