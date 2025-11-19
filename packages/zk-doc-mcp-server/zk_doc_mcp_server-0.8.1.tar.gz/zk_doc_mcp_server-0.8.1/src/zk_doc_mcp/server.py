"""MCP Server for ZK Framework Documentation."""

from fastmcp import FastMCP
import time
from typing import Optional

from .logger import setup_logging, logger

mcp = FastMCP(name="zk-doc-server")

# Module-level doc indexer instance
_indexer = None


def _get_indexer():
    """Get or create the document indexer instance."""
    global _indexer
    if _indexer is None:
        from pathlib import Path
        import os
        from .doc_indexer import DocIndexer

        doc_path = os.getenv(
            "ZK_DOC_SRC_DIR",
            str(Path.home() / ".zk-doc-mcp" / "repo")
        )
        persist_dir = os.getenv(
            "ZK_DOC_VECTOR_DB_DIR",
            str(Path.home() / ".zk-doc-mcp" / "chroma_db")
        )

        _indexer = DocIndexer(
            doc_path=doc_path,
            persist_dir=persist_dir
        )
    return _indexer


def _extract_title_from_content(content: str) -> str:
    """Extract the first heading from content as title."""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('#'):
            # Remove markdown heading markers
            return line.lstrip('#').strip()
    # If no heading found, use first 50 chars
    return content[:50] + "..." if len(content) > 50 else content


def _distance_to_relevance(distance: float) -> float:
    """Convert ChromaDB distance to relevance score (0-1)."""
    # ChromaDB distances are typically 0-2, where 0 is most similar
    # Convert to 0-1 scale where 1 is most relevant
    return max(0.0, 1.0 - distance)


def search_zk_docs_impl(
    query: str,
    limit: int = 5,
    min_relevance: float = 0.0,
    category: Optional[str] = None
) -> dict:
    """Search ZK documentation for relevant content - core implementation.

    This function contains the actual search logic and is exposed as a testable
    function. It performs semantic search on indexed ZK documentation using ChromaDB.

    The separation between search_zk_docs_impl() and search_zk_docs() exists because:
    - search_zk_docs_impl() contains the business logic and is testable directly
    - search_zk_docs() is decorated with @mcp.tool() to expose it as an MCP tool
    - FastMCP's @mcp.tool() decorator wraps the function, making direct testing difficult
    - By splitting them, we can test the implementation without relying on MCP internals

    Args:
        query: Search query string (required)
        limit: Maximum number of results to return (default: 5, range: 1-20)
        min_relevance: Minimum relevance score threshold (default: 0.0, range: 0-1)
        category: Optional filter for document categories (e.g., "tutorial", "reference", "guide")

    Returns:
        Dictionary with search results including:
        - results: List of matching documents with scores
        - total_found: Number of results returned
        - query_time_ms: Query execution time in milliseconds
    """
    start_time = time.time()

    # Parameter validation
    if not query or not isinstance(query, str):
        return {
            "error": "Invalid parameter: 'query' is required and cannot be empty."
        }

    if not isinstance(limit, int) or limit < 1 or limit > 20:
        return {
            "error": "Invalid parameter: 'limit' must be between 1 and 20."
        }

    if not isinstance(min_relevance, (int, float)) or min_relevance < 0 or min_relevance > 1:
        return {
            "error": "Invalid parameter: 'min_relevance' must be between 0 and 1."
        }

    # Validate category if provided
    if category is not None and not isinstance(category, str):
        return {
            "error": "Invalid parameter: 'category' must be a string."
        }

    try:
        # Get the indexer instance
        indexer = _get_indexer()

        # Perform the search with ChromaDB
        search_results = indexer.search(query, n_results=limit)

        # Format results according to spec
        formatted_results = []
        total_found = 0

        if search_results.get('results'):
            for result in search_results['results']:
                # Convert distance to relevance score
                relevance_score = _distance_to_relevance(result['distance'])

                # Filter by minimum relevance
                if relevance_score < min_relevance:
                    continue

                # Extract metadata
                metadata = result.get('metadata', {})
                file_path = metadata.get('source', '')

                # Filter by category if provided
                if category:
                    # Simple category extraction from file path
                    # e.g., "/path/to/tutorial/file.md" -> "tutorial"
                    path_parts = file_path.split('/')
                    doc_category = path_parts[-2] if len(path_parts) > 1 else ""
                    if category.lower() != doc_category.lower():
                        continue

                # Extract or derive title from content
                content = result.get('document', '')
                title = _extract_title_from_content(content)

                formatted_results.append({
                    "content": content,
                    "file_path": file_path,
                    "title": title,
                    "category": category or "",
                    "relevance_score": round(relevance_score, 4)
                })
                total_found += 1

        query_time_ms = int((time.time() - start_time) * 1000)

        return {
            "results": formatted_results,
            "total_found": total_found,
            "query_time_ms": query_time_ms
        }

    except ImportError as e:
        return {
            "error": "Search dependencies not available",
            "details": str(e)
        }
    except FileNotFoundError as e:
        return {
            "error": "Documentation path not found",
            "details": str(e)
        }
    except Exception as e:
        return {
            "error": "Internal server error during document search",
            "details": str(e)
        }


@mcp.tool()
def search_zk_docs(
    query: str,
    limit: int = 5,
    min_relevance: float = 0.0,
    category: Optional[str] = None
) -> dict:
    """Search ZK documentation for relevant content.

    This is the MCP tool entry point for searching. It delegates to search_zk_docs_impl()
    which contains the actual implementation. See search_zk_docs_impl() docstring for
    explanation of why they are separated.

    Args:
        query: Search query string (required)
        limit: Maximum number of results to return (default: 5, range: 1-20)
        min_relevance: Minimum relevance score threshold (default: 0.0, range: 0-1)
        category: Optional filter for document categories (e.g., "tutorial", "reference", "guide")

    Returns:
        Dictionary with search results including relevance scores
    """
    return search_zk_docs_impl(query, limit, min_relevance, category)


def index_documentation():
    """Index ZK documentation and initialize module-level indexer.
    """
    global _indexer
    from pathlib import Path
    import os

    # Get configuration from environment or defaults
    doc_path = os.getenv(
        "ZK_DOC_SRC_DIR",
        str(Path.home() / ".zk-doc-mcp" / "repo")
    )
    persist_dir = os.getenv(
        "ZK_DOC_VECTOR_DB_DIR",
        str(Path.home() / ".zk-doc-mcp" / "chroma_db")
    )
    force_reindex = os.getenv("ZK_DOC_FORCE_REINDEX", "false").lower() == "true"

    # use git to clone zk doc repository
    use_git = os.getenv("ZK_DOC_USE_GIT", "true").lower() == "true"

    try:
        from .doc_indexer import DocIndexer

        # If git mode is enabled, clone/pull from GitHub
        if use_git:
            logger.info("Using Git to clone repositories")
            from .git_manager import GitDocumentationManager

            # Get Git configuration
            clone_method = os.getenv("ZK_DOC_CLONE_METHOD", "https")
            repo_path = os.getenv("ZK_DOC_REPO_PATH", None)
            repo_url = os.getenv(
                "ZK_DOC_REPO_URL",
                "https://github.com/zkoss/zkdoc.git"
            )
            git_branch = os.getenv("ZK_DOC_GIT_BRANCH", "main")

            # Initialize Git manager
            git_manager = GitDocumentationManager(
                repo_path=repo_path,
                clone_method=clone_method,
                repo_url=repo_url,
                branch=git_branch
            )

            # Ensure repository exists and is up-to-date
            if not git_manager.ensure_repo_exists():
                logger.warning("Failed to clone repository. Attempting to use local path.")
                # Fall back to local path
            else:
                # Get last commit before pulling
                commit_before = git_manager.get_last_commit_hash()

                # Pull latest changes
                pull_success, pull_msg = git_manager.pull_latest()

                if pull_success:
                    commit_after = git_manager.get_last_commit_hash()
                    if commit_before != commit_after:
                        logger.info("Documentation updated. Re-indexing...")
                        force_reindex = True
                    else:
                        logger.info("Documentation unchanged.")

                # Use repository documentation path
                docs_path = git_manager.get_docs_path()
                if docs_path:
                    doc_path = str(docs_path)
                    logger.info(f"Using Git repository documentation from: {doc_path}")

        # Initialize the module-level indexer instance
        _indexer = DocIndexer(
            doc_path=doc_path,
            persist_dir=persist_dir,
            force_reindex=force_reindex
        )

        # Get index info
        info = _indexer.get_index_info()
        logger.info(f"Index info: {info}")

        # Index documents (will skip if already indexed unless force_reindex is True)
        _indexer.index_docs()

    except ImportError as e:
        logger.error(f"Search dependencies not available: {e}")
        logger.error("To enable search, install: pip install zk-doc-mcp-server[search]")
    except FileNotFoundError:
        logger.error(f"Documentation path not found: {doc_path}")
        logger.error("Skipping documentation indexing.")
    except Exception as e:
        logger.error(f"Error indexing documentation: {e}")
        import traceback
        logger.error(traceback.format_exc())


def show_settings_impl() -> dict:
    """Display all configuration settings - core implementation.

    This function contains the actual logic and is testable directly.
    It is wrapped by show_settings() which is exposed as an MCP tool.

    Returns:
        Dictionary with settings and summary statistics.
    """
    import os
    from pathlib import Path

    # Define all settings with their metadata
    settings_config = [
        # Phase 1: Core Settings
        {
            "key": "ZK_DOC_SRC_DIR",
            "description": "Documentation source directory (Git repo or local docs)",
            "default": str(Path.home() / ".zk-doc-mcp" / "repo"),
            "type": "string"
        },
        {
            "key": "ZK_DOC_VECTOR_DB_DIR",
            "description": "Vector database directory for storing embeddings and search indices",
            "default": str(Path.home() / ".zk-doc-mcp" / "chroma_db"),
            "type": "string"
        },
        {
            "key": "ZK_DOC_FORCE_REINDEX",
            "description": "Force re-indexing of documentation",
            "default": "false",
            "type": "boolean"
        },
        {
            "key": "ZK_DOC_LOG_LEVEL",
            "description": "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            "default": "INFO",
            "type": "enum",
            "enum_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        },
        # Phase 2: Git Integration Settings
        {
            "key": "ZK_DOC_USE_GIT",
            "description": "Enable Git synchronization for documentation",
            "default": "true",
            "type": "boolean"
        },
        {
            "key": "ZK_DOC_CLONE_METHOD",
            "description": "Git clone method (https or ssh)",
            "default": "https",
            "type": "enum",
            "enum_values": ["https", "ssh"]
        },
        {
            "key": "ZK_DOC_REPO_URL",
            "description": "Repository URL",
            "default": "https://github.com/zkoss/zkdoc.git",
            "type": "string"
        },
        {
            "key": "ZK_DOC_GIT_BRANCH",
            "description": "Git branch to pull from",
            "default": "master",
            "type": "string"
        },
        # Phase 3: Feedback Settings
        {
            "key": "ZK_DOC_FEEDBACK_ENABLED",
            "description": "Enable feedback collection for search improvements",
            "default": "true",
            "type": "boolean"
        },
        {
            "key": "ZK_DOC_FEEDBACK_RETENTION_DAYS",
            "description": "Days to retain local feedback files",
            "default": "90",
            "type": "integer"
        },
        {
            "key": "ZK_DOC_FEEDBACK_GITHUB_REPO",
            "description": "GitHub repository for feedback issues (built-in)",
            "default": "zkoss/zkdoc",
            "type": "string"
        },
    ]

    # Build response settings
    settings = []
    configured_count = 0

    for config in settings_config:
        key = config["key"]
        default_value = config["default"]
        current_value = os.getenv(key, default_value)

        # Count configured settings (non-default)
        if current_value != default_value:
            configured_count += 1

        # Build setting entry
        setting = {
            "key": key,
            "description": config["description"],
            "default_value": default_value,
            "current_value": current_value,
            "type": config["type"]
        }

        # Add enum_values if present
        if "enum_values" in config:
            setting["enum_values"] = config["enum_values"]

        settings.append(setting)

    # Build summary
    summary = {
        "total_settings": len(settings_config),
        "configured_settings": configured_count,
        "default_settings": len(settings_config) - configured_count
    }

    return {
        "settings": settings,
        "summary": summary
    }


@mcp.tool()
def show_settings() -> dict:
    """Display all configuration settings for the ZK Documentation MCP Server.

    This tool enables users and administrators to inspect the current server
    configuration, including all environment variables and their effective values.
    It helps with debugging, configuration verification, and discoverability of
    available settings.

    Returns:
        Dictionary with settings and summary statistics.
    """
    return show_settings_impl()


@mcp.tool()
def submit_feedback(
    query: str,
    results: list,
    expected: str,
    comments: str = None
) -> dict:
    """Submit feedback about search results to improve documentation.

    When search results don't meet user expectations, this tool captures feedback
    that helps the documentation team understand gaps and improve content.

    Feedback is:
    - Always saved locally to ~/.zk-doc-mcp/feedback/
    - Automatically submitted as GitHub issue to https://github.com/zkoss/zkdoc/issues
    - Non-blocking (returns immediately while GitHub submission happens async)

    Args:
        query: The search query that produced unsatisfactory results
        results: List of search results returned (each with title, file_path, content)
        expected: What the user expected to find
        comments: Optional additional context about why results don't match

    Returns:
        Dictionary with submission status:
        - success: Whether feedback was saved
        - feedback_id: Unique identifier for this feedback
        - local_path: Where feedback was saved locally
        - github_issue_url: GitHub issue URL (if successfully created)
        - message: Status message
    """
    from .feedback_manager import get_feedback_manager

    feedback_manager = get_feedback_manager()
    return feedback_manager.submit_feedback(query, results, expected, comments)


def main():
    """Run the MCP server."""
    setup_logging()
    logger.info("Starting ZK Documentation MCP Server...")
    index_documentation()
    mcp.run()


if __name__ == "__main__":
    main()
