# 安装

## 系统要求

- Python 3.8 或更高版本
- pip 包管理器
- htQuant账号及权限

## 使用 pip 安装

### 基础安装

```bash
pip install htQuant
```

## 验证安装

安装完成后，可以通过以下方式验证：

```python
import htQuant
print(f"htQuant 版本: {htQuant.__version__}")

# 验证主要模块
from htQuant import htData, HostsManager
print("✓ 安装成功！")
```

或者在命令行中：

```bash
python -c "import htQuant; print(htQuant.__version__)"
```

## 升级

升级到最新版本：

```bash
pip install --upgrade htQuant
```

## 卸载

如果需要卸载：

```bash
pip uninstall htQuant
```

## 常见问题

### 权限错误

如果安装时遇到权限错误，可以使用 `--user` 标志：

```bash
pip install --user htQuant
```

### 依赖冲突

如果遇到依赖冲突，建议使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装
pip install htQuant
```

### 网络问题

如果下载速度慢，可以使用国内镜像：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple htQuant
```

## 下一步

- [快速入门](quickstart.md) - 学习如何使用 htQuant
- [配置](configuration.md) - 配置你的环境
