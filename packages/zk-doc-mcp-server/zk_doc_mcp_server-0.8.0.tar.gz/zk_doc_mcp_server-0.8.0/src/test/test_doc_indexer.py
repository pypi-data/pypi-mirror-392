
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
from src.zk_doc_mcp.doc_indexer import DocIndexer

class TestDocIndexer(unittest.TestCase):

    def setUp(self):
        self.test_doc_path = "/tmp/test_docs"
        os.makedirs(self.test_doc_path, exist_ok=True)

        # Create a DocIndexer instance
        self.indexer = DocIndexer(doc_path=self.test_doc_path)

        # Mock the internal dependencies of the DocIndexer instance
        self.indexer.client = MagicMock()
        self.indexer.collection = MagicMock()

    def tearDown(self):
        # Clean up test directory
        if os.path.exists(self.test_doc_path):
            os.rmdir(self.test_doc_path)

    def test_chunk_content(self):
        content = "This is a test content that needs to be chunked. It is long enough to be split into multiple chunks."
        chunks = self.indexer._chunk_content(content, chunk_size=20, chunk_overlap=5)
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0], "This is a test conte")
        self.assertEqual(chunks[1], "content that needs t")

    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    def test_index_docs(self, mock_open_file, mock_os_walk):
        # Simulate a directory with a markdown file
        mock_os_walk.return_value = [
            (self.test_doc_path, [], ["test_doc.md"])
        ]
        mock_open_file.return_value.read.return_value = "# Test Document\nThis is some test content."

        self.indexer.index_docs()

        # Verify that open was called with the correct path
        expected_file_path = os.path.join(self.test_doc_path, "test_doc.md")
        mock_open_file.assert_called_once_with(expected_file_path, 'r', encoding='utf-8')

        # Verify that the collection.add method was called
        self.indexer.collection.add.assert_called_once()

    @patch.object(DocIndexer, '_chunk_content', return_value=["chunk1", "chunk2"])
    def test_embed_and_store(self, mock_chunk_content):
        file_path = "/tmp/test_docs/test_doc.md"
        chunks = ["chunk1", "chunk2"]

        self.indexer._embed_and_store(chunks, file_path)

        # Get the arguments passed to mock_collection.add
        args, kwargs = self.indexer.collection.add.call_args

        # Assert the arguments (ChromaDB handles embeddings internally)
        self.assertEqual(kwargs['documents'], chunks)
        self.assertEqual(len(kwargs['metadatas']), 2)
        self.assertEqual(kwargs['metadatas'][0]['source'], file_path)
        self.assertEqual(kwargs['ids'], [f"{file_path}-0", f"{file_path}-1"])

if __name__ == '__main__':
    unittest.main()
