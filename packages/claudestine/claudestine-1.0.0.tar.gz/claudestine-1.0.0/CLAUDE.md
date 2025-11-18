# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claudestine** is a reverse-engineered Python implementation of Claude Code's agent system prompt generator. It recreates the prompt building system used internally by Claude Code, extracted from obfuscated source code analysis.

**Core purpose**: Enable recursive agent invocations by replicating the exact system prompts used by Claude Code's general-purpose agent, specifically for use with [`zen-mcp-server` CLI Link feature](https://github.com/BeehiveInnovations/zen-mcp-server/blob/main/docs/tools/clink.md).

## Development Commands

### Package Management

```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=claudestine --cov-report=html

# Run specific test class
uv run pytest tests/test_prompts.py::TestPromptBuilder

# Run specific test method
uv run pytest tests/test_prompts.py::TestPromptBuilder::test_build_system_prompt_basic

# Run with verbose output
uv run pytest -v

# Run with detailed traceback
uv run pytest --tb=short
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint and auto-fix
uv run ruff check --fix .

# Type checking
uv run mypy src/claudestine
```

### Running Examples

```bash
# Run basic usage examples
uv run python examples/basic_usage.py
```

## Architecture

### Core Components

**`prompts.py`** - Central module containing all prompt building logic:

1. **`PromptBuilder`** - Main class for constructing system prompts
   - `build_system_prompt()` - Assembles complete prompt from sections (replicates binary's `jCD` function)
   - `get_environment_context()` - Generates environment info (replicates binary's `VTD` function)
   - `get_base_prompt()` - Selects base prompt by mode (replicates binary's `y_H` function)
   - `get_notes_section()` - Returns standard operational notes

2. **`AgentDefinition`** - Immutable dataclass defining agent properties
   - Frozen dataclass (cannot be modified after creation)
   - Validates agent_type, system_prompt, and model on initialization
   - Built-in agents: `GENERAL_PURPOSE_AGENT` (replicates `v0$`), `EXPLORE_AGENT` (replicates `A3`)

3. **`PromptMode`** - Enum for base prompt selection
   - `INTERACTIVE` - Standard CLI mode
   - `INTERACTIVE_SDK` - SDK with append support
   - `NON_INTERACTIVE_AGENT` - Non-interactive agent mode
   - `VERTEX` - Vertex AI mode

### Prompt Construction Flow

```
build_system_prompt()
├── Agent system prompt OR base prompt (by mode)
├── Security guidelines (if include_security=True)
├── Notes section (absolute paths, no emojis)
└── Environment context (platform, date, model info)
```

Each section is a separate string in the returned list.

### Key Binary Mappings

The implementation maps directly to Claude Code's obfuscated functions:

- `jCD` → `PromptBuilder.build_system_prompt()` - Main prompt construction
- `VTD` → `PromptBuilder.get_environment_context()` - Environment context generation
- `y_H` → `PromptBuilder.get_base_prompt()` - Base prompt selection
- `v0$` → `GENERAL_PURPOSE_AGENT` - General-purpose agent definition
- `A3` → `EXPLORE_AGENT` - Explore agent definition
- `xCD` → `DEFAULT_AGENT_INSTRUCTION` - Default agent instruction constant

### Constants

**`BASE_PROMPTS`** - Dictionary mapping PromptMode to base system prompts

**`SECURITY_GUIDELINES`** - Standard security instruction text (IMPORTANT: ...)

**`DEFAULT_AGENT_INSTRUCTION`** - Base instruction for agents

**`BUILT_IN_AGENTS`** - Registry of built-in agent definitions keyed by agent_type

## Design Patterns

### Immutability

`AgentDefinition` uses `@dataclass(frozen=True)` to ensure agents cannot be modified after creation. This prevents accidental mutations and ensures consistency.

### Validation

`AgentDefinition.__post_init__()` validates:
- `agent_type` is not empty
- `system_prompt` is not empty
- `model` is one of: "sonnet", "opus", "haiku"

Raises `ValueError` with descriptive messages for invalid inputs.

### Environment Context

`get_environment_context()` dynamically generates:
- Current working directory (from `cwd` param or `os.getcwd()`)
- Platform info (from `platform.system()`)
- OS version (from `platform.release()`)
- Today's date (YYYY-MM-DD format)
- Model display name (friendly name + exact model ID)
- Additional working directories (if provided)

### Model Display Names

`MODEL_DISPLAY_NAMES` maps technical model IDs to user-friendly names:
```python
"claude-sonnet-4-5-20250929" → "Claude Sonnet 4.5"
"claude-opus-4-20250514" → "Claude Opus 4"
```

Unknown models fall back to showing just the model ID.

## Testing Strategy

**Comprehensive test coverage** organized by component:

- `TestAgentDefinition` - Agent dataclass validation, immutability
- `TestPromptMode` - Enum completeness, base prompts
- `TestPromptBuilder` - Core prompt building logic
- `TestUtilityFunctions` - Helper functions (`get_agent`, `build_agent_prompt`)
- `TestConstants` - Module-level constants
- `TestIntegration` - End-to-end workflows
- `TestEdgeCases` - Error conditions, empty inputs

All tests use descriptive names and docstrings explaining what they verify.

## Common Development Tasks

### Adding a New Built-in Agent

1. Define agent constant in `prompts.py`:
```python
NEW_AGENT = AgentDefinition(
    agent_type="new-agent",
    when_to_use="Description of when to use this agent",
    system_prompt="The agent's system prompt...",
    model="sonnet",
    tools=("*",),  # or specific tools
    disallowed_tools=(),  # optional
    color="blue"  # optional
)
```

2. Add to `BUILT_IN_AGENTS` registry:
```python
BUILT_IN_AGENTS: dict[str, AgentDefinition] = {
    "general-purpose": GENERAL_PURPOSE_AGENT,
    "Explore": EXPLORE_AGENT,
    "new-agent": NEW_AGENT,  # Add here
}
```

3. Export in `__init__.py`:
```python
from .prompts import (
    # ...
    NEW_AGENT,  # Add here
)

__all__ = [
    # ...
    "NEW_AGENT",  # Add here
]
```

4. Add tests in `tests/test_prompts.py`:
```python
def test_new_agent(self):
    """Test new agent definition"""
    assert NEW_AGENT.agent_type == "new-agent"
    assert NEW_AGENT.model == "sonnet"
    # ... additional assertions
```

### Adding a New Model Display Name

Add entry to `MODEL_DISPLAY_NAMES` in `PromptBuilder`:
```python
MODEL_DISPLAY_NAMES = {
    # ...
    "claude-new-model-id": "Claude New Model Name",
}
```

## Important Notes

### Security Guidelines Control

The `include_security` parameter in `build_system_prompt()` controls whether security guidelines are included. This is documented in README as "the most important feature" - security guidelines can be excluded when not needed.

### Absolute Paths Requirement

All prompts include notes emphasizing absolute file paths because "Agent threads always have their cwd reset between bash calls". This is a fundamental constraint of the agent execution model.

### No Emoji Policy

All prompts include "MUST avoid using emojis" because the output is designed for programmatic consumption and terminal display.

### Python 3.12+ Required

Project uses modern Python features:
- PEP 604 union syntax (`str | None` instead of `Optional[str]`)
- Type annotations on all function signatures
- `dataclasses` with frozen=True

## Reverse Engineering Context

The project was created through:
1. Deobfuscating Claude Code binary using [webcrack](https://github.com/j4k0xb/webcrack)
2. Storing AST in Neo4j (~16GB graph database)
3. Using [`ccproxy`](https://github.com/starbased-co/ccproxy) to capture live Claude Code sessions
4. Finding prompt generation code via string search in AST
5. Reconstructing logic via Neo4j Traversal Framework
6. Translating JavaScript → Python using Claude

This context explains why function names reference binary symbols (`jCD`, `VTD`, etc.) - they map directly to the obfuscated source.
