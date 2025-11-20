"""
HTTP 连接器（只读）
"""
from typing import Dict, Any, List, Optional
import requests

from datastore.connectors.base import BaseConnector


class HttpConnector(BaseConnector):
    """HTTP API 连接器（只读）"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "")
        self.path = config.get("path", "")
    
    def connect(self) -> None:
        """连接 HTTP（HTTP 是无状态的，这里只标记为已连接）"""
        self._connected = True
    
    def disconnect(self) -> None:
        """断开连接"""
        self._connected = False
    
    def read(self, path: Optional[str] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        读取数据（GET 请求）
        
        Args:
            path: 请求路径（相对于 base_url）
            params: 查询参数
            **kwargs: 其他参数（如 headers）
            
        Returns:
            API 响应数据
        """
        if not self._connected:
            self.connect()
        
        url = self.base_url
        if path:
            url += path
        elif self.path:
            url += self.path
        
        try:
            headers = kwargs.get("headers", {})
            response = requests.get(url, params=params, headers=headers, timeout=kwargs.get("timeout", 30))
            response.raise_for_status()
            
            # 尝试解析 JSON
            content_type = response.headers.get('Content-Type', '').lower()
            if 'application/json' in content_type or 'text/json' in content_type:
                try:
                    return response.json()
                except ValueError:
                    # JSON 解析失败，返回文本
                    return response.text
            else:
                # 非 JSON 响应，返回文本
                return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP 请求失败: {e}")
    
    def write(self, data: Any, **kwargs) -> bool:
        """
        HTTP 连接器不支持写入操作
        
        Raises:
            NotImplementedError: HTTP 连接器只支持读取
        """
        raise NotImplementedError("HTTP 连接器只支持读取操作，不支持写入")

