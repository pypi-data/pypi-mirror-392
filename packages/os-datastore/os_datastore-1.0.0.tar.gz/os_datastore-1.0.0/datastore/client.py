"""
Datastore 客户端主类
"""
from typing import Dict, Any, Optional, Tuple, Iterator
import requests

from datastore.utils import parse_datasource_url
from datastore.schema import SchemaValidator
from datastore.connectors import (
    MinioConnector,
    CassandraConnector,
    RedisConnector,
    KafkaConnector,
    HttpConnector,
)


class DataStoreClient:
    """Datastore SDK 主客户端"""
    
    def __init__(self, api_base_url: str = "http://192.168.2.123:8067", enable_schema_validation: bool = True):
        """
        初始化客户端
        
        Args:
            api_base_url: API 基础 URL
            enable_schema_validation: 是否默认启用 Schema 校验（默认 True）
        """
        self.api_base_url = api_base_url.rstrip("/")
        self._connector = None
        self._schema_validator = None
        self._asset_info = None
        self._enable_schema_validation = enable_schema_validation
    
    def _fetch_asset_info(self, urn: str) -> Dict[str, Any]:
        """
        通过 URN 获取资产信息
        
        Args:
            urn: 资产 URN
            
        Returns:
            资产信息字典
        """
        url = f"{self.api_base_url}/v1/phm/assets/{urn}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 200:
                raise Exception(f"API 返回错误: {result.get('message', '未知错误')}")
            
            return result.get("data", {})
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取资产信息失败: {e}")
    
    def _create_connector(self, datasource_url: str) -> Any:
        """
        根据数据源 URL 创建对应的连接器
        
        Args:
            datasource_url: 数据源 URL
            
        Returns:
            连接器实例
        """
        config = parse_datasource_url(datasource_url)
        scheme = config["scheme"]
        
        connector_map = {
            "minio": MinioConnector,
            "cassandra": CassandraConnector,
            "redis": RedisConnector,
            "kafka": KafkaConnector,
            "http": HttpConnector,
            "https": HttpConnector,
        }
        
        connector_class = connector_map.get(scheme)
        if not connector_class:
            raise ValueError(f"不支持的数据源类型: {scheme}")
        
        return connector_class(config)
    
    def connect(self, urn: str, enable_schema_validation: Optional[bool] = None) -> None:
        """
        连接到指定的资产
        
        Args:
            urn: 资产 URN，例如：urn:store:os.iot.rotary_wheel_image
            enable_schema_validation: 是否启用 Schema 校验（None 时使用初始化时的默认值）
        """
        # 获取资产信息
        self._asset_info = self._fetch_asset_info(urn)
        
        # 获取数据源 URL
        datasource_url = self._asset_info.get("aspects", {}).get("datasource", {}).get("url")
        if not datasource_url:
            raise ValueError("资产信息中未找到数据源 URL")
        
        # 创建连接器
        self._connector = self._create_connector(datasource_url)
        self._connector.connect()
        
        # 确定是否启用 Schema 校验
        if enable_schema_validation is None:
            enable_schema_validation = self._enable_schema_validation
        
        # 创建 Schema 验证器（如果启用）
        if enable_schema_validation:
            properties = self._asset_info.get("aspects", {}).get("properties", {})
            if properties:
                self._schema_validator = SchemaValidator(properties)
            else:
                self._schema_validator = None
        else:
            self._schema_validator = None
    
    def disconnect(self) -> None:
        """断开连接"""
        if self._connector:
            self._connector.disconnect()
            self._connector = None
        self._schema_validator = None
        self._asset_info = None
    
    def read(self, **kwargs) -> Any:
        """
        读取数据
        
        Args:
            **kwargs: 传递给连接器的读取参数
                对于 Kafka：
                - group_id: Consumer Group ID（默认 "datastore-consumer"，None 表示不使用 consumer group）
                - auto_offset_reset: offset 重置策略（"earliest" 或 "latest"，默认 "latest"）
                - seek_to_end: 是否先定位到末尾（默认 False）
                - auto_commit: 是否自动提交偏移量（默认 False）
            
        Returns:
            读取的数据
        """
        if not self._connector:
            raise RuntimeError("未连接到任何资产，请先调用 connect() 方法")
        
        return self._connector.read(**kwargs)
    
    def readstream(self, poll_timeout_ms: int = 1000, **kwargs) -> Iterator[Dict[str, Any]]:
        """
        持续读取消息流（仅支持 Kafka）
        
        一旦 Kafka 主题有新数据，就会立即读取并 yield。
        这是一个生成器方法，会持续运行直到被停止（如 KeyboardInterrupt）。
        
        Args:
            poll_timeout_ms: 每次 poll 的超时时间（毫秒），默认 1000ms
            **kwargs: 传递给连接器的参数
                - group_id: Consumer Group ID（默认 "datastore-consumer-stream"，None 表示不使用 consumer group）
                - auto_offset_reset: offset 重置策略（"earliest" 或 "latest"，默认 "latest"）
                - seek_to_end: 是否先定位到末尾（用于只读取新消息，默认 False）
                - max_messages: 最大消息数量，达到后停止（默认 None，无限制）
                - stop_on_empty: 如果 poll 返回空是否停止（默认 False，继续等待）
                - auto_commit: 是否自动提交偏移量（默认 False，需要手动调用 commit_offset）
            
        Yields:
            消息字典
            
        Raises:
            RuntimeError: 如果未连接到任何资产
            AttributeError: 如果当前连接器不支持 readstream（非 Kafka）
            
        Example:
            >>> client.connect("urn:store:example.kafka")
            >>> for message in client.readstream():
            ...     print(f"收到消息: {message}")
            ...     # 处理消息
        """
        if not self._connector:
            raise RuntimeError("未连接到任何资产，请先调用 connect() 方法")
        
        # 检查连接器是否支持 readstream
        if not hasattr(self._connector, 'readstream'):
            raise AttributeError(f"当前连接器 {type(self._connector).__name__} 不支持 readstream 方法（仅 Kafka 支持）")
        
        return self._connector.readstream(poll_timeout_ms=poll_timeout_ms, **kwargs)
    
    def commit_offset(self, **kwargs) -> bool:
        """
        手动提交 Kafka 偏移量（仅支持 Kafka）
        
        Args:
            **kwargs: 传递给连接器的参数
                - offsets: 要提交的偏移量字典 {TopicPartition: OffsetAndMetadata}（默认提交所有分区）
                - async: 是否异步提交（默认 False，同步提交）
        
        Returns:
            True 如果提交成功
            
        Raises:
            RuntimeError: 如果未连接到任何资产或没有 consumer group
            AttributeError: 如果当前连接器不支持 commit_offset（非 Kafka）
        """
        if not self._connector:
            raise RuntimeError("未连接到任何资产，请先调用 connect() 方法")
        
        # 检查连接器是否支持 commit_offset
        if not hasattr(self._connector, 'commit_offset'):
            raise AttributeError(f"当前连接器 {type(self._connector).__name__} 不支持 commit_offset 方法（仅 Kafka 支持）")
        
        return self._connector.commit_offset(**kwargs)
    
    def write(self, data: Optional[Dict[str, Any]] = None, validate_schema: Optional[bool] = None, **kwargs) -> bool:
        """
        写入数据
        
        Args:
            data: 要写入的数据字典（对于 MinIO，如果提供了 file_data，此参数可以为 None）
            validate_schema: 是否验证 schema（None 时使用默认设置，True 强制验证，False 跳过验证）
            **kwargs: 传递给连接器的写入参数
                对于 MinIO：
                - file_data: 实际文件数据（字节），如果提供，data 可以为 None
                - metadata: metadata 字典（会被 Schema 校验）
                - object_name: 对象名称
                - content_type: 内容类型
            
        Returns:
            True 如果写入成功
            
        Raises:
            ValueError: 如果数据不符合 schema
            NotImplementedError: 如果数据源不支持写入（如 HTTP）
        """
        if not self._connector:
            raise RuntimeError("未连接到任何资产，请先调用 connect() 方法")
        
        # 对于 MinIO，如果提供了 file_data，data 可以为 None
        is_minio = isinstance(self._connector, MinioConnector)
        if is_minio and 'file_data' in kwargs:
            # MinIO 使用 file_data，data 可以为 None
            pass
        elif data is None:
            raise ValueError("data 参数不能为 None（除非是 MinIO 且提供了 file_data）")
        
        # Schema 验证
        # 如果 validate_schema 为 None，使用默认设置（只有在启用校验且有验证器时才校验）
        # 如果 validate_schema 为 True，强制校验（如果没有验证器则跳过）
        # 如果 validate_schema 为 False，跳过校验
        if validate_schema is None:
            # 使用默认设置：只有在启用校验且有验证器时才校验
            should_validate = self._enable_schema_validation and self._schema_validator is not None
        elif validate_schema:
            # 强制校验：如果有验证器则校验
            should_validate = self._schema_validator is not None
        else:
            # 跳过校验
            should_validate = False
        
        if should_validate and self._schema_validator:
            # 对于 MinIO，如果提供了 metadata，校验 metadata；否则校验 data
            if is_minio and 'metadata' in kwargs and kwargs['metadata']:
                # MinIO 有 metadata，校验 metadata
                validate_data = kwargs['metadata']
            elif data is not None:
                # 其他情况校验 data
                validate_data = data
            else:
                # MinIO 有 file_data 但没有 metadata 和 data，跳过校验
                validate_data = None
            
            if validate_data is not None:
                is_valid, error_msg = self._schema_validator.is_valid(validate_data)
                if not is_valid:
                    raise ValueError(f"数据不符合 schema: {error_msg}")
        
        return self._connector.write(data, **kwargs)
    
    def get_asset_info(self) -> Optional[Dict[str, Any]]:
        """
        获取当前资产的详细信息
        
        Returns:
            资产信息字典
        """
        return self._asset_info
    
    def get_schema(self) -> Optional[Dict[str, Any]]:
        """
        获取当前资产的 Schema
        
        Returns:
            Schema 字典
        """
        if self._schema_validator:
            return self._schema_validator.schema
        return None
    
    def validate_data(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证数据是否符合 schema（不写入）
        
        Args:
            data: 要验证的数据字典
            
        Returns:
            (is_valid, error_message) 元组
        """
        if not self._schema_validator:
            return True, None
        
        return self._schema_validator.is_valid(data)
    
    def enable_schema_validation(self) -> None:
        """启用 Schema 校验"""
        self._enable_schema_validation = True
        # 如果已连接且有 properties，重新创建验证器
        if self._asset_info:
            properties = self._asset_info.get("aspects", {}).get("properties", {})
            if properties:
                self._schema_validator = SchemaValidator(properties)
    
    def disable_schema_validation(self) -> None:
        """禁用 Schema 校验"""
        self._enable_schema_validation = False
        self._schema_validator = None
    
    def is_schema_validation_enabled(self) -> bool:
        """
        检查 Schema 校验是否启用
        
        Returns:
            True 如果 Schema 校验已启用
        """
        return self._enable_schema_validation
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()

