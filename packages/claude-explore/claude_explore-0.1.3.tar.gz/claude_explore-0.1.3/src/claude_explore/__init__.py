"""Ephemeral workspace manager for exploring GitHub repositories with Claude Code."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('claude-explore')
except PackageNotFoundError:
    __version__ = 'dev'
