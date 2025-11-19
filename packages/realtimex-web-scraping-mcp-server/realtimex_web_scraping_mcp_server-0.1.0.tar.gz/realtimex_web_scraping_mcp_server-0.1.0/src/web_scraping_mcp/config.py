"""
Configuration management for Web Scraping MCP Server.

Handles environment-based configuration for browser settings, LLM configuration,
and server settings with validation and secure credential management.
"""

import os
from typing import Any

import structlog
from pydantic import BaseModel, Field

from .models import OutputFormat

logger = structlog.get_logger(__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM integration via LiteLLM."""

    api_key: str | None = Field(None, description="LiteLLM API key")
    base_url: str | None = Field(None, description="LiteLLM base URL")
    timeout: int = Field(default=60, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    enabled: bool = Field(default=False, description="Whether LLM is enabled")


class BrowserConfig(BaseModel):
    """Configuration for browser providers."""

    cdp_url: str = Field(
        default="http://localhost:9222", description="CDP URL for managed browsers"
    )
    default_headless: bool = Field(default=True, description="Default headless mode")
    default_timeout: int = Field(default=60000, description="Default timeout in milliseconds")
    max_concurrent: int = Field(default=5, description="Maximum concurrent browser instances")
    user_data_dir: str | None = Field(None, description="Browser user data directory")


class ServerConfig(BaseModel):
    """MCP server configuration."""

    server_name: str = Field(default="web-scraping-mcp", description="MCP server name")
    server_version: str = Field(default="1.0.0", description="MCP server version")
    default_output_format: OutputFormat = Field(
        default=OutputFormat.MARKDOWN, description="Default output format"
    )
    default_timeout: int = Field(
        default=60000, description="Default request timeout in milliseconds"
    )
    max_urls_per_request: int = Field(default=100, description="Maximum URLs per request")
    enable_sessions: bool = Field(default=True, description="Enable session management")


class WebScrapingConfig(BaseModel):
    """Complete configuration for Web Scraping MCP Server."""

    server: ServerConfig = Field(default_factory=ServerConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)

    def is_llm_enabled(self) -> bool:
        """Check if LLM is enabled and properly configured."""
        return self.llm.enabled and bool(self.llm.api_key)


def load_config() -> WebScrapingConfig:
    """
    Load configuration from environment variables.

    Returns:
        WebScrapingConfig with all settings loaded from environment

    Raises:
        ValueError: If required configuration is missing
    """
    logger.info("Loading Web Scraping MCP server configuration")

    try:
        # Load server configuration
        output_format_env = os.getenv("WEB_SCRAPING_DEFAULT_OUTPUT_FORMAT") or os.getenv(
            "WEB_SCRAPING_DEFAULT_MODE", "markdown"
        )

        server_config = ServerConfig(
            server_name=os.getenv("WEB_SCRAPING_SERVER_NAME", "web-scraping-mcp"),
            server_version=os.getenv("WEB_SCRAPING_SERVER_VERSION", "1.0.0"),
            default_output_format=OutputFormat(output_format_env),
            default_timeout=int(os.getenv("WEB_SCRAPING_DEFAULT_TIMEOUT", "60000")),
            max_urls_per_request=int(os.getenv("WEB_SCRAPING_MAX_URLS", "100")),
            enable_sessions=os.getenv("WEB_SCRAPING_ENABLE_SESSIONS", "true").lower() == "true",
        )

        # Load browser configuration
        browser_config = BrowserConfig(
            cdp_url=os.getenv("WEB_SCRAPING_CDP_URL", "http://localhost:9222"),
            default_headless=os.getenv("WEB_SCRAPING_DEFAULT_HEADLESS", "true").lower() == "true",
            default_timeout=int(os.getenv("WEB_SCRAPING_BROWSER_TIMEOUT", "60000")),
            max_concurrent=int(os.getenv("WEB_SCRAPING_MAX_CONCURRENT", "5")),
            user_data_dir=os.getenv("WEB_SCRAPING_USER_DATA_DIR"),
        )

        # Load LLM configuration using LiteLLM environment variables
        litellm_api_key = os.getenv("LITELLM_API_KEY")
        litellm_base_url = os.getenv("LITELLM_API_BASE")

        llm_config = LLMConfig(
            api_key=litellm_api_key,
            base_url=litellm_base_url,
            timeout=int(os.getenv("LITELLM_TIMEOUT", "60")),
            max_retries=int(os.getenv("LITELLM_MAX_RETRIES", "3")),
            enabled=bool(litellm_api_key),  # Enable if API key is provided
        )

        config = WebScrapingConfig(
            server=server_config,
            browser=browser_config,
            llm=llm_config,
        )

        logger.info(
            "Configuration loaded successfully",
            llm_enabled=config.is_llm_enabled(),
            default_output_format=config.server.default_output_format.value,
            cdp_url=config.browser.cdp_url,
        )

        return config

    except Exception as e:
        logger.error("Failed to load configuration", error=str(e))
        raise


def get_environment_info() -> dict[str, Any]:
    """
    Get information about the current environment configuration.

    Returns:
        Dictionary with environment information (without sensitive data)
    """
    return {
        "server_name": os.getenv("WEB_SCRAPING_SERVER_NAME", "web-scraping-mcp"),
        "default_output_format": os.getenv(
            "WEB_SCRAPING_DEFAULT_OUTPUT_FORMAT",
            os.getenv("WEB_SCRAPING_DEFAULT_MODE", "markdown"),
        ),
        "cdp_url": os.getenv("WEB_SCRAPING_CDP_URL", "Not configured"),
        "litellm_configured": bool(os.getenv("LITELLM_API_KEY")),
        "litellm_base_url": os.getenv("LITELLM_API_BASE", "Not configured"),
        "sessions_enabled": os.getenv("WEB_SCRAPING_ENABLE_SESSIONS", "true").lower() == "true",
    }
