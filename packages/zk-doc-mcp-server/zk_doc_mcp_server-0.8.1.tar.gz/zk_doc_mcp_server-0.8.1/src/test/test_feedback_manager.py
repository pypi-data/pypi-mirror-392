"""Tests for feedback_manager module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from zk_doc_mcp.feedback_manager import FeedbackManager


class TestFeedbackManager:
    """Test suite for FeedbackManager."""

    @pytest.fixture
    def temp_feedback_dir(self):
        """Create a temporary feedback directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def manager(self, temp_feedback_dir):
        """Create a FeedbackManager instance with temp directory."""
        return FeedbackManager(
            feedback_dir=temp_feedback_dir,
            enabled=True,
            retention_days=90
        )

    def test_init_creates_directory(self, temp_feedback_dir):
        """Test that FeedbackManager creates feedback directory."""
        manager = FeedbackManager(feedback_dir=temp_feedback_dir)
        assert manager.feedback_dir.exists()
        assert manager.feedback_dir.is_dir()

    def test_submit_feedback_disabled(self, manager):
        """Test submission when feedback is disabled."""
        manager.enabled = False
        result = manager.submit_feedback(
            query="test",
            results=[],
            expected="something"
        )
        assert result["success"] is False
        assert "disabled" in result["message"].lower()

    def test_submit_feedback_invalid_query(self, manager):
        """Test submission with invalid query."""
        result = manager.submit_feedback(
            query="",
            results=[],
            expected="something"
        )
        assert result["success"] is False
        assert "query" in result["message"].lower()

    def test_submit_feedback_invalid_expected(self, manager):
        """Test submission with invalid expected."""
        result = manager.submit_feedback(
            query="test",
            results=[],
            expected=""
        )
        assert result["success"] is False
        assert "expected" in result["message"].lower()

    def test_submit_feedback_invalid_results(self, manager):
        """Test submission with invalid results."""
        result = manager.submit_feedback(
            query="test",
            results="not a list",
            expected="something"
        )
        assert result["success"] is False
        assert "results" in result["message"].lower()

    def test_submit_feedback_saves_locally(self, manager):
        """Test that feedback is saved locally."""
        result = manager.submit_feedback(
            query="data binding",
            results=[
                {
                    "title": "MVVM Binding",
                    "file_path": "/docs/mvvm.md",
                    "content": "Binding in MVVM..."
                }
            ],
            expected="How to bind data in MVVM",
            comments="Results were not clear"
        )

        # Check success
        assert result["success"] is True
        assert result["feedback_id"] is not None
        assert result["local_path"] is not None

        # Check file exists
        local_path = Path(result["local_path"])
        assert local_path.exists()

        # Verify file contents
        with open(local_path) as f:
            feedback = json.load(f)

        assert feedback["query"] == "data binding"
        assert feedback["expected"] == "How to bind data in MVVM"
        assert feedback["comments"] == "Results were not clear"
        assert len(feedback["results"]) == 1
        assert feedback["results"][0]["title"] == "MVVM Binding"

    def test_submit_feedback_with_no_comments(self, manager):
        """Test submission without comments."""
        result = manager.submit_feedback(
            query="test",
            results=[{"title": "Test", "file_path": "/test.md", "content": "test"}],
            expected="something"
        )

        assert result["success"] is True

        local_path = Path(result["local_path"])
        with open(local_path) as f:
            feedback = json.load(f)

        assert feedback["comments"] == ""

    def test_feedback_file_naming(self, manager):
        """Test that feedback files follow correct naming convention."""
        result = manager.submit_feedback(
            query="test",
            results=[{"title": "Test", "file_path": "/test.md", "content": "test"}],
            expected="something"
        )

        file_path = Path(result["local_path"])
        file_name = file_path.name

        # Check naming convention: feedback_YYYYMMDD_xxxxxxxx.json
        assert file_name.startswith("feedback_")
        assert file_name.endswith(".json")
        parts = file_name.replace(".json", "").split("_")
        assert len(parts) == 3  # feedback, date, random
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 8  # random hex

    def test_cleanup_old_feedback(self, manager):
        """Test cleanup of old feedback files."""
        import time
        import os

        # Create a feedback file
        result = manager.submit_feedback(
            query="test",
            results=[{"title": "Test", "file_path": "/test.md", "content": "test"}],
            expected="something"
        )

        # Verify file exists
        file_path = Path(result["local_path"])
        assert file_path.exists()

        # Set retention to 0 days (all should be deleted)
        manager.retention_days = 0

        # Make file old by setting mtime to past
        old_time = time.time() - (100 * 86400)  # 100 days ago
        os.utime(file_path, (old_time, old_time))

        # Cleanup
        deleted_count = manager.cleanup_old_feedback()

        # Verify file was deleted
        assert deleted_count == 1
        assert not file_path.exists()

    def test_cleanup_respects_retention(self, manager):
        """Test that cleanup respects retention period."""
        # Create a feedback file
        result = manager.submit_feedback(
            query="test",
            results=[{"title": "Test", "file_path": "/test.md", "content": "test"}],
            expected="something"
        )

        file_path = Path(result["local_path"])

        # Set retention to high value (should not delete)
        manager.retention_days = 365

        # Cleanup
        deleted_count = manager.cleanup_old_feedback()

        # Verify file was NOT deleted
        assert deleted_count == 0
        assert file_path.exists()

    def test_get_feedback_count(self, manager):
        """Test getting count of feedback files."""
        assert manager.get_feedback_count() == 0

        # Submit 3 feedbacks
        for i in range(3):
            manager.submit_feedback(
                query=f"test {i}",
                results=[{"title": "Test", "file_path": "/test.md", "content": "test"}],
                expected="something"
            )

        # Wait for async operations to complete (or give small delay)
        import time
        time.sleep(0.2)

        assert manager.get_feedback_count() == 3

    def test_format_github_issue_body(self, manager):
        """Test formatting of GitHub issue body."""
        feedback = {
            "query": "data binding",
            "results": [
                {"title": "Result 1", "file_path": "/path1.md"},
                {"title": "Result 2", "file_path": "/path2.md"}
            ],
            "expected": "How to bind data",
            "comments": "Results were not helpful",
            "id": "feedback_20250114_abc12345"
        }

        body = manager._format_github_issue_body(feedback)

        # Verify key content is in body
        assert "data binding" in body
        assert "How to bind data" in body
        assert "Results were not helpful" in body
        assert "Result 1" in body
        assert "Result 2" in body
        assert "feedback_20250114_abc12345" in body

    def test_format_github_issue_with_no_results(self, manager):
        """Test formatting GitHub issue when no results."""
        feedback = {
            "query": "test",
            "results": [],
            "expected": "something",
            "comments": "No results",
            "id": "feedback_test"
        }

        body = manager._format_github_issue_body(feedback)

        assert "No results returned" in body

    def test_format_github_issue_with_no_comments(self, manager):
        """Test formatting GitHub issue with no comments."""
        feedback = {
            "query": "test",
            "results": [{"title": "Result", "file_path": "/path.md"}],
            "expected": "something",
            "comments": "",
            "id": "feedback_test"
        }

        body = manager._format_github_issue_body(feedback)

        assert "(None)" in body

    @patch("zk_doc_mcp.feedback_manager.httpx.Client.post")
    def test_create_github_issue_success(self, mock_post, manager):
        """Test successful GitHub issue creation."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "html_url": "https://github.com/zkoss/zkdoc/issues/123"
        }
        mock_post.return_value = mock_response

        issue_url = manager._create_github_issue(
            title="[Feedback] Search: test",
            body="Test body"
        )

        assert issue_url == "https://github.com/zkoss/zkdoc/issues/123"
        mock_post.assert_called_once()

    @patch("zk_doc_mcp.feedback_manager.httpx.Client.post")
    def test_create_github_issue_failure(self, mock_post, manager):
        """Test GitHub issue creation failure."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        issue_url = manager._create_github_issue(
            title="[Feedback] Search: test",
            body="Test body"
        )

        assert issue_url is None

    def test_feedback_id_format(self, manager):
        """Test that feedback ID has correct format."""
        result = manager.submit_feedback(
            query="test",
            results=[{"title": "Test", "file_path": "/test.md", "content": "test"}],
            expected="something"
        )

        feedback_id = result["feedback_id"]

        # Should be feedback_YYYYMMDD_xxxxxxxx
        assert feedback_id.startswith("feedback_")
        parts = feedback_id.split("_")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # date
        assert len(parts[2]) == 8  # random hex

    def test_disabled_manager_no_local_save(self, manager):
        """Test that disabled manager doesn't save feedback."""
        manager.enabled = False

        result = manager.submit_feedback(
            query="test",
            results=[{"title": "Test", "file_path": "/test.md", "content": "test"}],
            expected="something"
        )

        assert result["success"] is False
        assert manager.get_feedback_count() == 0
