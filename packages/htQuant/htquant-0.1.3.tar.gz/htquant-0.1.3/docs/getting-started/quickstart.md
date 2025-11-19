# 快速入门

本指南将帮助你快速开始使用 htQuant。

## 基本概念

htQuant 主要包含两个部分：

- **htData** - 行情数据模块，提供历史数据和实时数据接口

- **utils** - 提供各种辅助工具，如 HostsManager

## 第一个程序

### 1. 导入模块

```python
from htQuant.htData.http import HistoricalClient
from htQuant.htData.config import settings
```

### 2. 创建客户端

#### 使用.env配置
- .env 文件配置
```python
HTQUANT_HTTP_BASE_URL=http://your-api-url.com
HTQUANT_HTTP_TIMEOUT=30
```
- 使用.env配置创建客户端
```python
client = HistoricalClient()
```

#### 自定义配置
```python
client = HistoricalClient(
    base_url="http://your-api-url.com",
    timeout=30
)
```

### 3. 登录认证

#### 使用配置中的凭证
- .env 文件配置
```python
HTQUANT_HTTP_USERNAME=your_username
HTQUANT_HTTP_PASSWORD=your_password
```
- 使用配置中的凭证登录
```python
client.connect()
```

#### 使用参数凭证
```python
client.connect(username="your_username", password="your_password")
```

### 4. 获取数据

```python
# 获取股票日线数据
data = client.get_stock_data(
    period="day1",           # 数据周期：day1=日线, min1=1分钟, min5=5分钟
    data_type="stock",       # 数据类型：stock=股票, index=指数, etf=ETF
    start="20240101 00:00:00",  # 开始时间
    end="20240131 23:59:59",    # 结束时间
    symbols=["000001", "600000"],  # 股票代码列表（最多10个）
    params=""                # 其他参数
)

# 处理数据
for record in data:
    print(f"代码: {record['code']}, "
          f"时间: {record['tradetime']}, "
          f"收盘价: {record['close']}")
```

### 5. 完整示例

```python
from htQuant.htData.http import HistoricalClient

def main():
    # 创建客户端
    client = HistoricalClient()
    
    try:
        # 登录
        print("正在登录...")
        client.connect()
        print("✓ 登录成功")
        
        # 获取平安银行近期日线数据
        print("\n正在获取数据...")
        data = client.get_stock_data(
            period="day1",
            data_type="stock",
            start="20240101 00:00:00",
            end="20240131 23:59:59",
            symbols=["000001"],
            params=""
        )
        
        print(f"✓ 获取到 {len(data)} 条数据\n")
        
        # 显示前5条数据
        for record in data[:5]:
            print(f"{record['tradetime']}: "
                  f"开 {record['open']:.2f}, "
                  f"高 {record['high']:.2f}, "
                  f"低 {record['low']:.2f}, "
                  f"收 {record['close']:.2f}, "
                  f"量 {record['volume']:.0f}")
    
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    finally:
        # 登出
        client.close()
        print("\n✓ 已登出")

if __name__ == "__main__":
    main()
```

## 环境变量配置

### 创建 .env 文件

在项目根目录创建 `.env` 文件：

```bash
# HTTP 客户端配置
HTQUANT_HTTP_BASE_URL=http://your-api-url.com
HTQUANT_HTTP_USERNAME=your_username
HTQUANT_HTTP_PASSWORD=your_password
HTQUANT_HTTP_TIMEOUT=30
```

### 使用配置

```python
from htQuant.htData.config import settings

# 配置会自动从环境变量加载
print(f"Base URL: {settings.http_base_url}")
print(f"Timeout: {settings.http_timeout}")

# 使用默认配置创建客户端
client = HistoricalClient()
client.connect()  # 使用配置中的用户名和密码
```

## Hosts 配置

如果需要配置 hosts 映射：

```python
from htQuant import HostsManager

# 添加 hosts 映射（需要管理员权限）
try:
    HostsManager.add_host(
        "HOST IP地址",
        "Host 域名地址",
        "Host 描述"
    )
    print("✓ Hosts 配置成功")
except PermissionError:
    print("✗ 需要管理员权限")
```

## 数据类型说明

### period（周期）

- `min1` - 1分钟线
- `min5` - 5分钟线
- `day1` - 日线

### data_type（数据类型）

- `stock` - 股票
- `index` - 指数
- `etf` - ETF
- `hk` - 港股
- `bond` - 债券
- `option` - 期权
- `bsm` - BSM期权

### 股票代码格式

- 深圳股票：`000001`
- 上海股票：`600000`
- 最多一次查询 10 个股票

## 注意事项

1. **时间格式**：必须使用 `yyyyMMdd HH:mm:ss` 格式
2. **时间范围**：单次查询时间跨度不能超过 1 年
3. **股票数量**：单次查询最多 10 个股票代码
4. **权限要求**：需要有效的 htQuant 账号

## 下一步

- [配置详解](configuration.md) - 了解详细的配置选项
- [HTTP 客户端](../guide/http-client.md) - 深入了解 HTTP 客户端
- [数据模型](../guide/data-models.md) - 了解数据结构
