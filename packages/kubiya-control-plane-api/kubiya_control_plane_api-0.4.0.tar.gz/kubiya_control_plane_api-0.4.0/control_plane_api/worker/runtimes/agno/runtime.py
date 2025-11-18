"""
Agno runtime implementation.

This is the main runtime class that provides Agno framework integration
for the Agent Control Plane.
"""

import asyncio
import queue
import threading
import time
import structlog
from typing import Dict, Any, Optional, AsyncIterator, Callable, TYPE_CHECKING

from ..base import (
    RuntimeType,
    RuntimeExecutionResult,
    RuntimeExecutionContext,
    RuntimeCapabilities,
    BaseRuntime,
    RuntimeRegistry,
)
from control_plane_api.worker.services.event_publisher import (
    EventPublisher,
    EventPublisherConfig,
    EventPriority,
)

from .config import build_agno_agent_config
from .hooks import create_tool_hook_for_streaming, create_tool_hook_with_callback
from .utils import (
    build_conversation_messages,
    extract_usage,
    extract_tool_messages,
    extract_response_content,
)

if TYPE_CHECKING:
    from control_plane_client import ControlPlaneClient
    from services.cancellation_manager import CancellationManager

logger = structlog.get_logger(__name__)


@RuntimeRegistry.register(RuntimeType.DEFAULT)
class AgnoRuntime(BaseRuntime):
    """
    Runtime implementation using Agno framework.

    This runtime wraps the Agno-based agent execution logic,
    providing a clean interface that conforms to the AgentRuntime protocol.

    Features:
    - LiteLLM-based model execution
    - Real-time streaming with event batching
    - Tool execution hooks
    - Conversation history support
    - Comprehensive usage tracking
    """

    def __init__(
        self,
        control_plane_client: "ControlPlaneClient",
        cancellation_manager: "CancellationManager",
        **kwargs,
    ):
        """
        Initialize the Agno runtime.

        Args:
            control_plane_client: Client for Control Plane API
            cancellation_manager: Manager for execution cancellation
            **kwargs: Additional configuration options
        """
        super().__init__(control_plane_client, cancellation_manager, **kwargs)
        self._custom_tools: Dict[str, Any] = {}  # tool_id -> tool instance

    def get_runtime_type(self) -> RuntimeType:
        """Return RuntimeType.DEFAULT."""
        return RuntimeType.DEFAULT

    def get_capabilities(self) -> RuntimeCapabilities:
        """Return Agno runtime capabilities."""
        return RuntimeCapabilities(
            streaming=True,
            tools=True,
            mcp=False,
            hooks=True,
            cancellation=True,
            conversation_history=True,
            custom_tools=True  # Agno supports custom Python tools
        )

    async def _execute_impl(
        self, context: RuntimeExecutionContext
    ) -> RuntimeExecutionResult:
        """
        Execute agent using Agno framework without streaming.

        Args:
            context: Execution context with prompt, history, config

        Returns:
            RuntimeExecutionResult with response and metadata
        """
        try:
            # Merge regular skills with custom tools
            all_skills = list(context.skills) if context.skills else []

            # Add custom tools
            if self._custom_tools:
                for tool_id, custom_tool in self._custom_tools.items():
                    try:
                        # Get toolkit from custom tool
                        toolkit = custom_tool.get_tools()

                        # Extract tools - handle both Toolkit objects and iterables
                        if hasattr(toolkit, 'tools'):
                            all_skills.extend(toolkit.tools)
                        elif hasattr(toolkit, '__iter__'):
                            all_skills.extend(toolkit)
                        else:
                            all_skills.append(toolkit)

                        self.logger.debug(
                            "custom_tool_loaded",
                            tool_id=tool_id,
                            execution_id=context.execution_id
                        )
                    except Exception as e:
                        self.logger.error(
                            "custom_tool_load_failed",
                            tool_id=tool_id,
                            error=str(e),
                            execution_id=context.execution_id
                        )

            # Create Agno agent with all tools
            agent = build_agno_agent_config(
                agent_id=context.agent_id,
                system_prompt=context.system_prompt,
                model_id=context.model_id,
                skills=all_skills,
                tool_hooks=None,
            )

            # Register for cancellation
            self.cancellation_manager.register(
                execution_id=context.execution_id,
                instance=agent,
                instance_type="agent",
            )

            # Build conversation context
            messages = build_conversation_messages(context.conversation_history)

            # Execute without streaming
            def run_agent():
                if messages:
                    return agent.run(context.prompt, stream=False, messages=messages)
                else:
                    return agent.run(context.prompt, stream=False)

            # Run in thread pool to avoid blocking
            result = await asyncio.to_thread(run_agent)

            # Cleanup
            self.cancellation_manager.unregister(context.execution_id)

            # Extract response and metadata
            response_content = extract_response_content(result)
            usage = extract_usage(result)
            tool_messages = extract_tool_messages(result)

            return RuntimeExecutionResult(
                response=response_content,
                usage=usage,
                success=True,
                finish_reason="stop",
                run_id=getattr(result, "run_id", None),
                model=context.model_id,
                tool_messages=tool_messages,
            )

        except asyncio.CancelledError:
            # Handle cancellation
            self.cancellation_manager.cancel(context.execution_id)
            self.cancellation_manager.unregister(context.execution_id)
            raise

        except Exception as e:
            self.logger.error(
                "agno_execution_failed",
                execution_id=context.execution_id,
                error=str(e),
            )
            self.cancellation_manager.unregister(context.execution_id)

            return RuntimeExecutionResult(
                response="",
                usage={},
                success=False,
                error=str(e),
            )

    async def _stream_execute_impl(
        self,
        context: RuntimeExecutionContext,
        event_callback: Optional[Callable[[Dict], None]] = None,
    ) -> AsyncIterator[RuntimeExecutionResult]:
        """
        Execute agent with streaming using Agno framework with efficient event batching.

        This implementation uses the EventPublisher service to batch message chunks,
        reducing HTTP requests by 90-96% while keeping tool events immediate.

        Args:
            context: Execution context
            event_callback: Optional callback for real-time events

        Yields:
            RuntimeExecutionResult chunks as they arrive in real-time
        """
        # Create event publisher with batching
        event_publisher = EventPublisher(
            control_plane=self.control_plane,
            execution_id=context.execution_id,
            config=EventPublisherConfig.from_env(),
        )

        try:
            # Build conversation context
            messages = build_conversation_messages(context.conversation_history)

            # Stream execution - publish events INSIDE the thread (like old code)
            accumulated_response = ""
            run_result = None

            # Create queue for streaming chunks from thread to async
            chunk_queue = queue.Queue()

            # Generate unique message ID
            message_id = f"{context.execution_id}_msg_{int(time.time() * 1000000)}"

            # Merge regular skills with custom tools
            all_skills = list(context.skills) if context.skills else []

            # Add custom tools
            if self._custom_tools:
                for tool_id, custom_tool in self._custom_tools.items():
                    try:
                        # Get toolkit from custom tool
                        toolkit = custom_tool.get_tools()

                        # Extract tools - handle both Toolkit objects and iterables
                        if hasattr(toolkit, 'tools'):
                            all_skills.extend(toolkit.tools)
                        elif hasattr(toolkit, '__iter__'):
                            all_skills.extend(toolkit)
                        else:
                            all_skills.append(toolkit)

                        self.logger.debug(
                            "custom_tool_loaded_streaming",
                            tool_id=tool_id,
                            execution_id=context.execution_id
                        )
                    except Exception as e:
                        self.logger.error(
                            "custom_tool_load_failed_streaming",
                            tool_id=tool_id,
                            error=str(e),
                            execution_id=context.execution_id
                        )

            # Create tool hook that publishes directly to Control Plane
            tool_hook = create_tool_hook_for_streaming(
                control_plane=self.control_plane,
                execution_id=context.execution_id,
            )

            # Create Agno agent with all tools and tool hooks
            agent = build_agno_agent_config(
                agent_id=context.agent_id,
                system_prompt=context.system_prompt,
                model_id=context.model_id,
                skills=all_skills,
                tool_hooks=[tool_hook],
            )

            # Register for cancellation
            self.cancellation_manager.register(
                execution_id=context.execution_id,
                instance=agent,
                instance_type="agent",
            )

            # Cache execution metadata
            self.control_plane.cache_metadata(context.execution_id, "AGENT")

            def stream_agent_run():
                """
                Run agent with streaming and publish events directly to Control Plane.
                This runs in a thread pool, so blocking HTTP calls are OK here.
                Put chunks in queue for async iterator to yield in real-time.
                """
                nonlocal accumulated_response, run_result
                run_id_published = False

                try:
                    if messages:
                        stream_response = agent.run(
                            context.prompt,
                            stream=True,
                            messages=messages,
                        )
                    else:
                        stream_response = agent.run(context.prompt, stream=True)

                    # Iterate over streaming chunks and publish IMMEDIATELY
                    for chunk in stream_response:
                        # Capture run_id for cancellation (first chunk)
                        if not run_id_published and hasattr(chunk, "run_id") and chunk.run_id:
                            self.cancellation_manager.set_run_id(
                                context.execution_id, chunk.run_id
                            )

                            # Publish run_id event
                            self.control_plane.publish_event(
                                execution_id=context.execution_id,
                                event_type="run_started",
                                data={
                                    "run_id": chunk.run_id,
                                    "execution_id": context.execution_id,
                                    "cancellable": True,
                                }
                            )
                            run_id_published = True

                        # Extract content
                        chunk_content = ""
                        if hasattr(chunk, "content") and chunk.content:
                            if isinstance(chunk.content, str):
                                chunk_content = chunk.content
                            elif hasattr(chunk.content, "text"):
                                chunk_content = chunk.content.text

                        if chunk_content:
                            accumulated_response += chunk_content

                            # Queue chunk for batched publishing (via EventPublisher in async context)
                            # This reduces 300 HTTP requests → 12 requests (96% reduction)
                            chunk_queue.put(("chunk", chunk_content, message_id))

                    # Store final result
                    run_result = stream_response

                    # Signal completion
                    chunk_queue.put(("done", run_result))

                except Exception as e:
                    self.logger.error("streaming_error", error=str(e))
                    chunk_queue.put(("error", e))
                    raise

            # Start streaming in background thread
            stream_thread = threading.Thread(target=stream_agent_run, daemon=True)
            stream_thread.start()

            # Yield chunks as they arrive in the queue and publish via EventPublisher
            while True:
                try:
                    # Non-blocking get with short timeout for responsiveness
                    queue_item = await asyncio.to_thread(chunk_queue.get, timeout=0.1)

                    if queue_item[0] == "chunk":
                        # Unpack chunk data
                        _, chunk_content, msg_id = queue_item

                        # Publish chunk via EventPublisher (batched, non-blocking)
                        await event_publisher.publish(
                            event_type="message_chunk",
                            data={
                                "role": "assistant",
                                "content": chunk_content,
                                "is_chunk": True,
                                "message_id": msg_id,
                            },
                            priority=EventPriority.NORMAL,  # Batched
                        )

                        # Yield chunk immediately to iterator
                        yield RuntimeExecutionResult(
                            response=chunk_content,
                            usage={},
                            success=True,
                        )
                    elif queue_item[0] == "done":
                        # Final result - extract metadata and break
                        run_result = queue_item[1]
                        break
                    elif queue_item[0] == "error":
                        # Error occurred in thread
                        raise queue_item[1]

                except queue.Empty:
                    # Queue empty, check if thread is still alive
                    if not stream_thread.is_alive():
                        # Thread died without putting "done" - something went wrong
                        break
                    # Thread still running, continue waiting
                    continue

            # Wait for thread to complete
            await asyncio.to_thread(stream_thread.join, timeout=5.0)

            # Yield final result with complete metadata
            usage = extract_usage(run_result) if run_result else {}
            tool_messages = extract_tool_messages(run_result) if run_result else []

            yield RuntimeExecutionResult(
                response=accumulated_response,  # Full accumulated response
                usage=usage,
                success=True,
                finish_reason="stop",
                run_id=getattr(run_result, "run_id", None) if run_result else None,
                model=context.model_id,
                tool_messages=tool_messages,
                metadata={"accumulated_response": accumulated_response},
            )

        finally:
            # Flush and close event publisher to ensure all batched events are sent
            await event_publisher.flush()
            await event_publisher.close()

            # Cleanup
            self.cancellation_manager.unregister(context.execution_id)

    # ==================== Custom Tool Extension API ====================

    def get_custom_tool_requirements(self) -> Dict[str, Any]:
        """
        Get requirements for creating custom tools for Agno runtime.

        Returns:
            Dictionary with format, examples, and documentation for Agno custom tools
        """
        return {
            "format": "python_class",
            "description": "Python class with get_tools() method returning Agno Toolkit",
            "example_code": '''
from agno.tools import Toolkit

class MyCustomTool:
    """Custom tool for Agno runtime."""

    def get_tools(self) -> Toolkit:
        """Return Agno toolkit with custom functions."""
        return Toolkit(
            name="my_tool",
            tools=[self.my_function]
        )

    def my_function(self, arg: str) -> str:
        """Tool function description."""
        return f"Result: {arg}"
            ''',
            "documentation_url": "https://docs.agno.ai/custom-tools",
            "required_methods": ["get_tools"],
            "schema": {
                "type": "object",
                "required": ["get_tools"],
                "properties": {
                    "get_tools": {
                        "type": "method",
                        "returns": "Toolkit"
                    }
                }
            }
        }

    def validate_custom_tool(self, tool: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a custom tool for Agno runtime.

        Args:
            tool: Tool instance to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for get_tools method
        if not hasattr(tool, 'get_tools'):
            return False, "Tool must have get_tools() method"

        if not callable(getattr(tool, 'get_tools')):
            return False, "get_tools must be callable"

        # Try calling to validate return type
        try:
            toolkit = tool.get_tools()

            # Check if it's a Toolkit-like object (has tools attribute or is iterable)
            if not (hasattr(toolkit, 'tools') or hasattr(toolkit, '__iter__')):
                return False, f"get_tools() must return Toolkit or iterable, got {type(toolkit)}"

        except Exception as e:
            return False, f"get_tools() failed: {str(e)}"

        return True, None

    def register_custom_tool(self, tool: Any, metadata: Optional[Dict] = None) -> str:
        """
        Register a custom tool with Agno runtime.

        Args:
            tool: Tool instance with get_tools() method
            metadata: Optional metadata (name, description, etc.)

        Returns:
            Tool identifier for this registered tool

        Raises:
            ValueError: If tool validation fails
        """
        # Validate first
        is_valid, error = self.validate_custom_tool(tool)
        if not is_valid:
            raise ValueError(f"Invalid custom tool: {error}")

        # Generate tool ID
        tool_name = metadata.get("name") if metadata else tool.__class__.__name__
        tool_id = f"custom_{tool_name}_{id(tool)}"

        # Store tool instance
        self._custom_tools[tool_id] = tool

        self.logger.info(
            "custom_tool_registered",
            tool_id=tool_id,
            tool_class=tool.__class__.__name__,
            tool_name=tool_name
        )

        return tool_id

    def get_registered_custom_tools(self) -> list[str]:
        """
        Get list of registered custom tool identifiers.

        Returns:
            List of tool IDs
        """
        return list(self._custom_tools.keys())
