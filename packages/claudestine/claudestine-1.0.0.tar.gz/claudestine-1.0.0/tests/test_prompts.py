"""
Comprehensive tests for Claudestine module
"""

import pytest
from claudestine import (
    PromptBuilder,
    AgentDefinition,
    PromptMode,
    GENERAL_PURPOSE_AGENT,
    EXPLORE_AGENT,
    BASE_PROMPTS,
    SECURITY_GUIDELINES,
    get_agent,
    build_agent_prompt,
)


class TestAgentDefinition:
    """Test AgentDefinition dataclass"""

    def test_general_purpose_agent(self):
        """Test general-purpose agent definition"""
        assert GENERAL_PURPOSE_AGENT.agent_type == "general-purpose"
        assert GENERAL_PURPOSE_AGENT.model == "sonnet"
        assert GENERAL_PURPOSE_AGENT.color == "orange"
        assert "*" in GENERAL_PURPOSE_AGENT.tools
        assert "You are an agent for Claude Code" in GENERAL_PURPOSE_AGENT.system_prompt

    def test_explore_agent(self):
        """Test Explore agent definition"""
        assert EXPLORE_AGENT.agent_type == "Explore"
        assert EXPLORE_AGENT.model == "sonnet"
        assert "file search specialist" in EXPLORE_AGENT.system_prompt
        assert "Task" in EXPLORE_AGENT.disallowed_tools

    def test_agent_immutability(self):
        """Test that agents are immutable (frozen dataclass)"""
        with pytest.raises(Exception):  # FrozenInstanceError
            GENERAL_PURPOSE_AGENT.model = "opus"

    def test_invalid_agent_model(self):
        """Test that invalid model raises ValueError"""
        with pytest.raises(ValueError, match="Invalid model"):
            AgentDefinition(
                agent_type="test",
                when_to_use="test",
                system_prompt="test",
                model="invalid"  # type: ignore
            )

    def test_empty_agent_type(self):
        """Test that empty agent_type raises ValueError"""
        with pytest.raises(ValueError, match="agent_type cannot be empty"):
            AgentDefinition(
                agent_type="",
                when_to_use="test",
                system_prompt="test"
            )

    def test_empty_system_prompt(self):
        """Test that empty system_prompt raises ValueError"""
        with pytest.raises(ValueError, match="system_prompt cannot be empty"):
            AgentDefinition(
                agent_type="test",
                when_to_use="test",
                system_prompt=""
            )


class TestPromptMode:
    """Test PromptMode enum"""

    def test_all_modes_present(self):
        """Test that all prompt modes are defined"""
        assert PromptMode.INTERACTIVE
        assert PromptMode.INTERACTIVE_SDK
        assert PromptMode.NON_INTERACTIVE_AGENT
        assert PromptMode.VERTEX

    def test_base_prompts_for_all_modes(self):
        """Test that BASE_PROMPTS has entries for all modes"""
        for mode in PromptMode:
            assert mode in BASE_PROMPTS
            assert isinstance(BASE_PROMPTS[mode], str)
            assert len(BASE_PROMPTS[mode]) > 0


class TestPromptBuilder:
    """Test PromptBuilder class"""

    def test_get_base_prompt_interactive(self):
        """Test getting interactive base prompt"""
        prompt = PromptBuilder.get_base_prompt(mode=PromptMode.INTERACTIVE)
        assert "Claude Code, Anthropic's official CLI" in prompt
        assert "SDK" not in prompt

    def test_get_base_prompt_sdk(self):
        """Test getting SDK base prompt"""
        prompt = PromptBuilder.get_base_prompt(
            is_non_interactive=True,
            has_append_system_prompt=True
        )
        assert "Claude Agent SDK" in prompt

    def test_get_base_prompt_vertex(self):
        """Test getting Vertex AI base prompt"""
        prompt = PromptBuilder.get_base_prompt(mode=PromptMode.VERTEX)
        assert "Claude Code" in prompt

    def test_get_environment_context_basic(self):
        """Test basic environment context generation"""
        context = PromptBuilder.get_environment_context(
            model="claude-sonnet-4-5-20250929"
        )
        assert "<env>" in context
        assert "Working directory:" in context
        assert "Platform:" in context
        assert "OS Version:" in context
        assert "Today's date:" in context
        assert "Claude Sonnet 4.5" in context
        assert "claude-sonnet-4-5-20250929" in context

    def test_get_environment_context_with_dirs(self):
        """Test environment context with additional working directories"""
        context = PromptBuilder.get_environment_context(
            model="claude-sonnet-4-5-20250929",
            additional_working_dirs=["/path/1", "/path/2"]
        )
        assert "Additional working directories" in context
        assert "/path/1" in context
        assert "/path/2" in context

    def test_get_environment_context_custom_cwd(self):
        """Test environment context with custom cwd"""
        context = PromptBuilder.get_environment_context(
            model="claude-sonnet-4-5-20250929",
            cwd="/custom/path"
        )
        assert "Working directory: /custom/path" in context

    def test_get_environment_context_unknown_model(self):
        """Test environment context with unknown model"""
        context = PromptBuilder.get_environment_context(
            model="claude-unknown-model"
        )
        assert "You are powered by the model claude-unknown-model" in context

    def test_get_notes_section(self):
        """Test notes section generation"""
        notes = PromptBuilder.get_notes_section()
        assert "Agent threads always have their cwd reset" in notes
        assert "absolute file paths" in notes
        assert "MUST be absolute" in notes
        assert "avoid using emojis" in notes

    def test_build_system_prompt_basic(self):
        """Test basic system prompt building"""
        prompts = PromptBuilder.build_system_prompt(
            agent=GENERAL_PURPOSE_AGENT,
            model="claude-sonnet-4-5-20250929"
        )

        assert len(prompts) == 4
        # Section 1: Agent's system prompt
        assert "You are an agent for Claude Code" in prompts[0]
        # Section 2: Security guidelines
        assert "IMPORTANT: Assist with authorized security testing" in prompts[1]
        # Section 3: Notes
        assert "Agent threads always have their cwd reset" in prompts[2]
        # Section 4: Environment
        assert "<env>" in prompts[3]

    def test_build_system_prompt_without_security(self):
        """Test building prompt without security guidelines"""
        prompts = PromptBuilder.build_system_prompt(
            agent=GENERAL_PURPOSE_AGENT,
            model="claude-sonnet-4-5-20250929",
            include_security=False
        )

        # Should have 3 sections instead of 4
        assert len(prompts) == 3
        assert not any("security testing" in p for p in prompts)

    def test_build_system_prompt_custom_base(self):
        """Test building prompt with custom base prompts"""
        custom_prompts = ["Custom prompt 1", "Custom prompt 2"]
        prompts = PromptBuilder.build_system_prompt(
            base_prompts=custom_prompts,
            model="claude-sonnet-4-5-20250929"
        )

        assert "Custom prompt 1" in prompts[0]
        assert "Custom prompt 2" in prompts[1]

    def test_build_system_prompt_all_options(self):
        """Test building prompt with all options"""
        prompts = PromptBuilder.build_system_prompt(
            agent=GENERAL_PURPOSE_AGENT,
            model="claude-sonnet-4-5-20250929",
            additional_working_dirs=["/project1", "/project2"],
            cwd="/custom/cwd",
            mode=PromptMode.INTERACTIVE_SDK,
            is_non_interactive=True,
            has_append_system_prompt=True,
            include_security=True
        )

        # Verify all sections present
        assert len(prompts) == 4
        assert any("/project1" in p for p in prompts)
        assert any("/project2" in p for p in prompts)
        assert any("/custom/cwd" in p for p in prompts)


class TestUtilityFunctions:
    """Test utility functions"""

    def test_get_agent_valid(self):
        """Test getting a valid agent"""
        agent = get_agent("general-purpose")
        assert agent is not None
        assert agent.agent_type == "general-purpose"

    def test_get_agent_invalid(self):
        """Test getting an invalid agent returns None"""
        agent = get_agent("nonexistent")
        assert agent is None

    def test_build_agent_prompt_general_purpose(self):
        """Test building general-purpose agent prompt"""
        prompts = build_agent_prompt("general-purpose")
        assert len(prompts) == 4
        assert any("general-purpose" in p or "Searching for code" in p for p in prompts)

    def test_build_agent_prompt_explore(self):
        """Test building Explore agent prompt"""
        prompts = build_agent_prompt("Explore")
        assert len(prompts) == 4
        assert any("file search specialist" in p for p in prompts)

    def test_build_agent_prompt_invalid(self):
        """Test building prompt for invalid agent raises ValueError"""
        with pytest.raises(ValueError, match="Unknown agent type"):
            build_agent_prompt("nonexistent")

    def test_build_agent_prompt_with_options(self):
        """Test building agent prompt with additional options"""
        prompts = build_agent_prompt(
            "general-purpose",
            model="claude-opus-4-20250514",
            additional_working_dirs=["/project"],
            include_security=False
        )

        assert len(prompts) == 3  # No security section
        assert any("Claude Opus 4" in p for p in prompts)
        assert any("/project" in p for p in prompts)


class TestConstants:
    """Test module constants"""

    def test_security_guidelines_present(self):
        """Test that security guidelines are defined"""
        assert SECURITY_GUIDELINES
        assert "IMPORTANT" in SECURITY_GUIDELINES
        assert "security testing" in SECURITY_GUIDELINES

    def test_base_prompts_structure(self):
        """Test BASE_PROMPTS structure"""
        assert isinstance(BASE_PROMPTS, dict)
        assert len(BASE_PROMPTS) == 4
        for prompt in BASE_PROMPTS.values():
            assert isinstance(prompt, str)
            assert "Claude" in prompt


class TestIntegration:
    """Integration tests"""

    def test_full_workflow_general_purpose(self):
        """Test complete workflow for general-purpose agent"""
        # Get agent
        agent = get_agent("general-purpose")
        assert agent is not None

        # Build prompt using builder directly
        prompts1 = PromptBuilder.build_system_prompt(
            agent=agent,
            model="claude-sonnet-4-5-20250929"
        )

        # Build prompt using convenience function
        prompts2 = build_agent_prompt("general-purpose")

        # Should produce same result
        assert len(prompts1) == len(prompts2)
        assert prompts1[0] == prompts2[0]  # Agent prompt should match

    def test_prompt_consistency(self):
        """Test that prompts are consistent across calls"""
        prompts1 = build_agent_prompt("general-purpose")
        prompts2 = build_agent_prompt("general-purpose")

        # Should be identical (except date might change)
        assert len(prompts1) == len(prompts2)
        assert prompts1[0] == prompts2[0]
        assert prompts1[1] == prompts2[1]
        assert prompts1[2] == prompts2[2]

    def test_all_agents_buildable(self):
        """Test that all built-in agents can build prompts"""
        from claudestine import BUILT_IN_AGENTS

        for agent_type in BUILT_IN_AGENTS.keys():
            prompts = build_agent_prompt(agent_type)
            assert len(prompts) == 4
            assert all(isinstance(p, str) for p in prompts)
            assert all(len(p) > 0 for p in prompts)


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_additional_dirs(self):
        """Test with empty additional directories list"""
        prompts = PromptBuilder.build_system_prompt(
            agent=GENERAL_PURPOSE_AGENT,
            additional_working_dirs=[]
        )
        # Should not include "Additional working directories" section
        assert not any("Additional working directories:" in p for p in prompts)

    def test_none_additional_dirs(self):
        """Test with None additional directories"""
        prompts = PromptBuilder.build_system_prompt(
            agent=GENERAL_PURPOSE_AGENT,
            additional_working_dirs=None
        )
        assert len(prompts) == 4

    def test_model_display_names_coverage(self):
        """Test that major models have display names"""
        known_models = [
            "claude-sonnet-4-5-20250929",
            "claude-opus-4-20250514",
            "claude-haiku-4-20250514",
        ]
        for model in known_models:
            context = PromptBuilder.get_environment_context(model)
            # Should have a friendly name, not just the model ID
            assert "Claude" in context
            assert model in context


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
