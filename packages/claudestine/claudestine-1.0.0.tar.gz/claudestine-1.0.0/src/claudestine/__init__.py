"""
Claude Code Agent Prompt System
Recreated from claude binary analysis for production use
"""

from .prompts import (
    # Main classes
    PromptBuilder,
    AgentDefinition,
    PromptMode,

    # Built-in agents
    GENERAL_PURPOSE_AGENT,
    EXPLORE_AGENT,
    BUILT_IN_AGENTS,

    # Constants
    BASE_PROMPTS,
    SECURITY_GUIDELINES,
    DEFAULT_AGENT_INSTRUCTION,

    # Utility functions
    get_agent,
    build_agent_prompt,
)

__version__ = "1.0.0"
__all__ = [
    "PromptBuilder",
    "AgentDefinition",
    "PromptMode",
    "GENERAL_PURPOSE_AGENT",
    "EXPLORE_AGENT",
    "BUILT_IN_AGENTS",
    "BASE_PROMPTS",
    "SECURITY_GUIDELINES",
    "DEFAULT_AGENT_INSTRUCTION",
    "get_agent",
    "build_agent_prompt",
]
