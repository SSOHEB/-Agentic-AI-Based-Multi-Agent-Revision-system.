import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from firebase_admin import credentials, initialize_app
import firebase_admin.auth as auth

from core.config import settings


_firebase_app = None

def init_firebase():
    """
    Initializes the Firebase Admin SDK singleton.
    Should be called during application startup.
    """
    global _firebase_app
    
    # Only initialize if not already initialized
    if _firebase_app is None:
        try:
            # Check if a credentials path is explicitly defined in config
            if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                _firebase_app = initialize_app(cred)
            else:
                # Default initialization (relies on GOOGLE_APPLICATION_CREDENTIALS env var)
                _firebase_app = initialize_app()
        except ValueError as e:
            # Happens if the app is already initialized in another thread/process inadvertently
            pass


def verify_firebase_token(token: str) -> dict:
    """
    Verifies a Firebase JWT token and returns the decoded payload.
    
    Args:
        token: The JWT string from the Authorization header
        
    Returns:
        A dictionary containing the decoded token claims (e.g. uid, email)
        
    Raises:
        ValueError: If the token is invalid, expired, or revoked
        firebase_admin.auth.AuthError: For other Firebase authentication errors
    """
    # Verify the ID token using the Firebase Admin SDK
    # By default, check_revoked is False. Set to True if you need to check session revocation.
    decoded_token = auth.verify_id_token(token, check_revoked=False)
    return decoded_token


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for initializing global resources.
    Use this in main.py to setup Firebase on startup.
    """
    # Startup actions
    init_firebase()
    
    yield
    
    # Shutdown actions
    pass
