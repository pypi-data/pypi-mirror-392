"""Shared client manager for both FastAPI and MCP servers."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from .api import ApiClient
from .types import CreateClientRequest
from .error_handler import ClientNotFoundError, InvalidArgumentError, XhsError

class ClientManager:
    """单例的客户端管理器"""
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClientManager, cls).__new__(cls)
            # 初始化实例属性
            cls._instance._clients: Dict[str, Tuple[ApiClient, datetime]] = {}
            cls._instance._counter = 0
            cls._instance._cleanup_task = None
            cls._instance._last_cleanup = datetime.now()
        return cls._instance

    async def start(self):
        """启动管理器，包括定期清理任务"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            print("ClientManager: 启动清理任务")

    async def stop(self):
        """停止管理器，清理资源"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            print("ClientManager: 停止清理任务")
            
        # 清理所有客户端
        print(f"ClientManager: 清理 {len(self._clients)} 个客户端")
        self._clients.clear()
        self._counter = 0

    async def create_client(self, request: CreateClientRequest) -> str:
        """创建新的客户端实例
        
        Args:
            request: 包含创建客户端所需参数的请求对象
            
        Returns:
            str: 新创建的客户端 ID
            
        Raises:
            InvalidArgumentError: 如果必需参数缺失
            XhsError: 如果客户端创建失败
        """
        async with self._lock:
            # 验证必需参数
            if not request.cookie:
                raise InvalidArgumentError("必须提供 cookie")

            try:
                # 创建客户端实例
                client = ApiClient(request)
                
                # 生成客户端 ID
                self._counter += 1
                client_id = f"client_{self._counter}"
                
                # 存储客户端实例和创建时间
                self._clients[client_id] = (client, datetime.now())
                print(f"ClientManager: 创建客户端 {client_id}")
                
                return client_id
                
            except Exception as e:
                raise XhsError(f"创建客户端失败: {str(e)}")

    async def get_client(self, client_id: str) -> ApiClient:
        """获取指定 ID 的客户端实例
        
        Args:
            client_id: 客户端 ID
            
        Returns:
            ApiClient: 客户端实例
            
        Raises:
            ClientNotFoundError: 如果找不到指定 ID 的客户端
        """
        client_tuple = self._clients.get(client_id)
        if not client_tuple:
            raise ClientNotFoundError(client_id)
            
        # 更新最后使用时间
        client, _ = client_tuple
        self._clients[client_id] = (client, datetime.now())
        return client

    async def delete_client(self, client_id: str) -> None:
        """删除指定 ID 的客户端实例
        
        Args:
            client_id: 客户端 ID
            
        Raises:
            ClientNotFoundError: 如果找不到指定 ID 的客户端
        """
        async with self._lock:
            if client_id not in self._clients:
                raise ClientNotFoundError(client_id)
            del self._clients[client_id]
            print(f"ClientManager: 删除客户端 {client_id}")

    def list_clients(self) -> list[str]:
        """列出所有客户端 ID"""
        return list(self._clients.keys())

    async def _cleanup_loop(self):
        """定期清理过期客户端的后台任务"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分钟清理一次
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"ClientManager: 清理任务出错: {e}")

    async def _cleanup_expired(self):
        """清理超时未使用的客户端"""
        async with self._lock:
            now = datetime.now()
            timeout = timedelta(hours=1)  # 1小时未使用则清理
            
            # 找出所有过期的客户端
            expired = [
                client_id
                for client_id, (_, last_used) in self._clients.items()
                if now - last_used > timeout
            ]
            
            # 删除过期客户端
            for client_id in expired:
                del self._clients[client_id]
                print(f"ClientManager: 清理过期客户端 {client_id}")
