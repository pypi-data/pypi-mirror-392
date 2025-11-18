"""
Configuration builder for Claude Code runtime.

This module handles the construction of ClaudeAgentOptions from execution
context, including LiteLLM integration, MCP servers, and session management.

BUG FIX #4: Added session_id validation before use.
"""

from typing import Dict, Any, Tuple, Optional, Callable
import structlog
import os

from .tool_mapper import map_skills_to_tools, validate_tool_names
from .mcp_builder import build_mcp_servers
from .hooks import build_hooks

logger = structlog.get_logger(__name__)


def validate_session_id(session_id: Optional[str]) -> Optional[str]:
    """
    Validate session_id format before use.

    BUG FIX #4: Ensures session_id is valid before storing for multi-turn.

    Args:
        session_id: Session ID to validate

    Returns:
        Valid session_id or None if invalid
    """
    if not session_id:
        return None

    if not isinstance(session_id, str) or len(session_id) < 10:
        logger.warning(
            "invalid_session_id_format",
            session_id=session_id if isinstance(session_id, str) else None,
            type=type(session_id).__name__,
            length=len(session_id) if isinstance(session_id, str) else 0,
        )
        return None

    return session_id


def build_claude_options(
    context: Any,  # RuntimeExecutionContext
    event_callback: Optional[Callable] = None,
) -> Tuple[Any, Dict[str, str]]:
    """
    Build ClaudeAgentOptions from execution context.

    Args:
        context: RuntimeExecutionContext with prompt, history, config
        event_callback: Optional event callback for hooks

    Returns:
        Tuple of (ClaudeAgentOptions instance, active_tools dict)
    """
    from claude_agent_sdk import ClaudeAgentOptions

    # Extract configuration
    agent_config = context.agent_config or {}
    runtime_config = context.runtime_config or {}

    # Get LiteLLM configuration (same as DefaultRuntime/Agno)
    litellm_api_base = os.getenv("LITELLM_API_BASE", "https://llm-proxy.kubiya.ai")
    litellm_api_key = os.getenv("LITELLM_API_KEY")

    if not litellm_api_key:
        raise ValueError("LITELLM_API_KEY environment variable not set")

    # Determine model (use LiteLLM format)
    model = context.model_id or os.environ.get(
        "LITELLM_DEFAULT_MODEL", "kubiya/claude-sonnet-4"
    )

    # Map skills to Claude Code tool names
    allowed_tools = map_skills_to_tools(context.skills)

    # Build MCP servers (both from context and custom skills)
    mcp_servers, mcp_tool_names = build_mcp_servers(
        context.skills, context.mcp_servers
    )

    # Add MCP tool names to allowed_tools so they have permission to execute
    allowed_tools.extend(mcp_tool_names)

    # Allow explicit MCP tool names from runtime_config
    # Usage: runtime_config = {"explicit_mcp_tools": ["mcp__check_prod_health", ...]}
    explicit_mcp_tools = runtime_config.get("explicit_mcp_tools", [])
    if explicit_mcp_tools:
        allowed_tools.extend(explicit_mcp_tools)
        logger.info(
            "added_explicit_mcp_tools_from_runtime_config",
            explicit_tools_count=len(explicit_mcp_tools),
            tools=explicit_mcp_tools,
        )

    # BUG FIX #6: Validate all tool names before using
    allowed_tools, invalid_tools = validate_tool_names(allowed_tools)

    logger.info(
        "final_allowed_tools_list_configured",
        total_count=len(allowed_tools),
        builtin_tools_count=(
            len(allowed_tools) - len(mcp_tool_names) - len(explicit_mcp_tools)
        ),
        mcp_tools_count=len(mcp_tool_names),
        explicit_mcp_tools_count=len(explicit_mcp_tools),
        all_tools=allowed_tools[:50],  # Limit to 50 for readability
        truncated=len(allowed_tools) > 50,
    )

    # If there are MCP servers and we have low confidence in tool extraction
    if context.mcp_servers and len(mcp_tool_names) < len(context.mcp_servers) * 2:
        logger.warning(
            "low_mcp_tool_confidence",
            mcp_servers_count=len(context.mcp_servers),
            mcp_tools_added=len(mcp_tool_names),
            recommendation="If you get permission errors, add to runtime_config.explicit_mcp_tools",
            example_config={
                "explicit_mcp_tools": [
                    "mcp__your_server_name__your_tool_name",
                    "# Example: mcp__check_prod_health__status",
                ]
            },
        )

    # Create shared active_tools dict for tool name tracking
    # This is populated in the stream when ToolUseBlock is received,
    # and used in hooks to look up tool names
    active_tools: Dict[str, str] = {}

    # Build hooks for tool execution monitoring
    hooks = (
        build_hooks(context.execution_id, event_callback, active_tools)
        if event_callback
        else {}
    )

    # Build environment with LiteLLM configuration
    env = runtime_config.get("env", {}).copy()

    # Configure Claude Code SDK to use LiteLLM proxy
    env["ANTHROPIC_BASE_URL"] = litellm_api_base
    env["ANTHROPIC_API_KEY"] = litellm_api_key

    # Pass Kubiya API credentials for workflow execution
    kubiya_api_key = os.environ.get("KUBIYA_API_KEY")
    if kubiya_api_key:
        env["KUBIYA_API_KEY"] = kubiya_api_key
        logger.debug("added_kubiya_api_key_to_environment")

    kubiya_api_base = os.environ.get("KUBIYA_API_BASE")
    if kubiya_api_base:
        env["KUBIYA_API_BASE"] = kubiya_api_base
        logger.debug(
            "added_kubiya_api_base_to_environment", kubiya_api_base=kubiya_api_base
        )

    # Get session_id from previous turn for conversation continuity
    # BUG FIX #4: Validate session_id format before use
    previous_session_id = None
    if context.user_metadata:
        raw_session_id = context.user_metadata.get("claude_code_session_id")
        previous_session_id = validate_session_id(raw_session_id)

        if raw_session_id and not previous_session_id:
            logger.warning(
                "invalid_session_id_from_user_metadata",
                raw_session_id=raw_session_id,
            )

    logger.info(
        "building_claude_code_options",
        has_user_metadata=bool(context.user_metadata),
        has_session_id_in_metadata=bool(previous_session_id),
        previous_session_id_prefix=(
            previous_session_id[:16] if previous_session_id else None
        ),
        will_resume=bool(previous_session_id),
    )

    # NEW: Support native subagents for team execution
    sdk_agents = None
    agents_config = agent_config.get('runtime_config', {}).get('agents')

    if agents_config:
        from claude_agent_sdk import AgentDefinition

        sdk_agents = {}
        for agent_id, agent_data in agents_config.items():
            sdk_agents[agent_id] = AgentDefinition(
                description=agent_data.get('description', ''),
                prompt=agent_data.get('prompt', ''),
                tools=agent_data.get('tools'),
                model=agent_data.get('model', 'inherit'),
            )

        logger.info(
            "native_subagents_configured",
            execution_id=context.execution_id[:8] if context.execution_id else "unknown",
            subagent_count=len(sdk_agents),
            subagent_ids=list(sdk_agents.keys()),
            subagent_models=[agent_data.get('model', 'inherit') for agent_data in agents_config.values()],
        )

    # Build options
    options = ClaudeAgentOptions(
        system_prompt=context.system_prompt,
        allowed_tools=allowed_tools,
        mcp_servers=mcp_servers,
        agents=sdk_agents,  # NEW: Native subagent support for teams
        permission_mode=runtime_config.get("permission_mode", "acceptEdits"),
        cwd=agent_config.get("cwd") or runtime_config.get("cwd"),
        model=model,
        env=env,
        max_turns=runtime_config.get("max_turns"),
        hooks=hooks,
        setting_sources=[],  # Explicit: don't load filesystem settings
        include_partial_messages=True,  # Enable character-by-character streaming
        resume=previous_session_id,  # Resume previous conversation if available
    )

    logger.info(
        "claude_code_options_configured",
        include_partial_messages=getattr(options, "include_partial_messages", "NOT SET"),
        permission_mode=options.permission_mode,
        model=options.model,
    )

    # Return both options and the shared active_tools dict for tool name tracking
    return options, active_tools
