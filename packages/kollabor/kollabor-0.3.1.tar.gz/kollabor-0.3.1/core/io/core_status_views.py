"""Core status views for the Kollabor CLI application."""

import logging
import psutil
from typing import List

from .status_renderer import StatusViewConfig, BlockConfig

logger = logging.getLogger(__name__)


class CoreStatusViews:
    """Provides default core status views for the application."""

    def __init__(self, llm_service=None):
        """Initialize core status views.

        Args:
            llm_service: LLM service instance for status data.
        """
        self.llm_service = llm_service

    def register_all_views(self, status_registry) -> None:
        """Register all core status views with the registry.

        Args:
            status_registry: StatusViewRegistry to register views with.
        """
        try:
            # View 1: Session Stats (priority 1000 - highest)
            session_view = StatusViewConfig(
                name="Session Stats",
                plugin_source="core",
                priority=1000,
                blocks=[
                    BlockConfig(
                        width_fraction=0.5,
                        content_provider=self._get_session_stats_content,
                        title="Session Stats",
                        priority=100,
                    ),
                    BlockConfig(
                        width_fraction=0.5,
                        content_provider=self._get_ai_status_content,
                        title="AI Status",
                        priority=90,
                    ),
                ],
            )
            status_registry.register_status_view("core", session_view)

            # View 2: Performance (priority 800)
            performance_view = StatusViewConfig(
                name="Performance",
                plugin_source="core",
                priority=800,
                blocks=[
                    BlockConfig(
                        width_fraction=1.0,
                        content_provider=self._get_performance_content,
                        title="Performance",
                        priority=100,
                    )
                ],
            )
            status_registry.register_status_view("core", performance_view)

            # View 3: Minimal (priority 600)
            minimal_view = StatusViewConfig(
                name="Minimal",
                plugin_source="core",
                priority=600,
                blocks=[
                    BlockConfig(
                        width_fraction=1.0,
                        content_provider=self._get_minimal_content,
                        title="Minimal",
                        priority=100,
                    )
                ],
            )
            status_registry.register_status_view("core", minimal_view)

            # View 4: LLM Details (priority 700)
            llm_view = StatusViewConfig(
                name="LLM Details",
                plugin_source="core",
                priority=700,
                blocks=[
                    BlockConfig(
                        width_fraction=1.0,
                        content_provider=self._get_llm_details_content,
                        title="LLM Configuration",
                        priority=100,
                    )
                ],
            )
            status_registry.register_status_view("core", llm_view)

            logger.info(
                "Registered 4 core status views: "
                "Session Stats, Performance, LLM Details, Minimal"
            )

        except Exception as e:
            logger.error(f"Failed to register core status views: {e}")

    def _get_session_stats_content(self) -> List[str]:
        """Get session statistics content."""
        try:
            # Get session stats from LLM service
            if self.llm_service and hasattr(self.llm_service, "session_stats"):
                stats = self.llm_service.session_stats
                return [
                    f"Messages: {stats.get('messages', 0)}",
                    f"Tokens In: {stats.get('input_tokens', 0)}",
                    f"Tokens Out: {stats.get('output_tokens', 0)}",
                ]
            return ["Messages: 0", "Tokens: 0"]
        except Exception:
            return ["Session: N/A"]

    def _get_ai_status_content(self) -> List[str]:
        """Get AI status content."""
        try:
            if self.llm_service:
                processing = (
                    "* Processing" if self.llm_service.is_processing else "✓ Ready"
                )
                if hasattr(self.llm_service, "processing_queue"):
                    queue_size = self.llm_service.processing_queue.qsize()
                else:
                    queue_size = 0

                # Get model and endpoint info from API service
                model = "Unknown"
                endpoint = "Unknown"
                if hasattr(self.llm_service, "api_service"):
                    api_service = self.llm_service.api_service
                    model = getattr(api_service, "model", "Unknown")
                    api_url = getattr(api_service, "api_url", "Unknown")
                    # Extract domain from URL for cleaner display
                    if api_url != "Unknown":
                        try:
                            from urllib.parse import urlparse

                            parsed = urlparse(api_url)
                            endpoint = parsed.hostname or api_url
                        except Exception:
                            endpoint = api_url

                return [
                    f"AI: {processing}",
                    f"Model: {model}",
                    f"Endpoint: {endpoint}",
                    f"Queue: {queue_size}",
                ]
            return ["AI: Unknown"]
        except Exception:
            return ["AI: N/A"]

    def _get_performance_content(self) -> List[str]:
        """Get performance content."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_gb = memory.used / (1024**3)

            return [
                f"CPU: {cpu_percent:.1f}%",
                f"RAM: {memory_gb:.1f}GB",
                f"Memory: {memory.percent:.1f}%",
            ]
        except Exception:
            return ["Performance: N/A"]

    def _get_minimal_content(self) -> List[str]:
        """Get minimal view content."""
        try:
            ai_status = "✓ Ready"
            model = "Unknown"
            if self.llm_service:
                if self.llm_service.is_processing:
                    ai_status = "* Processing"

                # Get model info
                if hasattr(self.llm_service, "api_service"):
                    model = getattr(self.llm_service.api_service, "model", "Unknown")

            messages = 0
            tokens = 0
            if self.llm_service and hasattr(self.llm_service, "session_stats"):
                stats = self.llm_service.session_stats
                messages = stats.get("messages", 0)
                input_tokens = stats.get("input_tokens", 0)
                output_tokens = stats.get("output_tokens", 0)
                tokens = input_tokens + output_tokens

            if tokens < 1000:
                token_display = f"{tokens}"
            else:
                token_display = f"{tokens/1000:.1f}K"

            return [
                f"AI: {ai_status} ({model}) | Messages: {messages} "
                f"| Tokens: {token_display}"
            ]
        except Exception:
            return ["Status: N/A"]

    def _get_llm_details_content(self) -> List[str]:
        """Get detailed LLM configuration content."""
        try:
            if not self.llm_service:
                return ["LLM: Not initialized"]

            ai_status = (
                "* Processing" if self.llm_service.is_processing else "✓ Ready"
            )
            model = "Unknown"
            endpoint = "Unknown"
            temperature = "Unknown"
            max_tokens = "Unknown"

            if hasattr(self.llm_service, "api_service"):
                api_service = self.llm_service.api_service
                model = getattr(api_service, "model", "Unknown")
                temperature = getattr(api_service, "temperature", "Unknown")
                max_tokens = getattr(api_service, "max_tokens", "Unknown")
                api_url = getattr(api_service, "api_url", "Unknown")

                # Extract domain from URL for cleaner display
                if api_url != "Unknown":
                    try:
                        from urllib.parse import urlparse

                        parsed = urlparse(api_url)
                        endpoint = parsed.hostname or api_url
                    except Exception:
                        endpoint = api_url

            return [
                f"Status: {ai_status}",
                f"Model: {model}",
                f"Endpoint: {endpoint}",
                f"Temperature: {temperature}",
                f"Max Tokens: {max_tokens}",
            ]
        except Exception:
            return ["LLM Details: N/A"]
