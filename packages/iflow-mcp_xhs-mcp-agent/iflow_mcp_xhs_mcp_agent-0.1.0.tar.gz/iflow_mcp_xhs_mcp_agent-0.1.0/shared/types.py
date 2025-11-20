"""Shared types for both FastAPI and MCP servers."""
from typing import TypeVar, Generic, Union, Dict, Any, Optional
from pydantic import BaseModel

# 统一的响应类型
T = TypeVar('T')  # 用于泛型响应类型

class ErrorResponse(BaseModel):
    """统一的错误响应格式"""
    error: str
    error_type: str
    detail: Optional[str] = None
    status_code: Optional[int] = None
    timestamp: Optional[str] = None

class ResponseType(BaseModel, Generic[T]):
    """统一的响应格式"""
    status: str = "success"
    result: Optional[T] = None
    error: Optional[ErrorResponse] = None

# FastAPI 和 MCP Server 共享的请求模型
class CreateClientRequest(BaseModel):
    """创建客户端请求"""
    cookie: str
    user_agent: Optional[str] = None
    timeout: Optional[int] = 10
    proxies: Optional[Dict[str, str]] = None

class NoteRequest(BaseModel):
    """笔记相关请求的基础模型"""
    note_id: str
    xsec_token: str
    xsec_source: str = "pc_feed"

class SearchNotesRequest(BaseModel):
    """搜索笔记请求"""
    keyword: str
    page: Optional[int] = 1
    page_size: Optional[int] = 20
    sort: Optional[str] = "general"
    note_type: Optional[int] = 0  # 0=全部, 1=视频, 2=图片

class SearchUsersRequest(BaseModel):
    """搜索用户请求"""
    keyword: str

class UserRequest(BaseModel):
    """用户相关请求"""
    user_id: str

# MCP 工具模式下的请求模型（包含 client_id）
class McpNoteRequest(NoteRequest):
    """MCP 笔记请求"""
    client_id: str

class McpSearchNotesRequest(SearchNotesRequest):
    """MCP 搜索笔记请求"""
    client_id: str

class McpSearchUsersRequest(SearchUsersRequest):
    """MCP 搜索用户请求"""
    client_id: str

class McpUserRequest(UserRequest):
    """MCP 用户请求"""
    client_id: str

class McpFeedRequest(BaseModel):
    """MCP Feed 请求"""
    client_id: str
    feed_type: Optional[str] = None  # 只在 get_feed 时需要

# 统一的响应模型
class ClientResponse(BaseModel):
    """客户端响应"""
    client_id: str

class NoteResponse(BaseModel):
    """笔记响应"""
    id: str
    title: str
    desc: str
    images: Optional[list[str]] = None
    video_url: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    time: Optional[str] = None
    likes: Optional[int] = None
    comments: Optional[int] = None

class SearchResponse(BaseModel):
    """搜索响应"""
    total: int
    has_more: bool
    cursor: Optional[str] = None
    items: list[Any]

class UserResponse(BaseModel):
    """用户信息响应"""
    user_id: str
    nickname: str
    avatar: Optional[str] = None
    desc: Optional[str] = None
    follows: Optional[int] = None
    fans: Optional[int] = None
    notes_count: Optional[int] = None
    
class FeedCategoryResponse(BaseModel):
    """Feed 分类响应"""
    categories: list[str]

class FeedResponse(BaseModel):
    """Feed 内容响应"""
    items: list[NoteResponse]
    cursor: Optional[str] = None
    has_more: bool
