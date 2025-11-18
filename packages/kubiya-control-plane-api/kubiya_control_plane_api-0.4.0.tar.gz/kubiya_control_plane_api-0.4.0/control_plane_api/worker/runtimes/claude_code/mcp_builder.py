"""
MCP (Model Context Protocol) server builder for Claude Code runtime.

This module handles the creation and configuration of MCP servers from
both external sources and custom skills, with proper tool name extraction
and validation.

BUG FIX #3: Made MCP fallback patterns explicit, not broad regex.
"""

from typing import Dict, Any, List, Tuple, Optional
import structlog
import asyncio

from .tool_mapper import construct_mcp_tool_name, sanitize_tool_name

logger = structlog.get_logger(__name__)


def extract_mcp_tool_names(
    server_name: str,
    server_obj: Any,
    explicit_tools: Optional[List[str]] = None
) -> List[str]:
    """
    Extract tool names from an MCP server object.

    Issue #5 Fix: Prioritizes explicit tool names from skill.yaml configuration.
    If not provided, attempts fallback extraction with clear warnings.

    Extraction approaches (in order of preference):
    0. Use explicit_tools from skill.yaml (RECOMMENDED)
    1. Check for 'tools' attribute (list of tool objects/dicts)
    2. Check for 'list_tools()' method
    3. Check if it's a dict with 'tools' key

    Args:
        server_name: Name of the MCP server
        server_obj: MCP server object (could be various types)
        explicit_tools: Optional list of tool names from skill.yaml configuration

    Returns:
        List of tool names extracted from the server
    """
    # Issue #5 Fix: Use explicit tools if provided
    if explicit_tools:
        logger.info(
            "using_explicit_mcp_tools_from_config",
            server_name=server_name,
            tool_count=len(explicit_tools),
            tools=explicit_tools,
        )
        return explicit_tools
    tool_names = []

    try:
        # Approach 1: Check if server has a 'tools' attribute (list)
        if hasattr(server_obj, "tools"):
            tools_attr = getattr(server_obj, "tools")
            if isinstance(tools_attr, list):
                for tool in tools_attr:
                    # Tool might be an object with 'name' attribute
                    if hasattr(tool, "name"):
                        tool_names.append(tool.name)
                    # Or a dict with 'name' key
                    elif isinstance(tool, dict) and "name" in tool:
                        tool_names.append(tool["name"])
                    # Or a callable with __name__
                    elif callable(tool) and hasattr(tool, "__name__"):
                        tool_names.append(tool.__name__)

        # Approach 2: Check if server has a list_tools() method
        elif hasattr(server_obj, "list_tools") and callable(
            getattr(server_obj, "list_tools")
        ):
            try:
                tools_list = server_obj.list_tools()
                if isinstance(tools_list, list):
                    for tool in tools_list:
                        if isinstance(tool, str):
                            tool_names.append(tool)
                        elif isinstance(tool, dict) and "name" in tool:
                            tool_names.append(tool["name"])
                        elif hasattr(tool, "name"):
                            tool_names.append(tool.name)
            except Exception as e:
                logger.debug(
                    "list_tools_method_failed",
                    server_name=server_name,
                    error=str(e),
                )

        # Approach 3: Check if it's a dict with 'tools' key
        elif isinstance(server_obj, dict) and "tools" in server_obj:
            tools_list = server_obj["tools"]
            if isinstance(tools_list, list):
                for tool in tools_list:
                    if isinstance(tool, str):
                        tool_names.append(tool)
                    elif isinstance(tool, dict) and "name" in tool:
                        tool_names.append(tool["name"])

        if tool_names:
            # Issue #5 Fix: Warn about fallback extraction
            logger.warning(
                "extracted_tools_from_mcp_server_using_fallback",
                server_name=server_name,
                tool_count=len(tool_names),
                tools=tool_names,
                recommendation=(
                    f"For production use, explicitly specify MCP tools in skill.yaml:\n"
                    f"  spec:\n"
                    f"    mcp_tools:\n"
                    f"      {server_name}: {tool_names}\n"
                    f"This ensures deterministic behavior and avoids runtime failures."
                ),
            )
        else:
            # Issue #5 Fix: Error if no tools found
            logger.error(
                "no_tools_extracted_from_mcp_server",
                server_name=server_name,
                recommendation=(
                    f"Failed to extract tools from MCP server '{server_name}'. "
                    f"Add explicit tool names to skill.yaml:\n"
                    f"  spec:\n"
                    f"    mcp_tools:\n"
                    f"      {server_name}: ['tool1', 'tool2']\n"
                    f"Check the MCP server documentation for available tool names."
                ),
            )

    except Exception as e:
        logger.error(
            "error_extracting_tools_from_mcp_server",
            server_name=server_name,
            error=str(e),
            exc_info=True,
        )

    return tool_names


def build_mcp_servers(
    skills: List[Any],
    context_mcp_servers: Dict[str, Any] = None,
    mcp_tools_config: Optional[Dict[str, List[str]]] = None
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Build MCP server configurations from context and custom skills.

    This converts skills into Claude Code MCP servers for custom tools.
    Handles both legacy get_tools() and Toolkit.functions patterns.

    Issue #5 Fix: Accepts explicit MCP tool names from configuration to avoid
    fragile runtime extraction.

    Args:
        skills: List of skill objects
        context_mcp_servers: Optional MCP servers from execution context
        mcp_tools_config: Optional dict mapping server_name -> list of tool names
                         from skill.yaml spec.mcp_tools

    Returns:
        Tuple of (MCP server configurations dict, list of all MCP tool names)
    """
    if mcp_tools_config is None:
        mcp_tools_config = {}
    from claude_agent_sdk import create_sdk_mcp_server, tool as mcp_tool

    mcp_servers = {}
    all_mcp_tool_names = []  # Track all tool names across all MCP servers

    # Include MCP servers from context (if any)
    if context_mcp_servers:
        logger.info(
            "processing_mcp_servers_from_context",
            server_count=len(context_mcp_servers),
            server_names=list(context_mcp_servers.keys()),
        )

        for server_name, server_obj in context_mcp_servers.items():
            mcp_servers[server_name] = server_obj

            # Issue #5 Fix: Try explicit tools first, then fallback to extraction
            explicit_tools = mcp_tools_config.get(server_name)
            extracted_tools = extract_mcp_tool_names(server_name, server_obj, explicit_tools)

            if extracted_tools:
                # Construct full MCP tool names: mcp__<server_name>__<tool_name>
                full_tool_names = []
                for tool_name in extracted_tools:
                    # If tool already has mcp__ prefix, use as-is
                    if tool_name.startswith("mcp__"):
                        full_tool_names.append(tool_name)
                    else:
                        # Construct: mcp__<server_name>__<tool_name>
                        full_tool_name = construct_mcp_tool_name(server_name, tool_name)
                        full_tool_names.append(full_tool_name)

                all_mcp_tool_names.extend(full_tool_names)
                logger.info(
                    "extracted_and_constructed_mcp_tool_names",
                    server_name=server_name,
                    raw_tool_count=len(extracted_tools),
                    raw_tools=extracted_tools,
                    full_tool_names=full_tool_names,
                )
            else:
                # BUG FIX #3: Only add server-level fallback, require explicit config
                sanitized_server = sanitize_tool_name(server_name)
                fallback_tool = construct_mcp_tool_name(server_name)
                all_mcp_tool_names.append(fallback_tool)

                logger.warning(
                    "mcp_tool_extraction_failed_requiring_explicit_config",
                    server_name=server_name,
                    fallback_tool=fallback_tool,
                    server_type=type(server_obj).__name__,
                    has_tools_attr=hasattr(server_obj, "tools"),
                    has_list_tools=hasattr(server_obj, "list_tools"),
                    is_dict=isinstance(server_obj, dict),
                    recommendation=(
                        f"To use tools from this MCP server, add to runtime_config:\n"
                        f"  {{'explicit_mcp_tools': ['mcp__{sanitized_server}__<tool1>', 'mcp__{sanitized_server}__<tool2>']}}\n"
                        f"Check the MCP server documentation for available tool names."
                    ),
                )

    # Convert custom skills to MCP servers
    for skill in skills:
        tools_list = []
        registered_tool_names = []  # Track tool names for logging
        skill_name = getattr(skill, "name", "custom_skill")

        # Check for Toolkit pattern (has .functions attribute)
        if hasattr(skill, "functions") and hasattr(skill.functions, "items"):
            logger.info(
                "found_skill_with_registered_functions",
                skill_name=skill_name,
                function_count=len(skill.functions),
                function_names=list(skill.functions.keys()),
            )

            # Extract tools from functions registry
            for func_name, func_obj in skill.functions.items():
                # Skip helper tools for workflow_executor skills to avoid confusion
                if func_name in ["list_all_workflows", "get_workflow_info"]:
                    logger.debug(
                        "skipping_helper_tool_for_workflow_executor",
                        skill_name=skill_name,
                        tool_name=func_name,
                    )
                    continue

                # Get entrypoint (the actual callable)
                entrypoint = getattr(func_obj, "entrypoint", None)
                if not entrypoint:
                    logger.warning(
                        "function_missing_entrypoint",
                        skill_name=skill_name,
                        function_name=func_name,
                    )
                    continue

                # Get function metadata - use function name as-is
                tool_name = func_name
                tool_description = (
                    getattr(func_obj, "description", None)
                    or entrypoint.__doc__
                    or f"{tool_name} tool"
                )
                tool_parameters = getattr(func_obj, "parameters", {})

                # Create a closure that captures the entrypoint with proper variable scope
                def make_tool_wrapper(
                    tool_entrypoint,
                    tool_func_name,
                    tool_func_description,
                    tool_func_parameters,
                ):
                    """Factory to create tool wrappers with proper closure"""

                    @mcp_tool(tool_func_name, tool_func_description, tool_func_parameters)
                    async def wrapped_tool(args: dict) -> dict:
                        try:
                            logger.debug(
                                "executing_workflow_tool",
                                tool_name=tool_func_name,
                                args=args,
                            )
                            # Call the entrypoint with unpacked args
                            if asyncio.iscoroutinefunction(tool_entrypoint):
                                result = (
                                    await tool_entrypoint(**args)
                                    if args
                                    else await tool_entrypoint()
                                )
                            else:
                                # Run synchronous tools in thread pool to avoid blocking
                                result = await asyncio.to_thread(
                                    lambda: tool_entrypoint(**args)
                                    if args
                                    else tool_entrypoint()
                                )

                            logger.info(
                                "workflow_tool_completed_successfully",
                                tool_name=tool_func_name,
                                result_length=len(str(result)),
                            )

                            return {
                                "content": [{"type": "text", "text": str(result)}]
                            }
                        except Exception as e:
                            logger.error(
                                "workflow_tool_execution_failed",
                                tool_name=tool_func_name,
                                error=str(e),
                                exc_info=True,
                            )
                            return {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Error executing {tool_func_name}: {str(e)}",
                                    }
                                ],
                                "isError": True,
                            }

                    return wrapped_tool

                wrapped_tool = make_tool_wrapper(
                    entrypoint, tool_name, tool_description, tool_parameters
                )
                tools_list.append(wrapped_tool)
                registered_tool_names.append(tool_name)

                # Construct full MCP tool name for allowed_tools
                full_mcp_tool_name = construct_mcp_tool_name(skill_name, tool_name)
                all_mcp_tool_names.append(full_mcp_tool_name)

                logger.info(
                    "registered_mcp_tool_from_skill_function",
                    skill_name=skill_name,
                    tool_name=tool_name,
                    full_mcp_tool_name=full_mcp_tool_name,
                )

        # Legacy: Check if skill has get_tools() method
        elif hasattr(skill, "get_tools"):
            for tool_func in skill.get_tools():
                # Wrap each tool function with MCP tool decorator
                tool_name = getattr(tool_func, "__name__", "custom_tool")
                tool_description = getattr(tool_func, "__doc__", f"{tool_name} tool")

                # Create MCP tool wrapper
                @mcp_tool(tool_name, tool_description, {})
                async def wrapped_tool(args: dict) -> dict:
                    # Run synchronous tools in thread pool to avoid blocking
                    if asyncio.iscoroutinefunction(tool_func):
                        result = (
                            await tool_func(**args) if args else await tool_func()
                        )
                    else:
                        result = await asyncio.to_thread(
                            lambda: tool_func(**args) if args else tool_func()
                        )
                    return {"content": [{"type": "text", "text": str(result)}]}

                tools_list.append(wrapped_tool)
                registered_tool_names.append(tool_name)

                # Construct full MCP tool name for allowed_tools
                full_mcp_tool_name = construct_mcp_tool_name(skill_name, tool_name)
                all_mcp_tool_names.append(full_mcp_tool_name)

        # Create MCP server for this skill if it has tools
        if tools_list:
            server_name = skill_name

            mcp_servers[server_name] = create_sdk_mcp_server(
                name=server_name, version="1.0.0", tools=tools_list
            )

            logger.info(
                "created_mcp_server_for_skill",
                skill_name=skill_name,
                server_name=server_name,
                tool_count=len(tools_list),
            )

    logger.info(
        "built_mcp_servers",
        server_count=len(mcp_servers),
        servers=list(mcp_servers.keys()),
        mcp_tool_count=len(all_mcp_tool_names),
        mcp_tools=(
            all_mcp_tool_names[:10]
            if len(all_mcp_tool_names) > 10
            else all_mcp_tool_names
        ),
    )

    return mcp_servers, all_mcp_tool_names
