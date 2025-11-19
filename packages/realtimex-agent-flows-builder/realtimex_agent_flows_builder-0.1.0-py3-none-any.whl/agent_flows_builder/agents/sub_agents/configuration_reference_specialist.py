"""Configuration Reference Specialist Agent for comprehensive parameter documentation.

This module contains the configuration reference specialist that provides exhaustive
parameter documentation for workflow executors without making configuration recommendations.
"""

from typing import Any

from deepagents.state import DeepAgentState
from langgraph.prebuilt import create_react_agent

from agent_flows_builder.config.settings import ModelProviderConfig
from agent_flows_builder.prompts import CONFIGURATION_REFERENCE_SPECIALIST_PROMPT
from agent_flows_builder.settings import AgentSettings
from agent_flows_builder.tools import read_file
from agent_flows_builder.utils.models import create_chat_model


def create_configuration_reference_specialist(
    provider_config: ModelProviderConfig,
    settings: AgentSettings | None = None,
) -> dict[str, Any]:
    """Create configuration reference specialist sub-agent configuration.

    The configuration reference specialist handles:
    - Comprehensive parameter documentation for all executor types
    - Machine-readable configuration references with complete coverage
    - Zero-opinion technical documentation for informed decision making

    Args:
        provider_config: Model provider configuration shared with the master agent.
        settings: Optional runtime settings override used to configure the specialist.

    Returns:
        Dictionary with configuration reference specialist sub-agent configuration
    """
    agent_settings = settings or AgentSettings.from_env()

    # Create configured chat model
    chat_model = create_chat_model(
        model=agent_settings.research.model,
        provider_config=provider_config,
        temperature=agent_settings.research.temperature,
        max_tokens=agent_settings.research.max_tokens,
        parallel_tool_calls=False,
    )

    # Create custom LangGraph agent with read-only tools
    specialist_graph = create_react_agent(
        model=chat_model,
        tools=[read_file],  # Read-only tool(s) for documentation
        prompt=CONFIGURATION_REFERENCE_SPECIALIST_PROMPT,
        state_schema=DeepAgentState,
    )

    # Return custom subagent configuration
    return {
        "name": "configuration-reference-specialist",
        "description": "Comprehensive parameter documentation specialist providing exhaustive configuration references for workflow executors. Documents every parameter, constraint, and option without making configuration recommendations.",
        "graph": specialist_graph,
    }
