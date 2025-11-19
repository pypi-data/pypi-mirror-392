# Architecture Design: ChromaDB Persistent Storage Migration

## Executive Summary

This document provides a comprehensive architectural design for migrating the ZK Documentation MCP Server from ChromaDB's ephemeral in-memory `Client` to the `PersistentClient` for durable storage. This migration enables documentation indices to persist across server restarts, eliminating the need to re-index documentation on every startup.

**Key Changes:**
- Migrate from `chromadb.Client()` to `chromadb.PersistentClient(path="...")`
- Introduce persistent storage location configuration
- Add initialization logic to handle existing vs. new indices
- Implement index version management for future migrations
- Maintain backward compatibility during transition

**Impact:** Low-risk change with significant operational benefits. No breaking changes to public API.

---

## 1. System Overview

### 1.1 Current Architecture

```
┌─────────────────────────────────────────────────────────┐
│  ZK Documentation MCP Server (server.py)                │
│  - Starts up and calls index_documentation()            │
│  - Creates DocIndexer with doc_path                     │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  DocIndexer (doc_indexer.py)                            │
│  - Initializes chromadb.Client() [IN-MEMORY]            │
│  - Walks doc_path and indexes all .md files             │
│  - Stores embeddings in ephemeral collection            │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  ChromaDB In-Memory Storage                             │
│  - Lives only during server process lifetime            │
│  - Lost on server restart                               │
│  - No filesystem footprint                              │
└─────────────────────────────────────────────────────────┘
```

**Problems:**
1. Documentation must be re-indexed on every server startup
2. Indexing time increases linearly with documentation size
3. No persistence of embeddings across restarts
4. Resource waste re-computing identical embeddings

### 1.2 Target Architecture

```
┌─────────────────────────────────────────────────────────┐
│  ZK Documentation MCP Server (server.py)                │
│  - Starts up and calls index_documentation()            │
│  - Creates DocIndexer with doc_path + persist_dir       │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  DocIndexer (doc_indexer.py)                            │
│  - Initializes chromadb.PersistentClient(path=...)      │
│  - Checks if index exists and is current                │
│  - Conditionally re-indexes only if needed              │
│  - Stores embeddings in persistent collection           │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  ChromaDB Persistent Storage                            │
│  - Stored at: ~/.zk-doc-mcp/chromadb/                   │
│  - Survives server restarts                             │
│  - Automatically loaded on startup                      │
│  - Platform-independent location                        │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
1. Instant startup for already-indexed documentation
2. Persistent embeddings across restarts
3. Incremental indexing capability (future enhancement)
4. Reduced computational overhead

---

## 2. Architecture Components

### 2.1 Storage Location Design

#### 2.1.1 Proposed Storage Path

**Primary Location:** `~/.zk-doc-mcp/chromadb/`

**Rationale:**
- **User-specific:** Uses home directory for user-level isolation
- **Hidden directory:** Follows Unix convention (dot-prefix) for application data
- **Platform-independent:** Works on macOS, Linux, Windows
- **Non-intrusive:** Outside project directory, won't be committed to git
- **Standard practice:** Aligns with tools like `.config/`, `.cache/`

**Expanded Path Examples:**
- macOS: `/Users/hawk/.zk-doc-mcp/chromadb/`
- Linux: `/home/username/.zk-doc-mcp/chromadb/`
- Windows: `C:\Users\Username\.zk-doc-mcp\chromadb\`

#### 2.1.2 Directory Structure

```
~/.zk-doc-mcp/
├── chromadb/              # ChromaDB persistent storage
│   ├── chroma.sqlite3     # ChromaDB metadata database
│   └── [internal files]   # ChromaDB managed files
├── config.json            # Future: user configuration
└── logs/                  # Future: application logs
```

#### 2.1.3 Alternative Locations Considered

| Location | Pros | Cons | Decision |
|----------|------|------|----------|
| Project directory `./data/chromadb/` | Simple, relative paths | Gets committed to git, not user-specific | **Rejected** |
| System temp directory | Auto-cleanup | Lost on reboot, defeats persistence | **Rejected** |
| XDG Base Directory `~/.local/share/zk-doc-mcp/` | Linux standard | Less intuitive on macOS/Windows | **Alternative** |
| `~/.zk-doc-mcp/chromadb/` | Cross-platform, hidden, intuitive | Slightly non-standard on Linux | **Selected** |

### 2.2 Configuration Management

#### 2.2.1 Configuration Approach

**Strategy:** Environment variables with sensible defaults

**Configuration Parameters:**

```python
# Environment variable: ZK_DOC_PERSIST_DIR
# Default: ~/.zk-doc-mcp/chromadb/
# Purpose: Override persistent storage location

# Environment variable: ZK_DOC_PATH
# Default: /Users/hawk/Documents/workspace/DOC/zkdoc/get_started
# Purpose: Documentation source directory
```

**Implementation:**

```python
import os
from pathlib import Path

def get_persist_dir() -> Path:
    """Get ChromaDB persistence directory with fallback."""
    default_dir = Path.home() / ".zk-doc-mcp" / "chromadb"
    persist_dir = os.getenv("ZK_DOC_PERSIST_DIR", str(default_dir))
    return Path(persist_dir)

def get_doc_path() -> Path:
    """Get documentation source path from environment or default."""
    default_path = "/Users/hawk/Documents/workspace/DOC/zkdoc/get_started"
    doc_path = os.getenv("ZK_DOC_PATH", default_path)
    return Path(doc_path)
```

#### 2.2.2 Future Configuration File Support

**File Location:** `~/.zk-doc-mcp/config.json`

**Schema (Future):**

```json
{
  "version": "1.0",
  "storage": {
    "persist_dir": "~/.zk-doc-mcp/chromadb/",
    "max_storage_mb": 1000
  },
  "indexing": {
    "doc_path": "/path/to/docs",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "auto_reindex": true
  },
  "embedding": {
    "model": "all-MiniLM-L6-v2",
    "device": "cpu"
  }
}
```

**Note:** Configuration file support is not part of this initial migration but is documented here for future extensibility.

---

## 3. Data Architecture

### 3.1 ChromaDB Collection Schema

**Collection Name:** `zk_docs` (unchanged)

**Document Structure:**

```python
{
    "id": str,              # Format: "{file_path}-{chunk_index}"
    "embedding": List[float],  # 384-dimensional vector (all-MiniLM-L6-v2)
    "document": str,        # Text chunk content
    "metadata": {
        "source": str,      # Absolute file path
        "indexed_at": str,  # ISO timestamp (new field)
        "doc_hash": str     # File content hash (future: incremental indexing)
    }
}
```

**Changes from Current:**
- **Added:** `indexed_at` timestamp for tracking index freshness
- **Future:** `doc_hash` for detecting changed files

### 3.2 Index Versioning Strategy

**Purpose:** Handle schema changes, model upgrades, and migrations

**Metadata Storage:** Use ChromaDB collection metadata

```python
collection_metadata = {
    "schema_version": "1.0",
    "embedding_model": "all-MiniLM-L6-v2",
    "created_at": "2025-11-13T10:00:00Z",
    "last_updated": "2025-11-13T10:30:00Z"
}

collection = client.get_or_create_collection(
    name="zk_docs",
    metadata=collection_metadata
)
```

**Version Compatibility Logic:**

```python
def is_index_compatible(collection) -> bool:
    """Check if existing index is compatible with current code."""
    metadata = collection.metadata or {}
    current_version = "1.0"
    current_model = "all-MiniLM-L6-v2"

    stored_version = metadata.get("schema_version")
    stored_model = metadata.get("embedding_model")

    if stored_version != current_version:
        return False
    if stored_model != current_model:
        return False

    return True
```

### 3.3 Data Migration Strategy

**Initial Migration (v0 → v1):**
- No existing persistent data
- Simply create new persistent storage
- No migration logic needed

**Future Migrations:**
1. Detect version mismatch
2. Log migration requirement
3. Optionally backup old index
4. Re-index with new schema/model
5. Update metadata version

---

## 4. API Design

### 4.1 DocIndexer Class Changes

#### 4.1.1 Updated Constructor

```python
class DocIndexer:
    """Document indexer using ChromaDB for vector search.

    Requires optional dependencies: chromadb, sentence-transformers
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

        # Initialize embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _get_or_create_collection(self):
        """Get existing collection or create new one with metadata."""
        from datetime import datetime

        metadata = {
            "schema_version": "1.0",
            "embedding_model": "all-MiniLM-L6-v2",
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }

        if self.force_reindex:
            # Delete existing collection if exists
            try:
                self.client.delete_collection(name=self.collection_name)
                print(f"Deleted existing collection: {self.collection_name}")
            except ValueError:
                pass  # Collection doesn't exist

        collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata=metadata
        )

        return collection
```

#### 4.1.2 Enhanced index_docs() Method

```python
def index_docs(self):
    """Index all markdown files from doc_path."""
    from datetime import datetime

    # Check if collection is empty
    collection_count = self.collection.count()

    if collection_count > 0 and not self.force_reindex:
        print(f"Collection '{self.collection_name}' already contains "
              f"{collection_count} documents.")
        print("Skipping indexing. Use force_reindex=True to rebuild.")
        return

    print(f"Starting indexing of files from: {self.doc_path}")
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
                    print(f"Error indexing {file_path}: {e}")

    # Update collection metadata
    self.collection.modify(
        metadata={
            **self.collection.metadata,
            "last_updated": datetime.utcnow().isoformat(),
            "indexed_files": indexed_files,
            "indexed_chunks": indexed_chunks
        }
    )

    print(f"Indexing complete: {indexed_files} files, {indexed_chunks} chunks")
```

#### 4.1.3 Enhanced _embed_and_store() Method

```python
def _embed_and_store(self, chunks, file_path):
    """Embed and store document chunks with metadata."""
    from datetime import datetime

    embeddings = self.model.encode(chunks)
    documents = chunks
    metadatas = [
        {
            "source": file_path,
            "indexed_at": datetime.utcnow().isoformat()
        }
        for _ in chunks
    ]
    ids = [f"{file_path}-{i}" for i in range(len(chunks))]

    self.collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
```

#### 4.1.4 New Utility Methods

```python
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
        "embedding_model": metadata.get("embedding_model"),
        "created_at": metadata.get("created_at"),
        "last_updated": metadata.get("last_updated"),
        "indexed_files": metadata.get("indexed_files"),
        "indexed_chunks": metadata.get("indexed_chunks")
    }

def reset_index(self):
    """Delete all documents from the collection."""
    self.client.delete_collection(name=self.collection_name)
    print(f"Collection '{self.collection_name}' deleted.")
    self.collection = self._get_or_create_collection()
    print(f"Collection '{self.collection_name}' recreated.")
```

### 4.2 Server Integration Changes

#### 4.2.1 Updated index_documentation() Function

```python
def index_documentation():
    """Index ZK documentation from configured path."""
    from pathlib import Path
    import os

    # Get configuration from environment or defaults
    doc_path = os.getenv(
        "ZK_DOC_PATH",
        "/Users/hawk/Documents/workspace/DOC/zkdoc/get_started"
    )
    persist_dir = os.getenv(
        "ZK_DOC_PERSIST_DIR",
        str(Path.home() / ".zk-doc-mcp" / "chromadb")
    )
    force_reindex = os.getenv("ZK_DOC_FORCE_REINDEX", "false").lower() == "true"

    try:
        from .doc_indexer import DocIndexer

        indexer = DocIndexer(
            doc_path=doc_path,
            persist_dir=persist_dir,
            force_reindex=force_reindex
        )

        # Get index info
        info = indexer.get_index_info()
        print(f"Index info: {info}")

        # Index documents (will skip if already indexed)
        indexer.index_docs()

    except ImportError as e:
        print(f"Search dependencies not available: {e}")
        print("To enable search, install: pip install zk-doc-mcp-server[search]")
    except FileNotFoundError:
        print(f"Documentation path not found: {doc_path}")
        print("Skipping documentation indexing.")
    except Exception as e:
        print(f"Error indexing documentation: {e}")
        import traceback
        traceback.print_exc()
```

### 4.3 Backward Compatibility

**Guarantee:** Existing code using `DocIndexer(doc_path)` continues to work without modification.

**Compatibility Matrix:**

| Usage Pattern | Status | Notes |
|---------------|--------|-------|
| `DocIndexer(doc_path)` | ✅ Compatible | Uses default persistent location |
| `DocIndexer(doc_path, collection_name)` | ✅ Compatible | Uses default persistent location |
| `DocIndexer(doc_path, persist_dir=None)` | ✅ Compatible | Explicit None uses default |
| `DocIndexer(doc_path, persist_dir="/custom/path")` | ✅ New Feature | Custom location |

**No Breaking Changes:** All existing constructor calls work identically, now with persistence.

---

## 5. Security Design

### 5.1 File System Security

#### 5.1.1 Directory Permissions

**Unix/Linux/macOS:**
```python
persist_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
# Ensures only owner can read/write/execute
```

**Rationale:**
- Documentation indices may contain proprietary information
- Restrict access to creating user only
- Standard practice for user data directories

#### 5.1.2 Path Validation

```python
def validate_persist_dir(persist_dir: Path) -> None:
    """Validate persistence directory for security."""
    # Resolve to absolute path, prevent path traversal
    persist_dir = persist_dir.resolve()

    # Prevent writing to sensitive system directories
    forbidden_paths = [
        Path("/etc"),
        Path("/sys"),
        Path("/proc"),
        Path("/dev"),
        Path("/"),
        Path("/System"),  # macOS
    ]

    for forbidden in forbidden_paths:
        if persist_dir.is_relative_to(forbidden):
            raise ValueError(
                f"Cannot use persistence directory under {forbidden}"
            )

    # Ensure path is within user's home or explicitly allowed locations
    home = Path.home()
    allowed_roots = [home, Path("/var/lib"), Path("/opt")]

    if not any(persist_dir.is_relative_to(root) for root in allowed_roots):
        print(f"Warning: Unusual persistence directory: {persist_dir}")
```

### 5.2 Data Privacy

**Concerns:**
1. Documentation content stored in plaintext (ChromaDB limitation)
2. Embeddings stored in plaintext
3. No encryption at rest

**Mitigations:**
1. File system permissions (0o700)
2. User-level isolation (home directory)
3. Clear documentation of privacy limitations

**Future Enhancements:**
- Option for encrypted ChromaDB storage
- Secure deletion of indices
- Data retention policies

### 5.3 Environment Variable Security

**Risk:** Sensitive paths in environment variables

**Best Practices:**
```bash
# Good: Relative to home
export ZK_DOC_PERSIST_DIR="~/.zk-doc-mcp/chromadb"

# Good: Absolute path to safe location
export ZK_DOC_PERSIST_DIR="/opt/zk-doc-mcp/data"

# Bad: Exposes internal paths
export ZK_DOC_PERSIST_DIR="/Users/hawk/secret-docs/data"
```

---

## 6. Scalability & Performance

### 6.1 Performance Characteristics

#### 6.1.1 Startup Performance

**Before (In-Memory):**
```
Server Start → Index All Docs → Ready
Time: O(n) where n = number of documents
Typical: 30-60 seconds for 1000 documents
```

**After (Persistent):**
```
Server Start → Load Existing Index → Ready
Time: O(1) - constant time
Typical: 1-2 seconds
```

**Performance Gain:** 15-30x faster startup for indexed documentation

#### 6.1.2 Storage Requirements

**Per Document:**
- Original text: ~2-5 KB
- Embeddings (384 dims × 4 bytes): ~1.5 KB per chunk
- Metadata: ~0.5 KB per chunk
- **Total:** ~4-7 KB per chunk

**Estimation Formula:**
```
Storage (MB) = (num_files × avg_file_size_kb / chunk_size_kb) × 6 KB
```

**Example:**
- 1000 markdown files
- Average file size: 10 KB
- Chunk size: 1000 chars ≈ 1 KB
- Chunks per file: 10
- Total chunks: 10,000
- **Storage:** 10,000 × 6 KB = 60 MB

#### 6.1.3 Query Performance

**Impact:** None - query performance unchanged by persistence

**Query Path:**
```
Query → Embedding → Vector Search → Results
Time: O(log n) with ChromaDB indexing
```

### 6.2 Scalability Considerations

#### 6.2.1 Storage Scaling

| Documentation Size | Estimated Storage | Notes |
|-------------------|-------------------|-------|
| Small (100 files) | ~6 MB | Single user, quick iteration |
| Medium (1000 files) | ~60 MB | Typical framework documentation |
| Large (10,000 files) | ~600 MB | Enterprise documentation |
| Very Large (100,000 files) | ~6 GB | Multi-product documentation |

**Recommended Limits:**
- Soft limit: 10,000 files (600 MB)
- Hard limit: 100,000 files (6 GB)
- Beyond: Consider client-server ChromaDB deployment

#### 6.2.2 Index Update Strategy

**Current Implementation:** Full reindex

**Future Optimization:** Incremental indexing

```python
def index_docs_incremental(self):
    """Index only new or modified documents."""
    # Pseudo-code for future implementation
    for file_path in self._get_markdown_files():
        current_hash = self._hash_file(file_path)
        stored_hash = self._get_stored_hash(file_path)

        if current_hash != stored_hash:
            # File is new or modified
            self._remove_file_from_index(file_path)
            self._index_file(file_path, current_hash)
```

**Implementation Complexity:** Medium (requires hash storage and tracking)

**Priority:** Low (optimize if users report slow re-indexing)

### 6.3 Resource Management

#### 6.3.1 Memory Usage

**PersistentClient Memory:** ~50-100 MB baseline (ChromaDB + SQLite)

**Indexing Memory:** Peaks at embedding batch size
```
Memory = batch_size × embedding_dim × 4 bytes
Example: 100 chunks × 384 dims × 4 = ~150 KB per batch
```

**Total Memory During Indexing:** ~150-200 MB

#### 6.3.2 Disk I/O

**Indexing I/O Pattern:**
- Sequential writes to SQLite database
- Batch inserts minimize write amplification
- No random I/O during indexing

**Query I/O Pattern:**
- Index-backed lookups (B-tree)
- Minimal disk reads due to caching

#### 6.3.3 Cleanup and Maintenance

```python
def cleanup_old_indices(persist_dir: Path, keep_days: int = 30):
    """Remove indices older than specified days (future utility)."""
    # Pseudo-code
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    # Check collection metadata timestamps
    # Delete collections older than cutoff
```

---

## 7. Implementation Phases

### Phase 1: Core Persistence Migration (Priority: High)

**Objective:** Replace in-memory client with persistent client

**Tasks:**
1. Update `DocIndexer.__init__()` to accept `persist_dir` parameter
2. Implement default persistence directory logic (`~/.zk-doc-mcp/chromadb/`)
3. Replace `chromadb.Client()` with `chromadb.PersistentClient(path=...)`
4. Add directory creation logic with proper permissions
5. Update `server.py` to pass persistence configuration

**Deliverables:**
- Modified `doc_indexer.py` with PersistentClient
- Modified `server.py` with persistence configuration
- Unit tests for persistence initialization

**Success Criteria:**
- Server starts and loads existing index
- New indices persist across restarts
- No breaking changes to existing API

**Effort Estimate:** ~4 hours development, ~2 hours testing

---

### Phase 2: Index Management Features (Priority: Medium)

**Objective:** Add index introspection and management capabilities

**Tasks:**
1. Add `get_index_info()` method to DocIndexer
2. Add `reset_index()` method for manual re-indexing
3. Implement collection metadata (schema version, timestamps)
4. Add skip logic if collection already populated
5. Add `force_reindex` parameter to override skip logic

**Deliverables:**
- Enhanced DocIndexer with management methods
- Collection metadata tracking
- Smart indexing that skips already-indexed docs

**Success Criteria:**
- `get_index_info()` returns accurate statistics
- `reset_index()` cleanly deletes and recreates collection
- Server skips indexing on subsequent starts

**Effort Estimate:** ~3 hours development, ~2 hours testing

---

### Phase 3: Configuration & Environment Variables (Priority: Medium)

**Objective:** Allow users to customize persistence behavior

**Tasks:**
1. Implement environment variable support (`ZK_DOC_PERSIST_DIR`)
2. Implement environment variable for doc path (`ZK_DOC_PATH`)
3. Add environment variable for force reindex (`ZK_DOC_FORCE_REINDEX`)
4. Add path validation and security checks
5. Document environment variables in README

**Deliverables:**
- Environment variable configuration support
- Path validation utilities
- Updated README with configuration instructions

**Success Criteria:**
- Users can override default persistence directory
- Invalid paths are rejected with clear error messages
- Configuration is documented

**Effort Estimate:** ~2 hours development, ~1 hour documentation

---

### Phase 4: Enhanced Metadata & Timestamps (Priority: Low)

**Objective:** Track detailed indexing metadata for future features

**Tasks:**
1. Add `indexed_at` timestamp to document metadata
2. Add `indexed_files` and `indexed_chunks` to collection metadata
3. Update `_embed_and_store()` to include timestamps
4. Implement metadata update after indexing complete

**Deliverables:**
- Timestamped document metadata
- Collection-level statistics
- Foundation for incremental indexing

**Success Criteria:**
- All indexed documents have `indexed_at` timestamp
- Collection metadata reflects accurate statistics
- Metadata survives restarts

**Effort Estimate:** ~2 hours development, ~1 hour testing

---

### Phase 5: Testing & Documentation (Priority: High)

**Objective:** Ensure reliability and usability of persistence features

**Tasks:**
1. Write unit tests for PersistentClient initialization
2. Write integration tests for index persistence across restarts
3. Test with different persistence directories
4. Test error handling (permissions, disk full, etc.)
5. Update README with persistence documentation
6. Create troubleshooting guide for common issues

**Deliverables:**
- Comprehensive test suite
- Updated README
- Troubleshooting documentation

**Success Criteria:**
- Test coverage > 80%
- All critical paths tested
- Documentation covers common scenarios

**Effort Estimate:** ~4 hours testing, ~2 hours documentation

---

### Phase 6: Future Enhancements (Priority: Low - Out of Scope)

**Objective:** Incremental indexing and advanced features

**Tasks (Future):**
1. Implement file hashing for change detection
2. Implement incremental indexing
3. Add index versioning and migration logic
4. Add configuration file support (`~/.zk-doc-mcp/config.json`)
5. Implement index cleanup utilities
6. Add telemetry for index usage

**Note:** These features are not part of the initial migration but provide a roadmap for future development.

---

## 8. Technical Risks & Mitigations

### Risk 1: Disk Space Exhaustion

**Probability:** Low
**Impact:** Medium

**Description:** Persistent indices consume disk space indefinitely if not managed.

**Mitigation:**
1. Document typical storage requirements in README
2. Add warning if collection size exceeds threshold (future: 1 GB)
3. Provide `reset_index()` method for manual cleanup
4. Future: Implement automatic cleanup of old indices

**Acceptance:** Low priority - users can manually delete `~/.zk-doc-mcp/` if needed

---

### Risk 2: Corrupted Index Data

**Probability:** Low
**Impact:** High

**Description:** ChromaDB storage corruption could prevent server startup.

**Mitigation:**
1. Add try-except around PersistentClient initialization
2. Detect corrupted indices and log clear error message
3. Provide automatic fallback: delete corrupted index and rebuild
4. Document manual recovery process

**Implementation:**
```python
try:
    self.client = chromadb.PersistentClient(path=str(persist_dir))
except Exception as e:
    print(f"Failed to load persistent index: {e}")
    print("Attempting to rebuild index...")
    shutil.rmtree(persist_dir, ignore_errors=True)
    persist_dir.mkdir(parents=True, exist_ok=True)
    self.client = chromadb.PersistentClient(path=str(persist_dir))
```

---

### Risk 3: Permission Denied Errors

**Probability:** Medium
**Impact:** Medium

**Description:** User lacks write permissions to default persistence directory.

**Mitigation:**
1. Check write permissions before creating directory
2. Provide clear error message with troubleshooting steps
3. Document alternative persistence locations
4. Support `ZK_DOC_PERSIST_DIR` environment variable

**Implementation:**
```python
def ensure_writable(persist_dir: Path) -> None:
    """Ensure persistence directory is writable."""
    persist_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Test write permissions
    test_file = persist_dir / ".write_test"
    try:
        test_file.touch()
        test_file.unlink()
    except PermissionError as e:
        raise PermissionError(
            f"Cannot write to persistence directory: {persist_dir}\n"
            f"Set ZK_DOC_PERSIST_DIR to a writable location."
        ) from e
```

---

### Risk 4: Cross-Platform Path Issues

**Probability:** Low
**Impact:** Low

**Description:** Path handling differences between Windows/Unix cause failures.

**Mitigation:**
1. Use `pathlib.Path` throughout for cross-platform compatibility
2. Test on Windows, macOS, Linux (at minimum macOS for current deployment)
3. Document platform-specific considerations
4. Use `Path.home()` for portable home directory detection

**Validation:**
```python
# Cross-platform path handling
persist_dir = Path.home() / ".zk-doc-mcp" / "chromadb"
# Works on Windows: C:\Users\User\.zk-doc-mcp\chromadb
# Works on macOS: /Users/user/.zk-doc-mcp/chromadb
# Works on Linux: /home/user/.zk-doc-mcp/chromadb
```

---

### Risk 5: Schema Version Incompatibility

**Probability:** Low (Future Risk)
**Impact:** High

**Description:** Future changes to embedding model or schema break existing indices.

**Mitigation:**
1. Implement schema versioning from day one
2. Store embedding model name in collection metadata
3. Check compatibility on startup
4. Auto-rebuild if incompatible (with user confirmation)

**Current Implementation:** Schema version "1.0" with `all-MiniLM-L6-v2` model

**Future Enhancement:** Migration utilities for version upgrades

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
# test_doc_indexer_persistence.py

def test_persistent_client_initialization():
    """Test PersistentClient is created with correct path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        indexer = DocIndexer(
            doc_path="/tmp/docs",
            persist_dir=tmpdir
        )
        assert isinstance(indexer.client, chromadb.PersistentClient)

def test_default_persistence_directory():
    """Test default persistence directory uses home directory."""
    indexer = DocIndexer(doc_path="/tmp/docs")
    expected = Path.home() / ".zk-doc-mcp" / "chromadb"
    # Verify directory was created
    assert expected.exists()

def test_index_survives_restart():
    """Test that indexed documents persist across DocIndexer instances."""
    with tempfile.TemporaryDirectory() as persist_dir:
        # First instance: index documents
        indexer1 = DocIndexer(
            doc_path="test/fixtures/docs",
            persist_dir=persist_dir
        )
        indexer1.index_docs()
        count1 = indexer1.collection.count()

        # Second instance: load existing index
        indexer2 = DocIndexer(
            doc_path="test/fixtures/docs",
            persist_dir=persist_dir
        )
        count2 = indexer2.collection.count()

        assert count1 == count2
        assert count2 > 0

def test_force_reindex():
    """Test force_reindex deletes and rebuilds collection."""
    with tempfile.TemporaryDirectory() as persist_dir:
        # Index documents
        indexer1 = DocIndexer(
            doc_path="test/fixtures/docs",
            persist_dir=persist_dir
        )
        indexer1.index_docs()

        # Force reindex
        indexer2 = DocIndexer(
            doc_path="test/fixtures/docs",
            persist_dir=persist_dir,
            force_reindex=True
        )
        indexer2.index_docs()

        # Should have same count (re-indexed)
        assert indexer2.collection.count() == indexer1.collection.count()

def test_get_index_info():
    """Test index info returns accurate metadata."""
    with tempfile.TemporaryDirectory() as persist_dir:
        indexer = DocIndexer(
            doc_path="test/fixtures/docs",
            persist_dir=persist_dir
        )
        indexer.index_docs()

        info = indexer.get_index_info()
        assert info["collection_name"] == "zk_docs"
        assert info["document_count"] > 0
        assert info["schema_version"] == "1.0"
        assert info["embedding_model"] == "all-MiniLM-L6-v2"

def test_reset_index():
    """Test reset_index deletes all documents."""
    with tempfile.TemporaryDirectory() as persist_dir:
        indexer = DocIndexer(
            doc_path="test/fixtures/docs",
            persist_dir=persist_dir
        )
        indexer.index_docs()
        assert indexer.collection.count() > 0

        indexer.reset_index()
        assert indexer.collection.count() == 0
```

### 9.2 Integration Tests

```python
def test_server_loads_persistent_index():
    """Test server.py loads existing persistent index."""
    # Set environment variables
    os.environ["ZK_DOC_PATH"] = "test/fixtures/docs"
    os.environ["ZK_DOC_PERSIST_DIR"] = "/tmp/test_persist"

    # First startup: index documents
    index_documentation()

    # Second startup: should skip indexing
    # Capture stdout to verify skip message
    import io, sys
    captured = io.StringIO()
    sys.stdout = captured

    index_documentation()

    output = captured.getvalue()
    assert "already contains" in output or "Skipping indexing" in output
```

### 9.3 Error Handling Tests

```python
def test_permission_error_handling():
    """Test graceful handling of permission denied errors."""
    with pytest.raises(PermissionError):
        indexer = DocIndexer(
            doc_path="/tmp/docs",
            persist_dir="/root/.zk-doc-mcp"  # Typically not writable
        )

def test_corrupted_index_recovery():
    """Test recovery from corrupted ChromaDB index."""
    # Create valid index
    # Corrupt SQLite database
    # Attempt to load
    # Verify automatic rebuild
    pass  # Implementation depends on corruption simulation
```

---

## 10. Deployment Considerations

### 10.1 Development Environment

**No Changes Required:**
- `uv pip install -e ".[search]"` continues to work
- Development workflow unchanged
- Tests run in isolated temporary directories

**Environment Setup:**
```bash
# Optional: Override default persistence directory for testing
export ZK_DOC_PERSIST_DIR="/tmp/zk-doc-mcp-dev"
export ZK_DOC_PATH="$(pwd)/test/fixtures/docs"

uv run python -m zk_doc_mcp
```

### 10.2 Production Deployment

**Claude Desktop Configuration:**

```json
{
  "mcpServers": {
    "zk-doc": {
      "command": "uvx",
      "args": ["zk-doc-mcp-server"],
      "env": {
        "ZK_DOC_PATH": "/path/to/zk/documentation",
        "ZK_DOC_PERSIST_DIR": "~/.zk-doc-mcp/chromadb"
      }
    }
  }
}
```

**First-Time Setup:**
1. Install server: `uvx zk-doc-mcp-server`
2. Configure path in Claude Desktop config
3. Restart Claude Desktop
4. Server auto-indexes on first start (30-60 seconds)
5. Subsequent starts are instant (<2 seconds)

**Updating Documentation:**
```bash
# Option 1: Environment variable (one-time reindex)
ZK_DOC_FORCE_REINDEX=true uv run python -m zk_doc_mcp

# Option 2: Delete persistence directory (manual)
rm -rf ~/.zk-doc-mcp/chromadb
# Next startup will auto-reindex

# Option 3: Python API (programmatic)
from zk_doc_mcp.doc_indexer import DocIndexer
indexer = DocIndexer(doc_path="/path/to/docs", force_reindex=True)
indexer.index_docs()
```

### 10.3 Migration from In-Memory to Persistent

**User Impact:** None - automatic migration on upgrade

**Migration Steps:**
1. User upgrades to new version with persistence
2. Server starts, creates `~/.zk-doc-mcp/chromadb/`
3. Indexes documentation (first-time only)
4. Subsequent starts use persistent index

**Rollback Plan:**
1. Downgrade to previous version
2. In-memory client continues to work
3. Persistent directory ignored but harmless
4. No data loss (can manually delete `~/.zk-doc-mcp/`)

---

## 11. Documentation Updates

### 11.1 README Changes

**Section: "Quick Start" - Add Note:**

```markdown
### First Startup

On first startup, the server will index your documentation and create a persistent index at `~/.zk-doc-mcp/chromadb/`. This initial indexing may take 30-60 seconds depending on documentation size. Subsequent startups will be instant as they reuse the persistent index.

To force re-indexing (after updating documentation):
```bash
ZK_DOC_FORCE_REINDEX=true uv run python -m zk_doc_mcp
```
```

**Section: "Configuration" - Add New Section:**

```markdown
### Configuration

The server can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ZK_DOC_PATH` | `(see config)` | Path to ZK documentation directory |
| `ZK_DOC_PERSIST_DIR` | `~/.zk-doc-mcp/chromadb/` | Persistent index storage location |
| `ZK_DOC_FORCE_REINDEX` | `false` | Force re-indexing on startup |

Example:
```bash
export ZK_DOC_PATH="/path/to/zk/docs"
export ZK_DOC_PERSIST_DIR="/opt/zk-doc-mcp/data"
uv run python -m zk_doc_mcp
```
```

### 11.2 Troubleshooting Guide

**Add to README - "Troubleshooting" Section:**

```markdown
### Persistent Index Issues

**Problem:** Index seems outdated or corrupted

**Solution:** Force re-indexing:
```bash
rm -rf ~/.zk-doc-mcp/chromadb
uv run python -m zk_doc_mcp
```

**Problem:** Permission denied when creating index

**Solution:** Set a writable persistence directory:
```bash
export ZK_DOC_PERSIST_DIR="/tmp/zk-doc-mcp"
uv run python -m zk_doc_mcp
```

**Problem:** Disk space warning

**Solution:** Delete old indices:
```bash
rm -rf ~/.zk-doc-mcp/chromadb
```

Index will be rebuilt on next startup.
```

---

## 12. Appendix

### 12.1 ChromaDB PersistentClient Reference

**Official Documentation:** https://docs.trychroma.com/docs/run-chroma/persistent-client

**Key Methods:**

```python
import chromadb

# Initialize PersistentClient
client = chromadb.PersistentClient(path="/path/to/data")

# Create/get collection
collection = client.get_or_create_collection(name="my_collection")

# Add documents
collection.add(
    embeddings=[[1.2, 2.3, ...]],
    documents=["doc content"],
    metadatas=[{"key": "value"}],
    ids=["id1"]
)

# Query
results = collection.query(
    query_embeddings=[[1.2, 2.3, ...]],
    n_results=10
)

# Utility methods
client.heartbeat()  # Returns nanosecond heartbeat
client.list_collections()  # List all collections
client.delete_collection(name="my_collection")  # Delete collection
client.reset()  # ⚠️ Delete all data
```

### 12.2 File Path Reference

**Project Files to Modify:**

1. `/Users/hawk/Documents/workspace/DOC/zk-doc-mcp/src/zk_doc_mcp/doc_indexer.py`
   - Update `__init__()` method
   - Update `index_docs()` method
   - Update `_embed_and_store()` method
   - Add `get_index_info()` method
   - Add `reset_index()` method

2. `/Users/hawk/Documents/workspace/DOC/zk-doc-mcp/src/zk_doc_mcp/server.py`
   - Update `index_documentation()` function
   - Add environment variable handling

3. `/Users/hawk/Documents/workspace/DOC/zk-doc-mcp/README.md`
   - Add configuration section
   - Add troubleshooting section
   - Update quick start guide

4. `/Users/hawk/Documents/workspace/DOC/zk-doc-mcp/src/test/test_doc_indexer.py`
   - Add persistence tests
   - Add integration tests

### 12.3 Code Examples Summary

**Minimal Migration (Just Persistence):**

```python
# Before
self.client = chromadb.Client()

# After
persist_dir = Path.home() / ".zk-doc-mcp" / "chromadb"
persist_dir.mkdir(parents=True, exist_ok=True)
self.client = chromadb.PersistentClient(path=str(persist_dir))
```

**Full Featured Implementation:**

See Section 4.1 for complete implementation with all features.

### 12.4 Glossary

- **PersistentClient:** ChromaDB client that saves data to disk
- **Collection:** Named container for documents and embeddings in ChromaDB
- **Embedding:** Numerical vector representation of text (384 dimensions for all-MiniLM-L6-v2)
- **Chunk:** Segment of document text (default: 1000 characters with 200 overlap)
- **Index:** Complete set of document chunks and embeddings in ChromaDB
- **Schema Version:** Version identifier for index structure and format

---

## Summary

This architecture design provides a complete blueprint for migrating the ZK Documentation MCP Server from ephemeral in-memory ChromaDB storage to persistent disk-based storage. The design prioritizes:

1. **Simplicity:** Minimal code changes, sensible defaults
2. **Backward Compatibility:** No breaking changes to existing API
3. **User Experience:** Faster startups, persistent indices
4. **Security:** Proper file permissions, path validation
5. **Extensibility:** Foundation for future enhancements

The implementation can be completed in phases, with the core persistence migration delivering immediate value. The engineering team has all necessary details to begin implementation without additional architectural decisions.

**Next Steps:**
1. Review this architecture design
2. Approve storage location and configuration approach
3. Implement Phase 1 (core persistence migration)
4. Test with real ZK documentation
5. Deploy and gather user feedback