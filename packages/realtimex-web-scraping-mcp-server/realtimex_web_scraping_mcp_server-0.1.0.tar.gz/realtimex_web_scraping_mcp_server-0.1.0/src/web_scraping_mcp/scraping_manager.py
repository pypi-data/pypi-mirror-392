"""
Scraping Manager for Web Scraping MCP Server.

Manages scraping operations using Crawl4AI with comprehensive error handling,
session management, and support for multiple output formats.
"""

import asyncio
import json
import os
import time
from urllib.parse import urlparse, urlunparse

import structlog
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import (
    JsonCssExtractionStrategy,
    LLMExtractionStrategy,
)
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import WebScrapingConfig
from .exceptions import BrowserError, ExtractionError, NetworkError
from .models import (
    OutputFormat,
    ScrapingMetadata,
    ScrapingRequest,
    ScrapingResponse,
    ScrapingResult,
    UserAgentMode,
)

logger = structlog.get_logger(__name__)


class ScrapingManager:
    """Manages web scraping operations using Crawl4AI."""

    def __init__(self, config: WebScrapingConfig):
        self.config = config
        self.crawlers: dict[str, AsyncWebCrawler] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the scraping manager."""
        if self._initialized:
            return

        try:
            logger.info("Initializing ScrapingManager")
            self._initialized = True
            logger.info("ScrapingManager initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize ScrapingManager", error=str(e))
            raise

    async def close(self) -> None:
        """Clean up resources."""
        try:
            logger.info("Closing ScrapingManager")

            for session_id, crawler in self.crawlers.items():
                try:
                    await crawler.close()
                    logger.debug("Closed crawler", session_id=session_id)
                except Exception as e:
                    logger.warning(
                        "Error closing crawler",
                        session_id=session_id,
                        error=str(e),
                    )

            self.crawlers.clear()
            self._initialized = False
            logger.info("ScrapingManager closed successfully")
        except Exception as e:
            logger.warning("Error closing ScrapingManager", error=str(e))

    async def scrape(self, request: ScrapingRequest) -> ScrapingResponse:
        """Perform web scraping based on the request configuration."""
        if not self._initialized:
            await self.initialize()

        start_time = time.time()

        try:
            logger.info(
                "Starting web scraping operation",
                url_count=len(request.urls),
                output_format=request.outputFormat.value,
                session_id=request.sessionId,
            )

            results = await self._execute_scraping_with_retries(request)
            execution_time = time.time() - start_time

            successful_count = sum(1 for result in results if result.success)
            failed_count = len(results) - successful_count

            summary = ScrapingMetadata(
                total_urls=len(request.urls),
                successful=successful_count,
                failed=failed_count,
                output_format=request.outputFormat.value,
                execution_time=execution_time,
            )

            logger.info(
                "Web scraping completed",
                execution_time=execution_time,
                successful=successful_count,
                failed=failed_count,
            )

            return ScrapingResponse(
                success=successful_count > 0,
                results=results,
                summary=summary,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            error_type = type(e).__name__

            logger.error(
                "Web scraping operation failed",
                error=error_msg,
                error_type=error_type,
                execution_time=execution_time,
            )

            return ScrapingResponse(
                success=False,
                results=[],
                summary=ScrapingMetadata(
                    total_urls=len(request.urls),
                    successful=0,
                    failed=len(request.urls),
                    output_format=request.outputFormat.value,
                    execution_time=execution_time,
                ),
                error=error_msg,
                error_type=error_type,
            )

    async def _execute_scraping_with_retries(
        self, request: ScrapingRequest
    ) -> list[ScrapingResult]:
        """Execute scraping with retry logic."""
        retry_config = request.get_retry_config()

        if retry_config.attempts == 0:
            return await self._scrape_urls(request)

        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(retry_config.attempts + 1),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                retry=retry_if_exception_type((NetworkError, BrowserError)),
                reraise=True,
            ):
                with attempt:
                    if attempt.retry_state.attempt_number > 1:
                        logger.info(
                            "Retrying web scraping",
                            attempt=attempt.retry_state.attempt_number,
                            max_attempts=retry_config.attempts + 1,
                        )

                    return await self._scrape_urls(request)

        except RetryError as e:
            original_error = e.last_attempt.exception()
            raise ExtractionError(
                f"Web scraping failed after {retry_config.attempts + 1} attempts: {original_error!s}"
            ) from original_error

    async def _scrape_urls(self, request: ScrapingRequest) -> list[ScrapingResult]:
        """Scrape multiple URLs with optional concurrency control."""
        if request.concurrency == 1 or len(request.urls) == 1:
            results = []
            for url in request.urls:
                result = await self._scrape_single_url(url, request)
                results.append(result)
            return results
        else:
            semaphore = asyncio.Semaphore(request.concurrency)
            tasks = []

            async def scrape_with_semaphore(url: str) -> ScrapingResult:
                async with semaphore:
                    return await self._scrape_single_url(url, request)

            for url in request.urls:
                task = asyncio.create_task(scrape_with_semaphore(url))
                tasks.append(task)

            return await asyncio.gather(*tasks, return_exceptions=False)

    async def _scrape_single_url(self, url: str, request: ScrapingRequest) -> ScrapingResult:
        """Scrape a single URL."""
        try:
            logger.debug(
                "Processing URL",
                url=self._mask_sensitive_url(url),
                output_format=request.outputFormat.value,
            )

            crawler = await self._get_crawler(request)
            run_config = self._create_crawler_config(request)
            result = await crawler.arun(url=url, config=run_config)

            if result.success:
                processed_result = self._process_crawl_result(result, request, url)

                logger.debug(
                    "Successfully processed URL",
                    url=self._mask_sensitive_url(url),
                    content_length=len(str(processed_result.content)),
                )

                return processed_result
            else:
                error_msg = result.error_message or "Unknown crawling error"
                logger.warning(
                    "Failed to process URL",
                    url=self._mask_sensitive_url(url),
                    error=error_msg,
                    status_code=result.status_code,
                )

                return ScrapingResult(
                    url=url,
                    success=False,
                    content=None,
                    metadata={"status_code": result.status_code},
                    error=error_msg,
                )

        except Exception as e:
            error_msg = str(e)
            logger.error(
                "Exception while processing URL",
                url=self._mask_sensitive_url(url),
                error=error_msg,
                error_type=type(e).__name__,
            )

            return ScrapingResult(
                url=url,
                success=False,
                content=None,
                metadata={},
                error=error_msg,
            )

    async def _get_crawler(self, request: ScrapingRequest) -> AsyncWebCrawler:
        """Get or create a crawler instance."""
        session_key = request.sessionId or "default"

        if session_key in self.crawlers:
            return self.crawlers[session_key]

        browser_config = self._create_browser_config(request.get_browser_config())
        crawler = AsyncWebCrawler(config=browser_config)
        await crawler.start()

        self.crawlers[session_key] = crawler

        logger.debug("Created new crawler", session_id=session_key)
        return crawler

    def _create_browser_config(self, browser_config) -> BrowserConfig:
        """Create Crawl4AI browser configuration."""
        config_dict = {
            "browser_type": "chromium",
            "headless": browser_config.headless,
            "text_mode": browser_config.textMode,
            "use_managed_browser": True,
            "cdp_url": browser_config.cdp_url or self.config.browser.cdp_url,
            "user_data_dir": os.path.join(os.path.expanduser("~"), ".realtimex.ai", "Chrome"),
        }

        if browser_config.userAgentMode == UserAgentMode.RANDOM:
            config_dict["user_agent_mode"] = "random"
        elif browser_config.userAgentMode == UserAgentMode.DEFAULT and browser_config.userAgent:
            config_dict["user_agent"] = browser_config.userAgent

        if browser_config.proxy:
            proxy_url = browser_config.proxy.server
            if browser_config.proxy.username and browser_config.proxy.password:
                parsed = urlparse(proxy_url)
                netloc = f"{browser_config.proxy.username}:{browser_config.proxy.password}@{parsed.netloc}"
                proxy_url = urlunparse(parsed._replace(netloc=netloc))

            config_dict["proxy"] = proxy_url

        logger.debug("Created browser config", config_dict=config_dict)
        return BrowserConfig(**config_dict)

    def _create_crawler_config(self, request: ScrapingRequest) -> CrawlerRunConfig:
        """Create Crawl4AI crawler run configuration."""
        page_config = request.get_page_config()
        advanced_config = request.get_advanced_config()

        run_config_dict = {
            "page_timeout": page_config.timeoutMs,
            "delay_before_return_html": page_config.delayBeforeReturnHtml,
        }

        if page_config.waitFor:
            run_config_dict["wait_for"] = page_config.waitFor

        if request.jsCode:
            run_config_dict["js_code"] = request.jsCode

        if request.sessionId:
            run_config_dict["session_id"] = request.sessionId

        # Content selection
        if request.contentSelection:
            if request.contentSelection.cssSelector:
                run_config_dict["css_selector"] = request.contentSelection.cssSelector
            elif request.contentSelection.targetElements:
                run_config_dict["target_elements"] = request.contentSelection.targetElements

        # Content filtering
        if request.contentFiltering:
            if request.contentFiltering.excludedTags:
                run_config_dict["excluded_tags"] = request.contentFiltering.excludedTags

            if request.contentFiltering.wordCountThreshold is not None:
                run_config_dict["word_count_threshold"] = (
                    request.contentFiltering.wordCountThreshold
                )

            if request.contentFiltering.links:
                if request.contentFiltering.links.excludeExternal:
                    run_config_dict["exclude_external_links"] = True
                if request.contentFiltering.links.excludeSocialMedia:
                    run_config_dict["exclude_social_media_links"] = True
                if request.contentFiltering.links.excludeDomains:
                    run_config_dict["exclude_domains"] = (
                        request.contentFiltering.links.excludeDomains
                    )

            if (
                request.contentFiltering.media
                and request.contentFiltering.media.excludeExternalImages
            ):
                run_config_dict["exclude_external_images"] = True

            if request.contentFiltering.processIframes:
                run_config_dict["process_iframes"] = True

            if request.contentFiltering.removeOverlays:
                run_config_dict["remove_overlay_elements"] = True

        # Advanced features
        run_config_dict["table_score_threshold"] = advanced_config.tableScoreThreshold
        run_config_dict["screenshot"] = advanced_config.captureScreenshot
        run_config_dict["pdf"] = advanced_config.capturePdf
        run_config_dict["capture_mhtml"] = advanced_config.captureMhtml

        # Extraction strategy for structured output
        if request.outputFormat == OutputFormat.STRUCTURED and request.outputOptions:
            structured_options = request.outputOptions.structured
            if structured_options:
                if structured_options.method == "css" and structured_options.css:
                    extraction_strategy = self._create_css_extraction_strategy(
                        structured_options.css
                    )
                    run_config_dict["extraction_strategy"] = extraction_strategy
                elif structured_options.method == "llm" and structured_options.llm:
                    extraction_strategy = self._create_llm_extraction_strategy(
                        structured_options.llm
                    )
                    run_config_dict["extraction_strategy"] = extraction_strategy

        logger.debug("Created crawler config", run_config_dict=run_config_dict)
        return CrawlerRunConfig(**run_config_dict)

    def _create_css_extraction_strategy(self, css_config) -> JsonCssExtractionStrategy:
        """Create JSON CSS extraction strategy."""
        crawl4ai_schema = {
            "name": "ExtractedData",
            "baseSelector": css_config.baseSelector,
            "fields": self._serialize_css_fields(css_config.fields),
        }

        return JsonCssExtractionStrategy(crawl4ai_schema)

    def _serialize_css_fields(self, fields: list) -> list[dict]:
        """Serialize CSS field configurations for Crawl4AI."""
        result = []
        for field in fields:
            field_def = {
                "name": field.name,
                "selector": field.selector,
                "type": field.type,
            }

            if field.type == "attribute" and field.attribute:
                field_def["attribute"] = field.attribute

            if field.type == "nested" and field.fields:
                field_def["fields"] = self._serialize_css_fields(field.fields)

            result.append(field_def)
        return result

    def _create_llm_extraction_strategy(self, llm_config) -> LLMExtractionStrategy:
        """Create LLM extraction strategy."""
        provider_model = self._build_crawl4ai_model_string(
            provider=llm_config.provider, model=llm_config.model
        )

        crawl4ai_llm_config = self._build_llm_provider_config(
            provider=llm_config.provider,
            provider_model=provider_model,
            temperature=llm_config.temperature,
        )

        # Handle schema-based vs block-based extraction
        kwargs = {
            "llm_config": crawl4ai_llm_config,
            "instruction": llm_config.instruction,
            "extraction_type": llm_config.extractionType,
        }

        # Add schema if extraction type is "schema"
        if llm_config.extractionType == "schema" and llm_config.schema:
            kwargs["schema"] = llm_config.schema.model_dump()

        return LLMExtractionStrategy(**kwargs)

    def _build_crawl4ai_model_string(self, provider: str | None, model: str) -> str:
        """Build Crawl4AI model string in provider/model format."""
        if not provider or provider == "realtimexai":
            return model

        if "/" in model:
            return model
        else:
            return f"{provider}/{model}"

    def _build_llm_provider_config(
        self, provider: str | None, provider_model: str, temperature: float
    ) -> LLMConfig:
        """Build LLM provider configuration for Crawl4AI."""
        if provider == "realtimexai":
            return LLMConfig(
                provider=provider_model,
                base_url=self.config.llm.base_url,
                api_token=self.config.llm.api_key,
                temperature=temperature,
            )
        else:
            return LLMConfig(
                provider=provider_model,
                temperature=temperature,
            )

    def _process_crawl_result(self, result, request: ScrapingRequest, url: str) -> ScrapingResult:
        """Process Crawl4AI result based on output format."""
        metadata = {
            "title": result.metadata.get("title", "") if result.metadata else "",
            "status_code": result.status_code,
            "final_url": result.url,
        }

        content = None

        # Process based on output format
        if request.outputFormat == OutputFormat.MARKDOWN:
            content = self._extract_markdown_content(result, request)

        elif request.outputFormat == OutputFormat.HTML:
            content = self._extract_html_content(result, request)

        elif request.outputFormat == OutputFormat.STRUCTURED:
            content = self._extract_structured_content(result, request, url)

        # Add additional metadata
        if result.links:
            metadata["links"] = {
                "internal": result.links.get("internal", []),
                "external": result.links.get("external", []),
            }

        if result.media:
            metadata["media"] = {
                "images": len(result.media.get("images", [])),
                "videos": len(result.media.get("videos", [])),
                "audio": len(result.media.get("audio", [])),
            }

        if result.tables:
            metadata["tables_count"] = len(result.tables)

        return ScrapingResult(
            url=url,
            success=True,
            content=content,
            metadata=metadata,
        )

    def _extract_markdown_content(self, result, request: ScrapingRequest) -> str:
        """Extract markdown content with optional citations."""
        if not result.markdown:
            return ""

        markdown_options = request.outputOptions.markdown if request.outputOptions else None

        if markdown_options:
            if markdown_options.includeCitations and hasattr(
                result.markdown, "markdown_with_citations"
            ):
                return result.markdown.markdown_with_citations
            if markdown_options.includeReferences and hasattr(
                result.markdown, "references_markdown"
            ):
                base_markdown = result.markdown.raw_markdown
                references = result.markdown.references_markdown
                return f"{base_markdown}\n\n{references}" if references else base_markdown

        return result.markdown.raw_markdown

    def _extract_html_content(self, result, request: ScrapingRequest) -> str:
        """Extract HTML content based on variant."""
        html_options = request.outputOptions.html if request.outputOptions else None
        variant = html_options.variant if html_options else "cleaned"

        if variant == "raw":
            return result.html or ""
        elif variant == "fit" and hasattr(result, "fit_html"):
            return result.fit_html or result.cleaned_html or ""
        else:  # cleaned (default)
            return result.cleaned_html or ""

    def _extract_structured_content(
        self, result, request: ScrapingRequest, url: str
    ) -> dict | list | str:
        """Extract structured content from extraction strategy."""
        if not result.extracted_content:
            return (
                []
                if request.outputOptions
                and request.outputOptions.structured
                and request.outputOptions.structured.method == "css"
                else ""
            )

        try:
            # Try to parse as JSON
            return json.loads(result.extracted_content)
        except json.JSONDecodeError:
            # Return as-is if not JSON (for block-based LLM extraction)
            logger.warning("Failed to parse structured extraction result as JSON", url=url)
            return result.extracted_content

    def _mask_sensitive_url(self, url: str) -> str:
        """Mask sensitive information in URL for logging."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return "[MASKED_URL]"

            if parsed.username or parsed.password:
                netloc = parsed.netloc
                if "@" in netloc:
                    netloc = "[MASKED]@" + netloc.split("@", 1)[1]
                return url.replace(parsed.netloc, netloc)

            if parsed.query:
                sensitive_params = [
                    "api_key",
                    "apikey",
                    "token",
                    "password",
                    "secret",
                    "auth",
                    "key",
                ]
                for param in sensitive_params:
                    if param in parsed.query.lower():
                        return (
                            f"{parsed.scheme}://{parsed.netloc}{parsed.path}?[MASKED_QUERY_PARAMS]"
                        )

            return url

        except Exception:
            return "[MASKED_URL]"

    async def kill_session(self, session_id: str) -> bool:
        """Kill a specific browser session."""
        if session_id in self.crawlers:
            try:
                await self.crawlers[session_id].close()
                del self.crawlers[session_id]
                logger.info("Killed browser session", session_id=session_id)
                return True
            except Exception as e:
                logger.error("Failed to kill session", session_id=session_id, error=str(e))
                return False
        return False
