"""FastAPI server for Xiaohongshu API."""
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from xhs.api import FeedType
from xhs.exception import XhsException

from shared.client_manager import ClientManager
from shared.error_handler import ErrorHandler, XhsError
from shared.types import (
    # 请求模型
    CreateClientRequest,
    NoteRequest,
    SearchNotesRequest,
    SearchUsersRequest,
    UserRequest,
    # 响应模型
    ResponseType,
    ClientResponse,
    NoteResponse,
    SearchResponse,
    UserResponse,
    FeedCategoryResponse,
    FeedResponse,
)

# 创建 FastAPI 应用
app = FastAPI(
    title="Xiaohongshu API Server",
    description="通过 FastAPI 提供小红书 API 服务",
    version="1.0.0",
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取客户端管理器实例
client_manager = ClientManager()

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    await client_manager.start()

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    await client_manager.stop()

@app.exception_handler(XhsException)
async def xhs_exception_handler(request: Request, exc: XhsException):
    """处理小红书 API 异常"""
    response = ErrorHandler.to_fastapi_response(exc)
    return JSONResponse(
        status_code=500,
        content=response.dict()
    )

@app.exception_handler(XhsError)
async def custom_exception_handler(request: Request, exc: XhsError):
    """处理自定义异常"""
    response = ErrorHandler.to_fastapi_response(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )

# API 路由定义
@app.post("/clients", response_model=ResponseType[ClientResponse])
async def create_client(request: CreateClientRequest):
    """创建新的小红书客户端实例"""
    client_id = await client_manager.create_client(request)
    return ResponseType(result=ClientResponse(client_id=client_id))

@app.get("/clients", response_model=ResponseType[List[str]])
async def list_clients():
    """列出所有客户端 ID"""
    client_ids = client_manager.list_clients()
    return ResponseType(result=client_ids)

@app.delete("/clients/{client_id}", response_model=ResponseType)
async def delete_client(client_id: str):
    """删除客户端实例"""
    await client_manager.delete_client(client_id)
    return ResponseType()

@app.post("/clients/{client_id}/note", response_model=ResponseType[NoteResponse])
async def get_note(client_id: str, request: NoteRequest):
    """获取笔记详情"""
    client = await client_manager.get_client(client_id)
    note = await client.get_note(request)
    return ResponseType(result=note)

@app.post("/clients/{client_id}/note/html", response_model=ResponseType[NoteResponse])
async def get_note_html(client_id: str, request: NoteRequest):
    """从 HTML 获取笔记详情"""
    client = await client_manager.get_client(client_id)
    note = await client.get_note_html(request)
    return ResponseType(result=note)

@app.post("/clients/{client_id}/search/notes", response_model=ResponseType[SearchResponse])
async def search_notes(client_id: str, request: SearchNotesRequest):
    """搜索笔记"""
    client = await client_manager.get_client(client_id)
    results = await client.search_notes(request)
    return ResponseType(result=results)

@app.post("/clients/{client_id}/search/users", response_model=ResponseType[SearchResponse])
async def search_users(client_id: str, request: SearchUsersRequest):
    """搜索用户"""
    client = await client_manager.get_client(client_id)
    results = await client.search_users(request)
    return ResponseType(result=results)

@app.post("/clients/{client_id}/user/info", response_model=ResponseType[UserResponse])
async def get_user_info(client_id: str, request: UserRequest):
    """获取用户信息"""
    client = await client_manager.get_client(client_id)
    user_info = await client.get_user_info(request)
    return ResponseType(result=user_info)

@app.post("/clients/{client_id}/user/notes", response_model=ResponseType[SearchResponse])
async def get_user_notes(client_id: str, request: UserRequest):
    """获取用户笔记列表"""
    client = await client_manager.get_client(client_id)
    results = await client.get_user_notes(request)
    return ResponseType(result=results)

@app.get("/clients/{client_id}/feed/categories", response_model=ResponseType[FeedCategoryResponse])
async def get_feed_categories(client_id: str):
    """获取推荐流分类"""
    client = await client_manager.get_client(client_id)
    categories = await client.get_feed_categories()
    return ResponseType(result=FeedCategoryResponse(categories=categories))

@app.get("/clients/{client_id}/feed/{feed_type}", response_model=ResponseType[FeedResponse])
async def get_feed(client_id: str, feed_type: str):
    """获取指定类型的推荐流内容"""
    client = await client_manager.get_client(client_id)
    feed = await client.get_feed(feed_type)
    return ResponseType(result=feed)

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}
