"""
Jsearch MCP Server

使用 FastMCP 的 from_openapi 方法自动生成

Version: 1.0.0
Transport: stdio
"""
import os
import json
import httpx
from fastmcp import FastMCP

# 服务器版本和配置
__version__ = "1.0.1"
__tag__ = "jsearch/1.0.1"

# API 配置
API_KEY = os.getenv("API_KEY", "")

# 传输协议配置
TRANSPORT = "stdio"


# OpenAPI 规范
OPENAPI_SPEC = """{\n  \"openapi\": \"3.0.0\",\n  \"info\": {\n    \"title\": \"Jsearch\",\n    \"version\": \"1.0.0\",\n    \"description\": \"RapidAPI: letscrape-6bRBa3QguO5/jsearch\"\n  },\n  \"servers\": [\n    {\n      \"url\": \"https://jsearch.p.rapidapi.com\"\n    }\n  ],\n  \"paths\": {\n    \"/search\": {\n      \"get\": {\n        \"summary\": \"Job Search\",\n        \"description\": \"Search for jobs posted on any public job site across the web on the largest job aggregate in the world (Google for Jobs). Extensive filtering support and most options available on Google for Jobs.\",\n        \"operationId\": \"job_search\",\n        \"parameters\": [\n          {\n            \"name\": \"query\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: developer jobs in chicago\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"page\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: 1\",\n            \"schema\": {\n              \"type\": \"integer\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"num_pages\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: 1\",\n            \"schema\": {\n              \"type\": \"integer\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"country\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: us\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"date_posted\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: all\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          }\n        ],\n        \"responses\": {\n          \"200\": {\n            \"description\": \"Successful response\",\n            \"content\": {\n              \"application/json\": {\n                \"schema\": {\n                  \"type\": \"object\"\n                }\n              }\n            }\n          }\n        }\n      }\n    },\n    \"/job-details\": {\n      \"get\": {\n        \"summary\": \"Job Details\",\n        \"description\": \"Get all job details, including additional information such as: application options / links, employer reviews and estimated salaries for similar jobs.\",\n        \"operationId\": \"job_details\",\n        \"parameters\": [\n          {\n            \"name\": \"job_id\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: n20AgUu1KG0BGjzoAAAAAA==\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"country\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: us\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          }\n        ],\n        \"responses\": {\n          \"200\": {\n            \"description\": \"Successful response\",\n            \"content\": {\n              \"application/json\": {\n                \"schema\": {\n                  \"type\": \"object\"\n                }\n              }\n            }\n          }\n        }\n      }\n    },\n    \"/estimated-salary\": {\n      \"get\": {\n        \"summary\": \"Job Salary\",\n        \"description\": \"Get estimated salaries / pay for a jobs around a location by job title and location. The salary estimation is returned for several periods, depending on data availability / relevance, and includes: hourly, daily, weekly, monthly, or yearly.\",\n        \"operationId\": \"job_salary\",\n        \"parameters\": [\n          {\n            \"name\": \"job_title\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: nodejs developer\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"location\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: new york\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"location_type\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: ANY\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"years_of_experience\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: ALL\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          }\n        ],\n        \"responses\": {\n          \"200\": {\n            \"description\": \"Successful response\",\n            \"content\": {\n              \"application/json\": {\n                \"schema\": {\n                  \"type\": \"object\"\n                }\n              }\n            }\n          }\n        }\n      }\n    },\n    \"/company-job-salary\": {\n      \"get\": {\n        \"summary\": \"Company Job Salary\",\n        \"description\": \"Get estimated job salaries/pay in a specific company by job title and optionally a location and experience level in years.\",\n        \"operationId\": \"company_job_salary\",\n        \"parameters\": [\n          {\n            \"name\": \"company\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: Amazon\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"job_title\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: software developer\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"location_type\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: ANY\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          },\n          {\n            \"name\": \"years_of_experience\",\n            \"in\": \"query\",\n            \"required\": false,\n            \"description\": \"Example value: ALL\",\n            \"schema\": {\n              \"type\": \"string\",\n              \"default\": null,\n              \"enum\": null\n            }\n          }\n        ],\n        \"responses\": {\n          \"200\": {\n            \"description\": \"Successful response\",\n            \"content\": {\n              \"application/json\": {\n                \"schema\": {\n                  \"type\": \"object\"\n                }\n              }\n            }\n          }\n        }\n      }\n    }\n  },\n  \"components\": {\n    \"securitySchemes\": {\n      \"ApiAuth\": {\n        \"type\": \"apiKey\",\n        \"in\": \"header\",\n        \"name\": \"X-RapidAPI-Key\"\n      }\n    }\n  },\n  \"security\": [\n    {\n      \"ApiAuth\": []\n    }\n  ]\n}"""

# 创建 HTTP 客户端

client = httpx.AsyncClient(base_url="https://jsearch.p.rapidapi.com", timeout=30.0)


# 如果需要认证，添加事件钩子

@client.event
async def request(request):
    """添加认证头"""
    if API_KEY:
        request.headers["Authorization"] = API_KEY


# 从 OpenAPI 规范创建 FastMCP 服务器
openapi_dict = json.loads(OPENAPI_SPEC)
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_dict,
    client=client,
    name="jsearch",
    version=__version__
)

def main():
    """主入口点"""
    print(f"🚀 启动 Jsearch MCP 服务器")
    print(f"📦 版本: {__tag__}")
    print(f"🔧 传输协议: {TRANSPORT}")
    
    print()
    
    # 运行服务器
    
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
