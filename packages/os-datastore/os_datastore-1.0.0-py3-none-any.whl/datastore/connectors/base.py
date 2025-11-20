"""
连接器基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseConnector(ABC):
    """数据源连接器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化连接器
        
        Args:
            config: 连接配置字典
        """
        self.config = config
        self._connected = False
    
    @abstractmethod
    def connect(self) -> None:
        """建立连接"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def read(self, **kwargs) -> Any:
        """
        读取数据
        
        Args:
            **kwargs: 读取参数
            
        Returns:
            读取的数据
        """
        pass
    
    @abstractmethod
    def write(self, data: Any, **kwargs) -> bool:
        """
        写入数据
        
        Args:
            data: 要写入的数据
            **kwargs: 写入参数
            
        Returns:
            True 如果写入成功
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()

