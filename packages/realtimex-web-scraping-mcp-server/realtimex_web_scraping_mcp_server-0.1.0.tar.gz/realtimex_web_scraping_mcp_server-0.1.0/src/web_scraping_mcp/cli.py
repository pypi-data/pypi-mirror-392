"""
Command-line interface for Web Scraping MCP Server.

Provides the main entry point for running the server with proper
logging configuration and error handling.
"""

import asyncio
import sys

from web_scraping_mcp.config import load_config
from web_scraping_mcp.logging_setup import get_logger, setup_logging
from web_scraping_mcp.server import WebScrapingMCPServer


async def main_async() -> None:
    """Main async entry point for the server."""
    logger = get_logger(__name__)

    try:
        # Load configuration
        config = load_config()

        # Create and start server
        server = WebScrapingMCPServer(config)
        await server.start()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down gracefully")
    except Exception as e:
        logger.error("Server startup failed", error=str(e), error_type=type(e).__name__)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    # Setup logging first
    setup_logging()

    logger = get_logger(__name__)
    logger.info("Starting Web Scraping MCP Server")

    try:
        # Run the async main function
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Server shutdown completed")
    except Exception as e:
        logger.error("Unexpected error", error=str(e), error_type=type(e).__name__)
        sys.exit(1)


if __name__ == "__main__":
    main()
