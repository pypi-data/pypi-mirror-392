# Meteostat MCP Server

[English](./README_EN.md) | [简体中文](./README.md) | 繁體中文

## 🚀 使用 EMCP 平台快速體驗

**[EMCP](https://sit-emcp.kaleido.guru)** 是一個強大的 MCP 伺服器管理平台，讓您無需手動配置即可快速使用各種 MCP 伺服器！

### 快速開始：

1. 🌐 造訪 **[EMCP 平台](https://sit-emcp.kaleido.guru)**
2. 📝 註冊並登入帳號
3. 🎯 進入 **MCP 廣場**，瀏覽所有可用的 MCP 伺服器
4. 🔍 搜尋或找到本伺服器（`bach-meteostat`）
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

這是一個使用 [FastMCP](https://fastmcp.wiki) 自動生成的 MCP 伺服器，用於存取 Meteostat API。

- **PyPI 套件名**: `bach-meteostat`
- **版本**: 1.0.0
- **傳輸協定**: stdio


## 安装

### 从 PyPI 安装:

```bash
pip install bach-meteostat
```

### 从源码安装:

```bash
pip install -e .
```

## 运行

### 方式 1: 使用 uvx（推荐，无需安装）

```bash
# 运行（uvx 会自动安装并运行）
uvx --from bach-meteostat bach_meteostat

# 或指定版本
uvx --from bach-meteostat@latest bach_meteostat
```

### 方式 2: 直接运行（开发模式）

```bash
python server.py
```

### 方式 3: 安装后作为命令运行

```bash
# 安装
pip install bach-meteostat

# 运行（命令名使用下划线）
bach_meteostat
```

## 配置

### API 認證

此 API 需要認證。請設定環境變數:

```bash
export API_KEY="your_api_key_here"
```

### 環境變數

| 變數名 | 說明 | 必需 |
|--------|------|------|
| `API_KEY` | API 金鑰 | 是 |
| `PORT` | 不適用 | 否 |
| `HOST` | 不適用 | 否 |



### 在 Claude Desktop 中使用

编辑 Claude Desktop 配置文件 `claude_desktop_config.json`:


```json
{
  "mcpServers": {
    "meteostat": {
      "command": "python",
      "args": ["E:\path\to\meteostat\server.py"],
      "env": {
        "API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**注意**: 請將 `E:\path\to\meteostat\server.py` 替換為實際的伺服器檔案路徑。


## 可用工具

此服务器提供以下工具:


### `monthly_point_data`

This endpoint provides historical monthly statistics for a geographic location. The data provided through this endpoint is aggregated from multiple governmental interfaces.

**端点**: `GET /point/monthly`


**参数**:

- `lat` (number) *必需*: The point's latitude.

- `lon` (number) *必需*: The point's longitude.

- `alt` (number): The point's elevation.

- `start` (string) *必需*: The start date of the period (YYYY-MM-DD).

- `end` (string) *必需*: The end date of the period (YYYY-MM-DD).

- `model` (string): Example value: 

- `freq` (string): The time frequency of the records. Can be used for custom aggregation. Default is null.

- `units` (string): The unit system of the meteorological parameters. Default is metric.

- `lat` (string) *必需*: Example value: 52.5244

- `lon` (string) *必需*: Example value: 13.4105

- `alt` (string): Example value: 43

- `start` (string) *必需*: Example value: 2020-01-01

- `end` (string) *必需*: Example value: 2020-12-31

- `model` (string): Example value: 

- `freq` (string): Example value: 

- `units` (string): Example value: 



---


### `monthly_station_data`

This endpoint provides historical monthly statistics for a particular weather station. The data provided through this endpoint is aggregated from multiple governmental interfaces.

**端点**: `GET /stations/monthly`


**参数**:

- `station` (string) *必需*: The Meteostat weather station identifier.

- `start` (string) *必需*: The start date of the period (YYYY-MM-DD).

- `end` (string) *必需*: The end date of the period (YYYY-MM-DD).

- `model` (string): Example value: 

- `freq` (string): The time frequency of the records. Can be used for custom aggregation. Default is null.

- `units` (string): The unit system of the meteorological parameters. Default is metric.

- `station` (string) *必需*: Example value: 10637

- `start` (string) *必需*: Example value: 2020-01-01

- `end` (string) *必需*: Example value: 2020-12-31

- `model` (string): Example value: 

- `freq` (string): Example value: 

- `units` (string): Example value: 



---


### `station_meta_data`

This endpoint provides meta data for a particular weather station.

**端点**: `GET /stations/meta`


**参数**:

- `id` (string): The Meteostat identifier of a weather station.

- `wmo` (string): The WMO identifier of a weather station.

- `icao` (string): The ICAO identifier of a weather station.

- `id` (string): Example value: 10637

- `wmo` (string): Example value: 

- `icao` (string): Example value: 



---


### `daily_point_data`

This endpoint provides historical daily statistics for a geographic location. The data provided through this endpoint is aggregated from multiple governmental interfaces.

**端点**: `GET /point/daily`


**参数**:

- `lat` (number) *必需*: The point's latitude.

- `lon` (number) *必需*: The point's longitude.

- `alt` (number): The point's elevation.

- `start` (string) *必需*: The start date of the period (YYYY-MM-DD).

- `end` (string) *必需*: The end date of the period (YYYY-MM-DD).

- `model` (string): Example value: 

- `freq` (string): The time frequency of the records. Can be used for custom aggregation. Default is null.

- `units` (string): The unit system of the meteorological parameters. Default is metric.

- `lat` (string) *必需*: Example value: 43.6667

- `lon` (string) *必需*: Example value: -79.4

- `alt` (string): Example value: 184

- `start` (string) *必需*: Example value: 2020-01-01

- `end` (string) *必需*: Example value: 2020-01-31

- `model` (string): Example value: 

- `freq` (string): Example value: 

- `units` (string): Example value: 



---


### `hourly_point_data`

This endpoint provides historical hourly observations for a geographic location. The data provided through this endpoint is aggregated from multiple governmental interfaces.

**端点**: `GET /point/hourly`


**参数**:

- `lat` (number) *必需*: The point's latitude.

- `lon` (number) *必需*: The point's longitude.

- `alt` (number): The point's elevation.

- `start` (string) *必需*: The start date of the period (YYYY-MM-DD).

- `end` (string) *必需*: The end date of the period (YYYY-MM-DD).

- `tz` (string): The time zone according to the tz database. Default is UTC.

- `model` (string): Example value: 

- `freq` (string): The time frequency of the records. Can be used for custom aggregation. Default is null.

- `units` (string): The unit system of the meteorological parameters. Default is metric.

- `lat` (string) *必需*: Example value: 43.6667

- `lon` (string) *必需*: Example value: -79.4

- `alt` (string): Example value: 113

- `start` (string) *必需*: Example value: 2020-01-01

- `end` (string) *必需*: Example value: 2020-01-01

- `tz` (string): Example value: America/Toronto

- `model` (string): Example value: 

- `freq` (string): Example value: 

- `units` (string): Example value: 



---


### `station_climate_data`

This endpoint provides climate normals for a particular weather station.

**端点**: `GET /stations/normals`


**参数**:

- `station` (string) *必需*: The Meteostat weather station identifier.

- `start` (number): The start year of the reference period.

- `end` (number): The end year of the reference period.

- `units` (string): The unit system of the meteorological parameters. Default is metric.

- `station` (string) *必需*: Example value: 10637

- `start` (string): Example value: 1961

- `end` (string): Example value: 1990

- `units` (string): Example value: 



---


### `point_climate_data`

This endpoint provides climate normals for any geo location.

**端点**: `GET /point/normals`


**参数**:

- `lat` (number) *必需*: The point's latitude.

- `lon` (number) *必需*: The point's longitude.

- `alt` (number): The point's elevation.

- `start` (number): The start year of the reference period.

- `end` (number): The end year of the reference period.

- `units` (string): The unit system of the meteorological parameters. Default is metric.

- `lat` (string) *必需*: Example value: 59.9127

- `lon` (string) *必需*: Example value: 10.7461

- `alt` (string): Example value: 26

- `start` (string): Example value: 1961

- `end` (string): Example value: 1990

- `units` (string): Example value: 



---


### `nearby_stations`

This endpoint provides a list of nearby weather stations for a given geographical location.

**端点**: `GET /stations/nearby`


**参数**:

- `lat` (number) *必需*: The location's latitude.

- `lon` (number) *必需*: The location's longitude.

- `limit` (number): The maximum number of weather stations. Default is 10.

- `radius` (number): The meter radius to search in. Default is 100000.

- `lat` (string) *必需*: Example value: 51.5085

- `lon` (string) *必需*: Example value: -0.1257

- `limit` (string): Example value: 

- `radius` (string): Example value: 



---


### `hourly_station_data`

This endpoint provides historical hourly observations for a particular weather station. The data provided through this endpoint is aggregated from multiple governmental interfaces.

**端点**: `GET /stations/hourly`


**参数**:

- `station` (string) *必需*: The Meteostat weather station identifier.

- `start` (string) *必需*: The start date of the period (YYYY-MM-DD).

- `end` (string) *必需*: The end date of the period (YYYY-MM-DD).

- `tz` (string): The time zone according to the tz database. Default is UTC.

- `model` (string): Example value: 

- `freq` (string): The time frequency of the records. Can be used for custom aggregation. Default is null.

- `units` (string): The unit system of the meteorological parameters. Default is metric.

- `station` (string) *必需*: Example value: 10637

- `start` (string) *必需*: Example value: 2020-01-01

- `end` (string) *必需*: Example value: 2020-01-01

- `tz` (string): Example value: Europe/Berlin

- `model` (string): Example value: 

- `freq` (string): Example value: 

- `units` (string): Example value: 



---


### `daily_station_data`

This endpoint provides historical daily statistics for a particular weather station. The data provided through this endpoint is aggregated from multiple governmental interfaces.

**端点**: `GET /stations/daily`


**参数**:

- `station` (string) *必需*: The Meteostat weather station identifier.

- `start` (string) *必需*: The start date of the period (YYYY-MM-DD).

- `end` (string) *必需*: The end date of the period (YYYY-MM-DD).

- `model` (string): Example value: 

- `freq` (string): The time frequency of the records. Can be used for custom aggregation. Default is null.

- `units` (string): The unit system of the meteorological parameters. Default is metric.

- `station` (string) *必需*: Example value: 10637

- `start` (string) *必需*: Example value: 2020-01-01

- `end` (string) *必需*: Example value: 2020-01-31

- `model` (string): Example value: 

- `freq` (string): Example value: 

- `units` (string): Example value: 



---



## 技术栈

- **FastMCP**: 快速、Pythonic 的 MCP 服务器框架
- **传输协议**: stdio
- **HTTP 客户端**: httpx

## 开发

此伺服器由 [API-to-MCP](https://github.com/BACH-AI-Tools/api-to-mcp) 工具自動生成。

版本: 1.0.0
