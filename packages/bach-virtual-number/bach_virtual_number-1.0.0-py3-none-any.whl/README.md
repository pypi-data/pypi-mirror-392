# Virtual Number MCP Server

[English](./README_EN.md) | 简体中文 | [繁體中文](./README_ZH-TW.md)

Virtual Number 的 MCP 服务器，由 API-to-MCP 工具自动生成。

## 🚀 使用 EMCP 平台快速体验

**[EMCP](https://sit-emcp.kaleido.guru)** 是一个强大的 MCP 服务器管理平台，让您无需手动配置即可快速使用各种 MCP 服务器！

### 快速开始：

1. 🌐 访问 **[EMCP 平台](https://sit-emcp.kaleido.guru)**
2. 📝 注册并登录账号
3. 🎯 进入 **MCP 广场**，浏览所有可用的 MCP 服务器
4. 🔍 搜索或找到本服务器（`bach-virtual_number`）
5. 🎉 点击 **"安装 MCP"** 按钮
6. ✅ 完成！即可在您的应用中使用

### EMCP 平台优势：

- ✨ **零配置**：无需手动编辑配置文件
- 🎨 **可视化管理**：图形界面轻松管理所有 MCP 服务器
- 🔐 **安全可靠**：统一管理 API 密钥和认证信息
- 🚀 **一键安装**：MCP 广场提供丰富的服务器选择
- 📊 **使用统计**：实时查看服务调用情况

立即访问 **[EMCP 平台](https://sit-emcp.kaleido.guru)** 开始您的 MCP 之旅！


---

## 简介

这是一个使用 [FastMCP](https://fastmcp.wiki) 自动生成的 MCP 服务器，用于访问 Virtual Number API。

- **PyPI 包名**: `bach-virtual_number`
- **版本**: 1.0.0
- **传输协议**: stdio


## 安装

### 从 PyPI 安装:

```bash
pip install bach-virtual_number
```

### 从源码安装:

```bash
pip install -e .
```

## 运行

### 方式 1: 使用 uvx（推荐，无需安装）

```bash
# 运行（uvx 会自动安装并运行）
uvx --from bach-virtual_number bach_virtual_number

# 或指定版本
uvx --from bach-virtual_number@latest bach_virtual_number
```

### 方式 2: 直接运行（开发模式）

```bash
python server.py
```

### 方式 3: 安装后作为命令运行

```bash
# 安装
pip install bach-virtual_number

# 运行（命令名使用下划线）
bach_virtual_number
```

## 配置

### API 认证

此 API 需要认证。请设置环境变量:

```bash
export API_KEY="your_api_key_here"
```

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `API_KEY` | API 密钥 | 是 |
| `PORT` | 不适用 | 否 |
| `HOST` | 不适用 | 否 |



### 在 Claude Desktop 中使用

编辑 Claude Desktop 配置文件 `claude_desktop_config.json`:


```json
{
  "mcpServers": {
    "virtual_number": {
      "command": "python",
      "args": ["E:\path\to\virtual_number\server.py"],
      "env": {
        "API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**注意**: 请将 `E:\path\to\virtual_number\server.py` 替换为实际的服务器文件路径。


## 可用工具

此服务器提供以下工具:


### `view_sms_history`

View All received SMS for the given number and country id

**端点**: `GET /api/v1/e-sim/view-messages`


**参数**:

- `countryId` (string) *必需*: Example value: 7

- `number` (string) *必需*: Example value: 79034134722

- `page` (string): Example value: 

- `countryId` (string) *必需*: Example value: 7

- `number` (string) *必需*: Example value: 79034134722

- `page` (string): Example value: 



---


### `get_number_by_country_id`

Get currently available numbers list by given country id

**端点**: `GET /api/v1/e-sim/country-numbers`


**参数**:

- `countryId` (string) *必需*: Example value: 7

- `countryId` (string) *必需*: Example value: 7



---


### `get_all_countries`

Get the list of currently available countries

**端点**: `GET /api/v1/e-sim/all-countries`



---



## 技术栈

- **FastMCP**: 快速、Pythonic 的 MCP 服务器框架
- **传输协议**: stdio
- **HTTP 客户端**: httpx

## 开发

此服务器由 [API-to-MCP](https://github.com/BACH-AI-Tools/api-to-mcp) 工具自动生成。

版本: 1.0.0
