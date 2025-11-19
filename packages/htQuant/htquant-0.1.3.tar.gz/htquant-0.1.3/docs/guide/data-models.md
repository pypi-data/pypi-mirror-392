# 数据模型

htQuant 使用 Pydantic 定义数据模型，提供数据验证和类型安全。

## HSStockData

沪深现货行情数据模型，包含完整的股票行情字段。

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | str | 标的代码（如 `SSE.STK.601236`） |
| `tradetime` | str | 成交时间 |
| `open` | float | 开盘价 |
| `close` | float | 收盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `volume` | float | 成交量 |
| `amount` | float | 成交额 |
| `sellVolume` | float | 内盘 |
| `buyVolume` | float | 外盘 |
| `openInterest` | float | 持仓量 |
| `tau` | float | tau 值 |
| `sigma` | float | 历史波动率 |
| `d2` | float | d2 值 |
| `delta` | float | Delta |
| `gamma` | float | Gamma |
| `vega` | float | Vega |
| `theta` | float | Theta |
| `rho` | float | Rho |
| `bsm_value` | float | 期权BSM价格 |
| `iv` | float | 隐含波动率 |
| `rf` | float | 无风险利率 |

**使用示例**

```python
from htQuant.htData.models import HSStockData

# 创建数据实例
data = HSStockData(
    code="SSE.STK.601236",
    tradetime="2024-01-01 09:30:00",
    open=10.50,
    close=10.80,
    high=11.00,
    low=10.20,
    volume=1000000.0,
    amount=10800000.0,
    sellVolume=500000.0,
    buyVolume=500000.0,
    openInterest=0.0,
    tau=0.0,
    sigma=0.0,
    d2=0.0,
    delta=0.0,
    gamma=0.0,
    vega=0.0,
    theta=0.0,
    rho=0.0,
    bsm_value=0.0,
    iv=0.0,
    rf=0.0
)

# 访问字段
print(f"股票代码: {data.code}")
print(f"收盘价: {data.close}")

# 转换为字典
data_dict = data.model_dump()

# 转换为 JSON
data_json = data.model_dump_json()
```

**数据验证**

```python
from pydantic import ValidationError

try:
    # 错误：缺少必需字段
    data = HSStockData(code="000001.SZ")
except ValidationError as e:
    print(e)

try:
    # 错误：类型不匹配
    data = HSStockData(
        code="000001.SZ",
        tradetime="2024-01-01",
        open="invalid",  # 应该是 float
        # ... 其他字段
    )
except ValidationError as e:
    print(e)
```

## 从 API 响应创建模型

```python
from htQuant.htData.http import HistoricalClient
from htQuant.htData.models import HSStockData

client = HistoricalClient()
client.connect()

# 获取数据
raw_data = client.get_stock_data(
    period="day1",
    data_type="stock",
    start="20240101 00:00:00",
    end="20240131 23:59:59",
    symbols=["000001.SZ"],
    params=""
)

# 转换为模型实例
stock_data = [HSStockData(**record) for record in raw_data]

# 使用模型
for data in stock_data:
    print(f"{data.tradetime}: {data.close}")
```

## 与 Pandas 集成

```python
import pandas as pd
from htQuant.htData.models import HSStockData

# 从 DataFrame 创建模型
df = pd.DataFrame(raw_data)
stock_data = [HSStockData(**row) for _, row in df.iterrows()]

# 从模型列表创建 DataFrame
stock_data = [HSStockData(**record) for record in raw_data]
df = pd.DataFrame([data.model_dump() for data in stock_data])
```

## 数据序列化

**JSON 序列化**

```python
import json
from htQuant.htData.models import HSStockData

data = HSStockData(...)

# 序列化
json_str = data.model_dump_json()

# 反序列化
data_restored = HSStockData.model_validate_json(json_str)
```

**字典转换**

```python
# 转换为字典
data_dict = data.model_dump()

# 从字典创建
data = HSStockData(**data_dict)

# 排除某些字段
data_dict = data.model_dump(exclude={'tau', 'sigma'})

# 只包含某些字段
data_dict = data.model_dump(include={'code', 'close', 'volume'})
```

## 自定义验证

```python
from pydantic import field_validator
from htQuant.htData.models import HSStockData

class ValidatedStockData(HSStockData):
    @field_validator('close')
    def validate_close(cls, v):
        if v <= 0:
            raise ValueError('收盘价必须大于0')
        return v
    
    @field_validator('volume')
    def validate_volume(cls, v):
        if v < 0:
            raise ValueError('成交量不能为负')
        return v
```

## 数据转换

**价格归一化**

```python
def normalize_prices(data_list):
    """归一化价格数据"""
    first_close = data_list[0].close
    return [
        {
            **data.model_dump(),
            'normalized_close': data.close / first_close
        }
        for data in data_list
    ]
```

**计算涨跌幅**

```python
def calculate_returns(data_list):
    """计算涨跌幅"""
    results = []
    for i in range(1, len(data_list)):
        prev_close = data_list[i-1].close
        curr_close = data_list[i].close
        return_pct = (curr_close - prev_close) / prev_close * 100
        
        results.append({
            **data_list[i].model_dump(),
            'return_pct': return_pct
        })
    
    return results
```

## 最佳实践

**使用类型提示**

```python
from typing import List
from htQuant.htData.models import HSStockData

def process_data(data: List[HSStockData]) -> None:
    for item in data:
        # IDE 会提供代码补全
        print(item.close)
```

**批量验证**

```python
def validate_batch(raw_data: list) -> list:
    validated = []
    for record in raw_data:
        try:
            validated.append(HSStockData(**record))
        except ValidationError as e:
            print(f"验证失败: {e}")
    return validated
```

**数据缓存**

```python
import pickle

# 保存
with open('stock_data.pkl', 'wb') as f:
    pickle.dump(stock_data, f)

# 加载
with open('stock_data.pkl', 'rb') as f:
    stock_data = pickle.load(f)
```

## 相关链接

- [HTTP 客户端](http-client.md)
