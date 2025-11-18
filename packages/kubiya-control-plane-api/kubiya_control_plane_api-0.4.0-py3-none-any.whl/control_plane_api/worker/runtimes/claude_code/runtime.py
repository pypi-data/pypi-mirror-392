"""
Claude Code runtime implementation using Claude Code SDK.

This runtime adapter integrates the Claude Code SDK to power agents with
advanced coding capabilities, file operations, and specialized tools.

ALL 7 BUGS FIXED:
- Bug #1: Added metadata = {} initialization
- Bug #2: Replaced print() with logger.debug()
- Bug #3: Made MCP fallback patterns explicit
- Bug #4: Added session_id validation
- Bug #5: Added explicit disconnect() calls with timeout
- Bug #6: Added tool name validation
- Bug #7: Removed debug output
"""

from typing import Dict, Any, Optional, AsyncIterator, Callable, TYPE_CHECKING
import structlog
import asyncio
import time

from ..base import (
    RuntimeType,
    RuntimeExecutionResult,
    RuntimeExecutionContext,
    RuntimeCapabilities,
    BaseRuntime,
    RuntimeRegistry,
)
from .config import build_claude_options
from .utils import (
    extract_usage_from_result_message,
    extract_session_id_from_result_message,
)

if TYPE_CHECKING:
    from control_plane_client import ControlPlaneClient
    from services.cancellation_manager import CancellationManager

logger = structlog.get_logger(__name__)

# ⚡ PERFORMANCE: Lazy load Claude SDK at module level (not per-execution)
# This imports the SDK once when the module loads, making subsequent executions faster
_CLAUDE_SDK_AVAILABLE = False
_CLAUDE_SDK_IMPORT_ERROR = None
_SDK_CLASSES = {}

try:
    from claude_agent_sdk import (
        ClaudeSDKClient,
        AssistantMessage,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
        ToolResultBlock,
    )
    _CLAUDE_SDK_AVAILABLE = True
    _SDK_CLASSES = {
        'ClaudeSDKClient': ClaudeSDKClient,
        'AssistantMessage': AssistantMessage,
        'ResultMessage': ResultMessage,
        'TextBlock': TextBlock,
        'ToolUseBlock': ToolUseBlock,
        'ToolResultBlock': ToolResultBlock,
    }
    logger.info("claude_code_sdk_preloaded", status="success")
except ImportError as e:
    _CLAUDE_SDK_IMPORT_ERROR = str(e)
    logger.warning("claude_code_sdk_not_available", error=str(e))


@RuntimeRegistry.register(RuntimeType.CLAUDE_CODE)
class ClaudeCodeRuntime(BaseRuntime):
    """
    Runtime implementation using Claude Code SDK.

    This runtime leverages Claude Code's specialized capabilities for
    software engineering tasks, file operations, and developer workflows.

    Features:
    - Streaming execution with real-time updates
    - Conversation history support via ClaudeSDKClient
    - Custom tool integration via MCP
    - Hooks for tool execution monitoring
    - Cancellation support via interrupt()

    All critical bugs have been fixed in this refactored version.
    """

    def __init__(
        self,
        control_plane_client: "ControlPlaneClient",
        cancellation_manager: "CancellationManager",
        **kwargs,
    ):
        """
        Initialize the Claude Code runtime.

        Args:
            control_plane_client: Client for Control Plane API
            cancellation_manager: Manager for execution cancellation
            **kwargs: Additional configuration options
        """
        super().__init__(control_plane_client, cancellation_manager, **kwargs)

        # Track active SDK clients for cancellation
        self._active_clients: Dict[str, Any] = {}

        # Track custom MCP servers
        self._custom_mcp_servers: Dict[str, Any] = {}  # server_name -> mcp_server

    def get_runtime_type(self) -> RuntimeType:
        """Return RuntimeType.CLAUDE_CODE."""
        return RuntimeType.CLAUDE_CODE

    def get_capabilities(self) -> RuntimeCapabilities:
        """Return Claude Code runtime capabilities."""
        return RuntimeCapabilities(
            streaming=True,
            tools=True,
            mcp=True,
            hooks=True,
            cancellation=True,
            conversation_history=True,
            custom_tools=True,
        )

    async def _execute_impl(
        self, context: RuntimeExecutionContext
    ) -> RuntimeExecutionResult:
        """
        Execute agent using Claude Code SDK (non-streaming).

        Production-grade implementation with:
        - Comprehensive error handling
        - Proper resource cleanup
        - Detailed logging
        - Timeout management
        - Graceful degradation

        BUG FIX #1: Added metadata = {} initialization
        BUG FIX #5: Added explicit disconnect() call

        Args:
            context: Execution context with prompt, history, config

        Returns:
            RuntimeExecutionResult with response and metadata
        """
        client = None
        start_time = asyncio.get_event_loop().time()

        try:
            # ⚡ PERFORMANCE: Use pre-loaded SDK classes (loaded at module level)
            if not _CLAUDE_SDK_AVAILABLE:
                return RuntimeExecutionResult(
                    response="",
                    usage={},
                    success=False,
                    error=f"Claude Code SDK not available: {_CLAUDE_SDK_IMPORT_ERROR}",
                )

            ClaudeSDKClient = _SDK_CLASSES['ClaudeSDKClient']
            ResultMessage = _SDK_CLASSES['ResultMessage']

            self.logger.info(
                "starting_claude_code_non_streaming_execution",
                execution_id=context.execution_id,
                model=context.model_id,
                has_history=bool(context.conversation_history),
            )

            # Build Claude Code options with validation
            options, _ = build_claude_options(context)

            # Merge custom MCP servers
            if self._custom_mcp_servers:
                if not options.mcp_servers:
                    options.mcp_servers = {}

                for server_name, mcp_server in self._custom_mcp_servers.items():
                    options.mcp_servers[server_name] = mcp_server

                    # Add tool names to allowed_tools for permission
                    if hasattr(mcp_server, 'tools') and mcp_server.tools:
                        for tool in mcp_server.tools:
                            if hasattr(tool, 'name'):
                                tool_name = f"mcp__{server_name}__{tool.name}"
                                if tool_name not in options.allowed_tools:
                                    options.allowed_tools.append(tool_name)

                    self.logger.debug(
                        "custom_mcp_server_added_non_streaming",
                        server_name=server_name,
                        execution_id=context.execution_id
                    )

            # Create client and manually manage lifecycle
            client = ClaudeSDKClient(options=options)
            await client.connect()
            self._active_clients[context.execution_id] = client

            # Send prompt (SDK handles conversation history via session resume)
            prompt = context.prompt

            self.logger.debug(
                "sending_query_to_claude_code_sdk",
                execution_id=context.execution_id,
                prompt_length=len(prompt),
                using_session_resume=bool(options.resume),
            )

            await client.query(prompt)

            # Collect complete response
            response_text = ""
            usage = {}
            tool_messages = []
            finish_reason = None
            message_count = 0

            # BUG FIX #1: Initialize metadata before use
            metadata = {}

            # Use receive_response() to get messages until ResultMessage
            async for message in client.receive_response():
                message_count += 1

                # Extract content from AssistantMessage
                if hasattr(message, "content"):
                    for block in message.content:
                        if hasattr(block, "text"):
                            response_text += block.text
                        elif hasattr(block, "name"):  # ToolUseBlock
                            tool_messages.append(
                                {
                                    "tool": block.name,
                                    "input": getattr(block, "input", {}),
                                    "tool_use_id": getattr(block, "id", None),
                                }
                            )

                # Extract usage, finish reason, and session_id from ResultMessage
                if isinstance(message, ResultMessage):
                    usage = extract_usage_from_result_message(message)

                    if usage:
                        self.logger.info(
                            "claude_code_usage_extracted",
                            execution_id=context.execution_id[:8],
                            input_tokens=usage["input_tokens"],
                            output_tokens=usage["output_tokens"],
                            cache_read=usage["cache_read_tokens"],
                        )

                    finish_reason = message.subtype  # "success" or "error"

                    # BUG FIX #4: Extract and validate session_id
                    session_id = extract_session_id_from_result_message(
                        message, context.execution_id
                    )

                    if session_id:
                        # BUG FIX #1: metadata is now properly initialized
                        metadata["claude_code_session_id"] = session_id

                    self.logger.info(
                        "claude_code_execution_completed",
                        execution_id=context.execution_id[:8],
                        finish_reason=finish_reason,
                        message_count=message_count,
                        response_length=len(response_text),
                        tool_count=len(tool_messages),
                        tokens=usage.get("total_tokens", 0),
                        has_session_id=bool(session_id),
                    )
                    break

            elapsed_time = asyncio.get_event_loop().time() - start_time

            # Merge metadata with execution stats
            final_metadata = {
                **metadata,  # Includes claude_code_session_id if present
                "elapsed_time": elapsed_time,
                "message_count": message_count,
            }

            return RuntimeExecutionResult(
                response=response_text,
                usage=usage,
                success=finish_reason == "success",
                finish_reason=finish_reason or "stop",
                tool_execution_messages=tool_messages,  # Use standard field name for analytics
                tool_messages=tool_messages,  # Keep for backward compatibility
                model=context.model_id,
                metadata=final_metadata,
            )

        except ImportError as e:
            self.logger.error(
                "claude_code_sdk_not_installed",
                execution_id=context.execution_id,
                error=str(e),
            )
            return RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error=f"Claude Code SDK not available: {str(e)}",
            )

        except asyncio.TimeoutError:
            self.logger.error(
                "claude_code_execution_timeout",
                execution_id=context.execution_id,
                elapsed_time=asyncio.get_event_loop().time() - start_time,
            )
            return RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error="Execution timeout exceeded",
            )

        except asyncio.CancelledError:
            self.logger.warning(
                "claude_code_execution_cancelled",
                execution_id=context.execution_id,
            )
            raise  # Re-raise to propagate cancellation

        except Exception as e:
            self.logger.error(
                "claude_code_execution_failed",
                execution_id=context.execution_id,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )

            return RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error=f"{type(e).__name__}: {str(e)}",
            )

        finally:
            # BUG FIX #5: Explicit disconnect() with timeout
            if context.execution_id in self._active_clients:
                try:
                    client = self._active_clients[context.execution_id]

                    # Try to disconnect gracefully
                    try:
                        await asyncio.wait_for(client.disconnect(), timeout=2.0)
                        self.logger.debug(
                            "claude_sdk_client_disconnected",
                            execution_id=context.execution_id,
                        )
                    except asyncio.TimeoutError:
                        self.logger.warning(
                            "claude_sdk_disconnect_timeout",
                            execution_id=context.execution_id,
                            message="Forcefully closing client",
                        )
                    except Exception as e:
                        # This is expected - asyncio cancel scope errors are benign
                        # The SDK manages its own cleanup internally
                        self.logger.debug(
                            "claude_sdk_disconnect_error",
                            execution_id=context.execution_id,
                            error=str(e)[:100],  # Truncate long error messages
                            message="Non-critical disconnect error (SDK cleans up internally)",
                        )

                    # Remove from active clients
                    del self._active_clients[context.execution_id]
                    self.logger.debug(
                        "cleaned_up_claude_sdk_client_reference",
                        execution_id=context.execution_id,
                    )

                except Exception as cleanup_error:
                    self.logger.warning(
                        "error_during_client_cleanup",
                        execution_id=context.execution_id,
                        error=str(cleanup_error),
                    )

    async def _stream_execute_impl(
        self,
        context: RuntimeExecutionContext,
        event_callback: Optional[Callable[[Dict], None]] = None,
    ) -> AsyncIterator[RuntimeExecutionResult]:
        """
        Production-grade streaming execution with Claude Code SDK.

        This implementation provides:
        - Comprehensive error handling with specific exception types
        - Detailed structured logging at each stage
        - Proper resource cleanup with finally blocks
        - Real-time event callbacks for tool execution
        - Accumulated metrics and metadata tracking

        BUG FIX #5: Added explicit disconnect() call
        BUG FIX #7: Removed all debug output

        Args:
            context: Execution context with prompt, history, config
            event_callback: Optional callback for real-time events

        Yields:
            RuntimeExecutionResult chunks as they arrive, ending with final metadata
        """
        client = None
        start_time = asyncio.get_event_loop().time()
        chunk_count = 0

        try:
            # ⚡ PERFORMANCE: Use pre-loaded SDK classes (loaded at module level)
            if not _CLAUDE_SDK_AVAILABLE:
                yield RuntimeExecutionResult(
                    response="",
                    usage={},
                    success=False,
                    error=f"Claude Code SDK not available: {_CLAUDE_SDK_IMPORT_ERROR}",
                    finish_reason="error",
                )
                return

            ClaudeSDKClient = _SDK_CLASSES['ClaudeSDKClient']
            AssistantMessage = _SDK_CLASSES['AssistantMessage']
            ResultMessage = _SDK_CLASSES['ResultMessage']
            TextBlock = _SDK_CLASSES['TextBlock']
            ToolUseBlock = _SDK_CLASSES['ToolUseBlock']
            ToolResultBlock = _SDK_CLASSES['ToolResultBlock']

            self.logger.info(
                "starting_claude_code_streaming_execution",
                execution_id=context.execution_id,
                model=context.model_id,
                has_history=bool(context.conversation_history),
                has_callback=event_callback is not None,
            )

            # Build Claude Code options with hooks
            options, active_tools = build_claude_options(context, event_callback)

            # Merge custom MCP servers
            if self._custom_mcp_servers:
                if not options.mcp_servers:
                    options.mcp_servers = {}

                for server_name, mcp_server in self._custom_mcp_servers.items():
                    options.mcp_servers[server_name] = mcp_server

                    # Add tool names to allowed_tools for permission
                    if hasattr(mcp_server, 'tools') and mcp_server.tools:
                        for tool in mcp_server.tools:
                            if hasattr(tool, 'name'):
                                tool_name = f"mcp__{server_name}__{tool.name}"
                                if tool_name not in options.allowed_tools:
                                    options.allowed_tools.append(tool_name)

                    self.logger.debug(
                        "custom_mcp_server_added_streaming",
                        server_name=server_name,
                        execution_id=context.execution_id
                    )

            self.logger.info(
                "created_claude_code_sdk_options",
                execution_id=context.execution_id,
                has_tools=bool(context.skills),
                has_mcp=(
                    len(options.mcp_servers) > 0
                    if hasattr(options, "mcp_servers")
                    else False
                ),
                has_custom_mcp=len(self._custom_mcp_servers) > 0,
                has_hooks=bool(options.hooks) if hasattr(options, "hooks") else False,
                has_event_callback=event_callback is not None,
            )

            # Create client and manually manage lifecycle
            client = ClaudeSDKClient(options=options)
            await client.connect()
            self._active_clients[context.execution_id] = client

            # Cache execution metadata
            try:
                self.control_plane.cache_metadata(context.execution_id, "AGENT")
            except Exception as cache_error:
                self.logger.warning(
                    "failed_to_cache_metadata_non_fatal",
                    execution_id=context.execution_id,
                    error=str(cache_error),
                )

            # Send prompt
            prompt = context.prompt

            self.logger.debug(
                "sending_streaming_query_to_claude_code_sdk",
                execution_id=context.execution_id,
                prompt_length=len(prompt),
                using_session_resume=bool(options.resume),
            )

            await client.query(prompt)

            # Stream messages
            accumulated_response = ""
            accumulated_usage = {}
            tool_messages = []
            message_count = 0
            received_stream_events = False  # Track if we got streaming events

            # Generate unique message_id for this turn
            message_id = f"{context.execution_id}_{int(time.time() * 1000000)}"

            async for message in client.receive_response():
                message_count += 1
                message_type_name = type(message).__name__

                # Handle StreamEvent messages (partial chunks)
                if message_type_name == "StreamEvent":
                    if hasattr(message, "event") and message.event:
                        event_data = message.event

                        # Extract text from event data
                        content = None
                        if isinstance(event_data, dict):
                            event_type = event_data.get("type")

                            # Handle content_block_delta events
                            if event_type == "content_block_delta":
                                delta = event_data.get("delta", {})
                                if isinstance(delta, dict):
                                    content = delta.get("text")
                                elif isinstance(delta, str):
                                    content = delta

                            # Fallback: try direct text extraction
                            if not content:
                                content = event_data.get("text") or event_data.get(
                                    "content"
                                )

                        elif isinstance(event_data, str):
                            content = event_data
                        elif hasattr(event_data, "content"):
                            content = event_data.content
                        elif hasattr(event_data, "text"):
                            content = event_data.text

                        if content:
                            received_stream_events = True
                            chunk_count += 1
                            accumulated_response += content

                            # Publish event
                            if event_callback:
                                try:
                                    event_callback(
                                        {
                                            "type": "content_chunk",
                                            "content": content,
                                            "message_id": message_id,
                                            "execution_id": context.execution_id,
                                        }
                                    )
                                except Exception as callback_error:
                                    self.logger.warning(
                                        "stream_event_callback_failed",
                                        execution_id=context.execution_id,
                                        error=str(callback_error),
                                    )

                            # Yield chunk
                            yield RuntimeExecutionResult(
                                response=content,
                                usage={},
                                success=True,
                            )
                    continue  # Skip to next message

                # Handle assistant messages (final complete message)
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Skip if already streamed via StreamEvents
                            if received_stream_events:
                                continue

                            # Only send if we didn't receive StreamEvents
                            chunk_count += 1
                            accumulated_response += block.text

                            if event_callback:
                                try:
                                    event_callback(
                                        {
                                            "type": "content_chunk",
                                            "content": block.text,
                                            "message_id": message_id,
                                            "execution_id": context.execution_id,
                                        }
                                    )
                                except Exception as callback_error:
                                    self.logger.warning(
                                        "event_callback_failed_non_fatal",
                                        execution_id=context.execution_id,
                                        error=str(callback_error),
                                    )

                            yield RuntimeExecutionResult(
                                response=block.text,
                                usage={},
                                success=True,
                            )

                        elif isinstance(block, ToolUseBlock):
                            # Tool use event - Store for later lookup
                            tool_info = {
                                "tool": block.name,
                                "input": block.input,
                                "tool_use_id": block.id,
                            }
                            tool_messages.append(tool_info)
                            active_tools[block.id] = block.name

                        elif isinstance(block, ToolResultBlock):
                            # Tool result - Look up tool name from active_tools
                            tool_name = active_tools.get(block.tool_use_id, "unknown")
                            if tool_name == "unknown":
                                self.logger.warning(
                                    "could_not_find_tool_name_for_tool_use_id",
                                    execution_id=context.execution_id,
                                    tool_use_id=block.tool_use_id,
                                    active_tools_keys=list(active_tools.keys()),
                                )

                            status = "success" if not block.is_error else "failed"

                            # Publish via callback
                            if event_callback:
                                try:
                                    event_callback(
                                        {
                                            "type": "tool_complete",
                                            "tool_name": tool_name,
                                            "tool_execution_id": block.tool_use_id,
                                            "status": status,
                                            "output": (
                                                str(block.content)[:1000]
                                                if block.content
                                                else None
                                            ),
                                            "error": (
                                                str(block.content)
                                                if block.is_error
                                                else None
                                            ),
                                            "execution_id": context.execution_id,
                                        }
                                    )
                                except Exception as callback_error:
                                    self.logger.error(
                                        "tool_complete_callback_failed",
                                        execution_id=context.execution_id,
                                        tool_name=tool_name,
                                        error=str(callback_error),
                                        exc_info=True,
                                    )

                # Handle result message (final)
                elif isinstance(message, ResultMessage):
                    accumulated_usage = extract_usage_from_result_message(message)

                    # BUG FIX #4: Extract and validate session_id
                    session_id = extract_session_id_from_result_message(
                        message, context.execution_id
                    )

                    elapsed_time = asyncio.get_event_loop().time() - start_time

                    self.logger.info(
                        "claude_code_streaming_completed",
                        execution_id=context.execution_id,
                        finish_reason=message.subtype,
                        chunk_count=chunk_count,
                        message_count=message_count,
                        response_length=len(accumulated_response),
                        tool_count=len(tool_messages),
                        usage=accumulated_usage,
                        elapsed_time=f"{elapsed_time:.2f}s",
                        has_session_id=bool(session_id),
                    )

                    # Final result message
                    yield RuntimeExecutionResult(
                        response="",  # Already streamed
                        usage=accumulated_usage,
                        success=message.subtype == "success",
                        finish_reason=message.subtype,
                        tool_execution_messages=tool_messages,  # Use standard field name for analytics
                        tool_messages=tool_messages,  # Keep for backward compatibility
                        model=context.model_id,
                        metadata={
                            "accumulated_response": accumulated_response,
                            "elapsed_time": elapsed_time,
                            "chunk_count": chunk_count,
                            "message_count": message_count,
                            "claude_code_session_id": session_id,
                        },
                    )
                    break

        except ImportError as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(
                "claude_code_sdk_not_installed",
                execution_id=context.execution_id,
                error=str(e),
                elapsed_time=f"{elapsed_time:.2f}s",
            )
            yield RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error=f"Claude Code SDK not available: {str(e)}",
            )

        except asyncio.TimeoutError:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(
                "claude_code_streaming_timeout",
                execution_id=context.execution_id,
                elapsed_time=f"{elapsed_time:.2f}s",
                chunks_before_timeout=chunk_count,
            )
            yield RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error="Streaming execution timeout exceeded",
            )

        except asyncio.CancelledError:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            self.logger.warning(
                "claude_code_streaming_cancelled",
                execution_id=context.execution_id,
                elapsed_time=f"{elapsed_time:.2f}s",
                chunks_before_cancellation=chunk_count,
            )
            # Yield error result before re-raising
            yield RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error="Execution was cancelled",
            )
            raise  # Re-raise to propagate cancellation

        except Exception as e:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(
                "claude_code_streaming_failed",
                execution_id=context.execution_id,
                error=str(e),
                error_type=type(e).__name__,
                elapsed_time=f"{elapsed_time:.2f}s",
                chunks_before_error=chunk_count,
                exc_info=True,
            )
            yield RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error=f"{type(e).__name__}: {str(e)}",
            )

        finally:
            # BUG FIX #5: Explicit disconnect() with timeout
            if context.execution_id in self._active_clients:
                try:
                    client = self._active_clients[context.execution_id]

                    # Try to disconnect gracefully
                    try:
                        await asyncio.wait_for(client.disconnect(), timeout=2.0)
                        self.logger.debug(
                            "claude_sdk_client_disconnected",
                            execution_id=context.execution_id,
                        )
                    except asyncio.TimeoutError:
                        self.logger.warning(
                            "claude_sdk_disconnect_timeout",
                            execution_id=context.execution_id,
                            message="Forcefully closing client",
                        )
                    except Exception as e:
                        # This is expected - asyncio cancel scope errors are benign
                        # The SDK manages its own cleanup internally
                        self.logger.debug(
                            "claude_sdk_disconnect_error",
                            execution_id=context.execution_id,
                            error=str(e)[:100],  # Truncate long error messages
                            message="Non-critical disconnect error (SDK cleans up internally)",
                        )

                    # Remove from active clients
                    del self._active_clients[context.execution_id]
                    self.logger.debug(
                        "cleaned_up_claude_sdk_client_reference",
                        execution_id=context.execution_id,
                    )

                except Exception as cleanup_error:
                    self.logger.warning(
                        "error_during_streaming_client_cleanup",
                        execution_id=context.execution_id,
                        error=str(cleanup_error),
                    )

    async def cancel(self, execution_id: str) -> bool:
        """
        Cancel an in-progress execution via Claude SDK interrupt.

        Args:
            execution_id: ID of execution to cancel

        Returns:
            True if cancellation succeeded
        """
        if execution_id in self._active_clients:
            try:
                client = self._active_clients[execution_id]
                await client.interrupt()
                self.logger.info(
                    "claude_code_execution_interrupted", execution_id=execution_id
                )
                return True
            except Exception as e:
                self.logger.error(
                    "failed_to_interrupt_claude_code_execution",
                    execution_id=execution_id,
                    error=str(e),
                )
                return False
        return False

    # ==================== Custom Tool Extension API ====================

    def get_custom_tool_requirements(self) -> Dict[str, Any]:
        """
        Get requirements for creating custom MCP servers for Claude Code runtime.

        Returns:
            Dictionary with format, examples, and documentation for MCP servers
        """
        return {
            "format": "mcp_server",
            "description": "MCP server created with @tool decorator and create_sdk_mcp_server()",
            "example_code": '''
from claude_agent_sdk import tool, create_sdk_mcp_server
from typing import Any

@tool("my_function", "Description of what this tool does", {"arg": str})
async def my_function(args: dict[str, Any]) -> dict[str, Any]:
    """Tool function implementation."""
    return {
        "content": [{
            "type": "text",
            "text": f"Result: {args['arg']}"
        }]
    }

# Create MCP server
mcp_server = create_sdk_mcp_server(
    name="my_tools",
    version="1.0.0",
    tools=[my_function]
)
            ''',
            "documentation_url": "https://docs.claude.ai/agent-sdk/custom-tools",
            "required_attributes": ["name", "version"],
            "schema": {
                "type": "mcp_server",
                "required": ["name", "version", "tools"]
            }
        }

    def validate_custom_tool(self, mcp_server: Any) -> tuple[bool, Optional[str]]:
        """
        Validate an MCP server for Claude Code runtime.

        Args:
            mcp_server: MCP server instance to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required attributes
        for attr in ['name', 'version']:
            if not hasattr(mcp_server, attr):
                return False, f"MCP server must have '{attr}' attribute"

        # Validate name
        if not isinstance(mcp_server.name, str) or not mcp_server.name:
            return False, "MCP server name must be non-empty string"

        # Check for tools (optional but recommended)
        if hasattr(mcp_server, 'tools'):
            if not mcp_server.tools:
                self.logger.warning(
                    "mcp_server_has_no_tools",
                    server_name=mcp_server.name
                )

        return True, None

    def register_custom_tool(self, mcp_server: Any, metadata: Optional[Dict] = None) -> str:
        """
        Register a custom MCP server with Claude Code runtime.

        Args:
            mcp_server: MCP server instance
            metadata: Optional metadata (ignored, server name is used)

        Returns:
            Server name (identifier for this MCP server)

        Raises:
            ValueError: If MCP server validation fails or name conflicts
        """
        # Validate first
        is_valid, error = self.validate_custom_tool(mcp_server)
        if not is_valid:
            raise ValueError(f"Invalid MCP server: {error}")

        server_name = mcp_server.name

        # Check for name conflicts
        if server_name in self._custom_mcp_servers:
            raise ValueError(f"MCP server '{server_name}' already registered")

        # Store MCP server
        self._custom_mcp_servers[server_name] = mcp_server

        # Extract tool names for logging
        tool_names = []
        if hasattr(mcp_server, 'tools') and mcp_server.tools:
            tool_names = [
                f"mcp__{server_name}__{t.name}"
                for t in mcp_server.tools
                if hasattr(t, 'name')
            ]

        self.logger.info(
            "custom_mcp_server_registered",
            server_name=server_name,
            tool_count=len(tool_names),
            tools=tool_names
        )

        return server_name

    def get_registered_custom_tools(self) -> list[str]:
        """
        Get list of registered custom MCP server names.

        Returns:
            List of server names
        """
        return list(self._custom_mcp_servers.keys())
