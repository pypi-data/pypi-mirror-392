"""
Sixfinger - AI Platform SDK
Official Python SDK for Sixfinger services
"""

__version__ = "1.0.0"
__author__ = "Sixfinger Team"
__email__ = "sixfingerdev@gmail.com"

from .api import API, AsyncAPI, Conversation
from .errors import (
    SixfingerError,
    AuthenticationError,
    RateLimitError,
    APIError,
    TimeoutError,
    ValidationError
)
from .models import Message, ChatResponse, UsageStats, ModelInfo

__all__ = [
    'API',
    'AsyncAPI',
    'Conversation',
    'SixfingerError',
    'AuthenticationError',
    'RateLimitError',
    'APIError',
    'TimeoutError',
    'ValidationError',
    'Message',
    'ChatResponse',
    'UsageStats',
    'ModelInfo'
]