"""
Data models for Web Scraping MCP Server.

Defines the core data structures for scraping requests, responses, and errors
with comprehensive type safety and validation.
"""
# ruff: noqa: N815

from enum import Enum
from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

# ============================================================================
# Enums
# ============================================================================


class UserAgentMode(str, Enum):
    """User agent configuration modes."""

    DEFAULT = "default"
    RANDOM = "random"


class OutputFormat(str, Enum):
    """Supported output formats for scraping results."""

    MARKDOWN = "markdown"
    HTML = "html"
    STRUCTURED = "structured"


# ============================================================================
# Content Selection Models
# ============================================================================


class ContentSelectionConfig(BaseModel):
    """Configuration for selecting specific page content."""

    cssSelector: str | None = Field(
        default=None, description="Single CSS selector for content scope"
    )
    targetElements: list[str] | None = Field(
        default=None, description="Multiple CSS selectors for targeted extraction"
    )

    @model_validator(mode="after")
    def validate_mutual_exclusivity(self) -> "ContentSelectionConfig":
        """Ensure cssSelector and targetElements are mutually exclusive."""
        if self.cssSelector and self.targetElements:
            raise ValueError("Cannot specify both cssSelector and targetElements")
        return self


# ============================================================================
# Content Filtering Models
# ============================================================================


class LinkFilteringConfig(BaseModel):
    """Configuration for link filtering."""

    excludeExternal: bool = Field(default=False, description="Exclude external links")
    excludeSocialMedia: bool = Field(default=False, description="Exclude social media links")
    excludeDomains: list[str] | None = Field(default=None, description="Custom domain blocklist")


class MediaFilteringConfig(BaseModel):
    """Configuration for media filtering."""

    excludeExternalImages: bool = Field(default=False, description="Exclude external images")


class ContentFilteringConfig(BaseModel):
    """Configuration for filtering page content."""

    excludedTags: list[str] | None = Field(default=None, description="HTML tags to exclude")
    wordCountThreshold: int | None = Field(default=None, description="Minimum words per text block")
    links: LinkFilteringConfig | None = Field(default=None, description="Link filtering options")
    media: MediaFilteringConfig | None = Field(default=None, description="Media filtering options")
    processIframes: bool = Field(default=False, description="Merge iframe content")
    removeOverlays: bool = Field(default=False, description="Remove overlay elements")


# ============================================================================
# Output Format Models
# ============================================================================


class MarkdownOutputOptions(BaseModel):
    """Options for markdown output."""

    includeCitations: bool = Field(default=False, description="Include inline citations")
    includeReferences: bool = Field(default=False, description="Include reference list")
    bodyWidth: int = Field(default=0, description="Markdown body width (0=no wrap)")


class HtmlOutputOptions(BaseModel):
    """Options for HTML output."""

    variant: Literal["raw", "cleaned", "fit"] = Field(
        default="cleaned", description="HTML output variant"
    )


class CssFieldConfig(BaseModel):
    """CSS selector field configuration."""

    name: str = Field(..., description="Field name")
    selector: str = Field(..., description="CSS selector")
    type: Literal["text", "attribute", "html", "nested"] = Field(..., description="Extraction type")
    attribute: str | None = Field(default=None, description="HTML attribute name")
    fields: list["CssFieldConfig"] | None = Field(default=None, description="Nested fields")

    @model_validator(mode="after")
    def validate_attribute_requirement(self) -> "CssFieldConfig":
        """Validate attribute field requirements."""
        if self.type == "attribute" and not self.attribute:
            raise ValueError("attribute field is required when type='attribute'")
        if self.type != "attribute" and self.attribute:
            raise ValueError("attribute field should only be set when type='attribute'")
        if self.type == "nested" and not self.fields:
            raise ValueError("fields are required when type='nested'")
        if self.type != "nested" and self.fields:
            raise ValueError("fields should only be set when type='nested'")
        return self


class CssExtractionConfig(BaseModel):
    """CSS-based structured extraction configuration."""

    baseSelector: str = Field(..., description="Base CSS selector")
    fields: list[CssFieldConfig] = Field(..., description="Fields to extract")


class LlmSchemaConfig(BaseModel):
    """JSON Schema configuration for LLM extraction."""

    type: Literal["object"] = Field(default="object", description="Schema type")
    properties: dict[str, Any] = Field(..., description="Schema properties")
    required: list[str] | None = Field(default=None, description="Required fields")


class LlmExtractionConfig(BaseModel):
    """LLM-based structured extraction configuration."""

    provider: str | None = Field(None, description="LLM provider (e.g., 'openai', 'anthropic')")
    model: str = Field(default="auto", description="LLM model identifier")
    instruction: str = Field(..., description="Extraction instruction for LLM")
    temperature: float = Field(default=0.0, description="Model temperature")
    extractionType: Literal["schema", "block"] = Field(
        ..., description="Extraction mode: schema=structured JSON, block=freeform text"
    )
    schema: LlmSchemaConfig | None = Field(
        default=None, description="JSON schema (for schema mode)"
    )

    @model_validator(mode="after")
    def validate_schema_requirement(self) -> "LlmExtractionConfig":
        """Validate schema requirements based on extraction type."""
        if self.extractionType == "schema" and not self.schema:
            raise ValueError("schema is required when extractionType='schema'")
        if self.extractionType == "block" and self.schema:
            raise ValueError("schema should not be provided when extractionType='block'")
        return self


class StructuredOutputOptions(BaseModel):
    """Options for structured data output."""

    method: Literal["css", "llm"] = Field(..., description="Extraction method")
    css: CssExtractionConfig | None = Field(default=None, description="CSS extraction config")
    llm: LlmExtractionConfig | None = Field(default=None, description="LLM extraction config")

    @model_validator(mode="after")
    def validate_method_config(self) -> "StructuredOutputOptions":
        """Validate method-specific configuration."""
        if self.method == "css" and not self.css:
            raise ValueError("css config is required when method='css'")
        if self.method == "llm" and not self.llm:
            raise ValueError("llm config is required when method='llm'")
        return self


class OutputOptionsConfig(BaseModel):
    """Output format options."""

    markdown: MarkdownOutputOptions | None = Field(default=None, description="Markdown options")
    html: HtmlOutputOptions | None = Field(default=None, description="HTML options")
    structured: StructuredOutputOptions | None = Field(
        default=None, description="Structured data extraction options"
    )


# ============================================================================
# Browser & Page Configuration Models
# ============================================================================


class ProxyConfig(BaseModel):
    """Proxy server configuration."""

    server: str = Field(..., description="Proxy server URL")
    username: str | None = Field(default=None, description="Proxy username")
    password: str | None = Field(default=None, description="Proxy password")

    @field_validator("server")
    @classmethod
    def validate_proxy_server(cls, v: str) -> str:
        """Validate proxy server URL format."""
        try:
            parsed = urlparse(v.strip())
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Proxy server must be a valid URL")
            if parsed.scheme not in ["http", "https", "socks4", "socks5"]:
                raise ValueError("Proxy scheme must be http, https, socks4, or socks5")
        except Exception as e:
            raise ValueError(f"Invalid proxy server URL: {e!s}") from e
        return v.strip()


class BrowserConfig(BaseModel):
    """Browser configuration."""

    cdp_url: str | None = Field(default=None, description="CDP URL for managed browsers")
    headless: bool = Field(default=True, description="Run in headless mode")
    userAgentMode: UserAgentMode = Field(
        default=UserAgentMode.RANDOM, description="User agent mode"
    )
    userAgent: str | None = Field(default=None, description="Custom user agent string")
    textMode: bool = Field(default=True, description="Disable images for faster crawling")
    proxy: ProxyConfig | None = Field(default=None, description="Proxy configuration")

    @model_validator(mode="after")
    def validate_user_agent_config(self) -> "BrowserConfig":
        """Validate user agent configuration."""
        if self.userAgentMode == UserAgentMode.DEFAULT and self.userAgent is None:
            raise ValueError("userAgent must be provided when userAgentMode is 'default'")
        if self.userAgentMode == UserAgentMode.RANDOM and self.userAgent is not None:
            raise ValueError("userAgent should not be provided when userAgentMode is 'random'")
        return self


class PageConfig(BaseModel):
    """Page interaction configuration."""

    waitFor: str | None = Field(default=None, description="Wait condition")
    timeoutMs: int = Field(default=60000, description="Page timeout in milliseconds")
    delayBeforeReturnHtml: float = Field(
        default=0.1, ge=0.0, description="Pause (seconds) before final HTML is captured"
    )

    @field_validator("waitFor")
    @classmethod
    def validate_wait_condition(cls, v: str | None) -> str | None:
        """Validate wait condition format."""
        if v is None:
            return v

        wait_condition = v.strip()
        if not wait_condition:
            return None

        if not (wait_condition.startswith("css:") or wait_condition.startswith("js:")):
            raise ValueError("waitFor must start with 'css:' or 'js:' prefix")

        condition_content = wait_condition[4:].strip()
        if not condition_content:
            raise ValueError("waitFor condition cannot be empty after prefix")

        return wait_condition


class RetryConfig(BaseModel):
    """Retry configuration."""

    attempts: int = Field(default=2, description="Maximum retry attempts")


class AdvancedConfig(BaseModel):
    """Advanced scraping features."""

    tableScoreThreshold: int = Field(default=7, description="Minimum score for table detection")
    captureScreenshot: bool = Field(default=False, description="Capture page screenshot")
    capturePdf: bool = Field(default=False, description="Capture page as PDF")
    captureMhtml: bool = Field(default=False, description="Capture page as MHTML")


# ============================================================================
# Main Request Model
# ============================================================================


class ScrapingRequest(BaseModel):
    """Web scraping request configuration."""

    sessionId: str | None = Field(default=None, description="Session identifier")
    urls: list[str] = Field(..., description="URLs to scrape")
    outputFormat: OutputFormat = Field(default=OutputFormat.MARKDOWN, description="Output format")

    # Content selection and filtering
    contentSelection: ContentSelectionConfig | None = Field(
        default=None, description="Content selection configuration"
    )
    contentFiltering: ContentFilteringConfig | None = Field(
        default=None, description="Content filtering configuration"
    )

    # Output options
    outputOptions: OutputOptionsConfig | None = Field(
        default=None, description="Output format options"
    )

    # Browser and page configuration
    browser: BrowserConfig | None = Field(default=None, description="Browser configuration")
    page: PageConfig | None = Field(default=None, description="Page configuration")
    retry: RetryConfig | None = Field(default=None, description="Retry configuration")

    # Advanced features
    advanced: AdvancedConfig | None = Field(default=None, description="Advanced features")

    # Legacy fields for session management
    jsCode: list[str] | None = Field(default=None, description="JavaScript code to execute")
    concurrency: int = Field(default=3, description="Maximum concurrent requests")

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: list[str]) -> list[str]:
        """Validate URLs format and uniqueness."""
        validated_urls = []

        for url in v:
            url = url.strip()
            if not url:
                raise ValueError("URL cannot be empty")

            if not url.startswith(("http://", "https://")):
                raise ValueError("URL must start with http:// or https://")

            validated_urls.append(url)

        if len(validated_urls) != len(set(validated_urls)):
            raise ValueError("Duplicate URLs are not allowed")

        return validated_urls

    @model_validator(mode="after")
    def validate_output_format_requirements(self) -> "ScrapingRequest":
        """Validate output format requirements."""
        if self.outputFormat == OutputFormat.STRUCTURED and (
            not self.outputOptions or not self.outputOptions.structured
        ):
            raise ValueError("outputOptions.structured is required when outputFormat='structured'")
        return self

    def get_browser_config(self) -> BrowserConfig:
        """Get browser configuration with defaults."""
        return self.browser or BrowserConfig()

    def get_page_config(self) -> PageConfig:
        """Get page configuration with defaults."""
        return self.page or PageConfig()

    def get_retry_config(self) -> RetryConfig:
        """Get retry configuration with defaults."""
        return self.retry or RetryConfig()

    def get_advanced_config(self) -> AdvancedConfig:
        """Get advanced configuration with defaults."""
        return self.advanced or AdvancedConfig()


# ============================================================================
# Response Models
# ============================================================================


class ScrapingResult(BaseModel):
    """Individual scraping result."""

    url: str = Field(description="Original URL")
    success: bool = Field(description="Whether scraping was successful")
    content: Any = Field(description="Extracted content based on mode")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error: str | None = Field(None, description="Error message if scraping failed")


class ScrapingMetadata(BaseModel):
    """Scraping metadata and summary information."""

    total_urls: int = Field(description="Total number of URLs processed")
    successful: int = Field(description="Number of successful extractions")
    failed: int = Field(description="Number of failed extractions")
    output_format: str = Field(description="Output format used")
    execution_time: float = Field(description="Total execution time in seconds")


class ScrapingResponse(BaseModel):
    """Complete scraping response structure."""

    success: bool = Field(description="Whether the overall operation was successful")
    results: list[ScrapingResult] = Field(description="List of scraping results")
    summary: ScrapingMetadata = Field(description="Summary metadata")
    error: str | None = Field(None, description="Error message if operation failed")
    error_type: str | None = Field(None, description="Error type classification")
