"""Git operations manager for documentation synchronization (Phase 2)."""

import os
import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("zk_doc_mcp")


class GitDocumentationManager:
    """Manages Git operations for automatic documentation synchronization.

    This class handles cloning and updating the ZK documentation repository
    from GitHub. It supports both SSH and HTTPS clone methods and provides
    robust error handling for various failure scenarios.

    Requires: Git (version 2.7 or higher) to be installed on the system.
    """

    def __init__(
        self,
        repo_path: Optional[str] = None,
        clone_method: str = "https",
        repo_url: str = "https://github.com/zkoss/zkdoc.git",
        branch: str = "main",
    ):
        """Initialize the Git documentation manager.

        Args:
            repo_path: Path to store the repository. Defaults to ~/.zk-doc-mcp/repo/
            clone_method: Clone method ("https" or "ssh"). Default: "https"
            repo_url: GitHub repository URL. Default: official ZK docs repo
            branch: Git branch to pull from. Default: "main"
        """
        # Determine repository path
        if repo_path:
            self.repo_path = Path(repo_path).expanduser().resolve()
        else:
            self.repo_path = Path.home() / ".zk-doc-mcp" / "repo"

        self.clone_method = clone_method.lower()
        self.repo_url = repo_url
        self.branch = branch

        # Validate clone method
        if self.clone_method not in ("https", "ssh"):
            raise ValueError(f"Invalid clone_method: {self.clone_method}. Must be 'https' or 'ssh'")

        # Convert URL if method changed
        self._update_repo_url_for_method()

    def _update_repo_url_for_method(self):
        """Update repository URL format based on clone method."""
        if self.clone_method == "ssh":
            # Convert HTTPS to SSH: https://github.com/user/repo.git -> git@github.com:user/repo.git
            if self.repo_url.startswith("https://github.com/"):
                self.repo_url = (
                    "git@github.com:" + self.repo_url[19:-4] + ".git"
                )
        else:
            # Convert SSH to HTTPS: git@github.com:user/repo.git -> https://github.com/user/repo.git
            if self.repo_url.startswith("git@github.com:"):
                self.repo_url = (
                    "https://github.com/" + self.repo_url[15:-4] + ".git"
                )

    def _run_git_command(self, command: list, cwd: Optional[Path] = None) -> Tuple[bool, str, str]:
        """Run a git command and return success status with output.

        Args:
            command: Git command as list (e.g., ["git", "clone", ...])
            cwd: Working directory for command. Default: repo_path

        Returns:
            Tuple of (success, stdout, stderr)
        """
        if cwd is None:
            cwd = self.repo_path

        try:
            result = subprocess.run(
                command,
                cwd=str(cwd) if self.repo_path.exists() or "clone" not in command else None,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return (result.returncode == 0, result.stdout.strip(), result.stderr.strip())
        except subprocess.TimeoutExpired:
            return (False, "", "Git command timed out after 60 seconds")
        except FileNotFoundError:
            return (False, "", "Git is not installed or not found in PATH")
        except Exception as e:
            return (False, "", str(e))

    def ensure_repo_exists(self) -> bool:
        """Ensure repository exists, cloning if necessary.

        Returns:
            True if repository exists or was successfully cloned, False otherwise.
        """
        # If repo already exists, nothing to do
        if self.repo_path.exists() and (self.repo_path / ".git").exists():
            return True

        # If directory exists but is not a repo, remove it
        if self.repo_path.exists():
            import shutil
            try:
                shutil.rmtree(self.repo_path)
            except Exception as e:
                logger.error(f"Failed to remove corrupted repository: {e}")
                return False

        # Create parent directories
        try:
            self.repo_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory {self.repo_path.parent}: {e}")
            return False

        # Clone repository
        logger.info(f"Cloning ZK documentation repository ({self.clone_method})...")
        logger.info(f"Repository URL: {self.repo_url}")
        logger.info(f"Target path: {self.repo_path}")

        success, stdout, stderr = self._run_git_command(
            ["git", "clone", "--depth", "1", "--branch", self.branch, self.repo_url, str(self.repo_path)],
            cwd=self.repo_path.parent,
        )

        if success:
            logger.info("Repository cloned successfully")
            return True
        else:
            error_msg = stderr if stderr else stdout
            logger.error(f"Failed to clone repository: {error_msg}")

            # Suggest fallback
            if "Permission denied" in error_msg or "Could not read" in error_msg:
                if self.clone_method == "ssh":
                    logger.info("SSH authentication failed. Suggestion: Configure SSH keys or try HTTPS method.")
                    logger.info("Set ZK_DOC_CLONE_METHOD=https to use HTTPS instead.")
            elif "Network" in error_msg or "Could not resolve" in error_msg:
                logger.info("Network error. Ensure you have internet connectivity.")

            return False

    def has_remote_updates(self) -> bool:
        """Check if remote repository has updates compared to local.

        Returns:
            True if remote has newer commits, False otherwise.
        """
        if not self._is_valid_repo():
            return False

        # Fetch latest refs from remote
        success, _, stderr = self._run_git_command(["git", "fetch", "origin", self.branch])
        if not success:
            logger.warning(f"Could not fetch from remote: {stderr}")
            return False

        # Compare local HEAD with remote HEAD
        success, local_head, _ = self._run_git_command(["git", "rev-parse", "HEAD"])
        if not success:
            return False

        success, remote_head, _ = self._run_git_command(
            ["git", "rev-parse", f"origin/{self.branch}"]
        )
        if not success:
            return False

        has_updates = local_head != remote_head
        return has_updates

    def pull_latest(self) -> Tuple[bool, str]:
        """Pull latest changes from remote repository.

        Returns:
            Tuple of (success, message)
        """
        if not self._is_valid_repo():
            return (False, "Repository does not exist or is invalid")

        logger.info(f"Fetching latest changes from {self.branch}...")

        # Fetch updates
        success, _, stderr = self._run_git_command(["git", "fetch", "origin", self.branch])
        if not success:
            msg = f"Failed to fetch: {stderr}"
            logger.warning(msg)
            return (False, msg)

        # Check if there are updates
        if not self.has_remote_updates():
            msg = "Repository is up-to-date"
            logger.info(msg)
            return (True, msg)

        # Pull changes
        success, stdout, stderr = self._run_git_command(
            ["git", "pull", "origin", self.branch]
        )

        if success:
            # Count commits in output
            lines = stdout.split("\n")
            msg = stdout if stdout else "Changes pulled successfully"
            logger.info(msg)
            return (True, msg)
        else:
            msg = f"Failed to pull: {stderr}"
            logger.warning(msg)

            # Suggest merge conflict resolution
            if "conflict" in stderr.lower():
                logger.info("Merge conflict detected. Manual resolution may be needed.")

            return (False, msg)

    def get_last_commit_hash(self) -> Optional[str]:
        """Get the hash of the latest commit.

        Returns:
            Commit hash as string, or None if unable to retrieve.
        """
        if not self._is_valid_repo():
            return None

        success, commit_hash, _ = self._run_git_command(["git", "rev-parse", "HEAD"])
        return commit_hash if success else None

    def _is_valid_repo(self) -> bool:
        """Check if the repository path contains a valid git repository.

        Returns:
            True if valid git repository exists, False otherwise.
        """
        return (
            self.repo_path.exists()
            and (self.repo_path / ".git").exists()
            and (self.repo_path / ".git").is_dir()
        )

    def get_docs_path(self) -> Optional[Path]:
        """Get the path to documentation files within the repository.

        Returns:
            Path to documentation directory, or None if not found.
        """
        if not self._is_valid_repo():
            return None

        # Common documentation directory names
        for doc_dir in ["docs", "documentation", "zk-doc"]:
            doc_path = self.repo_path / doc_dir
            if doc_path.exists() and doc_path.is_dir():
                return doc_path

        # If no standard directory found, return repo root
        return self.repo_path
