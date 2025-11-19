"""MemV AI client library for video processing and knowledge management."""

__version__ = "0.1.2"

from .client import MemVClient, MemVClientError, MemVAuthenticationError, MemVAPIError

__all__ = ["MemVClient", "MemVClientError", "MemVAuthenticationError", "MemVAPIError"]