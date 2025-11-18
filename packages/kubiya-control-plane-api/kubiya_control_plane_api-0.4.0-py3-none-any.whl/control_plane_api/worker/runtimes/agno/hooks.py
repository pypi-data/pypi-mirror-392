"""
Tool execution hooks for Agno runtime.

This module provides:
- Tool execution event hooks
- Real-time event publishing to Control Plane
- Event callback creation
- Tool execution tracking
"""

import time
import structlog
from typing import Callable, Any, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from control_plane_client import ControlPlaneClient

logger = structlog.get_logger(__name__)


def create_tool_hook_for_streaming(
    control_plane: "ControlPlaneClient",
    execution_id: str,
) -> Callable:
    """
    Create a tool hook for streaming execution that publishes directly to Control Plane.

    This hook publishes tool events immediately (not batched) for real-time visibility.
    Used in streaming execution mode.

    Args:
        control_plane: Control Plane client for publishing events
        execution_id: Execution ID for this run

    Returns:
        Tool hook function for Agno agent
    """
    def tool_hook(
        name: str = None,
        function_name: str = None,
        function=None,
        arguments: dict = None,
        **kwargs,
    ):
        """Hook to capture tool execution for real-time streaming"""
        tool_name = name or function_name or "unknown"
        tool_args = arguments or {}
        tool_execution_id = f"{tool_name}_{int(time.time() * 1000000)}"

        # Publish tool start event (blocking call - OK in thread)
        control_plane.publish_event(
            execution_id=execution_id,
            event_type="tool_started",
            data={
                "tool_name": tool_name,
                "tool_execution_id": tool_execution_id,
                "tool_arguments": tool_args,
                "message": f"Executing tool: {tool_name}",
            }
        )

        # Execute tool
        result = None
        error = None
        try:
            if function and callable(function):
                result = function(**tool_args) if tool_args else function()
            else:
                raise ValueError(f"Function not callable: {function}")
            status = "success"
        except Exception as e:
            error = e
            status = "failed"
            logger.error(
                "tool_execution_failed",
                tool_name=tool_name,
                error=str(e),
            )

        # Publish tool completion event
        control_plane.publish_event(
            execution_id=execution_id,
            event_type="tool_completed",
            data={
                "tool_name": tool_name,
                "tool_execution_id": tool_execution_id,
                "status": status,
                "tool_output": str(result)[:1000] if result else None,
                "tool_error": str(error) if error else None,
                "message": f"Tool {status}: {tool_name}",
            }
        )

        if error:
            raise error
        return result

    return tool_hook


def create_tool_hook_with_callback(
    execution_id: str,
    event_callback: Callable[[Dict[str, Any]], None],
) -> Callable:
    """
    Create a tool hook that uses a callback for event publishing.

    This hook uses a callback function to publish events, allowing for flexible
    event handling (batching, filtering, etc.). Used in non-streaming execution.

    Args:
        execution_id: Execution ID for this run
        event_callback: Callback function for event publishing

    Returns:
        Tool hook function for Agno agent
    """
    def tool_hook(
        name: str = None,
        function_name: str = None,
        function=None,
        arguments: dict = None,
        **kwargs,
    ):
        """Hook to capture tool execution for real-time streaming"""
        tool_name = name or function_name or "unknown"
        tool_args = arguments or {}
        tool_execution_id = f"{tool_name}_{int(time.time() * 1000000)}"

        # Publish tool start event via callback
        event_callback(
            {
                "type": "tool_start",
                "tool_name": tool_name,
                "tool_execution_id": tool_execution_id,
                "tool_args": tool_args,
                "execution_id": execution_id,
            }
        )

        # Execute tool
        result = None
        error = None
        try:
            if function and callable(function):
                result = function(**tool_args) if tool_args else function()
            else:
                raise ValueError(f"Function not callable: {function}")

            status = "success"

        except Exception as e:
            error = e
            status = "failed"
            logger.error(
                "tool_execution_failed",
                tool_name=tool_name,
                error=str(e),
            )

        # Publish tool completion event via callback
        event_callback(
            {
                "type": "tool_complete",
                "tool_name": tool_name,
                "tool_execution_id": tool_execution_id,
                "status": status,
                "output": str(result)[:1000] if result else None,
                "error": str(error) if error else None,
                "execution_id": execution_id,
            }
        )

        if error:
            raise error

        return result

    return tool_hook
