"""Prompt accessors for Agent Flows Builder."""

from .config_reference import CONFIGURATION_REFERENCE_SPECIALIST_PROMPT
from .flow_validator import FLOW_VALIDATOR_PROMPT
from .master import FLOW_BUILDER_MASTER_PROMPT

__all__ = [
    "FLOW_BUILDER_MASTER_PROMPT",
    "CONFIGURATION_REFERENCE_SPECIALIST_PROMPT",
    "FLOW_VALIDATOR_PROMPT",
]
