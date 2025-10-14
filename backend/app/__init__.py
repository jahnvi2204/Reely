"""
Reely Backend Application Package
Main application package for the video captioning API
"""

from .core.config import settings
from .core.auth import get_current_user, get_current_user_id, require_auth, require_user_id

__version__ = "1.0.0"
__author__ = "Reely Team"

__all__ = [
    'settings',
    'get_current_user',
    'get_current_user_id', 
    'require_auth',
    'require_user_id'
]