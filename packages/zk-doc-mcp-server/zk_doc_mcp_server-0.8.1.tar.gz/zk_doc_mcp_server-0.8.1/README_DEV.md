# ZK Documentation MCP Server - Development Guide

This guide is for developers contributing to the ZK Documentation MCP Server project.

## Project Structure

```
zk-doc-mcp/
├── src/
│   └── zk_doc_mcp/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Entry point
│       ├── server.py            # MCP server setup and tools
│       └── doc_indexer.py       # Documentation indexing
├── pyproject.toml               # Project configuration and dependencies
├── requirements.txt             # Additional requirements
├── README.md                    # User-facing documentation
├── README_DEV.md                # This file - Development guide
└── zk-mcp-server-spec.md       # Detailed specifications
```

## Specification
[ZK MCP Server Specification](./zk-mcp-server-spec.md) - Detailed technical specification


## Setting Up Development Environment

1. **Install all dependencies** (including dev dependencies):
```bash
uv pip install -e ".[dev]"
```

2. **Verify installation**:
```bash
uv run python3 -c "import zk_doc_mcp; print(f'Version: {zk_doc_mcp.__version__}')"
```

## Building

### Build the distribution package:
```bash
uv build
```

This creates both wheel and source distributions in the `dist/` directory.

### Verify the build:
```bash
ls -la dist/
```

## Testing

### Run unit tests:
```bash
uv run python3 -m pytest src/zk_doc_mcp/test/ -v
```

### Run specific test file:
```bash
uv run python3 -m pytest src/zk_doc_mcp/test/test_doc_indexer.py -v
```

### Run tests with coverage:
```bash
uv run python3 -m pytest src/zk_doc_mcp/test/ --cov=zk_doc_mcp --cov-report=html
```

### Run server functionality test:
```bash
# Start the server in the background and test basic functionality
uv run python3 -m zk_doc_mcp &
sleep 2
# Server should be running - verify by checking logs
```

## Code Quality

### Type checking:
```bash
uv run python3 -m mypy src/zk_doc_mcp/
```

### Code formatting:
```bash
uv run python3 -m black src/
```

### Linting:
```bash
uv run python3 -m ruff check src/
uv run python3 -m ruff check src/ --fix
```

## Adding New Tools

1. Create a new tool function in `src/zk_doc_mcp/server.py`
2. Decorate with `@mcp.tool()`
3. Add comprehensive docstrings
4. Update the README.md with tool documentation

Example:
```python
@mcp.tool()
def my_tool(param: str) -> dict:
    """Tool description.

    Args:
        param: Parameter description

    Returns:
        Result dictionary
    """
    # Implementation
    return {"result": "value"}
```

## Development Installation in Claude Code

If you're developing or want to use the latest code from your local repository:

```bash
# From the project root directory
claude mcp add zk-doc -- uv run -m zk_doc_mcp
```

This installs the server using the local development version.

## Publishing (release) process
1. Set the package version at [pyproject.toml](pyproject.toml)
2. [Building the package](#Building)
3. publish by running [publish.sh](publish.sh)

## Troubleshooting Development Issues

### Module not found errors
If you get `ModuleNotFoundError` when running the server:
```bash
# Ensure the package is installed in editable mode
uv pip install -e .
```

### ChromaDB or dependency issues
Reinstall dependencies cleanly:
```bash
uv pip install --force-reinstall -e .
```

### Platform compatibility issues
The project is configured for macOS (both Intel and Apple Silicon). For other platforms, you may need to adjust `tool.uv.required-environments` in `pyproject.toml`.

### Python version issues
Ensure you're using Python 3.10 or higher:
```bash
python3 --version
```

## References

- [Model Context Protocol (MCP) Documentation](https://modelcontextprotocol.io/docs/develop/build-server)
- [FastMCP Documentation](https://github.com/joehoover/fastmcp)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [uv Package Manager](https://docs.astral.sh/uv/)
- [ZK Framework Documentation](https://www.zkoss.org/)
