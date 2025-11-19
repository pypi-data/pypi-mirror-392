"""ZK Documentation MCP Server."""

__version__ = "0.1.0"
__author__ = "hawkchen from potix"
__description__ = "MCP server for ZK Framework documentation search and Q&A"

try:
    from .doc_indexer import DocIndexer
    __all__ = ["DocIndexer"]
except ImportError:
    # Search dependencies not installed, provide base functionality only
    __all__ = []
