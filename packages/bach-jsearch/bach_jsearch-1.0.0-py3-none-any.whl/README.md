# Jsearch MCP Server

RapidAPI: letscrape-6bRBa3QguO5/jsearch

## 简介

这是一个使用 [FastMCP](https://fastmcp.wiki) 自动生成的 MCP 服务器，用于访问 Jsearch API。

- **PyPI 包名**: `bach-jsearch`
- **版本**: 1.0.0
- **来源平台**: openapi
- **传输协议**: stdio


## 安装

从 PyPI 安装:

```bash
pip install bach-jsearch
```

或从源码安装:

```bash
pip install -e .
```

## 安装和运行

### 方式 1: 直接运行（推荐）

```bash
python server.py
```

### 方式 2: 安装后运行

```bash
# 安装依赖
pip install -e .

# 运行服务器
python server.py
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
    "jsearch": {
      "command": "python",
      "args": ["E:\path\to\jsearch\server.py"],
      "env": {
        "API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**注意**: 请将 `E:\path\to\jsearch\server.py` 替换为实际的服务器文件路径。


## 可用工具

此服务器提供以下工具:


### `job_search`

Search for jobs posted on any public job site across the web on the largest job aggregate in the world (Google for Jobs). Extensive filtering support and most options available on Google for Jobs.

**端点**: `GET /search`


**参数**:

- `query` (string): Example value: developer jobs in chicago

- `page` (integer): Example value: 1

- `num_pages` (integer): Example value: 1

- `country` (string): Example value: us

- `date_posted` (string): Example value: all



---


### `job_details`

Get all job details, including additional information such as: application options / links, employer reviews and estimated salaries for similar jobs.

**端点**: `GET /job-details`


**参数**:

- `job_id` (string): Example value: n20AgUu1KG0BGjzoAAAAAA==

- `country` (string): Example value: us



---


### `job_salary`

Get estimated salaries / pay for a jobs around a location by job title and location. The salary estimation is returned for several periods, depending on data availability / relevance, and includes: hourly, daily, weekly, monthly, or yearly.

**端点**: `GET /estimated-salary`


**参数**:

- `job_title` (string): Example value: nodejs developer

- `location` (string): Example value: new york

- `location_type` (string): Example value: ANY

- `years_of_experience` (string): Example value: ALL



---


### `company_job_salary`

Get estimated job salaries/pay in a specific company by job title and optionally a location and experience level in years.

**端点**: `GET /company-job-salary`


**参数**:

- `company` (string): Example value: Amazon

- `job_title` (string): Example value: software developer

- `location_type` (string): Example value: ANY

- `years_of_experience` (string): Example value: ALL



---



## 技术栈

- **FastMCP**: 快速、Pythonic 的 MCP 服务器框架
- **传输协议**: stdio
- **HTTP 客户端**: httpx

## 开发

此服务器由 [API-to-MCP](https://github.com/yourusername/APItoMCP) 工具自动生成。

生成时间: 1.0.0