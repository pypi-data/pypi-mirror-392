# HTTP 客户端使用指南

HTTP 客户端用于获取历史金融数据，支持多种品种和周期。

## 基本用法

**创建客户端**

```python
from htQuant.htData.http import HistoricalClient

# 使用默认配置
client = HistoricalClient()

# 自定义配置
client = HistoricalClient(
    base_url="http://your-api-url.com",
    timeout=30
)
```

**连接认证**

```python
# 使用配置中的凭证
client.connect()

# 使用自定义凭证
client.connect(username="your_user", password="your_pass")
```

**获取数据**

```python
data = client.get_stock_data(
    period="day1",
    data_type="stock",
    start="20240101 00:00:00",
    end="20240131 23:59:59",
    symbols=["000001.SZ"],
    params=""
)
```

**关闭连接**

```python
client.close()
```

## 参数说明

**period（数据周期）**

| 值 | 说明 |
|----|------|
| `min1` | 1分钟线 |
| `min5` | 5分钟线 |
| `day1` | 日线 |

**data_type（数据类型）**

| 值 | 说明 |
|----|------|
| `stock` | 股票 |
| `index` | 指数 |
| `etf` | ETF |
| `hk` | 港股 |
| `bond` | 债券 |
| `option` | 期权 |
| `bsm` | BSM期权 |

**symbols（股票代码）**

- 格式：`代码`
- 示例：`000001`、`600000`
- 限制：单次最多 10 个

**时间格式**

- 格式：`yyyyMMdd HH:mm:ss`
- 示例：`20240101 09:30:00`
- 限制：时间跨度不超过 1 年

## 常见问题

**Q: 如何获取最新数据？**

A: 设置 `end` 为当前时间：

```python
from datetime import datetime

now = datetime.now()
data = client.get_stock_data(
    period="day1",
    data_type="stock",
    start="20240101 00:00:00",
    end=now.strftime("%Y%m%d %H:%M:%S"),
    symbols=["000001.SZ"],
    params=""
)
```

**Q: 数据量很大怎么办？**

A: 使用生成器模式分批处理：

```python
def fetch_in_batches(symbols, batch_size=10):
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        yield client.get_stock_data(
            period="day1",
            data_type="stock",
            start="20240101 00:00:00",
            end="20240131 23:59:59",
            symbols=batch,
            params=""
        )

# 使用
for batch_data in fetch_in_batches(all_symbols):
    process_batch(batch_data)
```

## 相关链接

- [配置](../getting-started/configuration.md)
- [数据模型](data-models.md)
