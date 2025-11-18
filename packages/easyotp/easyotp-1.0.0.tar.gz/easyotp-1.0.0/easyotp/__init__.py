from .client import EasyOTP
from .exceptions import (
    EasyOTPError,
    AuthenticationError,
    InsufficientCreditsError,
    APIKeyDisabledError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError,
)

__version__ = "1.0.0"

__all__ = [
    "EasyOTP",
    "EasyOTPError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "APIKeyDisabledError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "ServerError",
]

