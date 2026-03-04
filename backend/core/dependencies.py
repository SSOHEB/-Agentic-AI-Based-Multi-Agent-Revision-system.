from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.firebase import verify_firebase_token


# Security scheme for Swagger UI
security = HTTPBearer()

# Type alias for database session injection
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> dict:
    """
    Dependency to authenticate user via Firebase JWT.
    Extracts the Bearer token, verifies it, and returns the decoded user payload.
    
    Raises:
        HTTPException: 401 if token is invalid, expired, or missing.
    """
    try:
        token = credentials.credentials
        # verify_firebase_token handles decoding and verifying the JWT signature
        # returning a dictionary of user claims (e.g., {"uid": "idxxx", ...})
        user_data = verify_firebase_token(token)
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
