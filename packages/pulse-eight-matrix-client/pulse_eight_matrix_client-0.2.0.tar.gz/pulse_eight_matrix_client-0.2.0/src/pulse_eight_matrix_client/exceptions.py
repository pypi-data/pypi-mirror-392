"""Exceptions for Pulse8 Matrix Client."""
from typing import Optional


class Pulse8Error(Exception):
    """Base exception for Pulse8 Matrix client."""
    pass


class Pulse8ConnectionError(Pulse8Error):
    """Connection error to Pulse8 Matrix."""
    pass


class Pulse8APIError(Pulse8Error):
    """API error from Pulse8 Matrix."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)