# glog 上传到 PyPI 官方库指南

## 📦 项目已准备就绪

你的 glog 日志库已经完全准备好上传到 PyPI！

## 🚀 快速上传（3步完成）

### 第一步：安装上传工具

```bash
pip install --upgrade build twine
```

### 第二步：构建包（已完成✅）

```bash
python -m build
```

当前已构建的包：
- `dist/glog_python-1.0.0-py3-none-any.whl`
- `dist/glog_python-1.0.0.tar.gz`

### 第三步：上传到 PyPI

```bash
# 方式1：使用脚本（推荐）
./publish.sh

# 方式2：手动上传
twine upload dist/*
```

## 📝 详细步骤

### 1. 注册 PyPI 账号

访问 https://pypi.org/account/register/ 注册账号

### 2. 创建 API Token

1. 登录 PyPI
2. 进入 Account settings -> API tokens
3. 点击 "Add API token"
4. 设置 Token name（如：glog-upload）
5. Scope 选择 "Entire account"
6. 创建并复制 token（只显示一次！）

### 3. 配置认证

创建 `~/.pypirc` 文件：

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-你的token粘贴在这里

[testpypi]
username = __token__
password = pypi-你的测试token粘贴在这里
EOF

chmod 600 ~/.pypirc
```

### 4. 上传

```bash
# 检查包
twine check dist/*

# 上传到 PyPI
twine upload dist/*
```

## 🧪 先测试后发布（推荐）

```bash
# 1. 上传到测试环境
twine upload --repository testpypi dist/*

# 2. 从测试环境安装
pip install --index-url https://test.pypi.org/simple/ glog-python

# 3. 测试功能
python -c "import glog; glog.info('Test message')"

# 4. 确认无误后上传到正式环境
twine upload dist/*
```

## ✅ 上传成功后

用户可以通过以下方式安装：

```bash
pip install glog-python
```

使用：

```python
import glog

logger = glog.default_logger().named("Runner")
trace_id = "59d428f7843866bd2863561f23c0c657"
log = logger.with_field(trace_id, "")
log.info("🚀 Initializing Ollama model: gemma3:27b")
```

## 📊 包信息

- **包名**: `glog-python`
- **版本**: `1.0.0`
- **Python 支持**: 3.7+
- **依赖**: 无
- **大小**: ~21KB (wheel), ~61KB (源码)

## 🔄 更新版本

当需要发布新版本时：

```bash
# 1. 更新版本号
# 编辑 glog/__init__.py: __version__ = "1.0.1"
# 编辑 setup.py: version="1.0.1"
# 编辑 pyproject.toml: version = "1.0.1"

# 2. 清理旧构建
rm -rf build/ dist/ *.egg-info

# 3. 重新构建
python -m build

# 4. 上传新版本
twine upload dist/*
```

## ❓ 常见问题

### Q: 包名 glog-python 已被占用怎么办？

A: 修改为其他名称，如：
- `glog-py`
- `python-glog`
- `glog-logger`

在 `setup.py` 和 `pyproject.toml` 中修改 `name` 字段。

### Q: 上传时提示认证失败？

A: 检查：
1. Token 是否正确复制（包含 `pypi-` 前缀）
2. `~/.pypirc` 文件权限是否正确（600）
3. Token 是否已过期

### Q: 如何删除已上传的版本？

A: PyPI 不允许删除版本，只能：
1. 标记为 "yanked"（不推荐安装）
2. 上传新版本

### Q: 如何查看包的下载统计？

A: 访问 https://pypistats.org/packages/glog-python

## 📚 相关文档

- [完整发布指南](PUBLISH.md)
- [快速命令参考](COMMANDS.md)
- [项目 README](README.md)
- [快速开始](QUICK_START.md)

## 🔗 有用的链接

- PyPI 官网: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Python 打包指南: https://packaging.python.org/
- Twine 文档: https://twine.readthedocs.io/

## 💡 提示

1. **首次上传建议先用 TestPyPI 测试**
2. **保存好 API Token，只显示一次**
3. **版本号一旦上传不能重复使用**
4. **上传前务必运行测试确保代码正常**

---

准备好了吗？运行 `./publish.sh` 开始发布！🚀
