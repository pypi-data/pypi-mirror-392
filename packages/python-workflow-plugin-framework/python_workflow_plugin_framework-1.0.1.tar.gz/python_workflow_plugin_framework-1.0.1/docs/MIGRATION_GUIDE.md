# 迁移指南 - 从原始代码到框架

本指南展示如何将现有的插件代码迁移到 Python Plugin Framework。

## 对比：原始代码 vs 框架代码

### 原始代码结构（~450 行）

```python
#!/usr/bin/env python3
import grpc
import json
import logging
from concurrent import futures
from grpc_reflection.v1alpha import reflection
from langchain_ollama import OllamaLLM
import node_plugin_pb2
import node_plugin_pb2_grpc

# 配置日志
logging.basicConfig(...)
logger = logging.getLogger('LangChainOllama')

class LangChainOllamaService(node_plugin_pb2_grpc.NodePluginServiceServicer):
    def __init__(self):
        self.node_config = None
        self.server_endpoint = None
        self.request_count = 0
        logger.info("Service initialized")

    def GetMetadata(self, request, context):
        """获取插件元数据 - 50+ 行"""
        return node_plugin_pb2.GetMetadataResponse(
            kind="langchain_ollama_python",
            parameters=[
                node_plugin_pb2.ParameterDef(...),
                node_plugin_pb2.ParameterDef(...),
                # ... 更多参数
            ]
        )

    def Init(self, request, context):
        """初始化节点 - 20+ 行"""
        try:
            self.node_config = json.loads(request.node_json)
            # ... 更多初始化代码
            return node_plugin_pb2.InitResponse(success=True)
        except Exception as e:
            return node_plugin_pb2.InitResponse(success=False, error=str(e))

    def Run(self, request, context):
        """执行节点 - 200+ 行"""
        # 提取 metadata
        metadata = dict(context.invocation_metadata())
        trace_id = ...
        
        # 转换参数
        parameters = self._convert_proto_map_to_dict(request.parameters)
        
        # 执行逻辑
        try:
            # ... 大量业务逻辑
            yield node_plugin_pb2.RunResponse(...)
        except Exception as e:
            yield node_plugin_pb2.RunResponse(type=ERROR, error=str(e))

    def TestSecret(self, request, context):
        """测试密钥 - 10+ 行"""
        return node_plugin_pb2.TestSecretResponse(...)

    def HealthCheck(self, request, context):
        """健康检查 - 20+ 行"""
        return node_plugin_pb2.HealthCheckResponse(...)

    def _convert_proto_value_to_python(self, proto_value):
        """转换 protobuf 值 - 30+ 行"""
        # ... 复杂的转换逻辑
        pass
    
    def _convert_proto_map_to_dict(self, proto_map):
        """转换 protobuf map - 10+ 行"""
        # ... 转换逻辑
        pass

def serve(port: int = 50052):
    """启动服务器 - 40+ 行"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = LangChainOllamaService()
    node_plugin_pb2_grpc.add_NodePluginServiceServicer_to_server(service, server)
    # ... 更多启动代码
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve(50052)
```

### 框架代码（~180 行）

```python
#!/usr/bin/env python3
import sys
from typing import Dict, Any, Iterator
from base_plugin import BasePluginService, serve_plugin
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class LangChainOllamaPlugin(BasePluginService):
    def __init__(self):
        super().__init__(plugin_name="LangChainOllama")

    def get_plugin_metadata(self) -> Dict[str, Any]:
        """定义插件元数据 - 只需返回字典"""
        return {
            "kind": "langchain_ollama_python",
            "node_type": "Node",
            "description": "LangChain v1.0 + Ollama plugin",
            "version": "1.0.0",
            "parameters": [
                {
                    "name": "model",
                    "type": "string",
                    "description": "Ollama model name",
                    "required": True,
                    "default_value": "llama3.2"
                },
                # ... 更多参数（简单的字典）
            ]
        }

    def execute(
        self,
        parameters: Dict[str, Any],
        parent_output: Dict[str, Any],
        global_vars: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Iterator[Dict[str, Any]]:
        """执行插件逻辑 - 只需关注业务逻辑"""
        
        # 获取参数（已经转换好了）
        model = parameters.get("model", "llama3.2")
        prompt_text = parameters.get("prompt", "")
        temperature = float(parameters.get("temperature", 0.7))
        
        # 发送日志（简单的字典）
        yield {"type": "log", "message": f"🚀 Initializing model: {model}"}
        
        # 业务逻辑
        llm = OllamaLLM(model=model, temperature=temperature)
        chain = llm | StrOutputParser()
        response_text = chain.invoke(prompt_text)
        
        # 返回结果（简单的字典）
        yield {
            "type": "result",
            "data": {
                "result": response_text,
                "model": model
            }
        }

    def health_check(self) -> tuple[bool, str]:
        """可选：自定义健康检查"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                return True, "✅ Ollama is healthy"
            return False, "⚠️ Ollama not responding"
        except Exception as e:
            return False, f"❌ Health check failed: {e}"

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50052
    serve_plugin(LangChainOllamaPlugin(), port)
```

## 迁移步骤

### 步骤 1：创建新文件

```bash
cp my_plugin.py my_plugin_new.py
```

### 步骤 2：导入框架

```python
# 删除这些导入
# import grpc
# from concurrent import futures
# from grpc_reflection.v1alpha import reflection
# import node_plugin_pb2
# import node_plugin_pb2_grpc

# 添加框架导入
from base_plugin import BasePluginService, serve_plugin
```

### 步骤 3：修改类定义

```python
# 原来
class MyService(node_plugin_pb2_grpc.NodePluginServiceServicer):
    def __init__(self):
        self.node_config = None
        # ...

# 现在
class MyPlugin(BasePluginService):
    def __init__(self):
        super().__init__(plugin_name="MyPlugin")
```

### 步骤 4：提取元数据

```python
# 原来的 GetMetadata 方法
def GetMetadata(self, request, context):
    return node_plugin_pb2.GetMetadataResponse(
        kind="my_plugin",
        parameters=[
            node_plugin_pb2.ParameterDef(
                name="param1",
                type="string",
                description="...",
                required=True,
                default_value="default"
            ),
        ]
    )

# 转换为
def get_plugin_metadata(self) -> Dict[str, Any]:
    return {
        "kind": "my_plugin",
        "parameters": [
            {
                "name": "param1",
                "type": "string",
                "description": "...",
                "required": True,
                "default_value": "default"
            },
        ]
    }
```

### 步骤 5：提取执行逻辑

```python
# 原来的 Run 方法（简化版）
def Run(self, request, context):
    # 提取参数
    parameters = self._convert_proto_map_to_dict(request.parameters)
    value = parameters.get("param1")
    
    # 发送日志
    yield node_plugin_pb2.RunResponse(
        type=node_plugin_pb2.RunResponse.LOG,
        log_message="Processing..."
    )
    
    # 执行逻辑
    result = self._process(value)
    
    # 返回结果
    yield node_plugin_pb2.RunResponse(
        type=node_plugin_pb2.RunResponse.RESULT,
        result_json=json.dumps({"result": result})
    )

# 转换为
def execute(self, parameters, parent_output, global_vars, context):
    # 获取参数（已经转换好了）
    value = parameters.get("param1")
    
    # 发送日志
    yield {"type": "log", "message": "Processing..."}
    
    # 执行逻辑
    result = self._process(value)
    
    # 返回结果
    yield {"type": "result", "data": {"result": result}}
```

### 步骤 6：可选的健康检查

```python
# 原来的 HealthCheck 方法
def HealthCheck(self, request, context):
    try:
        # 检查逻辑
        return node_plugin_pb2.HealthCheckResponse(
            healthy=True,
            message="Healthy"
        )
    except Exception as e:
        return node_plugin_pb2.HealthCheckResponse(
            healthy=False,
            message=str(e)
        )

# 转换为
def health_check(self) -> tuple[bool, str]:
    try:
        # 检查逻辑
        return True, "Healthy"
    except Exception as e:
        return False, str(e)
```

### 步骤 7：简化启动代码

```python
# 删除整个 serve() 函数（40+ 行）

# 替换为
if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50052
    serve_plugin(MyPlugin(), port)
```

### 步骤 8：删除辅助方法

```python
# 删除这些方法（框架已提供）
# def _convert_proto_value_to_python(self, proto_value): ...
# def _convert_proto_map_to_dict(self, proto_map): ...
# def Init(self, request, context): ...
# def TestSecret(self, request, context): ...
```

## 迁移检查清单

- [ ] 导入框架：`from base_plugin import BasePluginService, serve_plugin`
- [ ] 继承基类：`class MyPlugin(BasePluginService)`
- [ ] 调用父类构造函数：`super().__init__(plugin_name="...")`
- [ ] 实现 `get_plugin_metadata()` 返回字典
- [ ] 实现 `execute()` 使用 yield 返回字典
- [ ] 可选：实现 `health_check()` 返回元组
- [ ] 可选：实现 `test_credentials()` 返回元组
- [ ] 可选：实现 `on_init()` 初始化资源
- [ ] 简化启动代码：使用 `serve_plugin()`
- [ ] 删除不需要的辅助方法
- [ ] 测试插件

## 常见问题

### Q: 如何访问 trace_id？

```python
# 原来
metadata = dict(context.invocation_metadata())
trace_id = metadata.get('x-trace-id', 'unknown')

# 现在
def execute(self, parameters, parent_output, global_vars, context):
    trace_id = context.get("trace_id", "unknown")
```

### Q: 如何处理初始化？

```python
# 原来
def Init(self, request, context):
    self.node_config = json.loads(request.node_json)
    self.db = self._connect_db()
    return InitResponse(success=True)

# 现在
def on_init(self, node_config, workflow_entity):
    # node_config 已经是字典了
    self.db = self._connect_db()
```

### Q: 如何处理错误？

```python
# 原来
try:
    result = process()
    yield RunResponse(type=RESULT, result_json=json.dumps(result))
except Exception as e:
    yield RunResponse(type=ERROR, error=str(e))

# 现在
try:
    result = process()
    yield {"type": "result", "data": result}
except Exception as e:
    yield {"type": "error", "message": str(e)}
```

## 迁移效果

| 指标 | 迁移前 | 迁移后 | 改进 |
|------|--------|--------|------|
| 总行数 | ~450 | ~180 | -60% |
| 样板代码 | ~200 | ~0 | -100% |
| 核心逻辑 | ~250 | ~180 | -28% |
| 方法数量 | 8 | 2-5 | -38% to -75% |
| 复杂度 | 高 | 低 | ⬇️⬇️ |
| 可读性 | 中 | 高 | ⬆️⬆️ |
| 维护性 | 中 | 高 | ⬆️⬆️ |

## 完整示例

查看 `langchain_ollama_plugin.py` 了解完整的迁移示例。

## 下一步

1. 运行测试确保功能正常
2. 更新文档
3. 部署新版本
4. 删除旧代码

## 获取帮助

- 查看 [README.md](README.md) 了解 API 详情
- 查看 [QUICKSTART.md](QUICKSTART.md) 快速上手
- 查看示例插件了解最佳实践
