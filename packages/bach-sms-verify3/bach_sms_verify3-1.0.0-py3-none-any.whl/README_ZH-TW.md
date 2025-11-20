# Sms Verify3 MCP Server

[English](./README_EN.md) | [简体中文](./README.md) | 繁體中文

RapidAPI: Glavier/sms-verify3

## 🚀 使用 EMCP 平台快速體驗

**[EMCP](https://sit-emcp.kaleido.guru)** 是一個強大的 MCP 伺服器管理平台，讓您無需手動配置即可快速使用各種 MCP 伺服器！

### 快速開始：

1. 🌐 造訪 **[EMCP 平台](https://sit-emcp.kaleido.guru)**
2. 📝 註冊並登入帳號
3. 🎯 進入 **MCP 廣場**，瀏覽所有可用的 MCP 伺服器
4. 🔍 搜尋或找到本伺服器（`bach-sms_verify3`）
5. 🎉 點擊 **「安裝 MCP」** 按鈕
6. ✅ 完成！即可在您的應用中使用

### EMCP 平台優勢：

- ✨ **零配置**：無需手動編輯配置檔案
- 🎨 **視覺化管理**：圖形介面輕鬆管理所有 MCP 伺服器
- 🔐 **安全可靠**：統一管理 API 金鑰和認證資訊
- 🚀 **一鍵安裝**：MCP 廣場提供豐富的伺服器選擇
- 📊 **使用統計**：即時查看服務調用情況

立即造訪 **[EMCP 平台](https://sit-emcp.kaleido.guru)** 開始您的 MCP 之旅！


---

## 簡介

這是一個使用 [FastMCP](https://fastmcp.wiki) 自動生成的 MCP 伺服器，用於存取 Sms Verify3 API。

- **PyPI 套件名**: `bach-sms_verify3`
- **版本**: 1.0.0
- **來源平台**: openapi
- **傳輸協定**: stdio


## 安装

### 从 PyPI 安装:

```bash
pip install bach-sms_verify3
```

### 从源码安装:

```bash
pip install -e .
```

## 运行

### 方式 1: 使用 uvx（推荐，无需安装）

```bash
# 运行（uvx 会自动安装并运行）
uvx --from bach-sms_verify3 bach_sms_verify3

# 或指定版本
uvx --from bach-sms_verify3@latest bach_sms_verify3
```

### 方式 2: 直接运行（开发模式）

```bash
python server.py
```

### 方式 3: 安装后作为命令运行

```bash
# 安装
pip install bach-sms_verify3

# 运行（命令名使用下划线）
bach_sms_verify3
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
    "sms_verify3": {
      "command": "python",
      "args": ["E:\path\to\sms_verify3\server.py"],
      "env": {
        "API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**注意**: 请将 `E:\path\to\sms_verify3\server.py` 替换为实际的服务器文件路径。


## 可用工具

此服务器提供以下工具:


### `estimate_cost`

Estimate Cost

**端点**: `POST /send-numeric-verify`



---



## 技术栈

- **FastMCP**: 快速、Pythonic 的 MCP 服务器框架
- **传输协议**: stdio
- **HTTP 客户端**: httpx

## 开发

此服务器由 [API-to-MCP](https://github.com/yourusername/APItoMCP) 工具自动生成。

生成时间: 1.0.0