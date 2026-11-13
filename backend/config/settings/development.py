"""
Development settings for FlowOps.
"""
from .base import *  # noqa: F403

DEBUG = True

# In development, also allow all local origins if requested
CORS_ALLOW_ALL_ORIGINS = True

