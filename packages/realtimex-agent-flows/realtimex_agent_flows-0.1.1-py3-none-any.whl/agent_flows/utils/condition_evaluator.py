"""Condition evaluation logic for reuse across executors."""

import operator as op
from typing import Any

import structlog

from agent_flows.core.resources import VariableInterpolator
from agent_flows.models.shared import (
    Combinator,
    ComparisonOperator,
    ConditionDefinition,
    SimpleCondition,
)

logger = structlog.get_logger(__name__)


class ConditionEvaluator:
    """Evaluates conditions with support for combinators and nested conditions."""

    def __init__(self):
        """Initialize the condition evaluator."""
        self.interpolator = VariableInterpolator()

    async def evaluate(self, condition: ConditionDefinition, variables: dict[str, Any]) -> bool:
        """Evaluate a condition definition against variables.

        Args:
            condition: Condition definition to evaluate
            variables: Variables dictionary for evaluation

        Returns:
            Boolean result of condition evaluation

        Raises:
            ValueError: If condition evaluation fails
        """
        try:
            return await self._evaluate_condition_group(condition, variables)
        except Exception as e:
            raise ValueError(f"Failed to evaluate condition: {str(e)}") from e

    async def _evaluate_condition_group(
        self, condition_group: ConditionDefinition, variables: dict[str, Any]
    ) -> bool:
        """Evaluate a condition group with combinator.

        Args:
            condition_group: Condition group to evaluate
            variables: Variables dictionary for evaluation

        Returns:
            Boolean result of condition group evaluation
        """
        combinator = condition_group.combinator
        conditions = condition_group.conditions

        logger.debug(
            "Evaluating condition group",
            combinator=combinator,
            conditions_count=len(conditions),
        )

        # Evaluate each condition in the group
        results = []
        for i, sub_condition in enumerate(conditions):
            try:
                if isinstance(sub_condition, SimpleCondition):
                    result = await self._evaluate_simple_condition(sub_condition, variables)
                elif isinstance(sub_condition, ConditionDefinition):
                    result = await self._evaluate_condition_group(sub_condition, variables)
                else:
                    raise ValueError(f"Unsupported condition type: {type(sub_condition)}")

                results.append(result)

                logger.debug(
                    "Sub-condition evaluated",
                    condition_index=i,
                    condition_type=type(sub_condition).__name__,
                    result=result,
                )

            except Exception as e:
                raise ValueError(f"Failed to evaluate sub-condition {i}: {str(e)}") from e

        # Apply combinator logic
        if combinator == Combinator.AND:
            final_result = all(results)
        elif combinator == Combinator.OR:
            final_result = any(results)
        elif combinator == Combinator.NOT:
            # 'not' should have exactly one condition (validated in ConditionDefinition)
            final_result = not results[0]
        else:
            raise ValueError(f"Unsupported combinator: {combinator}")

        logger.debug(
            "Condition group evaluated",
            combinator=combinator,
            individual_results=results,
            final_result=final_result,
        )

        return final_result

    async def _evaluate_simple_condition(
        self, condition: SimpleCondition, variables: dict[str, Any]
    ) -> bool:
        """Evaluate a single condition.

        Args:
            condition: Simple condition to evaluate
            variables: Variables dictionary for evaluation

        Returns:
            Boolean result of condition evaluation
        """
        # Use interpolator for {{...}} format variable resolution
        variable_value = self.interpolator.interpolate_object(condition.variable, variables)

        # If interpolation returned the original string unchanged, variable was not found
        if (
            variable_value == condition.variable
            and isinstance(condition.variable, str)
            and condition.variable.strip().startswith("{{")
            and condition.variable.strip().endswith("}}")
        ):
            raise ValueError(f"Variable '{condition.variable}' not found in execution context")

        # Interpolate the comparison value (supports strings, objects, and complex templates)
        comparison_value = self.interpolator.interpolate_object(condition.value, variables)

        # Evaluate based on operator
        logger.debug(
            "Evaluating simple condition",
            variable=condition.variable,
            variable_value=variable_value,
            operator=condition.operator,
            comparison_value=comparison_value,
        )

        return self._apply_operator(variable_value, condition.operator, comparison_value)

    def _is_empty(self, v: Any) -> bool:
        """Check if a value is considered empty."""
        # None is empty
        if v is None:
            return True
        # Strings: empty after stripping
        if isinstance(v, str):
            return len(v.strip()) == 0
        # Collections: empty containers
        if isinstance(v, list | tuple | set | dict):
            return len(v) == 0
        # Everything else (numbers, booleans) are NOT "empty"
        return False

    def _apply_operator(  # noqa: PLR0911
        self, variable_value: Any, operator: ComparisonOperator, comparison_value: Any
    ) -> bool:
        """Apply comparison operator to values.

        Args:
            variable_value: Value from variable (can be None if variable not found)
            operator: Comparison operator
            comparison_value: Value to compare against

        Returns:
            Boolean result of comparison

        Raises:
            ValueError: If operator is not supported or comparison fails
        """
        try:
            # Handle empty/null checks first (don't need type conversion)
            if operator == ComparisonOperator.IS_EMPTY:
                return self._is_empty(variable_value)

            elif operator == ComparisonOperator.IS_NOT_EMPTY:
                return not self._is_empty(variable_value)

            # For other operators, handle different data types appropriately
            elif operator == ComparisonOperator.EQUALS:
                return self._compare_values(variable_value, comparison_value, "==")

            elif operator == ComparisonOperator.NOT_EQUALS:
                return self._compare_values(variable_value, comparison_value, "!=")

            elif operator == ComparisonOperator.GREATER_THAN:
                return self._compare_values(variable_value, comparison_value, ">")

            elif operator == ComparisonOperator.LESS_THAN:
                return self._compare_values(variable_value, comparison_value, "<")

            elif operator == ComparisonOperator.GREATER_THAN_OR_EQUAL:
                return self._compare_values(variable_value, comparison_value, ">=")

            elif operator == ComparisonOperator.LESS_THAN_OR_EQUAL:
                return self._compare_values(variable_value, comparison_value, "<=")

            # String operations (always convert to strings)
            elif operator == ComparisonOperator.CONTAINS:
                if isinstance(variable_value, list | tuple | set):
                    return comparison_value in variable_value
                return str(comparison_value) in str(variable_value)

            elif operator == ComparisonOperator.NOT_CONTAINS:
                if isinstance(variable_value, list | tuple | set):
                    return comparison_value not in variable_value
                return str(comparison_value) not in str(variable_value)

            elif operator == ComparisonOperator.STARTS_WITH:
                return str(variable_value).startswith(str(comparison_value))

            elif operator == ComparisonOperator.ENDS_WITH:
                return str(variable_value).endswith(str(comparison_value))

            else:
                raise ValueError(f"Unsupported operator: {operator}")

        except Exception as e:
            raise ValueError(f"Failed to apply operator {operator}: {str(e)}") from e

    def _compare_values(self, value1: Any, value2: Any, operator: str) -> bool:
        """Compare two values with intelligent type handling.

        Args:
            value1: First value to compare
            value2: Second value to compare
            operator: Comparison operator as string

        Returns:
            Boolean result of comparison

        Raises:
            ValueError: If comparison cannot be performed
        """
        # Define operator mappings
        numeric_ops = {"==": op.eq, "!=": op.ne, ">": op.gt, "<": op.lt, ">=": op.ge, "<=": op.le}

        equality_ops = {"==": op.eq, "!=": op.ne}
        relational_ops = {">": op.gt, "<": op.lt, ">=": op.ge, "<=": op.le}

        if operator not in numeric_ops:
            raise ValueError(f"Unsupported operator: {operator}")

        # Try numeric comparison first
        try:
            num1 = self._to_number(value1)
            num2 = self._to_number(value2)
            return numeric_ops[operator](num1, num2)
        except (ValueError, TypeError):
            pass

        # For equality operators, allow string fallback
        if operator in equality_ops:
            str1 = str(value1)
            str2 = str(value2)
            return equality_ops[operator](str1, str2)

        # For relational operators, try datetime comparison
        if operator in relational_ops:
            try:
                dt1 = self._to_datetime(value1)
                dt2 = self._to_datetime(value2)
                return relational_ops[operator](dt1, dt2)
            except (ValueError, TypeError, ImportError) as e:
                raise ValueError(
                    f"Cannot perform relational comparison '{operator}' between "
                    f"'{value1}' (type: {type(value1).__name__}) and "
                    f"'{value2}' (type: {type(value2).__name__}). "
                    f"Values must be numeric or valid datetime strings."
                ) from e

        # This should never be reached due to the initial operator check
        raise ValueError(f"Cannot perform comparison with operator {operator}")

    def _to_datetime(self, value: Any):
        """Convert a value to a datetime object.

        Args:
            value: Value to convert (string, datetime, or timestamp)

        Returns:
            datetime object

        Raises:
            ValueError: If value cannot be converted to datetime
        """
        from datetime import datetime

        import dateutil.parser

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            try:
                # Try to parse as ISO format first, then flexible parsing
                return dateutil.parser.parse(value)
            except (ValueError, TypeError) as e:
                raise ValueError(f"String '{value}' cannot be converted to datetime") from e

        if isinstance(value, int | float):
            try:
                # Assume it's a Unix timestamp
                return datetime.fromtimestamp(value)
            except (ValueError, OSError) as e:
                raise ValueError(f"Number '{value}' cannot be converted to datetime") from e

        raise ValueError(f"Value of type {type(value)} cannot be converted to datetime")

    def _to_number(self, value: Any) -> float:
        """Convert a value to a number (int or float).

        Args:
            value: Value to convert

        Returns:
            Numeric value

        Raises:
            ValueError: If value cannot be converted to a number
        """
        if isinstance(value, int | float):
            return float(value)

        if isinstance(value, str):
            # Try to convert string to number
            value = value.strip()

            # Handle empty strings
            if not value:
                raise ValueError("Empty string cannot be converted to number")

            # Try integer first, then float
            try:
                if "." in value or "e" in value.lower():
                    return float(value)
                else:
                    return float(int(value))
            except ValueError as e:
                raise ValueError(f"String '{value}' cannot be converted to number") from e

        # Try to convert other types
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Value of type {type(value)} cannot be converted to number") from e
