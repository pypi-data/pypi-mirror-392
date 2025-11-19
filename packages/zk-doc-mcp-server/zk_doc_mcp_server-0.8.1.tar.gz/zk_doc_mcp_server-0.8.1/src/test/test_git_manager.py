"""Test cases for GitDocumentationManager (Phase 2)."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

try:
    from src.zk_doc_mcp.git_manager import GitDocumentationManager
    HAS_GIT_MANAGER = True
except ImportError:
    HAS_GIT_MANAGER = False


class TestGitDocumentationManager(unittest.TestCase):
    """Test the GitDocumentationManager class."""

    @unittest.skipIf(not HAS_GIT_MANAGER, "GitDocumentationManager not available")
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_path = Path(self.temp_dir.name) / "test_repo"

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_initialization_https(self):
        """Test GitDocumentationManager initialization with HTTPS."""
        manager = GitDocumentationManager(
            repo_path=str(self.repo_path),
            clone_method="https"
        )

        self.assertEqual(manager.repo_path, self.repo_path.resolve())
        self.assertEqual(manager.clone_method, "https")
        self.assertTrue(manager.repo_url.startswith("https://"))

    def test_initialization_ssh(self):
        """Test GitDocumentationManager initialization with SSH."""
        manager = GitDocumentationManager(
            repo_path=str(self.repo_path),
            clone_method="ssh"
        )

        self.assertEqual(manager.clone_method, "ssh")
        self.assertTrue(manager.repo_url.startswith("git@github.com:"))

    def test_initialization_defaults(self):
        """Test default configuration values."""
        manager = GitDocumentationManager(repo_path=str(self.repo_path))

        self.assertEqual(manager.clone_method, "https")
        self.assertEqual(manager.branch, "main")
        self.assertIn("zkoss/zkdoc", manager.repo_url)

    def test_initialization_custom_path(self):
        """Test initialization with custom repository path."""
        custom_path = Path.home() / "custom_docs"
        manager = GitDocumentationManager(repo_path=str(custom_path))

        self.assertEqual(manager.repo_path, custom_path.resolve())

    def test_initialization_home_expansion(self):
        """Test that ~ is expanded to home directory."""
        manager = GitDocumentationManager(repo_path="~/test_repo")

        self.assertTrue(str(manager.repo_path).startswith(str(Path.home())))
        self.assertNotIn("~", str(manager.repo_path))

    def test_invalid_clone_method(self):
        """Test that invalid clone method raises error."""
        with self.assertRaises(ValueError) as context:
            GitDocumentationManager(clone_method="invalid")

        self.assertIn("Invalid clone_method", str(context.exception))

    def test_url_conversion_https_to_ssh(self):
        """Test URL conversion from HTTPS to SSH."""
        manager = GitDocumentationManager(
            repo_path=str(self.repo_path),
            clone_method="https"
        )
        original_url = manager.repo_url

        # Switch to SSH
        manager.clone_method = "ssh"
        manager._update_repo_url_for_method()

        self.assertTrue(manager.repo_url.startswith("git@github.com:"))
        self.assertFalse(manager.repo_url.startswith("https://"))

    def test_url_conversion_ssh_to_https(self):
        """Test URL conversion from SSH to HTTPS."""
        manager = GitDocumentationManager(
            repo_path=str(self.repo_path),
            clone_method="ssh"
        )

        # Switch to HTTPS
        manager.clone_method = "https"
        manager._update_repo_url_for_method()

        self.assertTrue(manager.repo_url.startswith("https://github.com"))
        self.assertFalse(manager.repo_url.startswith("git@"))

    @patch('subprocess.run')
    def test_run_git_command_success(self, mock_run):
        """Test successful git command execution."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="success output",
            stderr=""
        )

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        success, stdout, stderr = manager._run_git_command(["git", "status"])

        self.assertTrue(success)
        self.assertEqual(stdout, "success output")
        self.assertEqual(stderr, "")

    @patch('subprocess.run')
    def test_run_git_command_failure(self, mock_run):
        """Test failed git command execution."""
        mock_run.return_value = MagicMock(
            returncode=128,
            stdout="",
            stderr="fatal: not a git repository"
        )

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        success, stdout, stderr = manager._run_git_command(["git", "status"])

        self.assertFalse(success)
        self.assertIn("fatal", stderr)

    def test_run_git_command_timeout(self):
        """Test git command timeout."""
        import subprocess
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("git", 60)

            manager = GitDocumentationManager(repo_path=str(self.repo_path))
            success, stdout, stderr = manager._run_git_command(["git", "clone", "url"])

            self.assertFalse(success)
            self.assertIn("timed out", stderr.lower())

    @patch('subprocess.run')
    def test_run_git_command_not_installed(self, mock_run):
        """Test when git is not installed."""
        mock_run.side_effect = FileNotFoundError()

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        success, stdout, stderr = manager._run_git_command(["git", "status"])

        self.assertFalse(success)
        self.assertIn("not installed", stderr.lower())

    @patch('subprocess.run')
    def test_is_valid_repo_true(self, mock_run):
        """Test valid repository detection."""
        # Create minimal repo structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        self.assertTrue(manager._is_valid_repo())

    @patch('subprocess.run')
    def test_is_valid_repo_false_no_git(self, mock_run):
        """Test invalid repository (no .git directory)."""
        self.repo_path.mkdir(parents=True, exist_ok=True)

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        self.assertFalse(manager._is_valid_repo())

    @patch('subprocess.run')
    def test_is_valid_repo_false_not_exists(self, mock_run):
        """Test invalid repository (directory doesn't exist)."""
        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        self.assertFalse(manager._is_valid_repo())

    @patch('subprocess.run')
    def test_ensure_repo_exists_already_exists(self, mock_run):
        """Test ensure_repo_exists when repository already exists."""
        # Create minimal repo structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        result = manager.ensure_repo_exists()

        # Should succeed without calling git
        self.assertTrue(result)
        mock_run.assert_not_called()

    @patch('subprocess.run')
    def test_ensure_repo_exists_clone_success(self, mock_run):
        """Test successful repository cloning."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        result = manager.ensure_repo_exists()

        self.assertTrue(result)
        mock_run.assert_called_once()

        # Verify clone command was called with correct parameters
        call_args = mock_run.call_args
        self.assertIn("clone", call_args[0][0])
        self.assertIn(manager.repo_url, call_args[0][0])

    @patch('subprocess.run')
    def test_ensure_repo_exists_clone_failure(self, mock_run):
        """Test failed repository cloning."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="fatal: could not read Username"
        )

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        result = manager.ensure_repo_exists()

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_has_remote_updates_true(self, mock_run):
        """Test detection of remote updates available."""
        # Create minimal repo structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        # Mock git commands: fetch succeeds, local and remote HEADs differ
        side_effects = [
            MagicMock(returncode=0, stdout="", stderr=""),  # fetch
            MagicMock(returncode=0, stdout="abc123", stderr=""),  # local HEAD
            MagicMock(returncode=0, stdout="def456", stderr=""),  # remote HEAD
        ]
        mock_run.side_effect = side_effects

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        result = manager.has_remote_updates()

        self.assertTrue(result)

    @patch('subprocess.run')
    def test_has_remote_updates_false(self, mock_run):
        """Test when repository is up-to-date."""
        # Create minimal repo structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        # Mock git commands: HEADs are the same
        side_effects = [
            MagicMock(returncode=0, stdout="", stderr=""),  # fetch
            MagicMock(returncode=0, stdout="abc123", stderr=""),  # local HEAD
            MagicMock(returncode=0, stdout="abc123", stderr=""),  # remote HEAD (same)
        ]
        mock_run.side_effect = side_effects

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        result = manager.has_remote_updates()

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_has_remote_updates_fetch_fails(self, mock_run):
        """Test when fetch fails."""
        # Create minimal repo structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Could not resolve host"
        )

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        result = manager.has_remote_updates()

        self.assertFalse(result)

    @patch('subprocess.run')
    def test_pull_latest_success_with_updates(self, mock_run):
        """Test successful pull with updates available."""
        # Create minimal repo structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        # Mock: fetch succeeds, different HEADs, pull succeeds
        # Sequence: fetch1, fetch2 (in has_remote_updates), local_HEAD, remote_HEAD, pull
        side_effects = [
            MagicMock(returncode=0, stdout="", stderr=""),  # fetch in pull_latest
            MagicMock(returncode=0, stdout="", stderr=""),  # fetch in has_remote_updates
            MagicMock(returncode=0, stdout="abc123", stderr=""),  # local HEAD
            MagicMock(returncode=0, stdout="def456", stderr=""),  # remote HEAD (different)
            MagicMock(returncode=0, stdout="3 files changed", stderr=""),  # pull
        ]
        mock_run.side_effect = side_effects

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        success, message = manager.pull_latest()

        self.assertTrue(success)

    @patch('subprocess.run')
    def test_pull_latest_already_up_to_date(self, mock_run):
        """Test pull when repository is already up-to-date."""
        # Create minimal repo structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        # Mock: fetch succeeds, same HEADs
        side_effects = [
            MagicMock(returncode=0, stdout="", stderr=""),  # fetch
            MagicMock(returncode=0, stdout="abc123", stderr=""),  # local HEAD
            MagicMock(returncode=0, stdout="abc123", stderr=""),  # remote HEAD (same)
        ]
        mock_run.side_effect = side_effects

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        success, message = manager.pull_latest()

        self.assertTrue(success)
        self.assertIn("up-to-date", message.lower())

    @patch('subprocess.run')
    def test_pull_latest_fetch_fails(self, mock_run):
        """Test pull when fetch fails."""
        # Create minimal repo structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Network error"
        )

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        success, message = manager.pull_latest()

        self.assertFalse(success)

    @patch('subprocess.run')
    def test_get_last_commit_hash_success(self, mock_run):
        """Test retrieving the latest commit hash."""
        # Create minimal repo structure
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            stderr=""
        )

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        commit_hash = manager.get_last_commit_hash()

        self.assertEqual(commit_hash, "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")

    @patch('subprocess.run')
    def test_get_last_commit_hash_failure(self, mock_run):
        """Test retrieving commit hash when repository is invalid."""
        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        commit_hash = manager.get_last_commit_hash()

        self.assertIsNone(commit_hash)

    def test_get_docs_path_from_repo(self):
        """Test finding documentation path in repository."""
        # Create repo with docs directory
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)
        (self.repo_path / "docs").mkdir(exist_ok=True)

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        docs_path = manager.get_docs_path()

        self.assertEqual(docs_path, self.repo_path.resolve() / "docs")

    def test_get_docs_path_fallback_to_root(self):
        """Test that repo root is returned if no standard docs directory."""
        # Create repo without standard docs directory
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / ".git").mkdir(exist_ok=True)

        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        docs_path = manager.get_docs_path()

        self.assertEqual(docs_path, self.repo_path.resolve())

    def test_get_docs_path_invalid_repo(self):
        """Test get_docs_path returns None for invalid repository."""
        manager = GitDocumentationManager(repo_path=str(self.repo_path))
        docs_path = manager.get_docs_path()

        self.assertIsNone(docs_path)


if __name__ == '__main__':
    unittest.main()
