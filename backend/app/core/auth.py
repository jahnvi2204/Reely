"""
Authentication utilities for the Reely API
"""
import logging
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    # If a credentials path is provided, use it; otherwise fall back to default
    if getattr(settings, "firebase_credentials_path", None):
        cred = credentials.Certificate(settings.firebase_credentials_path)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()
except ValueError:
    # Already initialized
    pass

security = HTTPBearer()


async def verify_firebase_token(token: str) -> Optional[dict]:
    """
    Verify Firebase ID token and return user info
    """
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current authenticated user from Firebase token
    """
    token = credentials.credentials
    
    user_info = await verify_firebase_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_info


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Get current user ID from Firebase token
    """
    user_info = await get_current_user(credentials)
    return user_info.get('uid')


def require_auth():
    """
    Dependency to require authentication for endpoints
    """
    return Depends(get_current_user)


def require_user_id():
    """
    Dependency to get user ID for authenticated endpoints
    """
    return Depends(get_current_user_id)
