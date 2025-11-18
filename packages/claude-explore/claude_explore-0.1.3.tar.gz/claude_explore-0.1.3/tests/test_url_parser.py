"""Tests for URL parsing."""

import pytest
from claude_explore.url_parser import parse_github_url, get_repo_hash


class TestParseGitHubUrl:
    """Test GitHub URL parsing."""

    def test_simple_https_url(self):
        """Test simple HTTPS URL."""
        repo = parse_github_url("https://github.com/user/repo")
        assert repo.user == "user"
        assert repo.repo == "repo"
        assert repo.subdir is None
        assert repo.branch is None
        assert repo.clone_url == "https://github.com/user/repo.git"
        assert repo.full_name == "user/repo"

    def test_https_url_with_git_extension(self):
        """Test HTTPS URL with .git extension."""
        repo = parse_github_url("https://github.com/user/repo.git")
        assert repo.user == "user"
        assert repo.repo == "repo"
        assert repo.subdir is None

    def test_ssh_url(self):
        """Test SSH URL."""
        repo = parse_github_url("git@github.com:user/repo.git")
        assert repo.user == "user"
        assert repo.repo == "repo"
        assert repo.clone_url == "https://github.com/user/repo.git"

    def test_url_with_tree_and_subdir(self):
        """Test URL with tree path and subdirectory."""
        repo = parse_github_url("https://github.com/user/repo/tree/main/src/core")
        assert repo.user == "user"
        assert repo.repo == "repo"
        assert repo.branch == "main"
        assert repo.subdir == "src/core"

    def test_url_with_tree_no_subdir(self):
        """Test URL with tree but no subdirectory."""
        repo = parse_github_url("https://github.com/user/repo/tree/main")
        assert repo.user == "user"
        assert repo.repo == "repo"
        assert repo.branch == "main"
        assert repo.subdir is None

    def test_url_with_blob(self):
        """Test URL with blob (file) path."""
        repo = parse_github_url("https://github.com/user/repo/blob/main/src/file.py")
        assert repo.user == "user"
        assert repo.repo == "repo"
        assert repo.branch == "main"
        assert repo.subdir == "src/file.py"

    def test_url_with_trailing_slash(self):
        """Test URL with trailing slash."""
        repo = parse_github_url("https://github.com/user/repo/")
        assert repo.user == "user"
        assert repo.repo == "repo"

    def test_invalid_url(self):
        """Test invalid URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            parse_github_url("https://gitlab.com/user/repo")

    def test_invalid_url_format(self):
        """Test malformed URL raises ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            parse_github_url("not-a-url")


class TestGetRepoHash:
    """Test repository hash generation."""

    def test_same_repo_same_hash(self):
        """Test that same repo always gets same hash."""
        repo1 = parse_github_url("https://github.com/user/repo")
        repo2 = parse_github_url("https://github.com/user/repo.git")

        hash1 = get_repo_hash(repo1)
        hash2 = get_repo_hash(repo2)

        assert hash1 == hash2

    def test_subdir_same_hash(self):
        """Test that subdirectories share the same hash."""
        repo1 = parse_github_url("https://github.com/user/repo")
        repo2 = parse_github_url("https://github.com/user/repo/tree/main/src")

        hash1 = get_repo_hash(repo1)
        hash2 = get_repo_hash(repo2)

        assert hash1 == hash2

    def test_different_repos_different_hash(self):
        """Test that different repos get different hashes."""
        repo1 = parse_github_url("https://github.com/user/repo1")
        repo2 = parse_github_url("https://github.com/user/repo2")

        hash1 = get_repo_hash(repo1)
        hash2 = get_repo_hash(repo2)

        assert hash1 != hash2

    def test_hash_length(self):
        """Test that hash is 8 characters."""
        repo = parse_github_url("https://github.com/user/repo")
        hash_val = get_repo_hash(repo)
        assert len(hash_val) == 8
