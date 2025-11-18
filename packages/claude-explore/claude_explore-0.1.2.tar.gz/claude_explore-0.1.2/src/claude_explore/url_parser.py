"""GitHub URL parsing utilities."""

import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class GitHubRepo:
    """Parsed GitHub repository information."""
    user: str
    repo: str
    url: str
    subdir: Optional[str] = None
    branch: Optional[str] = None

    @property
    def clone_url(self) -> str:
        """Get the git clone URL."""
        return f"https://github.com/{self.user}/{self.repo}.git"

    @property
    def https_url(self) -> str:
        """Get the HTTPS GitHub URL."""
        return f"https://github.com/{self.user}/{self.repo}"

    @property
    def repo_name(self) -> str:
        """Get the repository name."""
        return self.repo

    @property
    def full_name(self) -> str:
        """Get the full repository name (user/repo)."""
        return f"{self.user}/{self.repo}"


def parse_github_url(url: str) -> GitHubRepo:
    """Parse a GitHub URL into components.

    Supports:
    - https://github.com/user/repo
    - https://github.com/user/repo.git
    - git@github.com:user/repo.git
    - https://github.com/user/repo/tree/branch/path/to/subdir
    - https://github.com/user/repo/blob/branch/path/to/file.py

    Args:
        url: GitHub URL to parse

    Returns:
        GitHubRepo object with parsed components

    Raises:
        ValueError: If URL is not a valid GitHub URL
    """
    # Remove trailing slashes
    url = url.rstrip('/')

    # Pattern for HTTPS URLs with optional tree/blob path
    https_pattern = r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/(?:tree|blob)/([^/]+)(?:/(.+))?)?$'

    # Pattern for SSH URLs
    ssh_pattern = r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$'

    # Try HTTPS pattern first
    match = re.match(https_pattern, url)
    if match:
        user, repo, branch, subdir = match.groups()
        return GitHubRepo(
            user=user,
            repo=repo,
            url=url,
            branch=branch,
            subdir=subdir
        )

    # Try SSH pattern
    match = re.match(ssh_pattern, url)
    if match:
        user, repo = match.groups()
        return GitHubRepo(
            user=user,
            repo=repo,
            url=url
        )

    raise ValueError(f"Invalid GitHub URL: {url}")


def get_repo_hash(repo: GitHubRepo) -> str:
    """Generate a deterministic hash for a repository.

    Uses the full repository name (user/repo) to generate a consistent
    identifier for the workspace directory.

    Args:
        repo: GitHubRepo object

    Returns:
        Short hash string (first 8 chars of hex digest)
    """
    import hashlib

    # Hash based on user/repo (not including subdir, so same repo = same workspace)
    content = f"{repo.user}/{repo.repo}"
    return hashlib.sha256(content.encode()).hexdigest()[:8]
