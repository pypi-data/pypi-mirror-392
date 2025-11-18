"""CLI for claude-explore."""

import os
import sys
import subprocess
from pathlib import Path
import click

from . import __version__
from .url_parser import parse_github_url
from .workspace import WorkspaceManager


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name='claude-explore')
@click.argument('repo_url', required=False)
@click.option('--skip-permissions', is_flag=True, help='Launch Claude with --dangerously-skip-permissions')
@click.option('--claude-args', help='Additional arguments to pass to Claude')
@click.option('--no-update', is_flag=True, help='Skip git pull if workspace exists')
@click.option('--workspace-dir', type=click.Path(), help='Custom workspace base directory')
@click.pass_context
def cli(ctx, repo_url, skip_permissions, claude_args, no_update, workspace_dir):
    """Ephemeral workspace manager for exploring GitHub repositories with Claude Code.

    Clone GitHub repositories to temporary workspaces and explore them with Claude.
    Workspaces are automatically cleaned up after a configurable period.

    Examples:

        # Explore a repository (default action)
        claude-explore https://github.com/user/repo

        # Explore with permissions skipped
        claude-explore --skip-permissions https://github.com/user/repo

        # Explore a subdirectory
        claude-explore https://github.com/user/repo/tree/main/src/core

        # Use subcommands explicitly
        claude-explore list
        claude-explore clean --days 7
        claude-explore resume <workspace-id>
    """
    # If a repo URL is provided without a subcommand, invoke explore
    if repo_url and ctx.invoked_subcommand is None:
        ctx.invoke(explore,
                   repo_url=repo_url,
                   skip_permissions=skip_permissions,
                   claude_args=claude_args,
                   no_update=no_update,
                   workspace_dir=workspace_dir)
    elif ctx.invoked_subcommand is None:
        # No URL and no subcommand, show help
        click.echo(ctx.get_help())


@cli.command()
@click.argument('repo_url')
@click.option('--no-update', is_flag=True, help='Skip git pull if workspace exists')
@click.option('--workspace-dir', type=click.Path(), help='Custom workspace base directory')
@click.option('--skip-permissions', is_flag=True, help='Launch Claude with --dangerously-skip-permissions')
@click.option('--claude-args', help='Additional arguments to pass to Claude (e.g., "--debug --verbose")')
def explore(repo_url: str, no_update: bool, workspace_dir: str, skip_permissions: bool, claude_args: str):
    """Explore a GitHub repository with Claude Code.

    REPO_URL can be:
    - https://github.com/user/repo
    - https://github.com/user/repo/tree/branch/path/to/subdir
    - git@github.com:user/repo.git

    The repository will be cloned to ~/.claude-explore/workspaces/ and Claude
    will be launched in that directory.
    """
    try:
        # Parse GitHub URL
        repo = parse_github_url(repo_url)
        click.echo(f"Repository: {repo.full_name}")

        # Initialize workspace manager
        base_dir = Path(workspace_dir) if workspace_dir else None
        manager = WorkspaceManager(base_dir=base_dir)

        # Get or create workspace
        click.echo("Preparing workspace...")
        workspace_path = manager.get_or_create_workspace(repo, update=not no_update)

        # Get working directory (handles subdirectories)
        work_dir = manager.get_working_directory(repo, workspace_path)

        # Display info
        click.echo(f"Workspace: {workspace_path}")
        if repo.subdir:
            if work_dir != workspace_path:
                click.echo(f"Working directory: {work_dir}")
            else:
                click.secho(
                    f"Warning: Subdirectory '{repo.subdir}' not found, using repository root",
                    fg='yellow'
                )

        # Launch Claude in the working directory
        click.echo(f"\nLaunching Claude Code in {work_dir.relative_to(workspace_path) if repo.subdir else 'repository root'}...")
        click.echo("(Exit Claude to return to this terminal)\n")

        # Check if claude command exists
        if not _claude_exists():
            click.secho(
                "Error: 'claude' command not found. Please install Claude Code first.",
                fg='red',
                err=True
            )
            sys.exit(1)

        # Build Claude command with flags
        claude_cmd = ['claude']
        if skip_permissions:
            claude_cmd.append('--dangerously-skip-permissions')
        if claude_args:
            # Parse additional args (simple split, handles quoted args via shell)
            claude_cmd.extend(claude_args.split())

        # Launch Claude
        os.chdir(work_dir)
        subprocess.run(claude_cmd)

    except ValueError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)
    except RuntimeError as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nCancelled.")
        sys.exit(0)


@cli.command()
@click.option('--days', type=int, help='Show sessions from last N days')
@click.option('--workspace-dir', type=click.Path(), help='Custom workspace base directory')
def list(days: int, workspace_dir: str):
    """List active exploration sessions."""
    base_dir = Path(workspace_dir) if workspace_dir else None
    manager = WorkspaceManager(base_dir=base_dir)

    sessions = manager.list_sessions(days=days)

    if not sessions:
        click.echo("No exploration sessions found.")
        return

    click.echo(f"Found {len(sessions)} session(s):\n")

    for session in sessions:
        click.echo(f"  {session.workspace_id}")
        click.echo(f"    Repository: {session.repo_name}")
        click.echo(f"    URL: {session.repo_url}")
        if session.subdir:
            click.echo(f"    Subdirectory: {session.subdir}")
        click.echo(f"    Last used: {session.last_used}")
        click.echo(f"    Created: {session.created_at}")
        click.echo()


@cli.command()
@click.option('--days', default=7, type=int, help='Remove workspaces not used in N days')
@click.option('--all', 'force', is_flag=True, help='Remove all workspaces')
@click.option('--workspace-dir', type=click.Path(), help='Custom workspace base directory')
def clean(days: int, force: bool, workspace_dir: str):
    """Clean up old exploration workspaces.

    By default, removes workspaces not used in the last 7 days.
    """
    base_dir = Path(workspace_dir) if workspace_dir else None
    manager = WorkspaceManager(base_dir=base_dir)

    if force:
        click.confirm(
            'This will remove ALL workspaces. Continue?',
            abort=True
        )

    removed = manager.clean(days=days, force=force)

    if removed:
        click.echo(f"Removed {len(removed)} workspace(s):")
        for workspace_id in removed:
            click.echo(f"  - {workspace_id}")
    else:
        if force:
            click.echo("No workspaces to remove.")
        else:
            click.echo(f"No workspaces older than {days} days found.")


@cli.command()
@click.argument('workspace_id')
@click.option('--workspace-dir', type=click.Path(), help='Custom workspace base directory')
@click.option('--skip-permissions', is_flag=True, help='Launch Claude with --dangerously-skip-permissions')
@click.option('--claude-args', help='Additional arguments to pass to Claude (e.g., "--debug --verbose")')
def resume(workspace_id: str, workspace_dir: str, skip_permissions: bool, claude_args: str):
    """Resume exploration of a previous workspace.

    WORKSPACE_ID is the identifier from 'claude-explore list'.
    """
    base_dir = Path(workspace_dir) if workspace_dir else None
    manager = WorkspaceManager(base_dir=base_dir)

    # Get session
    session = manager.get_session(workspace_id)
    if not session:
        click.secho(f"Error: Workspace '{workspace_id}' not found.", fg='red', err=True)
        click.echo("\nUse 'claude-explore list' to see available workspaces.")
        sys.exit(1)

    # Get workspace path
    workspace_path = manager.get_workspace_path(workspace_id)
    if not workspace_path.exists():
        click.secho(
            f"Error: Workspace directory not found: {workspace_path}",
            fg='red',
            err=True
        )
        sys.exit(1)

    # Determine working directory
    work_dir = workspace_path
    if session.subdir:
        subdir_path = workspace_path / session.subdir
        if subdir_path.exists() and subdir_path.is_dir():
            work_dir = subdir_path
        else:
            click.secho(
                f"Warning: Subdirectory '{session.subdir}' not found, using repository root",
                fg='yellow'
            )

    # Display info
    click.echo(f"Repository: {session.repo_name}")
    click.echo(f"Workspace: {workspace_path}")
    if session.subdir:
        click.echo(f"Working directory: {work_dir}")

    # Check if claude exists
    if not _claude_exists():
        click.secho(
            "Error: 'claude' command not found. Please install Claude Code first.",
            fg='red',
            err=True
        )
        sys.exit(1)

    # Build Claude command with flags
    claude_cmd = ['claude']
    if skip_permissions:
        claude_cmd.append('--dangerously-skip-permissions')
    if claude_args:
        claude_cmd.extend(claude_args.split())

    # Launch Claude
    click.echo(f"\nLaunching Claude Code...")
    click.echo("(Exit Claude to return to this terminal)\n")

    os.chdir(work_dir)
    subprocess.run(claude_cmd)


@cli.command()
@click.option('--workspace-dir', type=click.Path(), help='Custom workspace base directory')
def info(workspace_dir: str):
    """Show workspace manager information."""
    base_dir = Path(workspace_dir) if workspace_dir else None
    manager = WorkspaceManager(base_dir=base_dir)

    click.echo("Claude Explore Workspace Manager")
    click.echo("=" * 40)
    click.echo(f"Base directory: {manager.base_dir}")
    click.echo(f"Workspaces directory: {manager.workspaces_dir}")
    click.echo(f"Sessions file: {manager.sessions_file}")
    click.echo()

    # Calculate workspace sizes
    if manager.workspaces_dir.exists():
        total_size = 0
        workspace_count = 0
        for workspace in manager.workspaces_dir.iterdir():
            if workspace.is_dir():
                size = sum(f.stat().st_size for f in workspace.rglob('*') if f.is_file())
                total_size += size
                workspace_count += 1

        # Convert to human-readable
        size_mb = total_size / (1024 * 1024)
        click.echo(f"Active workspaces: {workspace_count}")
        click.echo(f"Total disk usage: {size_mb:.1f} MB")


def _claude_exists() -> bool:
    """Check if claude command exists."""
    try:
        subprocess.run(
            ['which', 'claude'],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
