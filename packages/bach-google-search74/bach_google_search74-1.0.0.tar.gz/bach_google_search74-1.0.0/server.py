"""
Google Search74 MCP Server

使用 FastMCP 的 from_openapi 方法自动生成

Version: 1.0.0
Transport: stdio
"""
import os
import json
import httpx
from fastmcp import FastMCP

# 服务器版本和配置
__version__ = "1.0.0"
__tag__ = "google_search74/1.0.0"

# API 配置
API_KEY = os.getenv("API_KEY", "")

# 传输协议配置
TRANSPORT = "stdio"


# OpenAPI 规范
OPENAPI_SPEC = """{\n  \"openapi\": \"3.0.0\",\n  \"info\": {\n    \"title\": \"Google Search74\",\n    \"version\": \"1.0.0\",\n    \"description\": \"RapidAPI: herosAPI/google-search74\"\n  },\n  \"servers\": [\n    {\n      \"url\": \"https://google-search74.p.rapidapi.com\"\n    }\n  ],\n  \"paths\": {\n    \"/\": {\n      \"get\": {\n        \"summary\": \"Perform a Google search and retrieve results with optional related keywords.\",\n        \"description\": \"The Google Search74 API endpoint allows users to perform a Google search query and retrieve relevant results based on the provided input. This endpoint is ideal for applications that require automated search capabilities, such as content aggregation, market research, or keyword analysis. ### Key Features: 1. **Search Functionality**: Execute a search query on Google and retrieve results. 2. **Limit Results**: Specify the maximum number of results to be returned. 3. **Related Keywords**: Optionally include related keywords in the response for deeper insights. ### Parameters: - **query (string)**: The search term or keyword to query on Google. For example, \\\"Nike\\\". - **limit (integer)**: The maximum number of search results to return. For example, `10`. - **related_keywords (boolean)**: A flag to include related keywords in the response. Set to `true` to retrieve related keywords, or `false` to exclude them. ### Response: The endpoint returns a structured JSON object containing: - **Search Results**: A list of search results, including titles, URLs, and snippets. - **Related Keywords** (if enabled): A list of keywords related to the search query for further exploration. This endpoint is designed to streamline search operations and provide actionable insights for applications leveraging Google search data.\",\n        \"operationId\": \"search\",\n        \"parameters\": [\n          {\n            \"name\": \"query\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: Nike\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"limit\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: 10\",\n            \"schema\": {\n              \"type\": \"integer\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"related_keywords\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: true\",\n            \"schema\": {\n              \"type\": \"boolean\",\n              \"default\": null,\n              \"enum\": null\n            }\n          }\n        ],\n        \"responses\": {\n          \"200\": {\n            \"description\": \"Successful response\",\n            \"content\": {\n              \"application/json\": {\n                \"schema\": {\n                  \"type\": \"object\"\n                }\n              }\n            }\n          }\n        }\n      }\n    }\n  },\n  \"components\": {\n    \"securitySchemes\": {\n      \"ApiAuth\": {\n        \"type\": \"apiKey\",\n        \"in\": \"header\",\n        \"name\": \"X-RapidAPI-Key\"\n      }\n    }\n  },\n  \"security\": [\n    {\n      \"ApiAuth\": []\n    }\n  ]\n}"""

# 创建 HTTP 客户端

# 如果需要认证，添加默认 headers
default_headers = {}
if API_KEY:
    default_headers["Authorization"] = API_KEY
    
    # RapidAPI 需要额外的 Host header
    default_headers["X-RapidAPI-Host"] = "google-search74.p.rapidapi.com"
    



client = httpx.AsyncClient(
    base_url="https://google-search74.p.rapidapi.com", 
    timeout=30.0,
    headers=default_headers
)


# 从 OpenAPI 规范创建 FastMCP 服务器
openapi_dict = json.loads(OPENAPI_SPEC)
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_dict,
    client=client,
    name="google_search74",
    version=__version__
)

def main():
    """主入口点"""
    print(f"🚀 启动 Google Search74 MCP 服务器")
    print(f"📦 版本: {__tag__}")
    print(f"🔧 传输协议: {TRANSPORT}")
    
    print()
    
    # 运行服务器
    
    mcp.run(transport="stdio")
    


if __name__ == "__main__":
    main()