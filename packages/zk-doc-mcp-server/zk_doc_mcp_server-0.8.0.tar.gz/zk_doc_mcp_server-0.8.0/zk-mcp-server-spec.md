# ZK Documentation MCP Server 規格

## 概述
ZK Documentation MCP Server 是一個基於 Model Context Protocol (MCP) 的服務器，旨在為 AI 助手提供 ZK Framework 文檔查詢和問答功能。該服務器整合 Chroma 向量資料庫，支援語義搜尋和智能問答。

完美！你的需求很明確：**多檔案開發 + 簡便安裝**。讓我給你一個完整的解決方案。

## 推薦方案：發布為 Python 套件

這是目前最佳實踐，結合了模組化開發和簡便安裝的優點。

### 專案結構

```
my-mcp-server/
├── pyproject.toml          # 套件配置（重要！）
├── README.md
├── .gitignore
└── src/
    └── my_mcp_server/
        ├── __init__.py
        ├── __main__.py     # 入口點
        ├── server.py       # 主要伺服器邏輯
        └── utils/          # 輔助功能
            ├── __init__.py
            └── helpers.py
```

### 關鍵配置：pyproject.toml

```toml
[project]
name = "my-mcp-server"
version = "0.1.0"
description = "My awesome MCP server"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    # 其他依賴...
]

[project.scripts]
my-mcp-server = "my_mcp_server.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
]
```

### 入口點：src/my_mcp_server/__main__.py

```python
"""MCP Server entry point."""
from .server import main

if __name__ == "__main__":
    main()
```

### 主要邏輯：src/my_mcp_server/server.py

```python
from mcp.server.fastmcp import FastMCP
from .tools.calculator import add, subtract
from .utils.helpers import format_result

# 建立 MCP 伺服器
mcp = FastMCP("My MCP Server")

# 註冊工具（從其他模組引入）
@mcp.tool()
def add_numbers(a: int, b: int) -> str:
    """Add two numbers and format the result."""
    result = add(a, b)
    return format_result(result)

@mcp.tool()
def subtract_numbers(a: int, b: int) -> str:
    """Subtract two numbers."""
    result = subtract(a, b)
    return format_result(result)

def main():
    """Run the MCP server."""
    mcp.run()
```

### 模組化的工具：src/my_mcp_server/tools/calculator.py

```python
"""Calculator tools."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b
```

## 發布方式

### 方式 1：發布到 PyPI（推薦，最簡便）

```bash
# 1. 建立套件
uv build

# 2. 發布到 PyPI
uv publish
```

**使用者安裝超簡單：**根據搜尋結果，我現在可以給你一個完整且簡便的解決方案！

## 最佳方案：使用 `uv` + Python 套件

結合搜尋結果，這是目前最簡單的方式：

### 1. 專案結構（模組化）

```
zk-doc-map/
├── pyproject.toml
├── README.md
└── src/
    └──── __init__.py
       ├── __main__.py
       ├── server.py
       └── test/
```

### 2. pyproject.toml（關鍵配置）


### 3. 入口點：src/__main__.py

```python
"""Entry point for the MCP server."""
from .server import main

if __name__ == "__main__":
    main()
```


## 使用者安裝方式（超簡單！）

### 方式 A：發布到 PyPI 後（推薦）

使用者只需一行指令就能安裝你的 MCP Server：

```bash
# Claude Code 安裝
claude mcp add my-server -- uvx my-mcp-server

# 或 Claude Desktop 配置
```

**Claude Desktop 配置：**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "uvx",
      "args": ["my-mcp-server"]
    }
  }
}
```

`uvx` 會自動下載並安裝套件及其所有依賴，使用者不需要手動安裝任何東西。

### 方式 B：直接從 GitHub 安裝（開發階段）

使用者可以直接從 GitHub 倉庫安裝：

```bash
# Claude Code
claude mcp add my-server -- uvx --from git+https://github.com/yourname/my-mcp-server my-mcp-server

# Claude Desktop 配置
```

```json
{
  "mcpServers": {
    "my-server": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yourname/my-mcp-server",
        "my-mcp-server"
      ]
    }
  }
}
```

### 方式 C：本地開發測試

在開發階段，你可以使用 `uv run mcp` 指令快速測試：

```bash
# 開發模式（自動重載）
uv run mcp dev src/my_mcp_server/server.py

# 安裝到 Claude Desktop 測試
uv run mcp install src/my_mcp_server/server.py --name "My MCP Server"
```

## 發布流程

### 1. 開發階段
```bash
# 初始化專案
uv init my-mcp-server
cd my-mcp-server

# 安裝依賴
uv add "mcp>=1.2.0"

# 開發測試
uv run mcp dev src/my_mcp_server/server.py
```

### 2. 發布到 PyPI
```bash
# 建立套件
uv build

# 發布（需要 PyPI 帳號）
uv publish
```

### 3. 使用者安裝（一行搞定！）
```bash
# Claude Code
claude mcp add my-server -- uvx my-mcp-server

# 或手動配置 Claude Desktop
```

## 為什麼這個方案最好？

✅ **模組化開發**：多個檔案，結構清晰  
✅ **超簡單安裝**：使用者只需一行 `uvx` 指令  
✅ **自動依賴管理**：`uvx` 自動處理所有依賴  
✅ **跨平台支援**：Windows/Mac/Linux 都能用  
✅ **無需預先安裝**：使用者不需要先安裝 Python 環境  
✅ **自動更新**：`uvx` 可以自動使用最新版本

## 完整範例

我幫你整理一個最小可運行的範例：

**src/my_mcp_server/server.py：**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator Server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

def main():
    mcp.run()

if __name__ == "__main__":
    main()
```

**使用者只需要：**
```bash
uvx your-package-name
```



## 核心功能

### 1. 文檔索引管理
- 自動同步 zkdoc GitHub 倉庫
- 解析 Markdown 文檔並建立向量索引
- 支援增量更新和重建索引

### 2. 語義搜尋
- 基於向量相似度的文檔片段搜尋
- 支援中英文混合查詢
- 可調整搜尋結果數量和相關性閾值

### 3. 智能問答
- 結合搜尋結果進行上下文問答
- 提供文檔來源引用
- 支援程式碼範例提取

## MCP Tools 規格

### Tool 1: search_zk_docs
**描述**：在 ZK 文檔中進行語義搜尋

**參數**：
```json
{
  "query": {
    "type": "string",
    "description": "搜尋查詢字串",
    "required": true
  },
  "limit": {
    "type": "integer",
    "description": "返回結果數量限制",
    "default": 5,
    "minimum": 1,
    "maximum": 20
  },
  "min_relevance": {
    "type": "number",
    "description": "最小相關性分數 (0-1)",
    "default": 0.6,
    "minimum": 0,
    "maximum": 1
  },
  "category": {
    "type": "string",
    "description": "文檔分類過濾 (如: tutorial, reference, guide)",
    "required": false
  }
}
```

**回傳格式**：
```json
{
  "results": [
    {
      "content": "文檔片段內容",
      "file_path": "文件相對路徑",
      "title": "章節標題",
      "category": "文檔分類",
      "relevance_score": 0.85,
      "url": "GitHub 連結"
    }
  ],
  "total_found": 10,
  "query_time_ms": 150
}
```

### Tool 2: get_zk_doc_content
**描述**：取得特定 ZK 文檔的完整內容

**參數**：
```json
{
  "file_path": {
    "type": "string",
    "description": "文檔的相對路徑",
    "required": true
  },
  "section": {
    "type": "string",
    "description": "特定章節名稱（可選）",
    "required": false
  }
}
```

**回傳格式**：
```json
{
  "content": "完整文檔內容或特定章節內容",
  "file_path": "文件路徑",
  "title": "文檔標題",
  "last_modified": "2024-01-01T10:00:00Z",
  "url": "GitHub 連結",
  "sections": ["章節1", "章節2", "..."]
}
```

### Tool 3: answer_zk_question
**描述**：基於 ZK 文檔回答特定問題

**參數**：
```json
{
  "question": {
    "type": "string",
    "description": "要回答的問題",
    "required": true
  },
  "context_limit": {
    "type": "integer",
    "description": "搜尋上下文片段數量",
    "default": 3,
    "minimum": 1,
    "maximum": 10
  },
  "include_code_examples": {
    "type": "boolean",
    "description": "是否包含程式碼範例",
    "default": true
  }
}
```

**回傳格式**：
```json
{
  "answer": "基於文檔的詳細回答",
  "sources": [
    {
      "file_path": "來源文件路徑",
      "title": "章節標題",
      "url": "GitHub 連結",
      "relevance": 0.9
    }
  ],
  "code_examples": [
    {
      "language": "java",
      "code": "程式碼範例",
      "description": "程式碼說明",
      "source_file": "來源文件"
    }
  ],
  "confidence": 0.85
}
```

### Tool 4: update_zk_docs
**描述**：更新本地 ZK 文檔索引

**參數**：
```json
{
  "force_rebuild": {
    "type": "boolean",
    "description": "是否強制重建整個索引",
    "default": false
  },
  "branch": {
    "type": "string",
    "description": "要同步的 Git 分支",
    "default": "main"
  }
}
```

**回傳格式**：
```json
{
  "status": "success",
  "updated_files": 15,
  "new_files": 3,
  "deleted_files": 1,
  "total_documents": 250,
  "update_time_ms": 5000,
  "last_sync": "2024-01-01T10:00:00Z"
}
```

### Tool 5: get_zk_categories
**描述**：取得可用的文檔分類列表

**參數**：無

**回傳格式**：
```json
{
  "categories": [
    {
      "name": "tutorial",
      "display_name": "教學指南",
      "doc_count": 45
    },
    {
      "name": "reference",
      "display_name": "API 參考",
      "doc_count": 120
    },
    {
      "name": "guide",
      "display_name": "開發指南",
      "doc_count": 85
    }
  ],
  "total_categories": 3,
  "total_documents": 250
}
```

## MCP Resources 規格

### Resource 1: zk-doc-stats
**URI**: `zk://stats`
**描述**：提供 ZK 文檔庫統計資訊
**MIME Type**: `application/json`

### Resource 2: zk-doc-index-status
**URI**: `zk://index-status`
**描述**：索引建立狀態和健康檢查
**MIME Type**: `application/json`

## 設定檔規格

### server-config.json
```json
{
  "server": {
    "name": "zk-documentation-server",
    "version": "1.0.0",
    "host": "localhost",
    "port": 8080
  },
  "repository": {
    "url": "https://github.com/zkoss/zkdoc",
    "branch": "main",
    "local_path": "./zkdoc",
    "sync_interval": 3600
  },
  "chroma": {
    "persist_directory": "./chroma_db",
    "collection_name": "zk_docs",
    "embedding_model": "all-MiniLM-L6-v2",
    "chunk_size": 1000,
    "chunk_overlap": 200
  },
  "search": {
    "default_limit": 5,
    "max_limit": 20,
    "min_relevance": 0.6
  },
  "features": {
    "auto_sync": true,
    "code_extraction": true,
    "multilingual": true
  }
}
```

## 技術架構

### 核心依賴
- **MCP SDK**: Model Context Protocol 實作
- **ChromaDB**: 向量資料庫
- **GitPython**: Git 操作
- **Sentence Transformers**: 文本嵌入
- **Markdown Parser**: Markdown 解析

### 資料處理流程
1. **文檔同步**: 定期從 GitHub 同步最新文檔
2. **內容解析**: 解析 Markdown 文件，提取標題、內容、程式碼
3. **分塊處理**: 將長文檔分割成適當大小的片段
4. **向量化**: 使用 embedding 模型轉換為向量
5. **索引儲存**: 存入 Chroma 資料庫

### 錯誤處理
- 網路連線錯誤重試機制
- 文檔解析失敗的優雅降級
- 向量資料庫連線異常處理
- 詳細的錯誤日誌記錄

## 部署要求

### 系統要求
- Python 3.8+
- 記憶體: 2GB+
- 磁碟空間: 5GB+
- 網路: 可訪問 GitHub

### 安裝步驟
1. 安裝相依套件
2. 設定設定檔
3. 初始化向量資料庫
4. 同步 ZK 文檔
5. 啟動 MCP 服務器

### 效能指標
- 搜尋回應時間: < 500ms
- 文檔同步時間: < 5 分鐘
- 記憶體使用: < 1GB
- 並發請求支援: 10+

## 使用範例

### 搜尋 ZK 組件用法
```bash
# AI Assistant 查詢
"如何在 ZK 中使用 Grid 組件？"

# MCP Server 執行
search_zk_docs(query="Grid component usage", limit=3)
answer_zk_question(question="如何在 ZK 中使用 Grid 組件？")
```

### 取得特定文檔
```bash
# 取得 Grid 組件完整文檔
get_zk_doc_content(file_path="components/grid.md")
```

### 更新文檔索引
```bash
# 更新本地文檔
update_zk_docs(force_rebuild=false)
```

## 擴展功能（未來版本）

1. **多語言支援**: 支援更多語言的查詢和回答
2. **版本管理**: 支援多個 ZK 版本的文檔
3. **使用統計**: 記錄查詢統計和熱門問題
4. **快取機制**: 實作查詢結果快取
5. **Web 介面**: 提供網頁版查詢介面