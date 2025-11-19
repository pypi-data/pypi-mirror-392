# TOOT (Train of Operadic Thought) MCP

Train of Operadic Thought (ToOT) is a context capture system that leaves Carton concept breadcrumbs for cross-conversation continuity and enables reinforcement learning through success pattern capture.

## Features

- **Context Capture**: Create reasoning chains and concept groups for conversation continuity
- **Success Pattern Recording**: Capture positive feedback and successful approaches with `user_said_i_did_a_good_job()`
- **Intention Setting**: Reference past successes when starting new work with `i_need_to_do_a_good_job()`
- **Automatic Feedback Loop**: Integrate with Claude Code hooks for seamless pattern capture

## Installation

```bash
pip install toot-mcp
```

## MCP Configuration

Add to your Claude Code configuration:

```json
{
  "mcpServers": {
    "toot": {
      "command": "python",
      "args": ["-m", "toot_mcp"],
      "env": {}
    }
  }
}
```

## Claude Code Hook Integration

TOOT includes a powerful Claude Code hook integration that automatically triggers success pattern capture when you give positive feedback.

### Setting Up the "Hey Good Job!" Hook

1. **Copy the hook file** to your Claude Code hooks directory:

```bash
cp claude_code_hook.example ~/.claude/hooks/good_job_interceptor.py
chmod +x ~/.claude/hooks/good_job_interceptor.py
```

2. **Add the hook configuration** to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/.claude/hooks/good_job_interceptor.py"
          }
        ]
      }
    ]
  }
}
```

**Important**: UserPromptSubmit hooks do NOT support the "matcher" field, unlike other hook types.

### How the Hook Works

1. When you start any message with "hey good job!", the hook detects it
2. The hook injects TOOT instructions as context for the assistant
3. The assistant sees the instructions and uses `user_said_i_did_a_good_job()` 
4. Your success pattern gets captured for future reference

### Adding to Existing Hook Configuration

If you already have other hooks, just add the UserPromptSubmit section:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/user/.claude/hooks/good_job_interceptor.py"
          }
        ]
      }
    ]
  }
}
```

## Core Functions

### `user_said_i_did_a_good_job(name, domain, process, description, filepaths_involved, sequencing)`

Records successful patterns for reinforcement learning.

**Parameters:**
- `name`: Brief description of what was done well
- `domain`: Area of work (e.g., "mcp_development", "system_architecture")
- `process`: Specific type of work (e.g., "writing_readme", "debugging_hooks", "creating_library")
- `description`: What specifically worked well and why
- `filepaths_involved`: List of files that were part of the success
- `sequencing`: Steps/actions that led to success

**Example:**
```python
user_said_i_did_a_good_job(
    name="claude_code_hook_integration",
    domain="system_integration",
    process="debugging_hooks", 
    description="Successfully created Claude Code hook that automatically triggers TOOT success capture",
    filepaths_involved=["/home/user/.claude/hooks/good_job_interceptor.py", "/home/user/.claude/settings.json"],
    sequencing=["Research hook documentation", "Create hook script", "Configure settings.json", "Test integration"]
)
```

### `i_need_to_do_a_good_job(description, domain=None)`

Sets intention for excellent work and references relevant past success patterns.

**Parameters:**
- `description`: What needs to be done well
- `domain`: Optional domain to find relevant success patterns

**Example:**
```python
i_need_to_do_a_good_job(
    description="Integrate new MCP server with existing Claude Code workflow",
    domain="system_integration"
)
```

### `create_train_of_thought(name, initial_data)`

Creates a new reasoning chain for complex problem solving.

### `update_train_of_thought(name, updated_data)`

Appends to existing reasoning chain (append-only for integrity).

## Workflow Integration

TOOT creates a powerful compound intelligence feedback loop:

1. **Work Phase**: Use `i_need_to_do_a_good_job()` to set intention and reference past successes
2. **Success Phase**: When work goes well, user says "hey good job!"
3. **Capture Phase**: Hook triggers, assistant uses `user_said_i_did_a_good_job()` 
4. **Compound Phase**: Success patterns accumulate for future reference

## File Storage

TOOT files are stored in `/tmp/heaven_data/toot/` as JSON files with timestamps and reasoning chains.

## Integration with Compound Intelligence Ecosystem

TOOT works seamlessly with:
- **Carton**: Concept relationships and knowledge graphs
- **STARLOG**: Project session tracking and development logs  
- **GIINT**: Multi-fire intelligence and response iteration
- **SEED**: Identity management and publishing workflows

ToOT enables **validated conceptual reasoning** within the compound intelligence ecosystem, turning architectural conversations into systematic knowledge building! 🧠✨