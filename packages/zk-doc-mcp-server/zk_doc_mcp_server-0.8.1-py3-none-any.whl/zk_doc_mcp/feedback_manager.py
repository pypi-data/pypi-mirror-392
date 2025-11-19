"""Feedback collection and management for documentation improvement."""

import os
import json
import logging
import uuid
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, timezone
import threading

import httpx

logger = logging.getLogger("zk_doc_mcp")


class FeedbackManager:
    """Manages feedback collection and submission to GitHub issues.

    Features:
    - Always saves feedback locally to ~/.zk-doc-mcp/feedback/
    - Automatically creates GitHub issues (async, non-blocking)
    - Graceful fallback if GitHub API fails
    - No user configuration needed (token built-in)
    """

    # Built-in GitHub configuration
    GITHUB_TOKEN = "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"
    GITHUB_REPO = "zkoss/zkdoc"
    GITHUB_API_URL = "https://api.github.com"

    def __init__(
        self,
        feedback_dir: Optional[str] = None,
        enabled: bool = True,
        retention_days: int = 90
    ):
        """Initialize the feedback manager.

        Args:
            feedback_dir: Directory to store feedback. Defaults to ~/.zk-doc-mcp/feedback/
            enabled: Enable feedback collection (default: True)
            retention_days: Days to keep feedback files (default: 90)
        """
        self.enabled = enabled
        self.retention_days = retention_days

        # Determine feedback directory
        if feedback_dir:
            self.feedback_dir = Path(feedback_dir).expanduser().resolve()
        else:
            self.feedback_dir = Path.home() / ".zk-doc-mcp" / "feedback"

        # Create feedback directory
        try:
            self.feedback_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create feedback directory {self.feedback_dir}: {e}")

    def submit_feedback(
        self,
        query: str,
        results: List[Dict],
        expected: str,
        comments: Optional[str] = None
    ) -> Dict:
        """Submit feedback about search results.

        Args:
            query: The search query
            results: List of search results (each with title, file_path, content)
            expected: What user expected to find
            comments: Optional additional comments

        Returns:
            Dictionary with submission status and details
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "Feedback collection is disabled"
            }

        # Validate inputs
        if not query or not isinstance(query, str):
            return {
                "success": False,
                "message": "Invalid query: must be non-empty string"
            }

        if not expected or not isinstance(expected, str):
            return {
                "success": False,
                "message": "Invalid expected: must be non-empty string"
            }

        if not isinstance(results, list):
            return {
                "success": False,
                "message": "Invalid results: must be a list"
            }

        # Create feedback record
        now_utc = datetime.now(timezone.utc)
        feedback_id = f"feedback_{now_utc.strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
        feedback_record = {
            "id": feedback_id,
            "timestamp": now_utc.isoformat(),
            "query": query,
            "results": results,
            "expected": expected,
            "comments": comments or "",
            "github_issue_url": None
        }

        # Save to local storage
        local_path = None
        try:
            local_path = self._save_feedback_locally(feedback_record)
            logger.info(f"Feedback saved locally: {local_path}")
        except Exception as e:
            logger.error(f"Failed to save feedback locally: {e}")
            return {
                "success": False,
                "feedback_id": feedback_id,
                "message": f"Failed to save feedback: {e}",
                "error": "storage_error"
            }

        # Submit to GitHub asynchronously (non-blocking)
        result = {
            "success": True,
            "feedback_id": feedback_id,
            "local_path": str(local_path),
            "github_issue_url": None,
            "message": "Feedback saved locally"
        }

        # Submit to GitHub in background thread
        thread = threading.Thread(
            target=self._submit_to_github,
            args=(feedback_record,),
            daemon=True
        )
        thread.start()

        return result

    def _save_feedback_locally(self, feedback: Dict) -> Path:
        """Save feedback to local JSON file.

        Args:
            feedback: Feedback record dictionary

        Returns:
            Path to saved file

        Raises:
            Exception: If save fails
        """
        feedback_id = feedback["id"]
        file_path = self.feedback_dir / f"{feedback_id}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(feedback, f, indent=2, ensure_ascii=False)

        return file_path

    def _submit_to_github(self, feedback: Dict) -> bool:
        """Submit feedback as GitHub issue (async, non-blocking).

        Args:
            feedback: Feedback record dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Format issue title and body
            title = f"[Feedback] Search: {feedback['query'][:50]}"
            body = self._format_github_issue_body(feedback)

            # Create GitHub issue via API
            issue_url = self._create_github_issue(title, body)

            if issue_url:
                # Update local feedback record with issue URL
                feedback["github_issue_url"] = issue_url
                file_path = self.feedback_dir / f"{feedback['id']}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(feedback, f, indent=2, ensure_ascii=False)

                logger.info(f"GitHub issue created: {issue_url}")
                return True
            else:
                logger.warning(f"Failed to create GitHub issue for feedback {feedback['id']}")
                return False

        except Exception as e:
            logger.error(f"Error submitting feedback to GitHub: {e}")
            return False

    def _format_github_issue_body(self, feedback: Dict) -> str:
        """Format feedback as GitHub issue body.

        Args:
            feedback: Feedback record dictionary

        Returns:
            Formatted issue body (markdown)
        """
        # Format results
        results_text = ""
        if feedback.get("results"):
            results_text = "\n".join([
                f"- **{r.get('title', 'Untitled')}** ({r.get('file_path', 'unknown')})"
                for r in feedback["results"][:5]  # Limit to first 5
            ])
        else:
            results_text = "(No results returned)"

        body = f"""## Search Query
`{feedback['query']}`

## Results Returned
{results_text}

## Expected Results
{feedback['expected']}

## Additional Comments
{feedback['comments'] if feedback['comments'] else '(None)'}

---
Submitted via ZK Doc MCP Server
Feedback ID: {feedback['id']}
"""
        return body

    def _create_github_issue(self, title: str, body: str) -> Optional[str]:
        """Create a GitHub issue via API.

        Args:
            title: Issue title
            body: Issue body (markdown)

        Returns:
            Issue URL if successful, None otherwise
        """
        try:
            url = f"{self.GITHUB_API_URL}/repos/{self.GITHUB_REPO}/issues"

            headers = {
                "Authorization": f"token {self.GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "zk-doc-mcp-server"
            }

            payload = {
                "title": title,
                "body": body,
                "labels": ["mcp", "search-improvement"]
            }

            # Use httpx for the request (already in dependencies)
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=headers, json=payload)

            if response.status_code == 201:
                issue_data = response.json()
                return issue_data.get("html_url")
            else:
                logger.warning(
                    f"GitHub API error: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Exception creating GitHub issue: {e}")
            return None

    def cleanup_old_feedback(self) -> int:
        """Delete feedback files older than retention period.

        Returns:
            Number of files deleted
        """
        if not self.feedback_dir.exists():
            return 0

        cutoff_time = datetime.now(timezone.utc).timestamp() - (self.retention_days * 86400)
        deleted_count = 0

        for feedback_file in self.feedback_dir.glob("feedback_*.json"):
            try:
                if feedback_file.stat().st_mtime < cutoff_time:
                    feedback_file.unlink()
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete old feedback {feedback_file}: {e}")

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old feedback files")

        return deleted_count

    def get_feedback_count(self) -> int:
        """Get count of stored feedback files.

        Returns:
            Number of feedback files
        """
        if not self.feedback_dir.exists():
            return 0

        return len(list(self.feedback_dir.glob("feedback_*.json")))


# Module-level instance
_feedback_manager: Optional[FeedbackManager] = None


def get_feedback_manager() -> FeedbackManager:
    """Get or create the feedback manager instance."""
    global _feedback_manager
    if _feedback_manager is None:
        feedback_enabled = os.getenv("ZK_DOC_FEEDBACK_ENABLED", "true").lower() == "true"
        retention_days = int(os.getenv("ZK_DOC_FEEDBACK_RETENTION_DAYS", "90"))

        _feedback_manager = FeedbackManager(
            enabled=feedback_enabled,
            retention_days=retention_days
        )

    return _feedback_manager
