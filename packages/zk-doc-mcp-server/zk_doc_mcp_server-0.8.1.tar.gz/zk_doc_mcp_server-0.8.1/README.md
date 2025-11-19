# ZK Documentation MCP Server

An MCP (Model Context Protocol) server for the ZK Framework documentation that provides semantic search, intelligent Q&A, and documentation indexing capabilities.

## Overview

This server integrates ChromaDB for vector-based semantic search and implements MCP tools for:
- Searching ZK documentation
- Retrieving specific documentation content
- Answering questions based on documentation
- Managing documentation indices
- Browsing documentation categories

## Quick Start

### Prerequisites
Your environment should have the following installed:
- Python 3.10 or higher
- `uv` package manager (https://docs.astral.sh/uv/) - optional but recommended
- **Git** (2.7 or higher) - Required for automatic documentation synchronization


### Installation zk doc MCP server from PyPI

```bash
# Using uv (recommended)
uv pip install zk-doc-mcp-server

# Using pip
pip install zk-doc-mcp-server
```

The package is available at:
- **PyPI (production)**: https://pypi.org/project/zk-doc-mcp-server/

### Using with Claude Code
The easiest way to use this MCP server is through Claude Code or Gemini CLI.
1. Add the ZK Documentation MCP server:
```bash
claude mcp add zk-doc -- uvx zk-doc-mcp-server
```

2. Start using it in Claude Code:
```
Search the ZK doc for "what is desktop"
```

Claude Code will automatically use the ZK documentation MCP server to search and retrieve information.

### Using with Gemini CLI

1. Add the MCP server to your Gemini configuration file (typically `~/.gemini/config.json` or similar):
```json
{
  "mcpServers": {
    "zk-doc": {
      "command": "uvx",
      "args": ["zk-doc-mcp-server"]
    }
  }
}
```

3. Start using it:
```
Ask the zk-doc server about ZK Framework components
```

## MCP Tools

### search_zk_docs
Search ZK documentation for relevant content using semantic search.

**Parameters:**
- `query` (string, required): Search query
- `limit` (integer, optional, default: 5): Maximum results to return (1-20)

**Response:**
```json
{
  "results": [],
  "query": "your search query",
  "limit": 5,
  "message": "Search functionality coming soon"
}
```

### submit_feedback
Submit feedback about search results to improve documentation.

When search results don't meet user expectations, this tool captures feedback that helps the documentation team understand gaps and improve content.

**Parameters:**
- `query` (string, required): The search query that produced unsatisfactory results
- `results` (list, required): List of search results returned (each with title, file_path, content)
- `expected` (string, required): What the user expected to find
- `comments` (string, optional): Additional context about why results don't match

**Features:**
- Feedback is **always saved locally** to `~/.zk-doc-mcp/feedback/`
- Automatically **submitted as GitHub issue** to https://github.com/zkoss/zkdoc/issues
- **Non-blocking operation** - returns immediately while GitHub submission happens in background
- **Graceful fallback** - feedback is preserved locally if network fails

**Response:**
```json
{
  "success": true,
  "feedback_id": "feedback_20250114_a7k9m2x8",
  "local_path": "/home/user/.zk-doc-mcp/feedback/feedback_20250114_a7k9m2x8.json",
  "github_issue_url": "https://github.com/zkoss/zkdoc/issues/456",
  "message": "Feedback saved and submitted to https://github.com/zkoss/zkdoc/issues/456"
}
```


## Configuration

The MCP server behavior can be customized using environment variables. These settings control documentation sources, indexing, and Git integration.

### Available Settings

The server provides the following configurable settings:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ZK_DOC_SRC_DIR` | string | `~/.zk-doc-mcp/repo` | Documentation source directory (Git repo or local docs) |
| `ZK_DOC_VECTOR_DB_DIR` | string | `~/.zk-doc-mcp/chroma_db` | Vector database directory for storing embeddings and search indices |
| `ZK_DOC_FORCE_REINDEX` | boolean | `false` | Force re-indexing of documentation on startup |
| `ZK_DOC_LOG_LEVEL` | enum | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `ZK_DOC_USE_GIT` | boolean | `true` | Enable Git synchronization for documentation |
| `ZK_DOC_CLONE_METHOD` | enum | `https` | Git clone method (`https` or `ssh`) |
| `ZK_DOC_REPO_URL` | string | `https://github.com/zkoss/zkdoc.git` | Repository URL to clone documentation from |
| `ZK_DOC_GIT_BRANCH` | string | `master` | Git branch to pull documentation from |
| `ZK_DOC_FEEDBACK_ENABLED` | boolean | `true` | Enable feedback collection for search improvements |
| `ZK_DOC_FEEDBACK_RETENTION_DAYS` | integer | `90` | Days to retain local feedback files |
| `ZK_DOC_FEEDBACK_GITHUB_REPO` | string | `zkoss/zkdoc` | GitHub repository for feedback issues (built-in) |

### Viewing Current Settings

To see all current settings and their values:

```bash
# Start the server
uv run python3 -m zk_doc_mcp

# In another terminal, or use the show_settings tool in Claude
# The server provides a show_settings tool that displays all configuration
```

### Setting Environment Variables

#### Example: Enabling Git Synchronization

By default, Git synchronization is **enabled** (`ZK_DOC_USE_GIT=true`). To change this behavior:

**Disable Git sync:**
```bash
export ZK_DOC_USE_GIT=false
uv run python3 -m zk_doc_mcp
```


#### Example: Using SSH for Git Clone

To clone the documentation repository using SSH instead of HTTPS:

```bash
export ZK_DOC_CLONE_METHOD=ssh
export ZK_DOC_USE_GIT=true
uv run python3 -m zk_doc_mcp
```

**Prerequisites for SSH:**
- SSH key configured and added to ssh-agent
- SSH key authorized on GitHub (or your Git hosting service)

#### Example: Using a Custom Documentation Directory

To use a local documentation directory instead of cloning from Git:

```bash
# Disable Git sync and point to local directory
export ZK_DOC_USE_GIT=false
export ZK_DOC_SRC_DIR=/path/to/local/docs
uv run python3 -m zk_doc_mcp
```

#### Example: Force Re-indexing Documentation

To rebuild the vector search index from scratch:

```bash
export ZK_DOC_FORCE_REINDEX=true
uv run python3 -m zk_doc_mcp
```

After re-indexing completes, the server will run normally with the updated index.

#### Example: Using a Different Git Branch

To pull documentation from a different branch (e.g., `develop` instead of `master`):

```bash
export ZK_DOC_GIT_BRANCH=develop
export ZK_DOC_USE_GIT=true
uv run python3 -m zk_doc_mcp
```

#### Example: Configuring Feedback Collection

Feedback collection is **enabled by default** and automatically submits feedback to https://github.com/zkoss/zkdoc/issues.

**To disable feedback collection:**
```bash
export ZK_DOC_FEEDBACK_ENABLED=false
uv run python3 -m zk_doc_mcp
```

**To change feedback retention period (default: 90 days):**
```bash
export ZK_DOC_FEEDBACK_RETENTION_DAYS=30
uv run python3 -m zk_doc_mcp
```

Feedback is automatically created as GitHub issues for documentation team review, helping improve search results and content gaps.

### Persisting Configuration

To persist settings across sessions, add them to your shell profile, for example

**For bash (add to `~/.bashrc` or `~/.bash_profile`):**
```bash
export ZK_DOC_USE_GIT=true
export ZK_DOC_CLONE_METHOD=https
export ZK_DOC_GIT_BRANCH=main
```

### Configuration Verification

Use the `show_settings` tool to verify your configuration is correct:

## Development

See [README_DEV.md](./README_DEV.md) for development setup, testing, building, and contribution guidelines.


### Running the Server Standalone

After installation from PyPI, you can run the server directly:

```bash
# Using the installed command
zk-doc-mcp-server

# Or using Python module
python -m zk_doc_mcp
```

## Troubleshooting

### Installation issues

**Permission denied errors:**
```bash
# Ensure you have execute permissions
chmod +x ~/.claude/mcp/zk-doc
```

**Module import errors:**
```bash
# Reinstall the package
uvx --refresh zk-doc-mcp-server
```

**Server not appearing in `claude mcp list`:**
```bash
# Check if the command is accessible
uvx zk-doc-mcp-server --help
```

For development-related troubleshooting (setup, testing, building), see [README_DEV.md](./README_DEV.md#troubleshooting-development-issues).

## License

[MIT License](LICENSE)
