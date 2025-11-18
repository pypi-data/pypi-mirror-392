"""
Configuration builder for Agno runtime.

This module handles:
- LiteLLM API configuration
- Model selection and setup
- Agent configuration
- Environment variable management
"""

import os
import structlog
from typing import Any, Optional, List

from agno.agent import Agent
from agno.models.litellm import LiteLLM

logger = structlog.get_logger(__name__)


def build_agno_agent_config(
    agent_id: str,
    system_prompt: Optional[str] = None,
    model_id: Optional[str] = None,
    skills: Optional[List[Any]] = None,
    tool_hooks: Optional[List[Any]] = None,
) -> Agent:
    """
    Build Agno Agent configuration with LiteLLM.

    Args:
        agent_id: Unique identifier for the agent
        system_prompt: System-level instructions
        model_id: Model identifier (overrides default)
        skills: List of skills/tools available to agent
        tool_hooks: List of tool execution hooks

    Returns:
        Configured Agno Agent instance

    Raises:
        ValueError: If required environment variables are missing
    """
    # Get LiteLLM configuration from environment
    litellm_api_base = os.getenv(
        "LITELLM_API_BASE", "https://llm-proxy.kubiya.ai"
    )
    litellm_api_key = os.getenv("LITELLM_API_KEY")

    if not litellm_api_key:
        raise ValueError("LITELLM_API_KEY environment variable not set")

    # Determine model to use
    model = model_id or os.environ.get(
        "LITELLM_DEFAULT_MODEL", "kubiya/claude-sonnet-4"
    )

    logger.info(
        "building_agno_agent_config",
        agent_id=agent_id,
        model=model,
        has_skills=bool(skills),
        has_tool_hooks=bool(tool_hooks),
    )

    # Create LiteLLM model instance
    litellm_model = LiteLLM(
        id=f"openai/{model}",
        api_base=litellm_api_base,
        api_key=litellm_api_key,
    )

    # Build agent configuration
    agent = Agent(
        name=f"Agent {agent_id}",
        role=system_prompt or "You are a helpful AI assistant",
        model=litellm_model,
        tools=skills if skills else None,
        tool_hooks=tool_hooks if tool_hooks else None,
    )

    return agent


def validate_litellm_config() -> bool:
    """
    Validate LiteLLM configuration is present.

    Returns:
        True if configuration is valid

    Raises:
        ValueError: If configuration is invalid
    """
    litellm_api_key = os.getenv("LITELLM_API_KEY")

    if not litellm_api_key:
        raise ValueError(
            "LITELLM_API_KEY environment variable not set. "
            "This is required for Agno runtime to function."
        )

    logger.debug(
        "litellm_config_validated",
        api_base=os.getenv("LITELLM_API_BASE", "https://llm-proxy.kubiya.ai"),
        default_model=os.environ.get("LITELLM_DEFAULT_MODEL", "kubiya/claude-sonnet-4"),
    )

    return True
