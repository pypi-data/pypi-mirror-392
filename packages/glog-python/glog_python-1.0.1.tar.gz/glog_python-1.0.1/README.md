# glog - Python Logging Library

一个兼容 Go glog 格式的 Python 日志库，支持 Python 3.7+。


github 地址 https://github.com/gw123/glog-python

pypi 下载 pip install glog-python==1.0.0

## 特性

- 🎯 与 Go glog 兼容的日志格式
- 📊 多种日志级别：DEBUG, INFO, WARN, ERROR, FATAL, PANIC
- 🏷️ 结构化日志字段支持
- 🔍 上下文日志追踪（trace_id, user_id 等）
- 📝 支持 Console 和 JSON 格式输出
- 🔧 灵活的配置选项
- 🧵 线程安全
- 🐍 兼容 Python 3.7+

## 安装

```bash
pip install glog-python
```

## 快速开始

### 基础使用

```python
import glog

# 简单日志
glog.info("Application started")
glog.warn("High memory usage")
glog.error("Connection failed")

# 格式化日志
glog.infof("User %s logged in", "Alice")
glog.debugf("Processing %d items", 42)
```

### 带字段的日志

```python
import glog

# 添加 trace_id 字段（显示在方括号中）
logger = glog.default_logger().named("Runner")
trace_id = "59d428f7843866bd2863561f23c0c657"
log = logger.with_field(trace_id, "")

log.info("🚀 Initializing Ollama model: gemma3:27b")
# 输出: [2025-11-15 17:10:29.461] [info] [Runner] main.py:10 [59d428f7843866bd2863561f23c0c657] 🚀 Initializing Ollama model: gemma3:27b

# 添加多个字段
plugin_name = "Plugin langchain_ollama_python"
log = logger.with_field(trace_id, "").with_field(plugin_name, "")
log.info("📤 Sending prompt to model...")
# 输出: [2025-11-15 17:10:29.503] [info] [Runner] main.py:15 [59d428f7843866bd2863561f23c0c657] [Plugin langchain_ollama_python] 📤 Sending prompt to model...
```

### 错误日志

```python
import glog

try:
    result = 1 / 0
except Exception as e:
    glog.with_error(e).error("Division failed")
```

### 上下文日志（请求追踪）

```python
import glog

# 初始化上下文
logger = glog.default_logger().named("API")
glog.to_context(logger)

# 添加追踪 ID
glog.add_trace_id("a1b2c3d4e5f6g7h8")

# 所有字段自动包含在日志中
log = glog.extract_entry()
log.info("Request started")
# 输出: [2025-11-15 17:10:29.461] [info] [API] main.py:10 [trace_id] Request started

# 添加更多字段
glog.add_field("user_id", "123")
glog.add_field("method", "POST")

log = glog.extract_entry()
log.info("Request completed")
# 输出: [2025-11-15 17:10:29.503] [info] [API] main.py:18 [trace_id] [user_id] [method] Request completed
```

### 自定义配置

```python
import glog
from glog import Level, Options

# 创建配置
options = Options(level=Level.DEBUG)
options.with_stdout_output_path()
options.with_output_path("logs/app.log")

# 应用配置
glog.set_default_logger_config(options)

glog.debug("Debug logging enabled")
```

### JSON 格式输出

```python
import glog
from glog import Options

options = Options()
options.with_json_encoding()
options.with_stdout_output_path()

glog.set_default_logger_config(options)

glog.info("This is JSON formatted")
# 输出: {"ts":"2024-01-01 12:00:00.000","level":"info","caller":"example.py:10","msg":"This is JSON formatted"}
```

### 命名日志器

```python
import glog

logger = glog.default_logger().named("api").named("users")
logger.info("User service started")
# 输出: [2024-01-01 12:00:00.000] [info] [api.users] example.py:5 User service started
```

## 日志级别

```python
from glog import Level

Level.DEBUG    # -1: 详细调试信息
Level.INFO     #  0: 一般信息（默认）
Level.WARN     #  1: 警告信息
Level.ERROR    #  2: 错误信息
Level.DPANIC   #  3: 开发环境 panic
Level.PANIC    #  4: Panic 并抛出异常
Level.FATAL    #  5: Fatal 并退出程序
```

## API 参考

### 包级函数

```python
# 基础日志
glog.debug(msg)
glog.info(msg)
glog.warn(msg)
glog.error(msg)

# 格式化日志
glog.debugf(format, *args)
glog.infof(format, *args)
glog.warnf(format, *args)
glog.errorf(format, *args)

# 创建带字段的日志器
glog.with_field(key, value) -> Logger
glog.with_error(err) -> Logger

# 配置
glog.set_default_logger_config(options)
glog.default_logger() -> Logger
```

### Logger 方法

```python
logger = glog.default_logger()

# 添加字段
logger.with_field(key, value) -> Logger
logger.with_fields(fields) -> Logger
logger.with_error(err) -> Logger

# 命名
logger.named(name) -> Logger

# 日志方法
logger.debug(*args)
logger.info(*args)
logger.warn(*args)
logger.error(*args)
logger.fatal(*args)  # 退出程序
logger.panic(*args)  # 抛出异常

# 格式化方法
logger.debugf(format, *args)
logger.infof(format, *args)
logger.warnf(format, *args)
logger.errorf(format, *args)
logger.fatalf(format, *args)
logger.panicf(format, *args)
```

### 上下文日志

```python
# 初始化上下文
glog.to_context(logger) -> ContextLogger

# 添加字段
glog.add_field(key, value)
glog.add_fields(fields)
glog.add_top_field(key, value)

# 特殊字段
glog.add_trace_id(trace_id)
glog.add_user_id(user_id)
glog.add_pathname(pathname)

# 提取
glog.extract_entry() -> Logger
glog.extract_trace_id() -> str
glog.extract_user_id() -> int
glog.extract_pathname() -> str
```

### 配置选项

```python
from glog import Options, Level, OutputPath, Encoding

options = Options(
    output_paths=[],           # 输出路径列表
    error_output_paths=[],     # 错误输出路径列表
    encoding=Encoding.CONSOLE, # 编码格式
    level=Level.INFO,          # 日志级别
    caller_skip=0              # 调用栈跳过层数
)

# 链式配置
options.with_stdout_output_path()
options.with_stderr_error_output_path()
options.with_output_path("logs/app.log")
options.with_console_encoding()
options.with_json_encoding()
options.with_level(Level.DEBUG)
options.with_caller_skip(1)
```

## 日志格式

### Console 格式（与 Go glog 兼容）

```
[2025-11-15 17:10:29.461] [info] [Runner] grpc_plugin_node.go:202 [59d428f7843866bd2863561f23c0c657] [Plugin langchain_ollama_python] 🚀 Initializing Ollama model: gemma3:27b
[2025-11-15 17:10:29.503] [info] [Runner] grpc_plugin_node.go:202 [59d428f7843866bd2863561f23c0c657] [Plugin langchain_ollama_python] 📤 Sending prompt to model...
[2025-11-15 17:10:30.596] [info] [Runner] grpc_plugin_node.go:202 [59d428f7843866bd2863561f23c0c657] [Plugin langchain_ollama_python] ✅ Model response received (10 chars)
```

格式说明：
- `[时间戳]` - 精确到毫秒（YYYY-MM-DD HH:MM:SS.mmm）
- `[日志级别]` - debug/info/warn/error 等
- `[日志器名称]` - 通过 `.named()` 设置，空则显示 `[]`
- `文件名:行号` - 自动获取调用位置（仅文件名）
- `[字段1] [字段2] ...` - 通过 `.with_field()` 添加的字段
- `消息内容` - 实际日志消息

### JSON 格式

```json
{"ts":"2025-11-15 17:10:29.461","level":"info","logger":"Runner","caller":"plugin/grpc_plugin_node.go:202","msg":"🚀 Initializing Ollama model: gemma3:27b","59d428f7843866bd2863561f23c0c657":"","Plugin langchain_ollama_python":""}
```

## 示例

查看 [examples/](https://github.com/gw123/glog-python/tree/main/examples) 目录获取更多示例：

- [basic_example.py](https://github.com/gw123/glog-python/blob/main/examples/basic_example.py) - 基础使用示例
- [context_example.py](https://github.com/gw123/glog-python/blob/main/examples/context_example.py) - 上下文日志示例
- [glog_format_example.py](https://github.com/gw123/glog-python/blob/main/examples/glog_format_example.py) - glog 格式示例
- [simple_usage.py](https://github.com/gw123/glog-python/blob/main/examples/simple_usage.py) - 简单使用示例

运行示例：

```bash
# 克隆仓库
git clone https://github.com/gw123/glog-python.git
cd glog-python

# 安装依赖
pip install glog-python

# 运行示例
python examples/basic_example.py
python examples/context_example.py
python examples/glog_format_example.py
python examples/simple_usage.py
```

## 与 Go glog 的对应关系

| Go glog | glog |
|---------|-------|
| `glog.Info()` | `glog.info()` |
| `glog.Infof()` | `glog.infof()` |
| `glog.WithField()` | `glog.with_field()` |
| `glog.WithError()` | `glog.with_error()` |
| `glog.ToContext()` | `glog.to_context()` |
| `glog.ExtractEntry()` | `glog.extract_entry()` |
| `glog.AddTraceID()` | `glog.add_trace_id()` |

## 兼容性

- Python 3.7+
- 使用 `contextvars` 实现上下文隔离（Python 3.7+）
- 线程安全
- 无外部依赖

## 许可证

MIT License
