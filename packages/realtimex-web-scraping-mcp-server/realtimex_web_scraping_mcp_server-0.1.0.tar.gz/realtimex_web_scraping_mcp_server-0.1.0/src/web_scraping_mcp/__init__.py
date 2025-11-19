"""
Web Scraping MCP Server

A Model Context Protocol (MCP) server that provides utility tools for web scraping
using Crawl4AI as the core engine. Supports multiple extraction modes including
markdown generation, HTML processing, structured data extraction via CSS selectors,
and AI-powered semantic analysis.

This package provides a production-ready MCP server with comprehensive web scraping
capabilities, structured output, and robust error handling.
"""

__version__ = "1.0.0"
__author__ = "RealTimeX"
__email__ = "info@realtimex.ai"

from web_scraping_mcp.exceptions import ScrapingError
from web_scraping_mcp.models import ScrapingResponse, ScrapingResult
from web_scraping_mcp.server import WebScrapingMCPServer

__all__ = [
    "ScrapingError",
    "ScrapingResponse",
    "ScrapingResult",
    "WebScrapingMCPServer",
]
