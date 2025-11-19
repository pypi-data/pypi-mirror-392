"""
Exception classes for Web Scraping MCP Server.

Defines custom exception types for different error scenarios in web scraping operations.
"""

from datetime import datetime


class ScrapingError(Exception):
    """Base exception for scraping-related errors."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        error_type: str | None = None,
        retry_after: int | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.url = url
        self.error_type = error_type or self.__class__.__name__
        self.retry_after = retry_after
        self.timestamp = datetime.now()


class ConfigurationError(ScrapingError):
    """Error in scraping configuration."""

    pass


class ExtractionError(ScrapingError):
    """Error during content extraction."""

    pass


class BrowserError(ScrapingError):
    """Error related to browser operations."""

    pass


class NetworkError(ScrapingError):
    """Network-related error during scraping."""

    pass


class ValidationError(ScrapingError):
    """Parameter validation error."""

    pass
