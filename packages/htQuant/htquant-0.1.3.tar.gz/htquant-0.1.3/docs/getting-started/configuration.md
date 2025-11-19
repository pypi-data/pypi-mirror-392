# 配置

htQuant 提供了灵活的配置系统，支持多种配置方式。

## 配置方式

配置按以下优先级加载（从高到低）：

1. 直接传递给类的参数
2. 环境变量（前缀 `HTQUANT_`）
3. `.env` 文件

## 环境变量配置

### 可用的环境变量

所有环境变量都使用 `HTQUANT_` 前缀：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `HTQUANT_HTTP_BASE_URL` | HTTP API 基础 URL | `http://your-api-url.com` |
| `HTQUANT_HTTP_USERNAME` | HTTP API 用户名 | `vue` |
| `HTQUANT_HTTP_PASSWORD` | HTTP API 密码 | `vue` |
| `HTQUANT_HTTP_TIMEOUT` | HTTP 请求超时时间（秒） | `30` |

### 设置环境变量

#### Windows (PowerShell)

```powershell
$env:HTQUANT_HTTP_BASE_URL = "http://your-api-url.com"
$env:HTQUANT_HTTP_USERNAME = "your_username"
$env:HTQUANT_HTTP_PASSWORD = "your_password"
$env:HTQUANT_HTTP_TIMEOUT = "60"
```

#### Linux/macOS (Bash)

```bash
export HTQUANT_HTTP_BASE_URL="http://your-api-url.com"
export HTQUANT_HTTP_USERNAME="your_username"
export HTQUANT_HTTP_PASSWORD="your_password"
export HTQUANT_HTTP_TIMEOUT="60"
```

## .env 文件配置

在项目根目录创建 `.env` 文件：

```bash
# HTTP 客户端配置
HTQUANT_HTTP_BASE_URL=http://your-api-url.com
HTQUANT_HTTP_USERNAME=your_username
HTQUANT_HTTP_PASSWORD=your_password
HTQUANT_HTTP_TIMEOUT=30
```

!!! warning "安全提示"
    `.env` 文件包含敏感信息，请勿提交到版本控制系统。
    建议将 `.env` 添加到 `.gitignore` 文件中。

## 代码配置

### 使用全局配置

```python
from htQuant.htData.config import settings

# 读取配置
print(f"Base URL: {settings.http_base_url}")
print(f"Username: {settings.http_username}")
print(f"Timeout: {settings.http_timeout}")
```

### 直接传参配置

```python
from htQuant.htData.http import HistoricalClient

# 创建客户端时传递配置
client = HistoricalClient(
    base_url="http://your-api-url.com",
    timeout=60
)

# 连接时传递凭证
client.connect(
    username="custom_user",
    password="custom_pass"
)
```

## 配置示例

### 示例 1：使用默认配置

```python
from htQuant.htData.http import HistoricalClient

# 使用所有默认配置
client = HistoricalClient()
client.connect()
```

### 示例 2：使用环境变量

```python
# 设置环境变量后
import os
os.environ["HTQUANT_HTTP_TIMEOUT"] = "30"

from htQuant.htData.http import HistoricalClient

# 自动使用环境变量中的配置
client = HistoricalClient()
```

### 示例 3：混合配置

```python
from htQuant.htData.http import HistoricalClient

# base_url 使用配置中的默认值
# timeout 使用自定义值
client = HistoricalClient(timeout=120)

# username/password 使用配置中的默认值
client.connect()
```

### 示例 4：完全自定义

```python
from htQuant.htData.http import HistoricalClient

# 所有参数都自定义
client = HistoricalClient(
    base_url="http://your-api-url.com",
    timeout=90
)

client.connect(
    username="prod_user",
    password="prod_password"
)
```

## 配置验证

验证配置是否正确加载：

```python
from htQuant.htData.config import settings

def validate_config():
    """验证配置"""
    print("当前配置:")
    print(f"  Base URL: {settings.http_base_url}")
    print(f"  Username: {settings.http_username}")
    print(f"  Password: {'*' * len(settings.http_password)}")
    print(f"  Timeout: {settings.http_timeout}s")
    
    # 检查必要的配置
    if not settings.http_base_url:
        print("⚠️  警告: Base URL 未配置")
    if not settings.http_username:
        print("⚠️  警告: Username 未配置")

validate_config()
```

## 最佳实践

- **使用 .env 文件**
   - 适合本地开发
   - 便于管理敏感信息
   - 添加到 `.gitignore`

- **使用环境变量**
   - 适合生产环境
   - 便于 CI/CD 集成

- **参数传递**
   - 适合临时配置
   - 适合多实例场景
   - 优先级最高

- **安全建议**
   - 不要在代码中硬编码密码
   - 使用环境变量或配置文件
   - 生产环境使用密钥管理服务

## 故障排查

### 配置未生效

```python
# 检查配置来源
from htQuant.htData.config import settings

print(settings.model_dump())
```

### 环境变量优先级

```python
import os

# 临时设置环境变量（最高优先级）
os.environ["HTQUANT_HTTP_TIMEOUT"] = "120"

# 重新加载配置
from htQuant.htData.config import Settings
new_settings = Settings()
print(new_settings.http_timeout)  # 120
```

## 下一步

- [HTTP 客户端](../guide/http-client.md) - 了解如何使用 HTTP 客户端
