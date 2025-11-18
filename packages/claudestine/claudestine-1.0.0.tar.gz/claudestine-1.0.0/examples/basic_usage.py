#!/usr/bin/env python3
"""
Basic usage examples for Claudestine

This demonstrates how to use the package to build prompts for Claude Code agents.
"""

import textwrap
from claudestine import (
    build_agent_prompt,
    get_agent,
    PromptBuilder,
    GENERAL_PURPOSE_AGENT,
    EXPLORE_AGENT,
)


def wrap_print(text: str, width: int = 80) -> None:
    """Print text with line wrapping at specified width."""
    wrapped = textwrap.fill(text, width=width)
    print(wrapped)


def example_1_quick_start():
    """Example 1: Quick start with built-in agents"""
    print("=" * 80)
    print("EXAMPLE 1: Quick Start")
    print("=" * 80)

    # Build a prompt for the general-purpose agent
    prompts = build_agent_prompt("general-purpose")

    print(f"\nGenerated {len(prompts)} prompt sections:")
    for i, section in enumerate(prompts, 1):
        print(f"\nSection {i}:")
        print("-" * 80)
        for line in section.split('\n'):
            if line:
                wrap_print(line)
            else:
                print()
        print("-" * 80)


def example_2_access_agents():
    """Example 2: Access agent definitions"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Access Agent Definitions")
    print("=" * 80)

    # Get agent by type
    agent = get_agent("Explore")
    if agent:
        print(f"\nAgent Type: {agent.agent_type}")
        print(f"Model: {agent.model}")
        print(f"Tools: {agent.tools}")
        print("\nWhen to use:")
        wrap_print(agent.when_to_use)


def example_3_custom_options():
    """Example 3: Custom prompt with options"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Custom Prompt with Options")
    print("=" * 80)

    # Build prompt with custom options
    prompts = build_agent_prompt(
        "general-purpose",
        model="claude-sonnet-4-5-20250929",
        additional_working_dirs=["/home/user/project1", "/home/user/project2"],
        include_security=True
    )

    # Show the environment section
    env_section = prompts[3]
    print("\nEnvironment section:")
    print("-" * 80)
    for line in env_section.split('\n'):
        if line:
            wrap_print(line)
        else:
            print()
    print("-" * 80)


def example_4_prompt_builder():
    """Example 4: Using PromptBuilder directly"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Using PromptBuilder Directly")
    print("=" * 80)

    # Build prompt with full control
    prompts = PromptBuilder.build_system_prompt(
        agent=GENERAL_PURPOSE_AGENT,
        model="claude-opus-4-20250514",
        additional_working_dirs=["/workspace"],
        cwd="/home/user/project",
        include_security=False  # Exclude security guidelines
    )

    print(f"\nGenerated {len(prompts)} sections (no security section)")
    print("\nFirst section:")
    print("-" * 80)
    for line in prompts[0].split('\n'):
        if line:
            wrap_print(line)
        else:
            print()
    print("-" * 80)


def example_5_notes_section():
    """Example 5: Understanding the Notes section"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Understanding the Notes Section")
    print("=" * 80)

    # Get just the notes section
    notes = PromptBuilder.get_notes_section()

    print("\nThe notes section that gets appended to ALL prompts:")
    print("-" * 80)
    for line in notes.split('\n'):
        if line:
            wrap_print(line)
        else:
            print()
    print("-" * 80)


def example_6_compare_agents():
    """Example 6: Compare different agents"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Compare Different Agents")
    print("=" * 80)

    agents = [GENERAL_PURPOSE_AGENT, EXPLORE_AGENT]

    for agent in agents:
        print(f"\n{agent.agent_type.upper()} AGENT:")
        print(f"  Model: {agent.model}")
        print(f"  Tools: {len(agent.tools)} tool(s)")
        print(f"  Disallowed: {len(agent.disallowed_tools)} tool(s)")
        print(f"  Color: {agent.color or 'None'}")
        print(f"  Prompt length: {len(agent.system_prompt)} chars")


def main():
    """Run all examples"""
    print("Claudestine - Basic Usage Examples\n")

    try:
        example_1_quick_start()
        example_2_access_agents()
        example_3_custom_options()
        example_4_prompt_builder()
        example_5_notes_section()
        example_6_compare_agents()

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise


if __name__ == "__main__":
    main()
