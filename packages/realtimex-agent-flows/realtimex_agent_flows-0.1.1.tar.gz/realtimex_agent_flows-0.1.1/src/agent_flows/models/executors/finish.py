"""Finish executor configuration model."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..shared import CommonValidators
from .stream_ui import UIComponentsConfig


class FinishExecutorConfig(BaseModel):
    """Configuration for FinishExecutor."""

    model_config = ConfigDict(extra="allow")

    message: str = Field(
        "Flow execution finished", description="Optional message to include with flow termination"
    )
    data: Any = Field(None, description="Optional custom data to include with termination")
    resultVariable: str | None = Field(None, description="Variable to store finish information")

    # UI streaming fields
    flowAsOutput: bool = Field(False, description="Whether to use flow result as the output")
    useLLM: bool | None = Field(
        None, description="Whether to use LLM to generate UI component data"
    )
    inputData: str | dict[str, Any] | list[Any] | None = Field(
        None, description="Input data for LLM or static mode (required when useLLM is true)"
    )
    uiComponents: UIComponentsConfig | None = Field(
        None, description="UI component configuration for finish step"
    )

    # Apply common validators
    _validate_message = CommonValidators.validate_finish_message
    _validate_result_variable = CommonValidators.validate_result_variable

    @field_validator("uiComponents", mode="before")
    @classmethod
    def validate_ui_components(cls, v: Any, info: Any) -> Any:
        """Validate UI components configuration."""
        use_llm = info.data.get("useLLM")

        # If uiComponents is provided, useLLM must also be provided
        if v is not None and use_llm is None:
            raise ValueError("useLLM must be specified when uiComponents is provided")

        # If useLLM is true, inputData and uiComponents are required
        if use_llm is True:
            if v is None:
                raise ValueError("uiComponents is required when useLLM is true")
            input_data = info.data.get("inputData")
            if input_data is None:
                raise ValueError("inputData is required when useLLM is true")

        return v
