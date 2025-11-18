# glog-python 示例

这个目录包含了 glog-python 的使用示例。

## 安装

```bash
pip install glog-python
```

## 示例列表

### 1. basic_example.py - 基础使用示例
展示 glog-python 的基本功能：
- 基础日志记录
- 格式化日志
- 带字段的日志
- 错误日志
- 自定义配置
- JSON 格式输出
- 命名日志器

运行：
```bash
python examples/basic_example.py
```

### 2. context_example.py - 上下文日志示例
展示如何使用上下文日志进行请求追踪：
- 请求处理器示例
- 嵌套操作追踪
- 错误处理
- 上下文值提取

运行：
```bash
python examples/context_example.py
```

### 3. glog_format_example.py - glog 格式示例
展示与 Go glog 兼容的日志格式：
- 插件风格日志
- 上下文日志器
- 请求追踪
- 不同日志级别
- 错误日志
- 格式化日志

运行：
```bash
python examples/glog_format_example.py
```

### 4. simple_usage.py - 简单使用示例
快速入门示例，展示最常用的功能：
- 基础日志
- 带 trace ID 的日志
- 多字段日志
- 上下文日志器
- 格式化日志

运行：
```bash
python examples/simple_usage.py
```

## 快速开始

```python
import glog

# 简单日志
glog.info("Application started")

# 带字段的日志
logger = glog.default_logger().named("Runner")
trace_id = "59d428f7843866bd2863561f23c0c657"
log = logger.with_field(trace_id, "")
log.info("🚀 Initializing Ollama model: gemma3:27b")

# 上下文日志
logger = glog.default_logger().named("API")
glog.to_context(logger)
glog.add_trace_id("a1b2c3d4e5f6g7h8")
log = glog.extract_entry()
log.info("Request started")
```

## 更多信息

- GitHub: https://github.com/gw123/glog-python
- PyPI: https://pypi.org/project/glog-python/
- 文档: [README.md](https://github.com/gw123/glog-python/blob/main/README.md)
