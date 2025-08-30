"""JWT authentication and authorization module."""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = structlog.get_logger()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    scopes: List[str] = []


class User(BaseModel):
    """User model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    roles: List[str] = []
    permissions: List[str] = []


class UserInDB(User):
    """User in database model."""
    hashed_password: str


# Role-based permissions
ROLE_PERMISSIONS = {
    "admin": [
        "read:all",
        "write:all",
        "delete:all",
        "admin:users",
        "admin:system"
    ],
    "developer": [
        "read:models",
        "write:models",
        "read:services",
        "write:services",
        "read:depot",
        "write:workspace"
    ],
    "viewer": [
        "read:models",
        "read:services",
        "read:depot"
    ],
    "service": [
        "read:api",
        "write:api"
    ]
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
    
    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token
    
    Returns:
        Token data
    
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        scopes: List[str] = payload.get("scopes", [])
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(username=username, scopes=scopes)
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> User:
    """
    Get current user from JWT token.
    
    Args:
        credentials: Bearer token credentials
    
    Returns:
        Current user
    
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = decode_token(credentials.credentials)
    
    # In production, fetch user from database
    # For now, create a user from token data
    user = User(
        username=token_data.username,
        roles=token_data.scopes,
        permissions=[]
    )
    
    # Expand permissions based on roles
    for role in user.roles:
        if role in ROLE_PERMISSIONS:
            user.permissions.extend(ROLE_PERMISSIONS[role])
    
    user.permissions = list(set(user.permissions))  # Remove duplicates
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current user from token
    
    Returns:
        Active user
    
    Raises:
        HTTPException: If user is disabled
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_permission(permission: str):
    """
    Dependency to require specific permission.
    
    Args:
        permission: Required permission
    
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if permission not in current_user.permissions and "write:all" not in current_user.permissions:
            logger.warning(
                f"Permission denied for user {current_user.username}: "
                f"required {permission}, has {current_user.permissions}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
        return current_user
    
    return permission_checker


def require_any_permission(permissions: List[str]):
    """
    Dependency to require any of the specified permissions.
    
    Args:
        permissions: List of permissions (any one is sufficient)
    
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not any(p in current_user.permissions for p in permissions):
            if "write:all" not in current_user.permissions:
                logger.warning(
                    f"Permission denied for user {current_user.username}: "
                    f"required one of {permissions}, has {current_user.permissions}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: one of {permissions}"
                )
        return current_user
    
    return permission_checker


def require_role(role: str):
    """
    Dependency to require specific role.
    
    Args:
        role: Required role
    
    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if role not in current_user.roles and "admin" not in current_user.roles:
            logger.warning(
                f"Role denied for user {current_user.username}: "
                f"required {role}, has {current_user.roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role}"
            )
        return current_user
    
    return role_checker


# API key authentication (backward compatibility)
async def verify_api_key_or_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings: Any = None  # Inject settings if needed
) -> str:
    """
    Verify either API key or JWT token.
    
    Args:
        credentials: Bearer token credentials
        settings: Application settings
    
    Returns:
        Username or API key identifier
    
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Try JWT first
    try:
        token_data = decode_token(token)
        return token_data.username
    except HTTPException:
        # Fall back to API key validation
        # In production, validate against database
        valid_api_keys = os.getenv("VALID_API_KEYS", "demo-key").split(",")
        
        if token in valid_api_keys:
            return f"api_key_{token[:8]}"  # Return identifier for API key user
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )