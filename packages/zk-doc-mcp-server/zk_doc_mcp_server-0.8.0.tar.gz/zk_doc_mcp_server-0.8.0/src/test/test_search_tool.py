"""Tests for the search_zk_docs MCP tool."""

import tempfile
import unittest
from pathlib import Path

try:
    from src.zk_doc_mcp.server import search_zk_docs_impl
    from src.zk_doc_mcp.doc_indexer import DocIndexer
    HAS_SEARCH_DEPS = True
except ImportError:
    HAS_SEARCH_DEPS = False


class TestSearchZkDocsTool(unittest.TestCase):
    """Test the search_zk_docs MCP tool."""

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def setUp(self):
        """Set up test fixtures."""
        self.doc_path = "/Users/hawk/Documents/workspace/DOC/zkdoc/get_started"
        if not Path(self.doc_path).exists():
            self.skipTest(f"Documentation directory not found: {self.doc_path}")

        # Create a temporary persistence directory for tests
        self.temp_dir = tempfile.TemporaryDirectory()

        # Initialize a module-level indexer with test data
        import src.zk_doc_mcp.server as server_module
        indexer = DocIndexer(
            doc_path=self.doc_path,
            persist_dir=self.temp_dir.name
        )
        indexer.index_docs()
        server_module._indexer = indexer

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_valid_search_query(self):
        """Test search with a valid query."""
        result = search_zk_docs_impl("ZK framework", min_relevance=0.0)

        self.assertIn("results", result)
        self.assertIn("total_found", result)
        self.assertIn("query_time_ms", result)
        self.assertGreater(result["total_found"], 0)

        # Check result format
        for item in result["results"]:
            self.assertIn("content", item)
            self.assertIn("file_path", item)
            self.assertIn("title", item)
            self.assertIn("category", item)
            self.assertIn("relevance_score", item)
            self.assertGreaterEqual(item["relevance_score"], 0)
            self.assertLessEqual(item["relevance_score"], 1)

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_limit_parameter(self):
        """Test that limit parameter works correctly."""
        result = search_zk_docs_impl("component", limit=3)

        self.assertLessEqual(len(result["results"]), 3)
        self.assertLessEqual(result["total_found"], 3)

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_min_relevance_filter(self):
        """Test that min_relevance parameter filters results."""
        result = search_zk_docs_impl("ZK", min_relevance=0.9)

        for item in result["results"]:
            self.assertGreaterEqual(item["relevance_score"], 0.9)

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_min_relevance_with_low_threshold(self):
        """Test search with low relevance threshold."""
        result = search_zk_docs_impl("ZK", limit=10, min_relevance=0.0)

        # Should return more results with lower threshold
        self.assertGreater(result["total_found"], 0)

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_empty_query_validation(self):
        """Test that empty query is rejected."""
        result = search_zk_docs_impl("")

        self.assertIn("error", result)
        self.assertIn("query", result["error"].lower())

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_invalid_limit_validation(self):
        """Test that invalid limit values are rejected."""
        # Test limit < 1
        result = search_zk_docs_impl("ZK", limit=0)
        self.assertIn("error", result)
        self.assertIn("limit", result["error"].lower())

        # Test limit > 20
        result = search_zk_docs_impl("ZK", limit=21)
        self.assertIn("error", result)
        self.assertIn("limit", result["error"].lower())

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_invalid_min_relevance_validation(self):
        """Test that invalid min_relevance values are rejected."""
        # Test min_relevance < 0
        result = search_zk_docs_impl("ZK", min_relevance=-0.1)
        self.assertIn("error", result)
        self.assertIn("min_relevance", result["error"].lower())

        # Test min_relevance > 1
        result = search_zk_docs_impl("ZK", min_relevance=1.1)
        self.assertIn("error", result)
        self.assertIn("min_relevance", result["error"].lower())

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_query_time_measurement(self):
        """Test that query time is measured and returned."""
        result = search_zk_docs_impl("ZK")

        self.assertIn("query_time_ms", result)
        self.assertIsInstance(result["query_time_ms"], int)
        self.assertGreater(result["query_time_ms"], 0)

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_relevance_score_conversion(self):
        """Test that relevance scores are properly converted from distances."""
        result = search_zk_docs_impl("ZK framework", limit=5)

        if result.get("results"):
            # All relevance scores should be between 0 and 1
            for item in result["results"]:
                score = item["relevance_score"]
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)


if __name__ == '__main__':
    unittest.main()
