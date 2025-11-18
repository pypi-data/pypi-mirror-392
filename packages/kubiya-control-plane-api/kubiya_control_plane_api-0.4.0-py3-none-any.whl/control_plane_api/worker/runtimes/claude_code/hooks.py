"""
Hook system for Claude Code runtime tool execution monitoring.

This module provides pre-tool and post-tool hooks for real-time event
publishing and monitoring of tool execution.

BUG FIX #2: Replaced all print() statements with structured logging.
"""

from typing import Dict, Any, Callable, Optional
import structlog
import os

logger = structlog.get_logger(__name__)

# Check if verbose debug logging is enabled
DEBUG_MODE = os.getenv("CLAUDE_CODE_DEBUG", "false").lower() == "true"


def build_hooks(
    execution_id: str,
    event_callback: Optional[Callable[[Dict], None]],
    active_tools: Dict[str, str],
) -> Dict[str, Any]:
    """
    Build hooks for tool execution monitoring.

    Hooks intercept events like PreToolUse and PostToolUse to provide
    real-time feedback and monitoring. Since Claude Code SDK doesn't send
    ToolResultBlock in the stream, hooks are the only place to publish
    tool_completed events.

    Args:
        execution_id: Execution ID for event tracking
        event_callback: Callback for publishing events
        active_tools: Shared dict mapping tool_use_id -> tool_name

    Returns:
        Dict of hook configurations
    """
    from claude_agent_sdk import HookMatcher

    async def pre_tool_hook(input_data, tool_use_id, tool_context):
        """
        Hook called before tool execution.

        BUG FIX #2: Uses logger.debug() instead of print().
        """
        # BUG FIX #2: Use structured logging instead of print
        if DEBUG_MODE:
            logger.debug(
                "pre_tool_hook_called",
                tool_use_id=tool_use_id,
                input_data_type=type(input_data).__name__,
                input_data_keys=(
                    list(input_data.keys()) if isinstance(input_data, dict) else None
                ),
                has_tool_context=bool(tool_context),
            )

        # Try to extract tool name from input_data
        tool_name = "unknown"
        tool_args = {}

        if isinstance(input_data, dict):
            # Check if input_data has tool_name like output_data does
            tool_name = input_data.get("tool_name", "unknown")
            tool_args = input_data.get("tool_input", {})

            if DEBUG_MODE:
                if tool_name == "unknown":
                    logger.debug(
                        "pre_tool_hook_no_tool_name",
                        tool_use_id=tool_use_id,
                        input_data_keys=list(input_data.keys()),
                    )
                else:
                    logger.debug(
                        "pre_tool_hook_found_tool_name",
                        tool_use_id=tool_use_id,
                        tool_name=tool_name,
                    )

        # Publish tool_start event
        if event_callback and tool_name != "unknown":
            try:
                event_callback(
                    {
                        "type": "tool_start",
                        "tool_name": tool_name,
                        "tool_args": tool_args,
                        "tool_execution_id": tool_use_id,
                        "execution_id": execution_id,
                    }
                )
                if DEBUG_MODE:
                    logger.debug(
                        "pre_tool_hook_published_tool_start",
                        tool_use_id=tool_use_id,
                        tool_name=tool_name,
                    )
            except Exception as e:
                logger.error(
                    "failed_to_publish_tool_start",
                    tool_name=tool_name,
                    tool_use_id=tool_use_id,
                    error=str(e),
                    exc_info=True,
                )

        return {}

    async def post_tool_hook(output_data, tool_use_id, tool_context):
        """
        Hook called after tool execution.

        BUG FIX #2: Uses logger.debug() instead of print().
        """
        # Extract tool name from output_data (provided by Claude Code SDK)
        tool_name = "unknown"
        if isinstance(output_data, dict):
            # Claude SDK provides tool_name directly in output_data
            tool_name = output_data.get("tool_name", "unknown")

        is_error = tool_context.get("is_error", False)

        # BUG FIX #2: Use structured logging instead of print
        if DEBUG_MODE:
            logger.debug(
                "post_tool_hook_called",
                tool_use_id=tool_use_id,
                tool_name=tool_name,
                is_error=is_error,
                status="failed" if is_error else "success",
            )

        # Publish tool_complete event (hooks are the ONLY place for Claude Code)
        # ToolResultBlock doesn't appear in Claude Code streams
        if event_callback:
            try:
                event_callback(
                    {
                        "type": "tool_complete",
                        "tool_name": tool_name,
                        "tool_execution_id": tool_use_id,
                        "status": "failed" if is_error else "success",
                        "output": str(output_data)[:1000] if output_data else None,
                        "error": str(output_data) if is_error else None,
                        "execution_id": execution_id,
                    }
                )
                if DEBUG_MODE:
                    logger.debug(
                        "post_tool_hook_published_tool_complete",
                        tool_use_id=tool_use_id,
                        tool_name=tool_name,
                        is_error=is_error,
                    )
            except Exception as e:
                logger.error(
                    "failed_to_publish_tool_complete",
                    tool_name=tool_name,
                    tool_use_id=tool_use_id,
                    error=str(e),
                    exc_info=True,
                )

        return {}

    # Build hook configuration
    hooks = {
        "PreToolUse": [HookMatcher(hooks=[pre_tool_hook])],
        "PostToolUse": [HookMatcher(hooks=[post_tool_hook])],
    }

    return hooks
