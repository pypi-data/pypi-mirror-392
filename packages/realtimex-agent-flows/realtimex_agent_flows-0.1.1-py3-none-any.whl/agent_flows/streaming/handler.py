"""Main streaming handler for flow execution events."""

import json
import logging
import uuid
from collections.abc import Callable
from typing import Any, Protocol

from .models import (
    InlineContent,
    InlineContentNested,
    StreamDataType,
    StreamMessage,
    StreamType,
)

logger = logging.getLogger(__name__)


class RedisClient(Protocol):
    """Protocol for Redis client to avoid importing redis at module level."""

    def ping(self) -> bool: ...
    def publish(self, channel: str, message: str) -> int: ...


class StreamingHandler:
    """Main handler for streaming flow execution events to the frontend."""

    def __init__(
        self,
        output_callback: Callable[[dict[str, Any]], None] | None = None,
        session_id: str | None = None,
        redis_url: str = "redis://localhost:6379",
    ):
        """Initialize the streaming handler.

        Args:
            output_callback: Custom callback for handling stream messages
            session_id: Session ID for Redis publishing
            redis_url: Redis connection URL
        """
        self.output_callback = output_callback or self._default_output
        self._message_id: str | None = None
        self._flow_name: str | None = None
        self._step_count = 0
        self._session_id = session_id
        self._redis_client: RedisClient | None = None
        self._redis_url = redis_url

    def _get_redis_client(self) -> RedisClient | None:
        """Get or create Redis client for session publishing."""
        if not self._session_id:
            return None

        if self._redis_client is None:
            try:
                import redis

                self._redis_client = redis.from_url(
                    self._redis_url,
                    db=1,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
                # Test connection
                self._redis_client.ping()
            except ImportError:
                logger.debug("Redis not available, falling back to callback output")
                self._redis_client = None
            except Exception:
                logger.debug("Redis connection failed, falling back to callback output")
                self._redis_client = None

        return self._redis_client

    def _default_output(self, message: dict[str, Any]) -> None:
        """Default output function that avoids noisy stdout during local runs."""
        logger.debug("Stream message: %s", message)

    def _get_message_id(self) -> str:
        """Get or create the fixed message ID for this flow execution."""
        if self._message_id is None:
            self._message_id = str(uuid.uuid4())
        return self._message_id

    def _emit(self, message: StreamMessage) -> None:
        """Emit a stream message via Redis or fallback to output callback."""
        message_dict = message.to_dict()

        # Try Redis publishing first if session ID is available
        redis_client = self._get_redis_client()
        if redis_client and self._session_id:
            try:
                redis_message = f".message {json.dumps(message_dict)}"
                redis_client.publish(self._session_id, redis_message)
                return
            except Exception:
                # Fallback to default output on Redis failure
                pass

        # Fallback to output callback
        self.output_callback(message_dict)

    def stream_step(
        self,
        tool_name: str,
        tool_icon: str,
        task: str,
        content: str,
        is_final: bool = False,
    ) -> None:
        """Stream a step update to the frontend.

        Args:
            tool_name: Display name for the tool/step type
            tool_icon: Lucide icon name
            task: Brief description of current task
            content: HTML content to display
            is_final: Whether this is the final step (status: completed)
        """
        self._step_count += 1
        status = "completed" if is_final else "processing"

        message = StreamMessage(
            uuid=self._get_message_id(),
            type=StreamType.RESPONSE_DATA,
            dataType=StreamDataType.INLINE_OPEN,
            data=InlineContent(
                blockId=1,
                content=InlineContentNested(
                    toolName=tool_name,
                    toolIcon=tool_icon,
                    task=task,
                    mainTask=self._flow_name or "Flow Execution",
                    content=content,
                    status=status,
                ),
            ),
        )
        self._emit(message)

    def flow_started(self, flow_name: str | None = None) -> None:
        """Initialize tracking for new flow execution.

        Args:
            flow_name: Optional display name for the flow
        """
        self._message_id = str(uuid.uuid4())
        self._step_count = 0
        self._flow_name = flow_name

    def flow_completed(self, success: bool, execution_time: float) -> None:
        """Stream final completion step."""
        icon = "CheckCircle" if success else "AlertCircle"
        task = "Execution finished" if success else "Execution failed"
        content = f"Flow completed {'successfully' if success else 'with errors'} in {execution_time:.1f}s"

        self.stream_step("Flow Complete", icon, task, content, is_final=True)

    def flow_error(self, error_message: str) -> None:
        """Stream error completion step."""
        content = f"Flow failed: {error_message}"
        self.stream_step("Flow Error", "AlertCircle", "Execution failed", content, is_final=True)

    def _get_tool_info(self, step_type: str | None) -> dict[str, str]:
        """Get tool icon and display name for step type."""
        tool_mapping = {
            "flow_variables": {"name": "Flow Variables", "icon": "Settings"},
            "apiCall": {"name": "API Call", "icon": "Globe"},
            "llmInstruction": {"name": "LLM Instruction", "icon": "Brain"},
            "webScraping": {"name": "Web Scraping", "icon": "Download"},
            "webSearch": {"name": "Web Search", "icon": "Search"},
            "conditional": {"name": "Conditional", "icon": "GitBranch"},
            "switch": {"name": "Switch", "icon": "ToggleLeft"},
            "loop": {"name": "Loop", "icon": "RotateCw"},
            "mcpServerAction": {"name": "MCP Server", "icon": "Server"},
        }
        return tool_mapping.get(step_type or "", {"name": "Unknown", "icon": "HelpCircle"})
