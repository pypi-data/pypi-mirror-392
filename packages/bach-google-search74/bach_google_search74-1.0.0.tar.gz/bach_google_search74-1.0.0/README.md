# Google Search74 MCP Server

RapidAPI: herosAPI/google-search74

## 简介

这是一个使用 [FastMCP](https://fastmcp.wiki) 自动生成的 MCP 服务器，用于访问 Google Search74 API。

- **PyPI 包名**: `bach-google_search74`
- **版本**: 1.0.0
- **来源平台**: openapi
- **传输协议**: stdio


## 安装

### 从 PyPI 安装:

```bash
pip install bach-google_search74
```

### 从源码安装:

```bash
pip install -e .
```

## 运行

### 方式 1: 使用 uvx（推荐，无需安装）

```bash
# 运行（uvx 会自动安装并运行）
uvx --from bach-google_search74 bach_google_search74

# 或指定版本
uvx --from bach-google_search74@latest bach_google_search74
```

### 方式 2: 直接运行（开发模式）

```bash
python server.py
```

### 方式 3: 安装后作为命令运行

```bash
# 安装
pip install bach-google_search74

# 运行（命令名使用下划线）
bach_google_search74
```

## 配置


### API 认证

此 API 需要认证。请设置环境变量:

```bash
export API_KEY="your_api_key_here"
```


### 在 Claude Desktop 中使用

编辑 Claude Desktop 配置文件 `claude_desktop_config.json`:


```json
{
  "mcpServers": {
    "google_search74": {
      "command": "python",
      "args": ["E:\path\to\google_search74\server.py"],
      "env": {
        "API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**注意**: 请将 `E:\path\to\google_search74\server.py` 替换为实际的服务器文件路径。


## 可用工具

此服务器提供以下工具:


### `search`

The Google Search74 API endpoint allows users to perform a Google search query and retrieve relevant results based on the provided input. This endpoint is ideal for applications that require automated search capabilities, such as content aggregation, market research, or keyword analysis. ### Key Features: 1. **Search Functionality**: Execute a search query on Google and retrieve results. 2. **Limit Results**: Specify the maximum number of results to be returned. 3. **Related Keywords**: Optionally include related keywords in the response for deeper insights. ### Parameters: - **query (string)**: The search term or keyword to query on Google. For example, "Nike". - **limit (integer)**: The maximum number of search results to return. For example, `10`. - **related_keywords (boolean)**: A flag to include related keywords in the response. Set to `true` to retrieve related keywords, or `false` to exclude them. ### Response: The endpoint returns a structured JSON object containing: - **Search Results**: A list of search results, including titles, URLs, and snippets. - **Related Keywords** (if enabled): A list of keywords related to the search query for further exploration. This endpoint is designed to streamline search operations and provide actionable insights for applications leveraging Google search data.

**端点**: `GET /`


**参数**:

- `query` (string): Example value: Nike

- `limit` (integer): Example value: 10

- `related_keywords` (boolean): Example value: true



---



## 技术栈

- **FastMCP**: 快速、Pythonic 的 MCP 服务器框架
- **传输协议**: stdio
- **HTTP 客户端**: httpx

## 开发

此服务器由 [API-to-MCP](https://github.com/yourusername/APItoMCP) 工具自动生成。

生成时间: 1.0.0