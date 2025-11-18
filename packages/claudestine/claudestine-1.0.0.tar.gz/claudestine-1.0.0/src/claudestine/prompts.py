"""
Claude Code Agent Prompt System
Recreated from claude binary analysis (strings ~/.local/bin/claude)

This module provides the complete prompt building system used by Claude Code,
including all base prompts, agent definitions, and dynamic prompt construction.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal
from enum import Enum
import platform
import os
from datetime import date


class PromptMode(Enum):
    """Different modes for base system prompts"""
    INTERACTIVE = "interactive"
    INTERACTIVE_SDK = "interactive_sdk"
    NON_INTERACTIVE_AGENT = "non_interactive_agent"
    VERTEX = "vertex"


# Base System Prompts (extracted from binary)
BASE_PROMPTS = {
    PromptMode.INTERACTIVE: "You are Claude Code, Anthropic's official CLI for Claude.",
    PromptMode.INTERACTIVE_SDK: "You are Claude Code, Anthropic's official CLI for Claude, running within the Claude Agent SDK.",
    PromptMode.NON_INTERACTIVE_AGENT: "You are a Claude agent, built on Anthropic's Claude Agent SDK.",
    PromptMode.VERTEX: "You are Claude Code, Anthropic's official CLI for Claude.",
}

# Security Guidelines (from binary)
SECURITY_GUIDELINES = """IMPORTANT: Assist with authorized security testing, defensive security, CTF challenges, and educational contexts. Refuse requests for destructive techniques, DoS attacks, mass targeting, supply chain compromise, or detection evasion for malicious purposes. Dual-use security tools (C2 frameworks, credential testing, exploit development) require clear authorization context: pentesting engagements, CTF competitions, security research, or defensive use cases."""

# Default agent instruction (from binary constant xCD)
DEFAULT_AGENT_INSTRUCTION = """You are an agent for Claude Code, Anthropic's official CLI for Claude. Given the user's message, you should use the tools available to complete the task. Do what has been asked; nothing more, nothing less. When you complete the task simply respond with a detailed writeup."""


@dataclass(frozen=True)
class AgentDefinition:
    """
    Definition of a Claude Code agent.

    This matches the agent definition structure found in the Claude Code binary.
    """
    agent_type: str
    when_to_use: str
    system_prompt: str
    model: Literal["sonnet", "opus", "haiku"] = "sonnet"
    source: str = "built-in"
    base_dir: str = "built-in"
    tools: tuple[str, ...] = field(default_factory=lambda: ("*",))
    disallowed_tools: tuple[str, ...] = field(default_factory=tuple)
    color: Optional[str] = None
    fork_context: bool = False

    def __post_init__(self):
        """Validate agent definition"""
        if not self.agent_type:
            raise ValueError("agent_type cannot be empty")
        if not self.system_prompt:
            raise ValueError("system_prompt cannot be empty")
        if self.model not in ("sonnet", "opus", "haiku"):
            raise ValueError(f"Invalid model: {self.model}")


# Built-in Agent Definitions (from binary: v0$ and A3)
GENERAL_PURPOSE_AGENT = AgentDefinition(
    agent_type="general-purpose",
    when_to_use="General-purpose agent for researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries use this agent to perform the search for you.",
    system_prompt="""You are an agent for Claude Code, Anthropic's official CLI for Claude. Given the user's message, you should use the tools available to complete the task. Do what has been asked; nothing more, nothing less. When you complete the task simply respond with a detailed writeup.

Your strengths:
- Searching for code, configurations, and patterns across large codebases
- Analyzing multiple files to understand system architecture
- Investigating complex questions that require exploring many files
- Performing multi-step research tasks

Guidelines:
- For file searches: Use Grep or Glob when you need to search broadly. Use Read when you know the specific file path.
- For analysis: Start broad and narrow down. Use multiple search strategies if the first doesn't yield results.
- Be thorough: Check multiple locations, consider different naming conventions, look for related files.
- NEVER create files unless they're absolutely necessary for achieving your goal. ALWAYS prefer editing an existing file to creating a new one.
- NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested.
- In your final response always share relevant file names and code snippets. Any file paths you return in your response MUST be absolute. Do NOT use relative paths.
- For clear communication, avoid using emojis.""",
    tools=("*",),
    model="sonnet",
    color="orange"
)

EXPLORE_AGENT = AgentDefinition(
    agent_type="Explore",
    when_to_use='Fast agent specialized for exploring codebases. Use this when you need to quickly find files by patterns (eg. "src/components/**/*.tsx"), search code for keywords (eg. "API endpoints"), or answer questions about the codebase (eg. "how do API endpoints work?"). When calling this agent, specify the desired thoroughness level: "quick" for basic searches, "medium" for moderate exploration, or "very thorough" for comprehensive analysis across multiple locations and naming conventions.',
    system_prompt="""You are a file search specialist for Claude Code, Anthropic's official CLI for Claude. You excel at thoroughly navigating and exploring codebases.

Your strengths:
- Finding files by patterns and glob searches
- Searching code for keywords and patterns
- Answering questions about codebase structure
- Comprehensive exploration across multiple locations

Guidelines:
- For clear communication with the user the assistant MUST avoid using emojis.""",
    disallowed_tools=("Task", "AgentOutputTool", "WebSearch", "WebFetch", "Skill"),
    model="sonnet"
)

# Built-in agents registry
BUILT_IN_AGENTS: dict[str, AgentDefinition] = {
    "general-purpose": GENERAL_PURPOSE_AGENT,
    "Explore": EXPLORE_AGENT,
}


class PromptBuilder:
    """
    Builds complete system prompts for Claude Code agents.

    This class replicates the prompt building logic from Claude Code's binary,
    specifically the jCD and VTD functions.
    """

    # Model display name mapping (from binary)
    MODEL_DISPLAY_NAMES = {
        "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",
        "claude-opus-4-20250514": "Claude Opus 4",
        "claude-haiku-4-20250514": "Claude Haiku 4",
        "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
        "claude-3-5-sonnet-20240620": "Claude 3.5 Sonnet",
        "claude-3-opus-20240229": "Claude 3 Opus",
        "claude-3-haiku-20240307": "Claude 3 Haiku",
    }

    @staticmethod
    def get_base_prompt(
        mode: PromptMode = PromptMode.INTERACTIVE,
        is_non_interactive: bool = False,
        has_append_system_prompt: bool = False
    ) -> str:
        """
        Get the appropriate base system prompt.

        This replicates the y_H function from the binary.

        Args:
            mode: Prompt mode
            is_non_interactive: Whether this is a non-interactive session
            has_append_system_prompt: Whether to append system prompt

        Returns:
            Base system prompt string
        """
        if mode == PromptMode.VERTEX:
            return BASE_PROMPTS[PromptMode.VERTEX]

        if is_non_interactive:
            if has_append_system_prompt:
                return BASE_PROMPTS[PromptMode.INTERACTIVE_SDK]
            return BASE_PROMPTS[PromptMode.NON_INTERACTIVE_AGENT]

        return BASE_PROMPTS[PromptMode.INTERACTIVE]

    @staticmethod
    def get_environment_context(
        model: str,
        additional_working_dirs: Optional[list[str]] = None,
        cwd: Optional[str] = None
    ) -> str:
        """
        Generate environment context section.

        This replicates the VTD function from the binary.

        Args:
            model: Model ID (e.g., "claude-sonnet-4-5-20250929")
            additional_working_dirs: Additional working directories
            cwd: Current working directory (defaults to os.getcwd())

        Returns:
            Environment context string
        """
        # Get model display name
        model_display = PromptBuilder.MODEL_DISPLAY_NAMES.get(model)

        # Build model info
        if model_display:
            model_info = f"You are powered by the model named {model_display}. The exact model ID is {model}."
        else:
            model_info = f"You are powered by the model {model}."

        # Get platform info (replicates Hh1 function)
        try:
            system = platform.system()
            release = platform.release()
            uname_info = f"{system} {release}"
        except Exception:
            uname_info = "unknown"

        # Build working directories section
        working_dirs = ""
        if additional_working_dirs and len(additional_working_dirs) > 0:
            working_dirs = f"\nAdditional working directories: {', '.join(additional_working_dirs)}\n"

        # Get current working directory
        if cwd is None:
            cwd = os.getcwd()

        # Get today's date
        today = date.today().strftime('%Y-%m-%d')

        # Build complete environment section
        env_context = f"""
Here is useful information about the environment you are running in:
<env>
Working directory: {cwd}
Platform: {platform.system()}
OS Version: {uname_info}
Today's date: {today}
{working_dirs}
</env>

{model_info}
"""
        return env_context.strip()

    @staticmethod
    def get_notes_section() -> str:
        """
        Get the standard notes section appended to all agents.

        This is part of the jCD function from the binary.

        Returns:
            Notes section string
        """
        return """Notes:
- Agent threads always have their cwd reset between bash calls, as a result please only use absolute file paths.
- In your final response always share relevant file names and code snippets. Any file paths you return in your response MUST be absolute. Do NOT use relative paths.
- For clear communication with the user the assistant MUST avoid using emojis."""

    @classmethod
    def build_system_prompt(
        cls,
        agent: Optional[AgentDefinition] = None,
        base_prompts: Optional[list[str]] = None,
        model: str = "claude-sonnet-4-5-20250929",
        additional_working_dirs: Optional[list[str]] = None,
        cwd: Optional[str] = None,
        mode: PromptMode = PromptMode.INTERACTIVE,
        is_non_interactive: bool = False,
        has_append_system_prompt: bool = False,
        include_security: bool = True,
    ) -> list[str]:
        """
        Build a complete system prompt for an agent.

        This replicates the jCD function from the binary, which constructs
        the final system prompt by combining multiple sections.

        Args:
            agent: Agent definition (if using a predefined agent)
            base_prompts: Custom base prompts (overrides agent's prompt)
            model: Model ID for environment context
            additional_working_dirs: Additional working directories
            cwd: Current working directory (defaults to os.getcwd())
            mode: Prompt mode (interactive, SDK, etc.)
            is_non_interactive: Whether this is a non-interactive session
            has_append_system_prompt: Whether to append system prompt
            include_security: Whether to include security guidelines

        Returns:
            List of system prompt sections
        """
        prompts = []

        # Add base prompt (agent's system prompt or custom prompts)
        if agent and not base_prompts:
            prompts.append(agent.system_prompt)
        elif base_prompts:
            prompts.extend(base_prompts)
        else:
            prompts.append(
                cls.get_base_prompt(
                    mode=mode,
                    is_non_interactive=is_non_interactive,
                    has_append_system_prompt=has_append_system_prompt
                )
            )

        # Add security guidelines if requested
        if include_security:
            prompts.append(SECURITY_GUIDELINES)

        # Add notes section (from jCD function)
        prompts.append(cls.get_notes_section())

        # Add environment context (from VTD function)
        prompts.append(
            cls.get_environment_context(
                model=model,
                additional_working_dirs=additional_working_dirs,
                cwd=cwd
            )
        )

        return prompts


def get_agent(agent_type: str) -> Optional[AgentDefinition]:
    """
    Get a built-in agent by type.

    Args:
        agent_type: Type of agent ("general-purpose", "Explore", etc.)

    Returns:
        AgentDefinition if found, None otherwise
    """
    return BUILT_IN_AGENTS.get(agent_type)


def build_agent_prompt(
    agent_type: str,
    model: str = "claude-sonnet-4-5-20250929",
    additional_working_dirs: Optional[list[str]] = None,
    **kwargs
) -> list[str]:
    """
    Convenience function to build a prompt for a built-in agent.

    Args:
        agent_type: Type of agent ("general-purpose", "Explore", etc.)
        model: Model ID
        additional_working_dirs: Additional working directories
        **kwargs: Additional arguments passed to build_system_prompt

    Returns:
        List of system prompt sections

    Raises:
        ValueError: If agent_type is not recognized
    """
    agent = get_agent(agent_type)
    if not agent:
        available = ", ".join(BUILT_IN_AGENTS.keys())
        raise ValueError(
            f"Unknown agent type: {agent_type}. "
            f"Available agents: {available}"
        )

    return PromptBuilder.build_system_prompt(
        agent=agent,
        model=model,
        additional_working_dirs=additional_working_dirs,
        **kwargs
    )
