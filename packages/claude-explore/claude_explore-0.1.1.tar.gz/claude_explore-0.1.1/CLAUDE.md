# Claude Code Instructions

## Python Environment Management

- ALWAYS use uv for python environment management! NEVER try to run the system python!
- uv commands should be run in the root repo directory to use the repo's .venv

### Development

- `uv sync` - Initialize .venv with dependencies via pyproject.toml
- `uv add <package>` - Install dependencies
- `uv run <command>` - Run cli tools locally installed (e.g. uv run python)

### Testing

- `uv run pytest tests/ -v` - Run all tests
- `uv run pytest <filename>` - Run specific test file

### Installation

- `uv tool install -e .` - Install tool in development mode
- `uv tool uninstall claude-explore` - Uninstall tool
