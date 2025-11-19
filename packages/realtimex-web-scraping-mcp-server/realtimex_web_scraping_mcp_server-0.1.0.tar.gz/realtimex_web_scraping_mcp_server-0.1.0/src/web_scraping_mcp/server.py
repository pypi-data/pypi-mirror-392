"""
Main MCP server implementation for Web Scraping.

Provides MCP tools for performing web scraping using Crawl4AI with multiple
extraction modes, browser automation, and comprehensive error handling.
"""

from typing import Any

import structlog
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import ValidationError

from .config import WebScrapingConfig
from .models import ScrapingMetadata, ScrapingRequest, ScrapingResponse
from .schema_builder import SchemaBuilder
from .scraping_manager import ScrapingManager

logger = structlog.get_logger(__name__)


class WebScrapingMCPServer:
    """
    MCP Server for Web Scraping operations.

    This server provides tools for performing web scraping using Crawl4AI
    with support for multiple extraction modes and browser automation.
    """

    def __init__(self, config: WebScrapingConfig):
        self.config = config
        self.server = Server(
            name=config.server.server_name,
            version=config.server.server_version,
        )
        self.scraping_manager = ScrapingManager(config)
        self.schema_builder = SchemaBuilder(
            max_urls_per_request=config.server.max_urls_per_request,
            max_concurrent=config.browser.max_concurrent,
        )
        self._initialized = False

        # Register MCP handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """Handle list_tools requests by returning available scraping tools."""
            try:
                logger.info("Received list_tools request")

                # Ensure server is initialized
                await self._ensure_initialized()

                # Build available tools
                tools = []

                # Main web scraping tool
                tools.append(self.schema_builder.build_web_scrape_tool())

                # Batch scraping tool
                tools.append(self.schema_builder.build_batch_scrape_tool())

                # Session-based scraping tool
                if self.config.server.enable_sessions:
                    tools.append(self.schema_builder.build_scrape_with_session_tool())

                logger.info(
                    "Returning available tools",
                    tool_count=len(tools),
                    tool_names=[tool.name for tool in tools],
                )

                return tools

            except Exception as e:
                logger.error("Error in list_tools handler", error=str(e))
                # Return empty list on error to avoid breaking MCP protocol
                return []

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            """Handle call_tool requests by executing the corresponding scraping operation."""
            logger.info(
                "Received call_tool request",
                tool_name=name,
                arguments=self._mask_sensitive_arguments(arguments),
            )

            try:
                # Ensure server is initialized
                await self._ensure_initialized()

                # Route to appropriate handler
                if name == "web_scrape":
                    return await self._handle_web_scrape(arguments)
                elif name == "batch_scrape":
                    return await self._handle_batch_scrape(arguments)
                elif name == "scrape_with_session":
                    return await self._handle_scrape_with_session(arguments)
                else:
                    available_tools = ["web_scrape", "batch_scrape"]
                    if self.config.server.enable_sessions:
                        available_tools.append("scrape_with_session")

                    error_msg = (
                        f"Unknown tool '{name}'. Available tools: {', '.join(available_tools)}"
                    )
                    logger.error("Unknown tool requested", tool_name=name)
                    raise ValueError(error_msg)

            except ValueError:
                # Re-raise ValueError for parameter validation errors
                raise
            except Exception as e:
                # Wrap unexpected errors
                error_msg = f"Internal server error while executing tool '{name}': {e!s}"
                logger.error(
                    "Unexpected error in call_tool handler",
                    tool_name=name,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise RuntimeError(error_msg) from e

    def _create_error_response(
        self, error: Exception, arguments: dict[str, Any], tool_name: str
    ) -> dict[str, Any]:
        """Create a ScrapingResponse-compliant error dictionary."""
        if isinstance(error, ValidationError):
            error_type = "ValidationError"
            error_message = f"Input validation error: {error}"
            logger.warning(
                "Input validation error in tool handler",
                tool_name=tool_name,
                error=error_message,
                arguments=self._mask_sensitive_arguments(arguments),
            )
        else:
            error_type = type(error).__name__
            error_message = str(error)
            logger.error(
                "Error in tool handler",
                tool_name=tool_name,
                error=error_message,
                error_type=error_type,
            )

        urls = arguments.get("urls", [])
        url_count = len(urls) if isinstance(urls, list) else 0

        output_format = arguments.get("outputFormat")
        if not isinstance(output_format, str):
            output_format = self.config.server.default_output_format.value

        summary = ScrapingMetadata(
            total_urls=url_count,
            successful=0,
            failed=url_count,
            output_format=output_format,
            execution_time=0.0,
        )

        response = ScrapingResponse(
            success=False,
            results=[],
            summary=summary,
            error=error_message,
            error_type=error_type,
        )
        return response.model_dump(mode="json")

    async def _ensure_initialized(self) -> None:
        """Ensure the server is properly initialized."""
        if not self._initialized:
            await self.scraping_manager.initialize()
            self._initialized = True

    async def _handle_web_scrape(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Handle web_scrape tool execution."""
        try:
            # Parse and validate request
            request = ScrapingRequest(**arguments)

            # Perform scraping
            response = await self.scraping_manager.scrape(request)

            # Convert to dict for MCP response
            return response.model_dump(mode="json")

        except (ValidationError, Exception) as e:
            # Create a structured error response instead of raising
            return self._create_error_response(e, arguments, "web_scrape")

    async def _handle_batch_scrape(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Handle batch_scrape tool execution."""
        try:
            # Parse and validate request
            request = ScrapingRequest(**arguments)

            # Ensure concurrency is set for batch processing
            if "concurrency" not in arguments:
                request.concurrency = 3

            # Perform scraping
            response = await self.scraping_manager.scrape(request)

            # Convert to dict for MCP response
            return response.model_dump(mode="json")

        except (ValidationError, Exception) as e:
            # Create a structured error response instead of raising
            return self._create_error_response(e, arguments, "batch_scrape")

    async def _handle_scrape_with_session(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Handle scrape_with_session tool execution."""
        try:
            # Parse and validate request
            request = ScrapingRequest(**arguments)

            # Perform scraping
            response = await self.scraping_manager.scrape(request)

            # Add session ID to response
            result_dict = response.model_dump(mode="json")
            result_dict["sessionId"] = request.sessionId

            return result_dict

        except (ValidationError, Exception) as e:
            # Create a structured error response instead of raising
            return self._create_error_response(e, arguments, "scrape_with_session")

    def _mask_sensitive_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]:
        """Mask sensitive information in arguments for logging."""
        masked = arguments.copy()

        # Mask proxy credentials
        if "browser" in masked and "proxy" in masked["browser"]:
            proxy = masked["browser"]["proxy"].copy()
            if "username" in proxy:
                proxy["username"] = "[MASKED]"
            if "password" in proxy:
                proxy["password"] = "[MASKED]"
            masked["browser"]["proxy"] = proxy

        # Mask JavaScript code (might contain sensitive data)
        if "jsCode" in masked:
            masked["jsCode"] = ["[MASKED_JS_CODE]"] * len(masked["jsCode"])

        return masked

    async def start(self) -> None:
        """Start the MCP server."""
        try:
            logger.info(
                "Starting Web Scraping MCP Server",
                server_name=self.config.server.server_name,
                default_output_format=self.config.server.default_output_format.value,
                llm_enabled=self.config.is_llm_enabled(),
                sessions_enabled=self.config.server.enable_sessions,
            )

            # Initialize components
            await self._ensure_initialized()

            # Start STDIO server
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP server started successfully")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )

        except Exception as e:
            logger.error("Failed to start MCP server", error=str(e))
            raise
        finally:
            await self.cleanup()

    async def cleanup(self) -> None:
        """Clean up server resources."""
        try:
            logger.info("Cleaning up MCP server resources")
            await self.scraping_manager.close()
            logger.info("MCP server cleanup completed")
        except Exception as e:
            logger.warning("Error during cleanup", error=str(e))
