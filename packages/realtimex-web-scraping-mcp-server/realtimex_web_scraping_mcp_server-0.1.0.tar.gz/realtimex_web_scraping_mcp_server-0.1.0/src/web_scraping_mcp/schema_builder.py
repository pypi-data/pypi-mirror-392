"""
Schema builder utilities for Web Scraping MCP Server.

Provides unified schema building functionality to eliminate duplication across tools.
"""

from mcp import types

from .models import OutputFormat, UserAgentMode


class SchemaBuilder:
    """Builder for MCP tool schemas with shared components."""

    def __init__(self, max_urls_per_request: int, max_concurrent: int):
        self.max_urls_per_request = max_urls_per_request
        self.max_concurrent = max_concurrent

    def build_base_input_schema(self, additional_properties: dict | None = None) -> dict:
        """Build the base input schema shared across all tools."""
        schema = {
            "type": "object",
            "properties": {
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": self.max_urls_per_request,
                    "description": "List of URLs to scrape",
                },
                "contentSelection": self._build_content_selection_schema(),
                "contentFiltering": self._build_content_filtering_schema(),
                "outputFormat": self._build_output_format_schema(),
                "outputOptions": self._build_output_options_schema(),
                "browser": self._build_browser_schema(),
                "page": self._build_page_schema(),
                "retry": self._build_retry_schema(),
                "advanced": self._build_advanced_schema(),
            },
            "required": ["urls"],
            "additionalProperties": False,
        }

        # Add additional properties if provided
        if additional_properties:
            schema["properties"].update(additional_properties)

        return schema

    def build_output_schema(self) -> dict:
        """Build the standard output schema for all tools."""
        return {
            "type": "object",
            "description": "Structured scraping results",
            "properties": {
                "success": {"type": "boolean"},
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "success": {"type": "boolean"},
                            "content": {"description": "Extracted content"},
                            "metadata": {"type": "object"},
                            "error": {"type": ["string", "null"]},
                        },
                    },
                },
                "summary": {
                    "type": "object",
                    "properties": {
                        "total_urls": {"type": "integer"},
                        "successful": {"type": "integer"},
                        "failed": {"type": "integer"},
                        "output_format": {"type": "string"},
                        "execution_time": {"type": "number"},
                    },
                },
                "error": {"type": ["string", "null"]},
                "error_type": {"type": ["string", "null"]},
            },
            "required": ["success", "results", "summary"],
        }

    def _build_output_format_schema(self) -> dict:
        """Build schema describing the output format selector."""
        return {
            "type": "string",
            "enum": [fmt.value for fmt in OutputFormat],
            "default": OutputFormat.MARKDOWN.value,
            "description": "Output format for the scraped content",
        }

    def _build_content_selection_schema(self) -> dict:
        """Build schema for content selection configuration."""
        return {
            "type": "object",
            "description": "Optional scoping of page regions prior to extraction",
            "properties": {
                "cssSelector": {
                    "type": "string",
                    "description": "Single CSS selector to scope the crawl",
                },
                "targetElements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "description": "Multiple selectors that focus markdown while retaining page context",
                },
            },
            "additionalProperties": False,
        }

    def _build_content_filtering_schema(self) -> dict:
        """Build schema for content filtering configuration."""
        return {
            "type": "object",
            "description": "Optional filters for tags, links, and media",
            "properties": {
                "excludedTags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "HTML tags to remove entirely",
                },
                "wordCountThreshold": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Minimum words required for a text block",
                },
                "links": {
                    "type": "object",
                    "description": "Link filtering options",
                    "properties": {
                        "excludeExternal": {
                            "type": "boolean",
                            "default": False,
                            "description": "Exclude links to external domains",
                        },
                        "excludeSocialMedia": {
                            "type": "boolean",
                            "default": False,
                            "description": "Exclude links to known social domains",
                        },
                        "excludeDomains": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Custom domain blocklist for links",
                        },
                    },
                    "additionalProperties": False,
                },
                "media": {
                    "type": "object",
                    "description": "Media filtering options",
                    "properties": {
                        "excludeExternalImages": {
                            "type": "boolean",
                            "default": False,
                            "description": "Exclude images hosted on other domains",
                        }
                    },
                    "additionalProperties": False,
                },
                "processIframes": {
                    "type": "boolean",
                    "default": False,
                    "description": "Merge iframe content into the main document",
                },
                "removeOverlays": {
                    "type": "boolean",
                    "default": False,
                    "description": "Attempt to remove overlay or modal elements",
                },
            },
            "additionalProperties": False,
        }

    def _build_output_options_schema(self) -> dict:
        """Build schema for output format options."""
        return {
            "type": "object",
            "description": "Fine-grained output options per format",
            "properties": {
                "markdown": self._build_markdown_options_schema(),
                "html": self._build_html_options_schema(),
                "structured": self._build_structured_options_schema(),
            },
            "additionalProperties": False,
        }

    def _build_markdown_options_schema(self) -> dict:
        """Build schema for markdown output options."""
        return {
            "type": "object",
            "properties": {
                "includeCitations": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include markdown with inline citations",
                },
                "includeReferences": {
                    "type": "boolean",
                    "default": False,
                    "description": "Append references section when citations are present",
                },
                "bodyWidth": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 0,
                    "description": "Wrap markdown to the specified column width (0 disables wrapping)",
                },
            },
            "additionalProperties": False,
        }

    @staticmethod
    def _build_html_options_schema() -> dict:
        """Build schema for HTML output options."""
        return {
            "type": "object",
            "properties": {
                "variant": {
                    "type": "string",
                    "enum": ["raw", "cleaned", "fit"],
                    "default": "cleaned",
                    "description": "HTML variant to return: raw, cleaned, or filtered (fit)",
                }
            },
            "additionalProperties": False,
        }

    def _build_structured_options_schema(self) -> dict:
        """Build schema for structured extraction options."""
        css_field_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Field name"},
                "selector": {"type": "string", "description": "CSS selector for the field"},
                "type": {
                    "type": "string",
                    "enum": ["text", "attribute", "html", "nested"],
                    "description": "Extraction type for this field",
                },
                "attribute": {
                    "type": "string",
                    "description": "Attribute to read when type=attribute",
                },
                "fields": {
                    "type": "array",
                    "items": {
                        "$ref": "#/properties/outputOptions/properties/structured/$defs/cssField"
                    },
                    "description": "Nested field definitions when type=nested",
                },
            },
            "required": ["name", "selector", "type"],
            "additionalProperties": False,
        }

        structured_schema = {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["css", "llm"],
                    "description": "Extraction method for structured output",
                },
                "css": {
                    "type": "object",
                    "properties": {
                        "baseSelector": {
                            "type": "string",
                            "description": "Base CSS selector for repeated blocks",
                        },
                        "fields": {
                            "type": "array",
                            "items": {
                                "$ref": "#/properties/outputOptions/properties/structured/$defs/cssField"
                            },
                            "minItems": 1,
                            "description": "Fields to extract from each matched block",
                        },
                    },
                    "required": ["baseSelector", "fields"],
                    "additionalProperties": False,
                    "description": "CSS-based structured extraction configuration",
                },
                "llm": {
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": ["string", "null"],
                            "description": "LLM provider name (e.g., openai, anthropic, realtimexai)",
                        },
                        "model": {
                            "type": "string",
                            "default": "auto",
                            "description": "Model identifier understood by the provider",
                        },
                        "instruction": {
                            "type": "string",
                            "description": "Instruction provided to the extraction model",
                        },
                        "temperature": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 2.0,
                            "default": 0.0,
                            "description": "Sampling temperature forwarded to the LLM",
                        },
                        "extractionType": {
                            "type": "string",
                            "enum": ["schema", "block"],
                            "description": "LLM extraction type: schema (structured JSON) or block (aggregated text)",
                        },
                        "schema": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "const": "object",
                                    "description": "JSON Schema type",
                                },
                                "properties": {
                                    "type": "object",
                                    "description": "JSON Schema properties definition",
                                },
                                "required": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Required JSON schema fields",
                                },
                            },
                            "required": ["type", "properties"],
                            "additionalProperties": True,
                            "description": "JSON Schema definition (required when extractionType=schema)",
                        },
                    },
                    "required": ["instruction", "extractionType"],
                    "additionalProperties": False,
                    "description": "LLM-powered structured extraction configuration",
                },
            },
            "required": ["method"],
            "additionalProperties": False,
            "allOf": [
                {
                    "if": {"properties": {"method": {"const": "css"}}},
                    "then": {"required": ["css"]},
                },
                {
                    "if": {"properties": {"method": {"const": "llm"}}},
                    "then": {"required": ["llm"]},
                },
                {
                    "if": {
                        "properties": {
                            "llm": {
                                "properties": {"extractionType": {"const": "schema"}},
                                "required": ["extractionType"],
                            }
                        },
                        "required": ["llm"],
                    },
                    "then": {"properties": {"llm": {"required": ["schema"]}}},
                },
            ],
            "$defs": {"cssField": css_field_schema},
        }

        return structured_schema

    @staticmethod
    def _build_advanced_schema() -> dict:
        """Build schema for advanced Crawl4AI options."""
        return {
            "type": "object",
            "description": "Advanced Crawl4AI controls",
            "properties": {
                "tableScoreThreshold": {
                    "type": "integer",
                    "minimum": 0,
                    "default": 7,
                    "description": "Minimum table score before inclusion",
                },
                "captureScreenshot": {
                    "type": "boolean",
                    "default": False,
                    "description": "Capture a screenshot of the page",
                },
                "capturePdf": {
                    "type": "boolean",
                    "default": False,
                    "description": "Capture a PDF representation of the page",
                },
                "captureMhtml": {
                    "type": "boolean",
                    "default": False,
                    "description": "Capture an MHTML snapshot of the page",
                },
            },
            "additionalProperties": False,
        }

    def _build_browser_schema(self) -> dict:
        """Build browser configuration schema."""
        return {
            "type": "object",
            "properties": {
                "headless": {
                    "type": "boolean",
                    "default": True,
                    "description": "Run in headless mode",
                },
                "userAgentMode": {
                    "type": "string",
                    "enum": [m.value for m in UserAgentMode],
                    "default": UserAgentMode.RANDOM.value,
                    "description": "User agent mode",
                },
                "userAgent": {
                    "type": "string",
                    "description": "Custom user agent string",
                },
                "textMode": {
                    "type": "boolean",
                    "default": True,
                    "description": "Disable images for faster crawling",
                },
                "proxy": {
                    "type": "object",
                    "properties": {
                        "server": {"type": "string"},
                        "username": {"type": "string"},
                        "password": {"type": "string"},
                    },
                    "required": ["server"],
                    "description": "Proxy configuration",
                },
            },
            "description": "Browser configuration",
        }

    def _build_page_schema(self) -> dict:
        """Build page interaction schema."""
        return {
            "type": "object",
            "properties": {
                "waitFor": {
                    "type": "string",
                    "description": "Wait condition (css: or js: prefix)",
                },
                "timeoutMs": {
                    "type": "integer",
                    "minimum": 1000,
                    "maximum": 300000,
                    "default": 60000,
                    "description": "Page timeout in milliseconds",
                },
            },
            "description": "Page interaction configuration",
        }

    def _build_retry_schema(self) -> dict:
        """Build retry configuration schema."""
        return {
            "type": "object",
            "properties": {
                "attempts": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 10,
                    "default": 2,
                    "description": "Maximum retry attempts",
                },
            },
            "description": "Retry configuration",
        }

    def build_web_scrape_tool(self) -> types.Tool:
        """Build the main web scraping tool."""
        return types.Tool(
            name="web_scrape",
            description="Perform web scraping using Crawl4AI with configurable content selection, filtering, and output formats",
            inputSchema=self.build_base_input_schema(),
            outputSchema=self.build_output_schema(),
        )

    def build_batch_scrape_tool(self) -> types.Tool:
        """Build the batch scraping tool."""
        additional_props = {
            "concurrency": {
                "type": "integer",
                "minimum": 1,
                "maximum": self.max_concurrent,
                "default": 3,
                "description": "Maximum concurrent requests",
            }
        }

        return types.Tool(
            name="batch_scrape",
            description="Perform batch web scraping with parallel processing for multiple URLs",
            inputSchema=self.build_base_input_schema(additional_props),
            outputSchema=self.build_output_schema(),
        )

    def build_scrape_with_session_tool(self) -> types.Tool:
        """Build the session-based scraping tool."""
        additional_props = {
            "sessionId": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100,
                "description": "Unique session identifier",
            },
            "jsCode": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 10,
                "description": "JavaScript code to execute",
            },
        }

        schema = self.build_base_input_schema(additional_props)
        schema["required"].append("sessionId")

        return types.Tool(
            name="scrape_with_session",
            description="Perform web scraping using persistent browser sessions for multi-step workflows",
            inputSchema=schema,
            outputSchema=self.build_output_schema(),
        )
