## 發布到 PyPI 的必要條件

### 1. **PyPI 帳號**
你需要在 PyPI 註冊帳號，並創建一個 API token 用於上傳套件。

- 註冊網址：https://pypi.org/account/register/
- 建議先在 TestPyPI 練習：https://test.pypi.org/account/register/

### 2. **唯一的套件名稱**
套件名稱必須在 PyPI 上是唯一的。你可以先在 https://pypi.org 搜尋確認名稱是否已被使用。

### 3. **必要的專案檔案**

標準的專案結構應該包含以下檔案：

```
your-project/
├── src/
│   └── your_package/
│       ├── __init__.py
│       └── core.py
├── tests/
├── README.md          # 必要
├── LICENSE            # 必要
├── .gitignore
└── pyproject.toml     # 必要
```

### 4. **pyproject.toml 配置**

這是最重要的配置檔案，必須包含專案的元資料：

```toml
[build-system]
requires = ["hatchling"]  # 或 "setuptools>=68"
build-backend = "hatchling.build_meta"

[project]
name = "my-mcp-server"              # 必須唯一
version = "0.1.0"                   # 必須指定版本
description = "My awesome MCP server"
readme = "README.md"                # 必要
requires-python = ">=3.10"
license = { file = "LICENSE" }      # 必要
authors = [
    { name = "Your Name", email = "you@example.com" }
]
keywords = ["mcp", "server", "ai"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
    "mcp>=1.2.0",
]

[project.urls]
Homepage = "https://github.com/yourname/my-mcp-server"
Issues = "https://github.com/yourname/my-mcp-server/issues"

[project.scripts]
my-mcp-server = "my_mcp_server.__main__:main"
```

### 5. **開源授權（LICENSE）**

你必須選擇一個開源授權並包含 LICENSE 檔案。常見選擇：
- MIT License（最寬鬆）
- Apache 2.0
- GPL-3.0

可以在這裡選擇：https://choosealicense.com/

## 發布步驟（使用 uv）

### Step 1: 先在 TestPyPI 測試

TestPyPI 是 PyPI 提供的測試環境，讓你可以安全地練習發布流程。

```bash
# 1. 建立套件
uv build

# 2. 發布到 TestPyPI（測試）
uv publish --publish-url https://test.pypi.org/legacy/
```

第一次發布時會要求輸入：
- Username: `__token__`
- Password: 你的 TestPyPI API token

### Step 2: 測試安裝

```bash
# 從 TestPyPI 安裝測試
uv pip install --index-url https://test.pypi.org/simple/ my-mcp-server
```

### Step 3: 正式發布到 PyPI

確認一切正常後：

```bash
# 發布到正式 PyPI
uv publish
```

## 完整實作範例

讓我給你一個完整的 MCP Server 發布範例：

### 1. pyproject.toml
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build_meta"

[project]
name = "awesome-mcp-server"
version = "0.1.0"
description = "An awesome MCP server for AI assistants"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
keywords = ["mcp", "ai", "claude", "server"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "mcp>=1.2.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/awesome-mcp-server"
Documentation = "https://github.com/yourusername/awesome-mcp-server#readme"
Repository = "https://github.com/yourusername/awesome-mcp-server"
Issues = "https://github.com/yourusername/awesome-mcp-server/issues"

[project.scripts]
awesome-mcp-server = "awesome_mcp_server.__main__:main"
```

### 2. README.md（重要！）
```markdown
# Awesome MCP Server

An awesome MCP server that does amazing things!

## Installation

```bash
uvx awesome-mcp-server
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "awesome-server": {
      "command": "uvx",
      "args": ["awesome-mcp-server"]
    }
  }
}
```

## Features

- Feature 1
- Feature 2

## License

MIT
```

### 3. LICENSE（MIT 範例）
```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge...
```

### 4. 發布指令
```bash
# 初始化專案
uv init awesome-mcp-server
cd awesome-mcp-server

# 開發你的程式碼...

# 建立套件
uv build

# 先測試發布到 TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/

# 測試安裝
uvx --from https://test.pypi.org/simple/ awesome-mcp-server

# 確認沒問題後，發布到正式 PyPI
uv publish
```

## 重要注意事項

⚠️ **版本管理**：每次更新都需要增加版本號（如 0.1.0 → 0.1.1）

⚠️ **無法刪除**：一旦發布到 PyPI，就無法完全刪除該版本號，所以要確認好再發布

⚠️ **先用 TestPyPI**：強烈建議先在 TestPyPI 測試整個流程

✅ **使用 GitHub Actions 自動發布**：可以設定當你在 GitHub 建立 release 時自動發布到 PyPI

## 最低要求總結

1. ✅ PyPI 帳號 + API Token
2. ✅ 唯一的套件名稱
3. ✅ `pyproject.toml`（包含必要元資料）
4. ✅ `README.md`
5. ✅ `LICENSE` 檔案
6. ✅ 正確的專案結構

就這樣！發布到 PyPI 其實沒有想像中複雜。你想要我幫你準備一個完整的專案範本嗎？