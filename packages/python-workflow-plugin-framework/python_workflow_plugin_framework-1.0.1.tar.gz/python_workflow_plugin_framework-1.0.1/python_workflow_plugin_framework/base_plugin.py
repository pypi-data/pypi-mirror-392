#!/usr/bin/env python3
"""
Python Plugin Framework - Base Plugin Class
通用的 Python 插件基类，简化插件开发
"""

import grpc
import json
import logging
import glog
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Iterator, Optional
from concurrent import futures

# gRPC 反射支持
from grpc_reflection.v1alpha import reflection

# 导入生成的 protobuf 代码
from . import node_plugin_pb2
from . import node_plugin_pb2_grpc


class BasePluginService(node_plugin_pb2_grpc.NodePluginServiceServicer, ABC):
    """
    插件服务基类
    
    子类只需要实现以下方法：
    - get_plugin_metadata(): 返回插件元数据
    - execute(): 执行插件的核心逻辑
    - health_check(): 可选，自定义健康检查
    """

    def __init__(self, plugin_name: str = "BasePlugin"):
        self.plugin_name = plugin_name
        self.node_config = None
        self.workflow_entity = None
        self.server_endpoint = None
        self.request_count = 0
        self.logger = self._setup_logger()
        self.logger.info(f"🎬 {plugin_name} initialized")

    def _setup_logger(self):
        """设置日志记录器 - 使用 glog"""
        # 创建命名的 logger
        logger = glog.default_logger().named(self.plugin_name)
        return logger

    # ==================== 抽象方法（子类必须实现） ====================

    @abstractmethod
    def get_plugin_metadata(self) -> Dict[str, Any]:
        """
        返回插件元数据
        
        Returns:
            dict: 包含以下字段的字典
                - kind: str, 插件类型标识
                - node_type: str, 节点类型
                - description: str, 插件描述
                - version: str, 版本号
                - parameters: List[Dict], 参数定义列表
                - credential_type: str, 可选，凭证类型
        """
        pass

    @abstractmethod
    def execute(
        self,
        parameters: Dict[str, Any],
        parent_output: Dict[str, Any],
        global_vars: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Iterator[Dict[str, Any]]:
        """
        执行插件核心逻辑（生成器函数）
        
        Args:
            parameters: 节点参数
            parent_output: 父节点输出
            global_vars: 全局变量
            context: 上下文信息（包含 trace_id, node_name 等）
        
        Yields:
            dict: 输出消息，格式为：
                - {"type": "log", "message": "日志消息"}
                - {"type": "result", "data": {...}}
                - {"type": "error", "message": "错误消息"}
        """
        pass

    # ==================== 可选方法（子类可以覆盖） ====================

    def health_check(self) -> tuple[bool, str]:
        """
        健康检查（子类可以覆盖）
        
        Returns:
            tuple: (is_healthy: bool, message: str)
        """
        return True, f"✅ {self.plugin_name} is healthy"

    def test_credentials(self, credentials: Dict[str, Any]) -> tuple[bool, str]:
        """
        测试凭证（子类可以覆盖）
        
        Args:
            credentials: 凭证信息
        
        Returns:
            tuple: (is_valid: bool, message: str)
        """
        return True, "No credentials required"

    def on_init(self, node_config: Dict[str, Any], workflow_entity: Optional[Dict[str, Any]]):
        """
        初始化回调（子类可以覆盖）
        
        Args:
            node_config: 节点配置
            workflow_entity: 工作流实体
        """
        pass

    # ==================== gRPC 服务方法实现 ====================

    def GetMetadata(self, request, context):
        """获取插件元数据"""
        self.logger.info("📋 GetMetadata called")
        try:
            metadata = self.get_plugin_metadata()
            
            # 转换参数定义
            parameters = []
            for param in metadata.get("parameters", []):
                parameters.append(node_plugin_pb2.ParameterDef(
                    name=param["name"],
                    type=param["type"],
                    description=param.get("description", ""),
                    required=param.get("required", False),
                    default_value=str(param.get("default_value", ""))
                ))
            
            return node_plugin_pb2.GetMetadataResponse(
                kind=metadata.get("kind", "unknown"),
                node_type=metadata.get("node_type", "Node"),
                credential_type=metadata.get("credential_type", ""),
                description=metadata.get("description", ""),
                version=metadata.get("version", "1.0.0"),
                parameters=parameters
            )
        except Exception as e:
            self.logger.error(f"❌ GetMetadata failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return node_plugin_pb2.GetMetadataResponse()

    def Init(self, request, context):
        """初始化节点"""
        self.logger.info("🔧 Init called")
        try:
            self.node_config = json.loads(request.node_json)
            node_name = self.node_config.get('name', 'unknown')
            self.logger.infof("   Node name: %s", node_name)
            
            if request.workflow_entity_json:
                self.workflow_entity = json.loads(request.workflow_entity_json)
                self.logger.info("   Workflow entity loaded")
            
            self.server_endpoint = request.server_endpoint
            if self.server_endpoint:
                self.logger.infof("   Server endpoint: %s", self.server_endpoint)
            
            # 调用子类的初始化回调
            self.on_init(self.node_config, self.workflow_entity)
            
            self.logger.info("✅ Init successful")
            return node_plugin_pb2.InitResponse(success=True, error="")
        except Exception as e:
            self.logger.with_error(e).error("❌ Init failed")
            return node_plugin_pb2.InitResponse(
                success=False,
                error=f"Init failed: {str(e)}"
            )

    def Run(self, request, context):
        """执行节点（流式响应）"""
        self.request_count += 1
        request_id = self.request_count
        start_time = datetime.now()
        
        # 提取上下文信息
        ctx = self._extract_context(context, request_id)
        
        # 创建带有 trace_id 和其他字段的 logger
        run_logger = self.logger.with_field(ctx['trace_id'], "")
        if ctx['node_name'] != 'unknown':
            run_logger = run_logger.with_field(f"Node {ctx['node_name']}", "")
        
        run_logger.info("=" * 60)
        run_logger.infof("🚀 Run called (Request #%d)", request_id)
        run_logger.infof("Workflow: %s , Node: %s (type: %s) ",ctx['workflow_name'],  ctx['node_name'], ctx['node_type'])
#         if ctx['workflow_instance_id']:
#             run_logger.infof("   Instance ID: %s", ctx['workflow_instance_id'])
#         run_logger.infof("🔗 Trace ID: %s", ctx['trace_id'])
        run_logger.info("=" * 60)
        
        try:
            # 解析请求参数
            parameters = self._convert_proto_map_to_dict(request.parameters)
            parent_output = self._convert_proto_map_to_dict(request.parent_output)
            global_vars = self._convert_proto_map_to_dict(request.global_vars)
            
            run_logger.infof("📥 Parameters: %s", list(parameters.keys()))
            run_logger.infof("   Parent output: %s", list(parent_output.keys()))
            run_logger.infof("   Global vars: %s", list(global_vars.keys()))
            
            # 调用子类的执行方法
            for output in self.execute(parameters, parent_output, global_vars, ctx):
                output_type = output.get("type")
                
                if output_type == "log":
                    yield node_plugin_pb2.RunResponse(
                        type=node_plugin_pb2.RunResponse.LOG,
                        log_message=output.get("message", "")
                    )
                elif output_type == "result":
                    result_data = output.get("data", {})
                    # 添加元数据
                    if "metadata" not in result_data:
                        result_data["metadata"] = {}
                    result_data["metadata"].update({
                        "request_id": request_id,
                        "trace_id": ctx["trace_id"],
                        "node_name": ctx["node_name"],
                        "workflow_name": ctx["workflow_name"]
                    })
                    
                    yield node_plugin_pb2.RunResponse(
                        type=node_plugin_pb2.RunResponse.RESULT,
                        result_json=json.dumps(result_data, ensure_ascii=False),
                        branch_index=output.get("branch_index", 0)
                    )
                elif output_type == "error":
                    yield node_plugin_pb2.RunResponse(
                        type=node_plugin_pb2.RunResponse.ERROR,
                        error=output.get("message", "Unknown error")
                    )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            run_logger.info("=" * 60)
            run_logger.infof("✅ Request #%d completed in %.2fs", request_id, duration)
            run_logger.info("=" * 60)
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            run_logger.error("=" * 60)
            run_logger.errorf("❌ Request #%d failed after %.2fs", request_id, duration)
            run_logger.with_error(e).error("   Execution error")
            run_logger.error("=" * 60)
            
            yield node_plugin_pb2.RunResponse(
                type=node_plugin_pb2.RunResponse.ERROR,
                error=f"Execution failed: {str(e)}\n{traceback.format_exc()}"
            )

    def TestSecret(self, request, context):
        """测试密钥"""
        self.logger.info("🔑 TestSecret called")
        try:
            credentials = json.loads(request.credential_json) if request.credential_json else {}
            is_valid, message = self.test_credentials(credentials)
            
            self.logger.infof("   Result: %s", message)
            return node_plugin_pb2.TestSecretResponse(
                success=is_valid,
                error="" if is_valid else message
            )
        except Exception as e:
            self.logger.with_error(e).error("❌ TestSecret failed")
            return node_plugin_pb2.TestSecretResponse(
                success=False,
                error=str(e)
            )

    def HealthCheck(self, request, context):
        """健康检查"""
        self.logger.info("🏥 HealthCheck called")
        try:
            is_healthy, message = self.health_check()
            self.logger.infof("   Result: %s", message)
            return node_plugin_pb2.HealthCheckResponse(
                healthy=is_healthy,
                message=message
            )
        except Exception as e:
            self.logger.with_error(e).error("❌ HealthCheck failed")
            return node_plugin_pb2.HealthCheckResponse(
                healthy=False,
                message=f"Health check failed: {str(e)}"
            )

    # ==================== 辅助方法 ====================

    def _decode_metadata_value(self, value: str) -> str:
        """解码metadata值"""
        import base64
        try:
            # 尝试base64解码
            decoded = base64.urlsafe_b64decode(value).decode('utf-8')
            return decoded
        except:
            # 如果解码失败，返回原始值
            return value

    def _extract_context(self, grpc_context, request_id: int) -> Dict[str, Any]:
        """从 gRPC context 中提取上下文信息"""
        ctx = {
            "trace_id": f"local-{request_id}",
            "span_id": "unknown",
            "trace_flags": "00",
            "node_name": "unknown",
            "node_type": "unknown",
            "workflow_name": "unknown",
            "workflow_instance_id": ""
        }
        
        try:
            metadata = dict(grpc_context.invocation_metadata())
            
            # W3C Trace Context
            if 'traceparent' in metadata:
                parts = metadata['traceparent'].split('-')
                if len(parts) == 4:
                    _, ctx["trace_id"], ctx["span_id"], ctx["trace_flags"] = parts
            
            # 自定义 metadata
            for key in ['x-node-name', 'x-node-type', 'x-workflow-name', 
                       'x-workflow-instance-id', 'x-trace-id']:
                metadata_key = key
                ctx_key = key.replace('x-', '').replace('-', '_')
                if metadata_key in metadata:
                    # 解码metadata值
                    ctx[ctx_key] = metadata[metadata_key]
                    if key == 'x-node-name' or key == 'x-workflow-name' :
                        ctx[ctx_key] = self._decode_metadata_value(metadata[metadata_key])
                    
        except Exception as e:
            self.logger.debugf("Could not extract metadata: %s", str(e))
        
        return ctx

    def _convert_proto_value_to_python(self, proto_value) -> Any:
        """将 protobuf Value 转换为 Python 值"""
        if proto_value is None:
            return None
            
        kind = proto_value.WhichOneof('kind')
        
        if kind == 'null_value':
            return None
        elif kind == 'string_value':
            return proto_value.string_value
        elif kind == 'int_value':
            return proto_value.int_value
        elif kind == 'double_value':
            return proto_value.double_value
        elif kind == 'bool_value':
            return proto_value.bool_value
        elif kind == 'bytes_value':
            return proto_value.bytes_value
        elif kind == 'list_value':
            return [self._convert_proto_value_to_python(v) for v in proto_value.list_value.values]
        elif kind == 'map_value':
            return {k: self._convert_proto_value_to_python(v) 
                   for k, v in proto_value.map_value.fields.items()}
        else:
            return None
    
    def _convert_proto_map_to_dict(self, proto_map) -> Dict:
        """将 protobuf map<string, Value> 转换为 Python dict"""
        return {k: self._convert_proto_value_to_python(v) for k, v in proto_map.items()}


def serve_plugin(plugin_service: BasePluginService, port: int = 50052):
    """
    启动插件服务器
    
    Args:
        plugin_service: 插件服务实例
        port: 监听端口
    """
    logger = plugin_service.logger
    
    logger.info("=" * 60)
    logger.infof("🚀 Starting %s", plugin_service.plugin_name)
    logger.info("=" * 60)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger.info("   Thread pool: 10 workers")
    
    # 添加服务
    node_plugin_pb2_grpc.add_NodePluginServiceServicer_to_server(plugin_service, server)
    logger.info("   Service registered: NodePluginService")
    
    # 启用反射 API
    SERVICE_NAMES = (
        node_plugin_pb2.DESCRIPTOR.services_by_name['NodePluginService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    logger.info("   Reflection API enabled")
    
    server.add_insecure_port(f"[::]:{port}")
    logger.infof("   Listening on port: %d", port)
    
    server.start()
    
    # 获取插件元数据用于显示
    metadata = plugin_service.get_plugin_metadata()
    
    print("=" * 60)
    print(f"🚀 {plugin_service.plugin_name}")
    print("=" * 60)
    print(f"📦 Version: {metadata.get('version', '1.0.0')}")
    print(f"🔗 Port: {port}")
    print(f"📝 Description: {metadata.get('description', 'N/A')}")
    print("=" * 60)
    print("✅ Server started successfully!")
    print("📝 Press Ctrl+C to stop...")
    print("=" * 60)
    
    logger.info("✅ Server is ready to accept requests")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
        server.stop(0)
        logger.info("👋 Server stopped gracefully")
