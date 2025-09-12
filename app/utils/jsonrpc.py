"""
JSON-RPC 2.0 协议封装类
用于统一处理JSON-RPC消息的格式化和解析
与mcp-endpoint-server保持兼容
"""

import json
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class JSONRPCError:
    """JSON-RPC错误对象"""

    code: int
    message: str
    data: Optional[Any] = None


@dataclass
class JSONRPCRequest:
    """JSON-RPC请求对象"""

    method: str
    params: Optional[Union[Dict, list]] = None
    id: Optional[Union[str, int]] = None
    jsonrpc: str = "2.0"


@dataclass
class JSONRPCResponse:
    """JSON-RPC响应对象"""

    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None
    id: Optional[Union[str, int]] = None
    jsonrpc: str = "2.0"


class JSONRPCProtocol:
    """JSON-RPC 2.0 协议封装类"""

    # 预定义错误码
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # 自定义错误码
    TOOL_NOT_CONNECTED = -32001
    FORWARD_FAILED = -32002
    CONNECTION_ERROR = -32003
    AUTHENTICATION_ERROR = -32004

    @staticmethod
    def create_request(
        method: str,
        params: Optional[Union[Dict, list]] = None,
        request_id: Optional[Union[str, int]] = None,
    ) -> JSONRPCRequest:
        """创建JSON-RPC请求"""
        return JSONRPCRequest(
            method=method, params=params, id=request_id, jsonrpc="2.0"
        )

    @staticmethod
    def create_success_response(
        result: Any, request_id: Optional[Union[str, int]] = None
    ) -> JSONRPCResponse:
        """创建成功响应"""
        return JSONRPCResponse(result=result, id=request_id, jsonrpc="2.0")

    @staticmethod
    def create_error_response(
        error_code: int,
        error_message: str,
        error_data: Optional[Any] = None,
        request_id: Optional[Union[str, int]] = None,
    ) -> JSONRPCResponse:
        """创建错误响应"""
        error = JSONRPCError(code=error_code, message=error_message, data=error_data)
        return JSONRPCResponse(error=error, id=request_id, jsonrpc="2.0")

    @staticmethod
    def create_notification(
        method: str, params: Optional[Union[Dict, list]] = None
    ) -> JSONRPCRequest:
        """创建通知消息（无ID的请求）"""
        return JSONRPCRequest(method=method, params=params, id=None, jsonrpc="2.0")

    @staticmethod
    def to_dict(obj: Union[JSONRPCRequest, JSONRPCResponse]) -> Dict:
        """将对象转换为字典"""
        return asdict(obj)

    @staticmethod
    def to_json(
        obj: Union[JSONRPCRequest, JSONRPCResponse], ensure_ascii: bool = False
    ) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(asdict(obj), ensure_ascii=ensure_ascii)

    @staticmethod
    def parse_request(json_str: str) -> Optional[JSONRPCRequest]:
        """解析JSON-RPC请求"""
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                return None

            # 验证必需字段
            if "jsonrpc" not in data or data["jsonrpc"] != "2.0":
                return None
            if "method" not in data:
                return None

            return JSONRPCRequest(
                method=data["method"],
                params=data.get("params"),
                id=data.get("id"),
                jsonrpc=data["jsonrpc"],
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    @staticmethod
    def parse_response(json_str: str) -> Optional[JSONRPCResponse]:
        """解析JSON-RPC响应"""
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                return None

            # 验证必需字段
            if "jsonrpc" not in data or data["jsonrpc"] != "2.0":
                return None

            # 检查是否有result或error字段
            has_result = "result" in data
            has_error = "error" in data

            if not has_result and not has_error:
                return None
            if has_result and has_error:
                return None

            response = JSONRPCResponse(id=data.get("id"), jsonrpc=data["jsonrpc"])

            if has_result:
                response.result = data["result"]
            else:
                error_data = data["error"]
                response.error = JSONRPCError(
                    code=error_data["code"],
                    message=error_data["message"],
                    data=error_data.get("data"),
                )

            return response
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    @staticmethod
    def is_valid_request(json_str: str) -> bool:
        """验证是否为有效的JSON-RPC请求"""
        return JSONRPCProtocol.parse_request(json_str) is not None

    @staticmethod
    def is_valid_response(json_str: str) -> bool:
        """验证是否为有效的JSON-RPC响应"""
        return JSONRPCProtocol.parse_response(json_str) is not None

    @staticmethod
    def is_notification(json_str: str) -> bool:
        """检查是否为通知消息（无ID的请求）"""
        request = JSONRPCProtocol.parse_request(json_str)
        return request is not None and request.id is None


def create_tool_not_connected_error(
    request_id: Optional[Union[str, int]] = None, agent_id: Optional[str] = None
) -> str:
    """创建工具端未连接的错误消息"""
    error_data = (
        {"agent_id": agent_id, "details": "请求的工具端连接不存在或已断开"}
        if agent_id
        else None
    )

    response = JSONRPCProtocol.create_error_response(
        error_code=JSONRPCProtocol.TOOL_NOT_CONNECTED,
        error_message="工具端未连接",
        error_data=error_data,
        request_id=request_id,
    )
    return JSONRPCProtocol.to_json(response, ensure_ascii=False)


def create_forward_failed_error(
    request_id: Optional[Union[str, int]] = None, agent_id: Optional[str] = None
) -> str:
    """创建转发失败的错误消息"""
    error_data = (
        {"agent_id": agent_id, "details": "消息转发过程中发生错误"}
        if agent_id
        else None
    )

    response = JSONRPCProtocol.create_error_response(
        error_code=JSONRPCProtocol.FORWARD_FAILED,
        error_message="转发消息失败",
        error_data=error_data,
        request_id=request_id,
    )
    return JSONRPCProtocol.to_json(response, ensure_ascii=False)


def create_authentication_error(message: str = "认证失败") -> str:
    """创建认证错误消息"""
    response = JSONRPCProtocol.create_error_response(
        error_code=JSONRPCProtocol.AUTHENTICATION_ERROR, error_message=message
    )
    return JSONRPCProtocol.to_json(response, ensure_ascii=False)
