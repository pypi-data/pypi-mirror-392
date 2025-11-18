"""Workspace management for ephemeral repository exploration."""

import json
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

from .url_parser import GitHubRepo, get_repo_hash


@dataclass
class Session:
    """Exploration session metadata."""
    workspace_id: str
    repo_url: str
    repo_name: str
    subdir: Optional[str]
    created_at: str
    last_used: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        """Create from dictionary."""
        return cls(**data)


class WorkspaceManager:
    """Manage ephemeral workspaces for repository exploration."""

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize workspace manager.

        Args:
            base_dir: Base directory for workspaces (defaults to ~/.claude-explore)
        """
        self.base_dir = base_dir or Path.home() / ".claude-explore"
        self.workspaces_dir = self.base_dir / "workspaces"
        self.sessions_file = self.base_dir / "sessions.json"

        # Ensure directories exist
        self.workspaces_dir.mkdir(parents=True, exist_ok=True)

    def _load_sessions(self) -> Dict[str, Session]:
        """Load sessions from JSON file."""
        if not self.sessions_file.exists():
            return {}

        try:
            with open(self.sessions_file, 'r') as f:
                data = json.load(f)
                return {k: Session.from_dict(v) for k, v in data.items()}
        except (json.JSONDecodeError, KeyError):
            # Corrupted sessions file, return empty
            return {}

    def _save_sessions(self, sessions: Dict[str, Session]) -> None:
        """Save sessions to JSON file."""
        data = {k: v.to_dict() for k, v in sessions.items()}
        with open(self.sessions_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _update_session(self, workspace_id: str, repo: GitHubRepo) -> None:
        """Update or create a session."""
        sessions = self._load_sessions()
        now = datetime.now().isoformat()

        if workspace_id in sessions:
            # Update existing session
            sessions[workspace_id].last_used = now
            if repo.subdir:
                sessions[workspace_id].subdir = repo.subdir
        else:
            # Create new session
            sessions[workspace_id] = Session(
                workspace_id=workspace_id,
                repo_url=repo.https_url,
                repo_name=repo.full_name,
                subdir=repo.subdir,
                created_at=now,
                last_used=now
            )

        self._save_sessions(sessions)

    def get_workspace_path(self, workspace_id: str) -> Path:
        """Get the path for a workspace."""
        return self.workspaces_dir / workspace_id

    def get_or_create_workspace(self, repo: GitHubRepo, update: bool = True) -> Path:
        """Get existing workspace or create new one.

        Args:
            repo: GitHubRepo object
            update: Whether to update (git pull) if workspace exists

        Returns:
            Path to workspace directory
        """
        workspace_id = get_repo_hash(repo)
        workspace_path = self.get_workspace_path(workspace_id)

        if workspace_path.exists():
            if update:
                # Update existing workspace (git pull)
                self._git_pull(workspace_path)
        else:
            # Clone new workspace
            self._git_clone(repo.clone_url, workspace_path)

        # Update session metadata
        self._update_session(workspace_id, repo)

        return workspace_path

    def _git_clone(self, clone_url: str, dest: Path) -> None:
        """Clone a git repository.

        Args:
            clone_url: Git clone URL
            dest: Destination directory

        Raises:
            RuntimeError: If git clone fails
        """
        try:
            subprocess.run(
                ['git', 'clone', '--depth=1', clone_url, str(dest)],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git clone failed: {e.stderr}")

    def _git_pull(self, repo_path: Path) -> None:
        """Update a git repository.

        Args:
            repo_path: Path to git repository

        Raises:
            RuntimeError: If git pull fails
        """
        try:
            subprocess.run(
                ['git', 'pull'],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            # Pull might fail if there are local changes or no upstream
            # Just log and continue
            pass

    def list_sessions(self, days: Optional[int] = None) -> List[Session]:
        """List exploration sessions.

        Args:
            days: Only show sessions from last N days (None = all)

        Returns:
            List of Session objects, sorted by last_used (newest first)
        """
        sessions = self._load_sessions()

        if days is not None:
            cutoff = datetime.now() - timedelta(days=days)
            sessions = {
                k: v for k, v in sessions.items()
                if datetime.fromisoformat(v.last_used) > cutoff
            }

        # Sort by last_used, newest first
        sorted_sessions = sorted(
            sessions.values(),
            key=lambda s: s.last_used,
            reverse=True
        )

        return sorted_sessions

    def clean(self, days: int = 7, force: bool = False) -> List[str]:
        """Clean up old workspaces.

        Args:
            days: Remove workspaces not used in N days
            force: Remove all workspaces regardless of age

        Returns:
            List of removed workspace IDs
        """
        sessions = self._load_sessions()
        removed = []

        if force:
            # Remove all workspaces
            for workspace_id in list(sessions.keys()):
                workspace_path = self.get_workspace_path(workspace_id)
                if workspace_path.exists():
                    shutil.rmtree(workspace_path)
                removed.append(workspace_id)
                del sessions[workspace_id]
        else:
            # Remove old workspaces
            cutoff = datetime.now() - timedelta(days=days)
            for workspace_id, session in list(sessions.items()):
                last_used = datetime.fromisoformat(session.last_used)
                if last_used < cutoff:
                    workspace_path = self.get_workspace_path(workspace_id)
                    if workspace_path.exists():
                        shutil.rmtree(workspace_path)
                    removed.append(workspace_id)
                    del sessions[workspace_id]

        # Save updated sessions
        self._save_sessions(sessions)

        return removed

    def get_session(self, workspace_id: str) -> Optional[Session]:
        """Get a session by workspace ID.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Session object or None if not found
        """
        sessions = self._load_sessions()
        return sessions.get(workspace_id)

    def get_working_directory(self, repo: GitHubRepo, workspace_path: Path) -> Path:
        """Get the working directory for exploration.

        If repo has a subdir, returns that subdirectory path.
        Otherwise returns the workspace root.

        Args:
            repo: GitHubRepo object
            workspace_path: Path to workspace

        Returns:
            Path to working directory
        """
        if repo.subdir:
            subdir_path = workspace_path / repo.subdir
            if subdir_path.exists() and subdir_path.is_dir():
                return subdir_path
            # If subdir doesn't exist, fall back to root with warning
            return workspace_path
        return workspace_path
