# htQuant

欢迎使用 **htQuant** 量化 Python 框架！

## 简介

htQuant 是以 Python 库的形式提供策略交易所需要的行情和相关的 API 接口。

## 主要特性

### 📊 htData 行情模块

- **HTTP 客户端** - 获取历史行情数据
  - 支持股票、指数、ETF、港股、债券、期权等多种品种
  - 支持分钟线、日线等多种周期
  - 内置重试机制，确保数据获取稳定性
  - 支持 OAuth 2.0 认证

- **配置系统** - 灵活的配置管理
  - 支持 `.env` 环境变量配置
  - 支持参数化配置

- **数据模型** - 完善的数据结构
  - `HSStockData` - 沪深现货行情数据
  - 基于 Pydantic 的数据验证

### 🛠️ 工具类

- **HostsManager** - 跨平台 hosts 文件管理
  - 添加/更新/删除 hosts 映射
  - 备份和恢复 hosts 文件
  - 自动权限检查
  - 支持 Windows、Linux、macOS

## 快速开始

### 安装

```bash
pip install htQuant
```

### 基本使用

#### 获取历史数据

```python
from htQuant.htData.http import HistoricalClient

# 创建客户端
client = HistoricalClient()

# 登录
client.connect()

# 获取股票数据
data = client.get_stock_data(
    period="day1",
    data_type="stock",
    start="20240101 00:00:00",
    end="20240131 23:59:59",
    symbols=["000001.SZ"],
    params=""
)

# 处理数据
for record in data:
    print(record)
```

#### 使用 HostsManager

```python
from htQuant import HostsManager

# 添加 hosts 映射（需要管理员权限）
HostsManager.add_host("your_ip", "your_hostname")

# 列出自定义的 hosts
hosts = HostsManager.list_custom_hosts()
for host in hosts:
    print(f"{host['ip']} -> {host['hostname']}")
```

## 环境要求

- Python 3.8+
- 相关账号及权限

## 文档导航

- [快速开始](getting-started/installation.md) - 安装和快速入门
- [用户指南](guide/http-client.md) - 详细的使用说明
- [更新日志](changelog.md) - 版本更新记录

## 支持与反馈

- htQuant量化团队

## 许可证

本项目由 htQuant 量化团队开发维护。
---

**htQuant Team** © 2025