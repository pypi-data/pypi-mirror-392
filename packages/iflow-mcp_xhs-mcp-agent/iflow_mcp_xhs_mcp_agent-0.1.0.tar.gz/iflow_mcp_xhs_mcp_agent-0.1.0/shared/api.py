"""Base API layer using async XhsClient."""
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
import aiohttp

from xhs.api import XhsClient, FeedType, SearchSortType, SearchNoteType, NoteType
from xhs.exception import XhsException

from .types import (
    CreateClientRequest,
    NoteRequest,
    SearchNotesRequest,
    SearchUsersRequest,
    UserRequest,
    NoteResponse,
    SearchResponse,
    UserResponse,
    FeedResponse,
)
from .error_handler import XhsError

class ApiClient:
    """异步的 API 客户端包装器"""
    
    def __init__(self, request: CreateClientRequest):
        """从统一的请求类型创建客户端"""
        self._request = request
        self._session = aiohttp.ClientSession()
        self._client = XhsClient(
            cookie=request.cookie,
            user_agent=request.user_agent,
            timeout=request.timeout,
            proxies=request.proxies
        )
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self._session.close()

    async def close(self):
        """关闭客户端"""
        await self._session.close()

    async def get_note(self, request: NoteRequest) -> NoteResponse:
        """获取笔记详情"""
        try:
            note = self._client.get_note_by_id(
                note_id=request.note_id,
                xsec_token=request.xsec_token,
                xsec_source=request.xsec_source
            )
            return NoteResponse(**note)
        except XhsException as e:
            raise XhsError(f"获取笔记失败: {str(e)}")
            
    async def get_note_html(self, request: NoteRequest) -> NoteResponse:
        """从 HTML 获取笔记详情"""
        try:
            note = self._client.get_note_by_id_from_html(
                note_id=request.note_id,
                xsec_token=request.xsec_token,
                xsec_source=request.xsec_source
            )
            return NoteResponse(**note)
        except XhsException as e:
            raise XhsError(f"从 HTML 获取笔记失败: {str(e)}")
            
    async def search_notes(self, request: SearchNotesRequest) -> SearchResponse:
        """搜索笔记"""
        try:
            sort_map = {
                "general": SearchSortType.GENERAL,
                "popularity_descending": SearchSortType.MOST_POPULAR,
                "time_descending": SearchSortType.LATEST
            }
            note_type_map = {
                0: SearchNoteType.ALL,
                1: SearchNoteType.VIDEO,
                2: SearchNoteType.IMAGE
            }
            results = self._client.get_note_by_keyword(
                keyword=request.keyword,
                page=request.page,
                page_size=request.page_size,
                sort=sort_map.get(request.sort, SearchSortType.GENERAL),
                note_type=note_type_map.get(request.note_type, SearchNoteType.ALL)
            )
            return SearchResponse(**results)
        except XhsException as e:
            raise XhsError(f"搜索笔记失败: {str(e)}")
            
    async def search_users(self, request: SearchUsersRequest) -> SearchResponse:
        """搜索用户"""
        try:
            results = self._client.get_user_by_keyword(keyword=request.keyword)
            return SearchResponse(**results)
        except XhsException as e:
            raise XhsError(f"搜索用户失败: {str(e)}")
            
    async def get_user_info(self, request: UserRequest) -> UserResponse:
        """获取用户信息"""
        try:
            user_info = self._client.get_user_info(user_id=request.user_id)
            return UserResponse(**user_info)
        except XhsException as e:
            raise XhsError(f"获取用户信息失败: {str(e)}")
            
    async def get_user_notes(self, request: UserRequest) -> SearchResponse:
        """获取用户笔记列表"""
        try:
            results = self._client.get_user_notes(user_id=request.user_id)
            return SearchResponse(**results)
        except XhsException as e:
            raise XhsError(f"获取用户笔记失败: {str(e)}")
            
    async def get_feed_categories(self) -> List[str]:
        """获取推荐流分类"""
        try:
            return self._client.get_home_feed_category()
        except XhsException as e:
            raise XhsError(f"获取推荐流分类失败: {str(e)}")
            
    async def get_feed(self, feed_type: Union[str, FeedType]) -> FeedResponse:
        """获取推荐流内容"""
        try:
            if isinstance(feed_type, str):
                try:
                    feed_type = FeedType(feed_type)
                except ValueError:
                    raise XhsError(f"无效的推荐流类型: {feed_type}", status_code=400)
                    
            feed = self._client.get_home_feed(feed_type=feed_type)
            return FeedResponse(**feed)
        except XhsException as e:
            raise XhsError(f"获取推荐流内容失败: {str(e)}")
