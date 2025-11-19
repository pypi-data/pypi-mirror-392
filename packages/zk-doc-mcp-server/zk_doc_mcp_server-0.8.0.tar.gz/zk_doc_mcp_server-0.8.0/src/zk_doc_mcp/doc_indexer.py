"""Documentation indexing module for ChromaDB integration."""

import os
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger("zk_doc_mcp")

try:
    import chromadb
    HAS_SEARCH_DEPS = True
except ImportError:
    HAS_SEARCH_DEPS = False


class DocIndexer:
    """Document indexer using ChromaDB for vector search.

    Uses ChromaDB's built-in embeddings (no external model required).
    Requires optional dependencies: chromadb
    Install with: pip install zk-doc-mcp-server[search]
    """

    def __init__(
        self,
        doc_path: str,
        collection_name: str = "zk_docs",
        persist_dir: Optional[str] = None,
        force_reindex: bool = False
    ):
        """Initialize the document indexer.

        Args:
            doc_path: Path to documentation directory
            collection_name: Name of the ChromaDB collection
            persist_dir: Directory for persistent storage.
                        Defaults to ~/.zk-doc-mcp/chromadb/
            force_reindex: If True, delete existing index and reindex all docs

        Raises:
            ImportError: If chromadb or sentence-transformers not installed
        """
        if not HAS_SEARCH_DEPS:
            raise ImportError(
                "Search dependencies not installed. "
                "Install with: pip install zk-doc-mcp-server[search]"
            )

        self.doc_path = Path(doc_path)
        self.collection_name = collection_name
        self.force_reindex = force_reindex

        # Determine persistence directory
        if persist_dir is None:
            persist_dir = Path.home() / ".zk-doc-mcp" / "chromadb"
        else:
            persist_dir = Path(persist_dir)

        # Ensure directory exists
        persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize PersistentClient
        self.client = chromadb.PersistentClient(path=str(persist_dir))

        # Get or create collection with metadata
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Get existing collection or create new one with metadata."""
        if self.force_reindex:
            # Delete existing collection if exists
            try:
                self.client.delete_collection(name=self.collection_name)
                logger.info(f"Deleted existing collection: {self.collection_name}")
            except ValueError:
                pass  # Collection doesn't exist

        # Create collection with metadata tracking indexing info
        metadata = {
            "schema_version": "1.0",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }

        collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata=metadata
        )

        return collection

    def index_docs(self):
        """Index all markdown files from doc_path."""
        # Check if collection is empty
        collection_count = self.collection.count()

        if collection_count > 0 and not self.force_reindex:
            logger.info(f"Collection '{self.collection_name}' already contains "
                        f"{collection_count} documents.")
            logger.info("Skipping indexing. Use force_reindex=True to rebuild.")
            return

        logger.info(f"Starting indexing of files from: {self.doc_path}")
        indexed_files = 0
        indexed_chunks = 0

        for root, _, files in os.walk(self.doc_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            chunks = self._chunk_content(content)
                            self._embed_and_store(chunks, file_path)
                            indexed_files += 1
                            indexed_chunks += len(chunks)
                    except Exception as e:
                        logger.error(f"Error indexing {file_path}: {e}")

        # Update collection metadata
        self.collection.modify(
            metadata={
                **self.collection.metadata,
                "last_updated": datetime.utcnow().isoformat(),
                "indexed_files": indexed_files,
                "indexed_chunks": indexed_chunks
            }
        )

        logger.info(f"Indexing complete: {indexed_files} files, {indexed_chunks} chunks")

    def _chunk_content(self, content, chunk_size=1000, chunk_overlap=200):
        chunks = []
        start = 0
        while start < len(content):
            end = start + chunk_size
            chunks.append(content[start:end])
            start += chunk_size - chunk_overlap
        return chunks

    def _embed_and_store(self, chunks, file_path):
        """Store document chunks with metadata (ChromaDB handles embeddings)."""
        documents = chunks
        metadatas = [
            {
                "source": file_path,
                "indexed_at": datetime.utcnow().isoformat()
            }
            for _ in chunks
        ]
        ids = [f"{file_path}-{i}" for i in range(len(chunks))]

        # ChromaDB automatically generates embeddings for documents
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def get_index_info(self) -> dict:
        """Get information about the current index.

        Returns:
            Dictionary with index statistics and metadata
        """
        metadata = self.collection.metadata or {}
        count = self.collection.count()

        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "schema_version": metadata.get("schema_version"),
            "created_at": metadata.get("created_at"),
            "last_updated": metadata.get("last_updated"),
            "indexed_files": metadata.get("indexed_files"),
            "indexed_chunks": metadata.get("indexed_chunks")
        }

    def reset_index(self):
        """Delete all documents from the collection."""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Collection '{self.collection_name}' deleted.")
        self.collection = self._get_or_create_collection()
        logger.info(f"Collection '{self.collection_name}' recreated.")

    def search(self, query: str, n_results: int = 5) -> dict:
        """Search the indexed documents using semantic similarity.

        Args:
            query: Search query string
            n_results: Maximum number of results to return

        Returns:
            Dictionary with search results including documents, distances, and metadata
        """
        # Query the collection (ChromaDB automatically embeds the query)
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # Format results
        formatted_results = []
        if results and results.get('documents'):
            for i, (doc, distance, metadata) in enumerate(
                zip(
                    results['documents'][0],
                    results['distances'][0],
                    results['metadatas'][0]
                )
            ):
                formatted_results.append({
                    "index": i,
                    "document": doc,
                    "distance": float(distance),
                    "metadata": metadata
                })

        return {
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        }

if __name__ == '__main__':
    from .logger import setup_logging
    setup_logging()
    indexer = DocIndexer(doc_path="/Users/hawk/Documents/workspace/DOC/zkdoc/get_started")
    indexer.index_docs()
    logger.info("Documentation indexed successfully!")
