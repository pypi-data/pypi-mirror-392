# glog-python 集成说明

## 概述

框架已完全集成 `glog-python==1.0.0`，这是一个与 Go glog 格式完全兼容的 Python 日志库。

## 主要变更

### 1. 依赖更新

**requirements.txt:**
```txt
glog-python==1.0.0  # 新增
```

### 2. 框架核心更新

**base_plugin.py:**
- 移除 `logging` 模块
- 导入 `glog as log`
- 简化 `_setup_logger()` 方法
- 所有日志调用更新为 glog 格式

**主要变化：**
```python
# 之前
import logging
logger = logging.getLogger(name)
logger.info(f"Message: {value}")

# 现在
import glog as log
logger = log.default_logger().named(name)
logger.infof("Message: %s", value)
```

### 3. 日志方法更新

| 之前 | 现在 | 说明 |
|------|------|------|
| `logger.info(f"text {var}")` | `logger.infof("text %s", var)` | 使用格式化 |
| `logger.error(str(e))` | `logger.with_error(e).error("msg")` | 错误日志 |
| `logger.debug(msg)` | `logger.debug(msg)` | 保持不变 |

### 4. 新增功能

#### 带字段的日志
```python
# 添加 trace_id
logger = self.logger.with_field(trace_id, "")
logger.info("Processing...")

# 添加多个字段
logger = self.logger \
    .with_field(trace_id, "") \
    .with_field(f"Node {node_name}", "")
logger.info("Request completed")
```

#### 错误日志
```python
try:
    process()
except Exception as e:
    self.logger.with_error(e).error("Processing failed")
```

## 日志格式

### Console 格式（默认）

```
[2025-11-15 17:10:29.461] [info] [PluginName] file.py:10 [trace_id] [Node name] Message
```

**格式说明：**
- `[时间戳]` - 精确到毫秒（YYYY-MM-DD HH:MM:SS.mmm）
- `[日志级别]` - debug/info/warn/error
- `[Logger名称]` - 插件名称
- `文件名:行号` - 自动获取调用位置
- `[字段1] [字段2]` - 通过 with_field() 添加
- `消息内容` - 实际日志消息

### 与 Go glog 的兼容性

**Go 服务日志：**
```
[2025-11-15 17:10:29.461] [info] [Runner] grpc_plugin_node.go:202 [59d428f7843866bd2863561f23c0c657] [Plugin langchain_ollama_python] 🚀 Initializing model
```

**Python 插件日志：**
```
[2025-11-15 17:10:29.503] [info] [LangChainOllama] langchain_ollama_plugin.py:85 [59d428f7843866bd2863561f23c0c657] 📤 Sending prompt to model
```

格式完全一致，便于日志聚合和分析！

## 更新的文件

### 核心文件
- ✅ `base_plugin.py` - 完全集成 glog
- ✅ `requirements.txt` - 添加 glog-python 依赖

### 示例插件
- ✅ `example_plugin.py` - 更新为 glog 格式
- ✅ `langchain_ollama_plugin.py` - 更新为 glog 格式
- ✅ `http_api_plugin.py` - 更新为 glog 格式
- ✅ `glog_example_plugin.py` - 新增完整示例

### 文档
- ✅ `GLOG_USAGE.md` - 新增使用指南
- ✅ `README.md` - 更新日志说明
- ✅ `INDEX.md` - 添加 glog 文档索引
- ✅ `GLOG_INTEGRATION.md` - 本文件

### 工具
- ✅ `Makefile` - 添加 glog 示例命令

## 使用示例

### 基础使用

```python
from base_plugin import BasePluginService, serve_plugin

class MyPlugin(BasePluginService):
    def __init__(self):
        super().__init__(plugin_name="MyPlugin")
    
    def execute(self, parameters, parent_output, global_vars, context):
        # 简单日志
        self.logger.info("Processing started")
        
        # 格式化日志
        count = len(parameters)
        self.logger.infof("Received %d parameters", count)
        
        # 带 trace_id
        trace_id = context.get("trace_id")
        logger = self.logger.with_field(trace_id, "")
        logger.info("Processing with trace")
        
        yield {"type": "result", "data": {...}}
```

### 运行 glog 示例

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 glog 示例插件
make run-glog
# 或
python glog_example_plugin.py 50055
```

## 迁移指南

### 对于现有插件

如果你有使用旧版本框架的插件，需要做以下更新：

1. **更新依赖**
   ```bash
   pip install glog-python==1.0.0
   ```

2. **更新日志调用**
   ```python
   # 字符串拼接 → 格式化
   self.logger.info(f"Count: {count}")  # 旧
   self.logger.infof("Count: %d", count)  # 新
   
   # 错误日志
   self.logger.error(str(e))  # 旧
   self.logger.with_error(e).error("Failed")  # 新
   ```

3. **添加上下文字段（可选）**
   ```python
   trace_id = context.get("trace_id")
   logger = self.logger.with_field(trace_id, "")
   logger.info("Processing...")
   ```

### 兼容性

- ✅ 所有现有的 `logger.info()`, `logger.error()` 等调用仍然有效
- ✅ 可以逐步迁移到格式化日志
- ✅ 新功能（with_field, with_error）是可选的

## 优势

### 1. 与 Go 服务统一
- 日志格式完全一致
- 便于日志聚合和分析
- 统一的追踪体验

### 2. 结构化日志
- 字段自动格式化
- 易于解析和搜索
- 支持日志分析工具

### 3. 更好的性能
- 格式化日志避免字符串拼接
- 条件日志（字段只在需要时添加）

### 4. 更好的错误处理
- `with_error()` 自动包含堆栈
- 错误信息结构化

## 示例输出

### 简单日志
```
[2025-11-15 17:10:29.461] [info] [MyPlugin] plugin.py:10 Processing started
```

### 格式化日志
```
[2025-11-15 17:10:29.503] [info] [MyPlugin] plugin.py:15 Received 5 parameters
```

### 带 trace_id
```
[2025-11-15 17:10:29.596] [info] [MyPlugin] plugin.py:20 [59d428f7843866bd2863561f23c0c657] Processing with trace
```

### 带多个字段
```
[2025-11-15 17:10:30.123] [info] [MyPlugin] plugin.py:25 [59d428f7843866bd2863561f23c0c657] [Node my_node] Request completed
```

### 错误日志
```
[2025-11-15 17:10:31.456] [error] [MyPlugin] plugin.py:30 [59d428f7843866bd2863561f23c0c657] Processing failed
error="division by zero"
Traceback (most recent call last):
  File "plugin.py", line 28, in execute
    result = 1 / 0
ZeroDivisionError: division by zero
```

## 测试

运行 glog 示例插件查看不同的日志格式：

```bash
# 启动插件
python glog_example_plugin.py 50055

# 在另一个终端测试不同的操作
# simple - 简单日志
# formatted - 格式化日志
# traced - 带追踪的日志
# error - 错误日志
# progress - 进度日志
```

## 参考文档

- [GLOG_USAGE.md](GLOG_USAGE.md) - 详细使用指南
- [README.md](README.md) - 框架文档
- [glog_example_plugin.py](glog_example_plugin.py) - 完整示例
- glog-python: https://pypi.org/project/glog-python/1.0.0/

## 总结

✅ 框架已完全集成 glog-python  
✅ 与 Go glog 格式完全兼容  
✅ 所有示例已更新  
✅ 提供完整文档和示例  
✅ 向后兼容，可逐步迁移  

**开始使用 glog 让你的日志更专业！** 🚀
