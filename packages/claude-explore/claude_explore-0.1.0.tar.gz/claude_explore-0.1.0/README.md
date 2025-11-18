# claude-explore

Ephemeral workspace manager for exploring GitHub repositories with Claude Code.

## Overview

`claude-explore` makes it easy to explore GitHub repositories with Claude Code without cluttering your workspace. It automatically:

- Clones repositories to a temporary workspace (`~/.claude-explore/`)
- Launches Claude Code in the right directory (including subdirectories)
- Tracks your exploration sessions
- Cleans up old workspaces automatically

## Features

- **Context-agnostic**: Run from any terminal, no need to cd first
- **Subdirectory support**: Explore specific parts of a repository
- **Session tracking**: Resume previous explorations
- **Auto-cleanup**: Remove old workspaces based on age
- **Disk usage monitoring**: Track workspace sizes
- **No manual setup**: Works out of the box

## Installation

```bash
# Install using uv (recommended)
uv tool install claude-explore

# Or using pip
pip install claude-explore
```

## Quick Start

```bash
# Explore a repository (options can come before URL)
claude-explore https://github.com/user/repo
claude-explore --skip-permissions https://github.com/user/repo

# Explore a subdirectory
claude-explore https://github.com/user/repo/tree/main/src/core

# List active workspaces
claude-explore list

# Clean up old workspaces (older than 7 days)
claude-explore clean

# Get workspace info
claude-explore info
```

## Usage

### Explore a Repository

The default action is to explore - just pass a URL directly:

```bash
# Basic usage (no 'explore' subcommand needed!)
claude-explore https://github.com/anthropics/anthropic-sdk-python

# Explore a specific subdirectory
claude-explore https://github.com/anthropics/anthropic-sdk-python/tree/main/src/anthropic

# Skip git pull if workspace exists
claude-explore --no-update https://github.com/user/repo

# Launch Claude with --dangerously-skip-permissions
claude-explore --skip-permissions https://github.com/user/repo

# Pass additional Claude arguments
claude-explore --claude-args "--debug --verbose" https://github.com/user/repo

# Combine multiple options (flags before URL)
claude-explore --skip-permissions --no-update https://github.com/user/repo

# You can also use the explicit 'explore' subcommand if you prefer
claude-explore explore --skip-permissions https://github.com/user/repo
```

Supported URL formats:
- `https://github.com/user/repo`
- `https://github.com/user/repo.git`
- `git@github.com:user/repo.git`
- `https://github.com/user/repo/tree/branch/path/to/subdir`

### List Sessions

```bash
# List all exploration sessions
claude-explore list

# Show only recent sessions (last 7 days)
claude-explore list --days 7
```

Output example:
```
Found 3 session(s):

  a1b2c3d4
    Repository: user/awesome-repo
    URL: https://github.com/user/awesome-repo
    Subdirectory: src/core
    Last used: 2025-11-14T10:30:00
    Created: 2025-11-13T15:20:00

  e5f6g7h8
    Repository: org/another-repo
    URL: https://github.com/org/another-repo
    Last used: 2025-11-12T14:15:00
    Created: 2025-11-12T14:15:00
```

### Resume a Session

```bash
# Resume a previous exploration (use ID from 'list' command)
claude-explore resume a1b2c3d4

# Resume with permissions skipped
claude-explore resume --skip-permissions a1b2c3d4

# Resume with additional Claude args
claude-explore resume --claude-args "--debug" a1b2c3d4
```

### Clean Up Workspaces

```bash
# Remove workspaces not used in 7 days (default)
claude-explore clean

# Remove workspaces not used in 30 days
claude-explore clean --days 30

# Remove ALL workspaces (with confirmation)
claude-explore clean --all
```

### Workspace Information

```bash
# Show workspace manager info and disk usage
claude-explore info
```

Output example:
```
Claude Explore Workspace Manager
========================================
Base directory: /home/user/.claude-explore
Workspaces directory: /home/user/.claude-explore/workspaces
Sessions file: /home/user/.claude-explore/sessions.json

Active workspaces: 3
Total disk usage: 450.5 MB
```

## How It Works

### Directory Structure

```
~/.claude-explore/
├── workspaces/
│   ├── a1b2c3d4/          # Hashed workspace ID (user/repo)
│   │   ├── .git/
│   │   ├── src/
│   │   └── ...
│   └── e5f6g7h8/
│       └── ...
└── sessions.json          # Session metadata and timestamps
```

### Workspace IDs

Each repository gets a unique workspace ID based on `user/repo`:
- Same repository always gets the same workspace ID
- Different subdirectories of the same repo share the same workspace
- This avoids duplicate clones and saves disk space

### Session Tracking

The `sessions.json` file tracks:
- Workspace ID
- Repository name and URL
- Subdirectory (if exploring a subdir)
- Created and last used timestamps

This enables:
- Resuming previous explorations
- Automatic cleanup of old workspaces
- Usage tracking and statistics

## Command Reference

### `claude-explore <repo_url>`

Explore a GitHub repository.

**Arguments:**
- `repo_url`: GitHub repository URL (HTTPS or SSH)

**Options:**
- `--no-update`: Skip git pull if workspace exists
- `--workspace-dir PATH`: Use custom workspace base directory
- `--skip-permissions`: Launch Claude with `--dangerously-skip-permissions`
- `--claude-args TEXT`: Additional arguments to pass to Claude (e.g., `"--debug --verbose"`)

### `claude-explore list`

List active exploration sessions.

**Options:**
- `--days N`: Show only sessions from last N days
- `--workspace-dir PATH`: Use custom workspace base directory

### `claude-explore resume <workspace_id>`

Resume a previous exploration session.

**Arguments:**
- `workspace_id`: Workspace identifier (from `list` command)

**Options:**
- `--workspace-dir PATH`: Use custom workspace base directory
- `--skip-permissions`: Launch Claude with `--dangerously-skip-permissions`
- `--claude-args TEXT`: Additional arguments to pass to Claude (e.g., `"--debug --verbose"`)

### `claude-explore clean`

Clean up old workspaces.

**Options:**
- `--days N`: Remove workspaces not used in N days (default: 7)
- `--all`: Remove all workspaces (prompts for confirmation)
- `--workspace-dir PATH`: Use custom workspace base directory

### `claude-explore info`

Show workspace manager information and disk usage.

**Options:**
- `--workspace-dir PATH`: Use custom workspace base directory

## Advanced Usage

### Shell Aliases

Create convenient aliases for your common workflows:

```bash
# Add to ~/.bashrc or ~/.zshrc

# Always skip permissions when exploring
alias clauded-explore='claude-explore --skip-permissions'

# Explore with debug mode enabled
alias claude-debug='claude-explore --claude-args "--debug"'

# Explore without updating (faster for repeat visits)
alias claude-cached='claude-explore --no-update'
```

Usage:
```bash
# Use your alias
clauded-explore https://github.com/user/repo

# Expands to: claude-explore --skip-permissions https://github.com/user/repo
```

### Custom Workspace Directory

Use a different base directory for workspaces:

```bash
# Use custom directory
claude-explore --workspace-dir /mnt/data/claude-workspaces https://github.com/user/repo

# All commands support this option
claude-explore list --workspace-dir /mnt/data/claude-workspaces
claude-explore clean --workspace-dir /mnt/data/claude-workspaces
```

### Workflow Examples

**Quick repository exploration:**
```bash
# One-liner to explore a repo you found
claude-explore https://github.com/user/interesting-repo
# Claude opens, ask your questions
# Exit when done

# With your alias (always skip permissions)
clauded-explore https://github.com/user/interesting-repo
```

**Regular cleanup routine:**
```bash
# Weekly cleanup (cron job or manual)
claude-explore clean --days 14
```

**Check disk usage:**
```bash
# See how much space workspaces are using
claude-explore info
```

## Comparison with Manual Workflow

**Without claude-explore:**
```bash
cd ~/temp
git clone https://github.com/user/repo
cd repo/src/core
claude
# Later: manually clean up ~/temp
```

**With claude-explore:**
```bash
claude-explore https://github.com/user/repo/tree/main/src/core
# Automatic cleanup after 7 days
```

## Requirements

- Python 3.10+
- Git
- Claude Code (`claude` command must be available)

## Development

```bash
# Clone the repository
git clone https://github.com/user/claude-explore
cd claude-explore

# Install in development mode
uv tool install -e .

# Run tests
pytest tests/
```

## License

MIT

## Related Tools

- [llmd](https://github.com/user/llmd) - Generate LLM context from repositories
- [cc-conversation-search](https://github.com/akatz-ai/cc-conversation-search) - Search Claude Code conversations

## Tips

- Workspaces are shallow clones (`--depth=1`) to save disk space
- The same repository always uses the same workspace (no duplicates)
- Subdirectory explorations share the parent repo's workspace
- Use `--no-update` if you're working with a specific commit/state
- Set up a weekly cron job to run `claude-explore clean`
