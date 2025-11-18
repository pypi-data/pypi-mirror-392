"""Tests for workspace management."""

import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

import pytest
from claude_explore.workspace import WorkspaceManager, Session
from claude_explore.url_parser import parse_github_url


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestWorkspaceManager:
    """Test workspace manager functionality."""

    def test_initialization(self, temp_workspace):
        """Test workspace manager initialization."""
        manager = WorkspaceManager(base_dir=temp_workspace)

        assert manager.base_dir == temp_workspace
        assert manager.workspaces_dir == temp_workspace / "workspaces"
        assert manager.sessions_file == temp_workspace / "sessions.json"
        assert manager.workspaces_dir.exists()

    def test_session_persistence(self, temp_workspace):
        """Test that sessions are persisted to JSON."""
        manager = WorkspaceManager(base_dir=temp_workspace)
        repo = parse_github_url("https://github.com/user/repo")

        # Update session
        workspace_id = "test123"
        manager._update_session(workspace_id, repo)

        # Load sessions from file
        sessions = manager._load_sessions()
        assert workspace_id in sessions
        assert sessions[workspace_id].repo_name == "user/repo"
        assert sessions[workspace_id].repo_url == "https://github.com/user/repo"

    def test_list_sessions_empty(self, temp_workspace):
        """Test listing sessions when none exist."""
        manager = WorkspaceManager(base_dir=temp_workspace)
        sessions = manager.list_sessions()
        assert sessions == []

    def test_list_sessions_with_data(self, temp_workspace):
        """Test listing sessions with data."""
        manager = WorkspaceManager(base_dir=temp_workspace)
        repo1 = parse_github_url("https://github.com/user/repo1")
        repo2 = parse_github_url("https://github.com/user/repo2")

        manager._update_session("id1", repo1)
        manager._update_session("id2", repo2)

        sessions = manager.list_sessions()
        assert len(sessions) == 2
        assert any(s.workspace_id == "id1" for s in sessions)
        assert any(s.workspace_id == "id2" for s in sessions)

    def test_list_sessions_filtered_by_days(self, temp_workspace):
        """Test filtering sessions by days."""
        manager = WorkspaceManager(base_dir=temp_workspace)

        # Create old session
        old_session = Session(
            workspace_id="old",
            repo_url="https://github.com/user/old",
            repo_name="user/old",
            subdir=None,
            created_at=(datetime.now() - timedelta(days=10)).isoformat(),
            last_used=(datetime.now() - timedelta(days=10)).isoformat()
        )

        # Create recent session
        recent_session = Session(
            workspace_id="recent",
            repo_url="https://github.com/user/recent",
            repo_name="user/recent",
            subdir=None,
            created_at=datetime.now().isoformat(),
            last_used=datetime.now().isoformat()
        )

        # Save sessions
        sessions = {"old": old_session, "recent": recent_session}
        manager._save_sessions(sessions)

        # Filter to last 7 days
        recent_sessions = manager.list_sessions(days=7)
        assert len(recent_sessions) == 1
        assert recent_sessions[0].workspace_id == "recent"

    def test_get_session(self, temp_workspace):
        """Test getting a specific session."""
        manager = WorkspaceManager(base_dir=temp_workspace)
        repo = parse_github_url("https://github.com/user/repo")

        manager._update_session("test", repo)

        session = manager.get_session("test")
        assert session is not None
        assert session.workspace_id == "test"
        assert session.repo_name == "user/repo"

        # Non-existent session
        assert manager.get_session("nonexistent") is None

    def test_get_workspace_path(self, temp_workspace):
        """Test getting workspace path."""
        manager = WorkspaceManager(base_dir=temp_workspace)
        path = manager.get_workspace_path("test123")
        assert path == temp_workspace / "workspaces" / "test123"

    def test_get_working_directory_root(self, temp_workspace):
        """Test getting working directory for repo root."""
        manager = WorkspaceManager(base_dir=temp_workspace)
        repo = parse_github_url("https://github.com/user/repo")
        workspace_path = temp_workspace / "workspace"
        workspace_path.mkdir()

        work_dir = manager.get_working_directory(repo, workspace_path)
        assert work_dir == workspace_path

    def test_get_working_directory_subdir(self, temp_workspace):
        """Test getting working directory for subdirectory."""
        manager = WorkspaceManager(base_dir=temp_workspace)
        repo = parse_github_url("https://github.com/user/repo/tree/main/src")
        workspace_path = temp_workspace / "workspace"
        workspace_path.mkdir()
        subdir_path = workspace_path / "src"
        subdir_path.mkdir()

        work_dir = manager.get_working_directory(repo, workspace_path)
        assert work_dir == subdir_path

    def test_get_working_directory_subdir_not_exists(self, temp_workspace):
        """Test getting working directory when subdirectory doesn't exist."""
        manager = WorkspaceManager(base_dir=temp_workspace)
        repo = parse_github_url("https://github.com/user/repo/tree/main/nonexistent")
        workspace_path = temp_workspace / "workspace"
        workspace_path.mkdir()

        # Should fall back to root
        work_dir = manager.get_working_directory(repo, workspace_path)
        assert work_dir == workspace_path


class TestSession:
    """Test Session dataclass."""

    def test_session_to_dict(self):
        """Test converting session to dict."""
        session = Session(
            workspace_id="test",
            repo_url="https://github.com/user/repo",
            repo_name="user/repo",
            subdir="src",
            created_at="2025-01-01T00:00:00",
            last_used="2025-01-02T00:00:00"
        )

        data = session.to_dict()
        assert data["workspace_id"] == "test"
        assert data["repo_url"] == "https://github.com/user/repo"
        assert data["subdir"] == "src"

    def test_session_from_dict(self):
        """Test creating session from dict."""
        data = {
            "workspace_id": "test",
            "repo_url": "https://github.com/user/repo",
            "repo_name": "user/repo",
            "subdir": None,
            "created_at": "2025-01-01T00:00:00",
            "last_used": "2025-01-02T00:00:00"
        }

        session = Session.from_dict(data)
        assert session.workspace_id == "test"
        assert session.repo_url == "https://github.com/user/repo"
        assert session.subdir is None
