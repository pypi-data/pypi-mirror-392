"""Shared error handling for both FastAPI and MCP servers."""
from datetime import datetime
from typing import Optional, Union

from fastapi import HTTPException
from mcp import types as mcp_types

from .types import ErrorResponse, ResponseType

class XhsError(Exception):
    """统一的小红书 API 错误基类"""
    def __init__(self, message: str, error_type: str = "XhsError", status_code: int = 500):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        super().__init__(self.message)

class ClientNotFoundError(XhsError):
    """客户端未找到错误"""
    def __init__(self, client_id: str):
        super().__init__(
            message=f"未找到 ID 为 '{client_id}' 的客户端实例",
            error_type="ClientNotFoundError",
            status_code=404
        )

class InvalidArgumentError(XhsError):
    """无效参数错误"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_type="InvalidArgumentError",
            status_code=400
        )

class ErrorHandler:
    """统一的错误处理器"""
    
    @staticmethod
    def create_error_response(error: Union[Exception, XhsError]) -> ErrorResponse:
        """创建统一的错误响应"""
        now = datetime.now().isoformat()
        
        if isinstance(error, XhsError):
            return ErrorResponse(
                error=error.message,
                error_type=error.error_type,
                status_code=error.status_code,
                timestamp=now
            )
        else:
            return ErrorResponse(
                error=str(error),
                error_type=error.__class__.__name__,
                status_code=500,
                timestamp=now
            )

    @staticmethod
    def to_fastapi_response(error: Union[Exception, XhsError]) -> ResponseType:
        """转换为 FastAPI 响应格式"""
        error_response = ErrorHandler.create_error_response(error)
        return ResponseType(
            status="error",
            error=error_response
        )

    @staticmethod
    def to_fastapi_exception(error: Union[Exception, XhsError]) -> HTTPException:
        """转换为 FastAPI 异常"""
        if isinstance(error, XhsError):
            status_code = error.status_code
        else:
            status_code = 500
        
        error_response = ErrorHandler.create_error_response(error)
        return HTTPException(
            status_code=status_code,
            detail=error_response.dict()
        )

    @staticmethod
    def to_mcp_response(error: Union[Exception, XhsError]) -> list[mcp_types.TextContent]:
        """转换为 MCP 响应格式"""
        error_response = ErrorHandler.create_error_response(error)
        response = ResponseType(
            status="error",
            error=error_response
        )
        return [mcp_types.TextContent(type="text", text=response.json(ensure_ascii=False))]
