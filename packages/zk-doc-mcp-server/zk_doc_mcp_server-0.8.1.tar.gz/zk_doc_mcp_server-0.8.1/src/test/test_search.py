"""Integration tests for searching ZK documentation."""

import tempfile
import unittest
import os
from pathlib import Path

try:
    from src.zk_doc_mcp.doc_indexer import DocIndexer
    HAS_SEARCH_DEPS = True
except ImportError:
    HAS_SEARCH_DEPS = False


class TestDocumentationSearch(unittest.TestCase):
    """Test searching documentation with persistent ChromaDB."""

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_search_zk_documentation(self):
        """Test searching actual ZK documentation from get_started directory."""
        doc_path = "/Users/hawk/Documents/workspace/DOC/zkdoc/get_started"

        # Skip if documentation path doesn't exist
        if not Path(doc_path).exists():
            self.skipTest(f"Documentation directory not found: {doc_path}")

        # Use a temporary directory for persistence
        with tempfile.TemporaryDirectory() as persist_dir:
            # Create indexer
            indexer = DocIndexer(
                doc_path=doc_path,
                persist_dir=persist_dir
            )

            # Index the documents
            print("Indexing documentation...")
            indexer.index_docs()

            # Get index info
            info = indexer.get_index_info()
            print(f"\nIndex Info: {info}")

            # Verify index was populated
            self.assertGreater(
                info['document_count'],
                0,
                "Index should have documents after indexing"
            )

            # Test 1: Search for "ZK" (should find relevant results)
            print("\n=== Test 1: Search for 'ZK' ===")
            results = indexer.search("ZK framework", n_results=5)
            print(f"Query: {results['query']}")
            print(f"Found {results['count']} results:")
            for i, result in enumerate(results['results']):
                print(f"\n  Result {i + 1}:")
                print(f"    Distance: {result['distance']:.4f}")
                print(f"    Source: {result['metadata'].get('source', 'unknown')}")
                print(f"    Text: {result['document'][:100]}...")

            self.assertGreater(
                results['count'],
                0,
                "Search for 'ZK framework' should return results"
            )

            # Test 2: Search for unrelated term to demonstrate higher distance scores
            print("\n=== Test 2: Search for 'angular' (unrelated term) ===")
            results2 = indexer.search("angular", n_results=3)
            print(f"Query: {results2['query']}")
            print(f"Found {results2['count']} results:")
            for i, result in enumerate(results2['results']):
                print(f"\n  Result {i + 1}:")
                print(f"    Distance: {result['distance']:.4f}")
                print(f"    Source: {result['metadata'].get('source', 'unknown')}")
                print(f"    Text: {result['document'][:100]}...")

            self.assertGreater(
                results2['count'],
                0,
                "Search for 'angular' should return results"
            )

            # Assert that all distances are > 1.0 (showing unrelated content)
            for result in results2['results']:
                self.assertGreater(
                    result['distance'],
                    1.0,
                    f"Unrelated query 'angular' should have distance > 1.0, "
                    f"got {result['distance']:.4f}"
                )

            # Test 3: Search for "component"
            print("\n=== Test 3: Search for 'component architecture' ===")
            results3 = indexer.search("component architecture", n_results=5)
            print(f"Query: {results3['query']}")
            print(f"Found {results3['count']} results:")
            for i, result in enumerate(results3['results']):
                print(f"\n  Result {i + 1}:")
                print(f"    Distance: {result['distance']:.4f}")
                print(f"    Source: {result['metadata'].get('source', 'unknown')}")
                print(f"    Text: {result['document'][:100]}...")

            self.assertGreater(
                results3['count'],
                0,
                "Search for 'component architecture' should return results"
            )

    @unittest.skipIf(not HAS_SEARCH_DEPS, "Search dependencies not installed")
    def test_persistence_across_instances(self):
        """Test that indexed documents persist across indexer instances."""
        doc_path = "/Users/hawk/Documents/workspace/DOC/zkdoc/get_started"

        # Skip if documentation path doesn't exist
        if not Path(doc_path).exists():
            self.skipTest(f"Documentation directory not found: {doc_path}")

        with tempfile.TemporaryDirectory() as persist_dir:
            # First instance: Index documents
            print("\n=== Creating first indexer instance ===")
            indexer1 = DocIndexer(
                doc_path=doc_path,
                persist_dir=persist_dir
            )
            indexer1.index_docs()
            count1 = indexer1.collection.count()
            print(f"First instance indexed {count1} documents")

            # Second instance: Load existing index
            print("\n=== Creating second indexer instance ===")
            indexer2 = DocIndexer(
                doc_path=doc_path,
                persist_dir=persist_dir
            )
            count2 = indexer2.collection.count()
            print(f"Second instance found {count2} documents")

            # Verify counts match
            self.assertEqual(
                count1,
                count2,
                "Document count should be same across instances"
            )

            # Verify search works in second instance
            results = indexer2.search("ZK", n_results=3)
            self.assertGreater(
                results['count'],
                0,
                "Search should work in second instance with persistent index"
            )
            print(f"Search in second instance returned {results['count']} results")


if __name__ == '__main__':
    unittest.main()
