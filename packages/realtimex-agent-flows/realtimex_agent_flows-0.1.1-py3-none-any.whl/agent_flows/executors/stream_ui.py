"""StreamUIExecutor for rendering UI components during execution."""

import time
from typing import Any

from pydantic import ValidationError

from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors import StreamUIExecutorConfig
from agent_flows.models.executors.stream_ui import UIComponentDataType
from agent_flows.services import UIComponentProcessor
from agent_flows.streaming.models import (
    StreamDataContent,
    StreamDataType,
    StreamMessage,
    StreamType,
)
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class StreamUIExecutor(BaseExecutor):
    """Executor for streaming UI components to the chat interface."""

    def __init__(self) -> None:
        """Initialize the stream UI executor."""
        self.ui_processor = UIComponentProcessor()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["useLLM", "uiComponents"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return ["inputData"]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate stream UI configuration.

        Args:
            config: Step configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ValidationError: If configuration is invalid (Pydantic validation)
            ConfigurationError: If configuration is invalid (wrapped ValidationError)
        """
        try:
            StreamUIExecutorConfig(**config)
            return True

        except ValidationError as e:
            raise ConfigurationError(
                f"Stream UI executor configuration validation failed: {str(e)}"
            ) from e
        except Exception as e:
            raise ConfigurationError(
                f"Stream UI executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute stream UI component rendering.

        Args:
            config: Step configuration containing UI component parameters
            context: Execution context

        Returns:
            ExecutorResult with UI component data

        Raises:
            ExecutorError: If UI component streaming fails
        """
        start_time = time.time()

        try:
            validated_config = StreamUIExecutorConfig(**config)

            log.info(
                "Starting stream UI execution",
                use_llm=validated_config.useLLM,
                data_type=validated_config.uiComponents.dataType.value,
            )

            # Process UI component using shared service
            ui_component_data = await self.ui_processor.process(validated_config, context)
            llm_generated = validated_config.useLLM

            # Stream the UI component
            self._stream_ui_component(validated_config, ui_component_data, context)

            execution_time = time.time() - start_time

            log.info(
                "Stream UI completed successfully",
                execution_time=execution_time,
                data_type=validated_config.uiComponents.dataType.value,
                llm_generated=llm_generated,
            )

            return ExecutorResult(
                success=True,
                data=ui_component_data,
                variables_updated={},
                execution_time=execution_time,
                metadata={
                    "step_type": "streamUI",
                    "data_type": validated_config.uiComponents.dataType.value,
                    "llm_generated": llm_generated,
                    "streamed": True,
                },
            )

        except ValidationError as e:
            raise ConfigurationError(
                f"Stream UI executor configuration validation failed: {str(e)}"
            ) from e
        except ConfigurationError:
            raise
        except Exception as e:
            raise ExecutorError(f"Stream UI execution failed: {str(e)}") from e

    def _stream_ui_component(
        self,
        config: StreamUIExecutorConfig,
        ui_component_data: dict[str, Any],
        context: ExecutionContext,
    ) -> None:
        """Stream UI component via streaming handler.

        Args:
            config: Validated configuration
            ui_component_data: Processed UI component data
            context: Execution context
        """
        streaming_handler = getattr(context.step_execution_service, "streaming_handler", None)
        if not streaming_handler:
            log.debug("No streaming handler available, skipping UI component stream")
            return

        # Map data type to StreamDataType
        stream_data_type = self._map_to_stream_data_type(config.uiComponents.dataType.value)

        # Extract payload from the data structure
        payload = ui_component_data.get("data", {})

        if self._is_widget_data_type(config.uiComponents.dataType):
            stream_payload: StreamDataContent | dict[str, Any] = payload
        elif isinstance(payload, dict):
            # For dict payloads, preserve all fields as-is
            # This includes content, language, meta, and any custom extra fields
            # If 'content' is missing, use the entire payload as content
            if "content" not in payload:
                stream_payload = {"content": payload, "language": None}
            else:
                # Use dict directly to preserve all extra fields (language, meta, custom fields)
                stream_payload = payload
        else:
            # Non-dict payload (string or primitive) - wrap as StreamDataContent
            stream_payload = StreamDataContent(content=payload, language=None)

        # Create stream message
        message = StreamMessage(
            type=StreamType.RESPONSE_DATA,
            dataType=stream_data_type,
            data=stream_payload,
        )

        # Emit the message
        streaming_handler._emit(message)

        log.debug(
            "UI component streamed",
            data_type=config.uiComponents.dataType.value,
            stream_data_type=stream_data_type.value,
        )

    def _map_to_stream_data_type(self, ui_data_type: str) -> StreamDataType:
        """Map UIComponentDataType to StreamDataType.

        Args:
            ui_data_type: UI component data type

        Returns:
            Corresponding StreamDataType
        """
        type_mapping = {
            "text": StreamDataType.TEXT,
            "markdown": StreamDataType.MARKDOWN,
            "html": StreamDataType.HTML,
            "code": StreamDataType.CODE,
            "json": StreamDataType.JSON,
            "table": StreamDataType.TABLE,
            "image": StreamDataType.IMAGE,
            "video": StreamDataType.VIDEO,
            "audio": StreamDataType.AUDIO,
            "files": StreamDataType.FILES,
            "chart": StreamDataType.CHART,
            "mermaid": StreamDataType.MERMAID,
            "map": StreamDataType.MAP,
            "search": StreamDataType.SEARCH,
            "toolUse": StreamDataType.TOOL_USE,
            "openTab": StreamDataType.OPEN_TAB,
            "mcpUi": StreamDataType.MCP_UI,
            "widget": StreamDataType.WIDGET,
        }

        # For types not in the mapping, use AI_MESSAGE as a generic container
        return type_mapping.get(ui_data_type, StreamDataType.AI_MESSAGE)

    def _is_widget_data_type(self, data_type: UIComponentDataType) -> bool:
        """Check if the supplied UI data type represents a widget."""
        return data_type == UIComponentDataType.WIDGET
