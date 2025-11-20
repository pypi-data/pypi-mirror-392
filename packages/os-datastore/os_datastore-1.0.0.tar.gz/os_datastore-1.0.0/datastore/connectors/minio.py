"""
MinIO 连接器
"""
from typing import Dict, Any, List, Optional
from minio import Minio
from minio.error import S3Error
from io import BytesIO
import json

from datastore.connectors.base import BaseConnector


class MinioConnector(BaseConnector):
    """MinIO 对象存储连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client: Optional[Minio] = None
        self.bucket = config.get("bucket", "")
    
    def connect(self) -> None:
        """连接 MinIO"""
        endpoint = f"{self.config['host']}:{self.config.get('port', 9000)}"
        # 使用 username 和 password（兼容旧版本的 access_key 和 secret_key）
        username = self.config.get("username") or self.config.get("access_key", "")
        password = self.config.get("password") or self.config.get("secret_key", "")
        secure = self.config.get("secure", False)
        
        if not username or not password:
            raise ValueError("MinIO 配置中缺少 username 或 password")
        
        self.client = Minio(
            endpoint,
            access_key=username,
            secret_key=password,
            secure=secure
        )
        self._connected = True
    
    def disconnect(self) -> None:
        """断开连接"""
        self.client = None
        self._connected = False
    
    def read(self, object_name: str, **kwargs) -> Any:
        """
        读取对象
        
        Args:
            object_name: 对象名称
            **kwargs: 其他参数
                - as_json: 是否尝试解析为 JSON（默认 True，如果失败则返回原始字节）
                - encoding: 文本编码（默认 'utf-8'，仅在 as_json=False 时使用）
                - include_metadata: 是否包含 metadata（默认 True）
            
        Returns:
            对象内容
            - 如果 include_metadata=True，返回字典 {"data": ..., "metadata": {...}}
            - 如果 include_metadata=False，返回数据本身
            - 如果 as_json=True 且对象是有效的 JSON，data 为解析后的字典
            - 否则 data 为字节数据
        """
        if not self._connected:
            self.connect()
        
        try:
            # 读取对象数据
            response = self.client.get_object(self.bucket, object_name)
            data_bytes = response.read()
            
            # 提取 metadata（MinIO metadata 在 response.headers 中，以 x-amz-meta- 开头）
            metadata = {}
            if hasattr(response, 'headers'):
                # 从响应头中提取 metadata
                for key, value in response.headers.items():
                    if key.lower().startswith('x-amz-meta-'):
                        # 移除前缀
                        meta_key = key.lower().replace('x-amz-meta-', '')
                        metadata[meta_key] = value
            
            response.close()
            response.release_conn()
            
            # 尝试解析为 JSON
            as_json = kwargs.get("as_json", True)
            data = None
            
            if as_json:
                try:
                    # 尝试解析为 JSON
                    data = json.loads(data_bytes.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # 如果不是 JSON 或不是 UTF-8 文本，使用原始字节
                    data = data_bytes
            else:
                # 如果不尝试解析 JSON，直接返回字节
                encoding = kwargs.get("encoding", None)
                if encoding:
                    try:
                        data = data_bytes.decode(encoding)
                    except UnicodeDecodeError:
                        data = data_bytes
                else:
                    data = data_bytes
            
            # 是否包含 metadata
            include_metadata = kwargs.get("include_metadata", True)
            if include_metadata:
                return {
                    "data": data,
                    "metadata": metadata
                }
            else:
                return data
                
        except S3Error as e:
            raise Exception(f"读取 MinIO 对象失败: {e}")
    
    def write(self, data: Optional[Any] = None, object_name: Optional[str] = None, **kwargs) -> bool:
        """
        写入对象
        
        Args:
            data: 要写入的数据（可选，如果提供了 file_data，此参数可以为 None）
                - 如果是字典，会序列化为 JSON
                - 如果是字节，直接写入
                - 如果是字符串，编码为 UTF-8
            object_name: 对象名称（必需）
            **kwargs: 其他参数
                - metadata: 要写入的 metadata 字典（可选）
                - content_type: 内容类型（默认根据数据类型自动判断）
                - file_data: 实际文件数据（字节），如果提供，data 可以为 None
            
        Returns:
            True 如果写入成功
        """
        if not self._connected:
            self.connect()
        
        # 从 kwargs 中获取 object_name（如果未作为位置参数提供）
        if object_name is None:
            object_name = kwargs.get("object_name")
        
        if not object_name:
            raise ValueError("object_name 参数是必需的")
        
        try:
            # 处理 metadata
            metadata = kwargs.get("metadata", {})
            file_data = kwargs.get("file_data", None)
            
            # 如果提供了 file_data，使用 file_data 作为实际文件数据
            if file_data is not None:
                if isinstance(file_data, bytes):
                    data_bytes = file_data
                elif isinstance(file_data, str):
                    data_bytes = file_data.encode('utf-8')
                else:
                    raise ValueError("file_data 必须是 bytes 或 str")
            elif data is not None:
                # 否则 data 就是实际要写入的数据
                if isinstance(data, bytes):
                    data_bytes = data
                elif isinstance(data, str):
                    data_bytes = data.encode('utf-8')
                elif isinstance(data, dict):
                    data_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
                else:
                    raise ValueError(f"不支持的数据类型: {type(data)}")
            else:
                raise ValueError("必须提供 data 或 file_data 参数")
            
            data_stream = BytesIO(data_bytes)
            length = len(data_bytes)
            
            # 准备 metadata（MinIO 需要 x-amz-meta- 前缀）
            minio_metadata = {}
            for key, value in metadata.items():
                # 确保 key 以 x-amz-meta- 开头
                meta_key = key if key.lower().startswith('x-amz-meta-') else f'x-amz-meta-{key}'
                # metadata 值必须是字符串
                minio_metadata[meta_key] = str(value)
            
            # 确定 content_type
            content_type = kwargs.get("content_type")
            if not content_type:
                if isinstance(data, dict) and file_data is None:
                    content_type = "application/json"
                else:
                    content_type = "application/octet-stream"
            
            self.client.put_object(
                self.bucket,
                object_name,
                data_stream,
                length,
                content_type=content_type,
                metadata=minio_metadata if minio_metadata else None
            )
            return True
        except S3Error as e:
            raise Exception(f"写入 MinIO 对象失败: {e}")

