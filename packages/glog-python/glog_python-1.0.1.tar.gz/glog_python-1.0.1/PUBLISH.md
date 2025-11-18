# 发布 glog 到 PyPI

## 准备工作

### 1. 安装必要的工具

```bash
# 安装构建和上传工具
pip install --upgrade pip
pip install --upgrade build twine
```

### 2. 注册 PyPI 账号

- 访问 https://pypi.org/account/register/ 注册账号
- 访问 https://test.pypi.org/account/register/ 注册测试账号（可选，用于测试）

### 3. 配置 API Token（推荐）

在 PyPI 网站上创建 API token：
1. 登录 PyPI
2. 进入 Account settings -> API tokens
3. 创建新的 token
4. 保存 token（只显示一次）

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...你的token...

[testpypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...你的测试token...
```

## 发布步骤

### 方法一：完整发布流程

```bash
# 1. 清理旧的构建文件
rm -rf build/ dist/ *.egg-info

# 2. 构建分发包
python -m build

# 3. 检查构建的包
twine check dist/*

# 4. 上传到 TestPyPI（可选，用于测试）
twine upload --repository testpypi dist/*

# 5. 测试安装（从 TestPyPI）
pip install --index-url https://test.pypi.org/simple/ glog-python

# 6. 上传到正式 PyPI
twine upload dist/*
```

### 方法二：使用脚本一键发布

创建 `publish.sh` 脚本：

```bash
#!/bin/bash

set -e

echo "开始发布 glog 到 PyPI..."

# 清理
echo "1. 清理旧文件..."
rm -rf build/ dist/ *.egg-info glog.egg-info

# 构建
echo "2. 构建分发包..."
python -m build

# 检查
echo "3. 检查包..."
twine check dist/*

# 询问是否继续
read -p "是否上传到 PyPI? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "4. 上传到 PyPI..."
    twine upload dist/*
    echo "✅ 发布成功！"
else
    echo "❌ 取消发布"
fi
```

使用：
```bash
chmod +x publish.sh
./publish.sh
```

### 方法三：先测试后发布

```bash
# 1. 清理并构建
rm -rf build/ dist/ *.egg-info
python -m build

# 2. 上传到 TestPyPI 测试
twine upload --repository testpypi dist/*

# 3. 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ --no-deps glog-python

# 4. 测试功能
python -c "import glog; glog.info('Test message')"

# 5. 确认无误后上传到正式 PyPI
twine upload dist/*
```

## 安装使用

发布成功后，用户可以通过以下方式安装：

```bash
# 从 PyPI 安装
pip install glog-python

# 使用
python -c "import glog; glog.info('Hello glog')"
```

## 版本更新

更新版本时：

1. 修改 `glog/__init__.py` 中的 `__version__`
2. 修改 `setup.py` 中的 `version`
3. 修改 `pyproject.toml` 中的 `version`
4. 重新构建和上传

```bash
# 更新版本号
# 编辑 glog/__init__.py: __version__ = "1.0.1"
# 编辑 setup.py: version="1.0.1"
# 编辑 pyproject.toml: version = "1.0.1"

# 清理并重新构建
rm -rf build/ dist/ *.egg-info
python -m build

# 上传新版本
twine upload dist/*
```

## 常见问题

### 1. 包名已存在

如果 `glog-python` 已被占用，可以修改为其他名称：
- `glog-py`
- `python-glog`
- `glog-logger`

修改 `setup.py` 和 `pyproject.toml` 中的 `name` 字段。

### 2. 上传失败

```bash
# 检查网络连接
ping pypi.org

# 检查 token 是否正确
cat ~/.pypirc

# 使用详细模式查看错误
twine upload --verbose dist/*
```

### 3. 版本冲突

PyPI 不允许重复上传相同版本，需要：
- 删除 dist/ 目录
- 更新版本号
- 重新构建上传

### 4. 包结构检查

```bash
# 查看构建的包内容
tar -tzf dist/glog-python-1.0.0.tar.gz

# 或
unzip -l dist/glog_python-1.0.0-py3-none-any.whl
```

## 验证发布

发布成功后验证：

```bash
# 1. 在新环境中安装
python -m venv test_env
source test_env/bin/activate
pip install glog-python

# 2. 测试导入
python -c "import glog; print(glog.__version__)"

# 3. 运行示例
python -c "
import glog
logger = glog.default_logger().named('Test')
log = logger.with_field('trace-123', '')
log.info('Hello from glog!')
"

# 4. 清理
deactivate
rm -rf test_env
```

## 快速命令参考

```bash
# 安装工具
pip install build twine

# 构建
python -m build

# 检查
twine check dist/*

# 测试上传
twine upload --repository testpypi dist/*

# 正式上传
twine upload dist/*

# 清理
rm -rf build/ dist/ *.egg-info
```

## 相关链接

- PyPI 官网: https://pypi.org/
- TestPyPI: https://test.pypi.org/
- Twine 文档: https://twine.readthedocs.io/
- Python 打包指南: https://packaging.python.org/
