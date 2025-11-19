"""Flow Validator Agent for comprehensive flow configuration validation.

This module contains the flow validator specialist that performs structural correctness
and variable consistency validation without making configuration recommendations.
"""

from typing import Any

from deepagents.state import DeepAgentState
from langgraph.prebuilt import create_react_agent

from agent_flows_builder.config.settings import ModelProviderConfig
from agent_flows_builder.prompts import FLOW_VALIDATOR_PROMPT
from agent_flows_builder.settings import AgentSettings
from agent_flows_builder.tools.flow_validation import validate_flow_configuration
from agent_flows_builder.utils.models import create_chat_model


def create_flow_validator(
    provider_config: ModelProviderConfig,
    settings: AgentSettings | None = None,
) -> dict[str, Any]:
    """Create flow validator specialist as custom sub-agent.

    The flow validator specialist handles:
    - Comprehensive validation of flow.json structural correctness
    - Variable reference consistency checking across workflow steps
    - Schema compliance validation using Agent Flows Python package
    - Machine-readable validation reports with specific issue locations

    Args:
        provider_config: Model provider configuration shared with the master agent.
        settings: Optional runtime settings override used to configure the specialist.

    Returns:
        Dictionary with flow validator custom sub-agent configuration
    """
    agent_settings = settings or AgentSettings.from_env()

    # Create configured chat model
    chat_model = create_chat_model(
        model=agent_settings.validator.model,
        provider_config=provider_config,
        temperature=agent_settings.validator.temperature,
        max_tokens=agent_settings.validator.max_tokens,
        parallel_tool_calls=False,
    )

    # Create custom LangGraph agent with validation tool
    validator_graph = create_react_agent(
        model=chat_model,
        tools=[validate_flow_configuration],
        prompt=FLOW_VALIDATOR_PROMPT,
        state_schema=DeepAgentState,
    )

    # Return custom subagent configuration
    return {
        "name": "flow-validator",
        "description": "Flow configuration validation specialist that validates flow.json structural correctness and variable consistency. Reports validation issues without making configuration recommendations.",
        "graph": validator_graph,
    }
