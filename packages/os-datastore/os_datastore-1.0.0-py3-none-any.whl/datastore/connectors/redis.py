"""
Redis 连接器
"""
from typing import Dict, Any, List, Optional
import redis
import json

from datastore.connectors.base import BaseConnector


class RedisConnector(BaseConnector):
    """Redis 缓存连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client: Optional[redis.Redis] = None
        self.db = config.get("db", 0)
    
    def connect(self) -> None:
        """连接 Redis"""
        password = self.config.get("password", None)
        
        self.client = redis.Redis(
            host=self.config['host'],
            port=self.config.get('port', 6379),
            db=self.db,
            password=password if password else None,
            decode_responses=True
        )
        # 测试连接
        self.client.ping()
        self._connected = True
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.client:
            self.client.close()
        self.client = None
        self._connected = False
    
    def read(self, key: str, **kwargs) -> Any:
        """
        读取数据
        
        Args:
            key: Redis key
            **kwargs: 其他参数
                - data_type: 数据类型（"string", "hash", "list", "set", "zset"）
                            如果为 None，会自动检测数据类型
                - field: Hash 类型的字段名（仅当 data_type="hash" 时使用）
                - start: List 类型的起始索引（默认 0）
                - end: List 类型的结束索引（默认 -1，表示最后一个元素）
            
        Returns:
            存储的数据
        """
        if not self._connected:
            self.connect()
        
        try:
            data_type = kwargs.get("data_type")
            
            # 如果没有指定类型，自动检测
            if data_type is None:
                # 检测 key 的类型
                key_type_result = self.client.type(key)
                # redis-py 可能返回 bytes 或 str
                if isinstance(key_type_result, bytes):
                    key_type = key_type_result.decode('utf-8')
                else:
                    key_type = str(key_type_result)
                
                if key_type == "none":
                    return None
                elif key_type == "hash":
                    data_type = "hash"
                elif key_type == "list":
                    data_type = "list"
                elif key_type == "set":
                    data_type = "set"
                elif key_type == "zset":
                    data_type = "zset"
                else:
                    data_type = "string"
            
            data_type = data_type.lower()
            
            if data_type == "hash":
                # Hash 类型
                field = kwargs.get("field")
                if field:
                    # 读取单个字段
                    value = self.client.hget(key, field)
                    return value
                else:
                    # 读取所有字段
                    return self.client.hgetall(key)
            
            elif data_type == "list":
                # List 类型
                start = kwargs.get("start", 0)
                end = kwargs.get("end", -1)
                return self.client.lrange(key, start, end)
            
            elif data_type == "set":
                # Set 类型
                return list(self.client.smembers(key))
            
            elif data_type == "zset":
                # Sorted Set 类型
                with_scores = kwargs.get("with_scores", False)
                start = kwargs.get("start", 0)
                end = kwargs.get("end", -1)
                if with_scores:
                    return self.client.zrange(key, start, end, withscores=True)
                else:
                    return self.client.zrange(key, start, end)
            
            else:
                # String 类型（默认）
                value = self.client.get(key)
                if value is None:
                    return None
                # 尝试解析 JSON
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
                    
        except Exception as e:
            raise Exception(f"读取 Redis 数据失败: {e}")
    
    def write(self, data: Any, key: str, ttl: Optional[int] = None, **kwargs) -> bool:
        """
        写入数据
        
        Args:
            data: 要写入的数据
                - String: 字符串、数字等基本类型
                - Hash: 字典类型，会写入为 Hash
                - List: 列表类型，会追加到 List
                - Set: 列表类型，会写入为 Set
                - ZSet: 字典类型 {member: score}，会写入为 Sorted Set
            key: Redis key
            ttl: 过期时间（秒）
            **kwargs: 其他参数
                - data_type: 数据类型（"string", "hash", "list", "set", "zset"）
                            如果为 None，会根据 data 的类型自动判断：
                            - dict -> hash 或 zset（如果提供了 scores）
                            - list -> list 或 set（根据 use_set 参数）
                            - 其他 -> string
                - use_set: 当 data 是 list 时，是否使用 Set 而不是 List（默认 False）
                - scores: ZSet 的分数字典 {member: score}（仅当 data_type="zset" 时使用）
                - field: Hash 类型的字段名（仅当写入单个字段时使用）
                - append: List 类型是否追加（默认 True，追加到末尾）
                - replace: 是否替换现有数据（Hash/Set/ZSet 默认 False，List 默认 True）
            
        Returns:
            True 如果写入成功
        """
        if not self._connected:
            self.connect()
        
        try:
            data_type = kwargs.get("data_type")
            
            # 如果没有指定类型，根据 data 的类型自动判断
            if data_type is None:
                if isinstance(data, dict):
                    # 检查是否有 scores 参数（ZSet）
                    if kwargs.get("scores") is not None:
                        data_type = "zset"
                    else:
                        data_type = "hash"
                elif isinstance(data, list):
                    # 根据 use_set 参数决定使用 List 还是 Set
                    data_type = "set" if kwargs.get("use_set", False) else "list"
                else:
                    data_type = "string"
            
            data_type = data_type.lower()
            
            if data_type == "hash":
                # Hash 类型
                field = kwargs.get("field")
                replace = kwargs.get("replace", False)
                
                # 检查 key 是否存在且类型是否匹配
                if not field:  # 只有写入整个 Hash 时才需要检查类型
                    key_exists = self.client.exists(key)
                    if key_exists:
                        key_type_result = self.client.type(key)
                        if isinstance(key_type_result, bytes):
                            key_type = key_type_result.decode('utf-8')
                        else:
                            key_type = str(key_type_result)
                        
                        if key_type != "hash" and key_type != "none":
                            # 类型不匹配
                            if replace:
                                # 如果允许替换，删除现有 key
                                self.client.delete(key)
                            else:
                                raise ValueError(
                                    f"Key '{key}' 已存在且类型为 '{key_type}'，无法写入 Hash 类型。"
                                    f"请设置 replace=True 来替换现有数据，或使用不同的 key。"
                                )
                
                if field:
                    # 写入单个字段
                    self.client.hset(key, field, str(data))
                else:
                    # 写入整个 Hash
                    # 将 data 转换为字符串字典
                    hash_data = {}
                    for k, v in data.items():
                        if isinstance(v, (dict, list)):
                            hash_data[k] = json.dumps(v, ensure_ascii=False)
                        else:
                            hash_data[k] = str(v)
                    self.client.hset(key, mapping=hash_data)
            
            elif data_type == "list":
                # List 类型
                replace = kwargs.get("replace", True)
                append = kwargs.get("append", True)
                
                # 检查 key 是否存在且类型是否匹配
                key_exists = self.client.exists(key)
                if key_exists:
                    key_type_result = self.client.type(key)
                    if isinstance(key_type_result, bytes):
                        key_type = key_type_result.decode('utf-8')
                    else:
                        key_type = str(key_type_result)
                    
                    if key_type != "list" and key_type != "none":
                        # 类型不匹配
                        if replace:
                            # 如果允许替换，删除现有 key
                            self.client.delete(key)
                        else:
                            raise ValueError(
                                f"Key '{key}' 已存在且类型为 '{key_type}'，无法写入 List 类型。"
                                f"请设置 replace=True 来替换现有数据，或使用不同的 key。"
                            )
                
                if replace:
                    # 删除现有 key，然后写入
                    self.client.delete(key)
                
                # 将列表元素转换为字符串
                list_data = []
                for item in data:
                    if isinstance(item, (dict, list)):
                        list_data.append(json.dumps(item, ensure_ascii=False))
                    else:
                        list_data.append(str(item))
                
                if list_data:
                    if append:
                        # 追加到末尾
                        self.client.rpush(key, *list_data)
                    else:
                        # 从头部插入
                        self.client.lpush(key, *list_data)
            
            elif data_type == "set":
                # Set 类型
                replace = kwargs.get("replace", False)
                
                # 检查 key 是否存在且类型是否匹配
                key_exists = self.client.exists(key)
                if key_exists:
                    key_type_result = self.client.type(key)
                    if isinstance(key_type_result, bytes):
                        key_type = key_type_result.decode('utf-8')
                    else:
                        key_type = str(key_type_result)
                    
                    if key_type != "set" and key_type != "none":
                        # 类型不匹配
                        if replace:
                            # 如果允许替换，删除现有 key
                            self.client.delete(key)
                        else:
                            raise ValueError(
                                f"Key '{key}' 已存在且类型为 '{key_type}'，无法写入 Set 类型。"
                                f"请设置 replace=True 来替换现有数据，或使用不同的 key。"
                            )
                
                if replace:
                    # 删除现有 key，然后写入
                    self.client.delete(key)
                
                # 将列表元素转换为字符串
                set_data = set()
                for item in data:
                    if isinstance(item, (dict, list)):
                        set_data.add(json.dumps(item, ensure_ascii=False))
                    else:
                        set_data.add(str(item))
                
                if set_data:
                    self.client.sadd(key, *set_data)
            
            elif data_type == "zset":
                # Sorted Set 类型
                replace = kwargs.get("replace", False)
                scores = kwargs.get("scores")
                
                # 检查 key 是否存在且类型是否匹配
                key_exists = self.client.exists(key)
                if key_exists:
                    key_type_result = self.client.type(key)
                    if isinstance(key_type_result, bytes):
                        key_type = key_type_result.decode('utf-8')
                    else:
                        key_type = str(key_type_result)
                    
                    if key_type != "zset" and key_type != "none":
                        # 类型不匹配
                        if replace:
                            # 如果允许替换，删除现有 key
                            self.client.delete(key)
                        else:
                            raise ValueError(
                                f"Key '{key}' 已存在且类型为 '{key_type}'，无法写入 ZSet 类型。"
                                f"请设置 replace=True 来替换现有数据，或使用不同的 key。"
                            )
                
                if replace:
                    # 删除现有 key，然后写入
                    self.client.delete(key)
                
                # 准备分数字典
                if scores:
                    # 使用提供的 scores
                    zset_data = {}
                    for member in data if isinstance(data, list) else data.keys():
                        score = scores.get(member, 0)
                        if isinstance(member, (dict, list)):
                            member_str = json.dumps(member, ensure_ascii=False)
                        else:
                            member_str = str(member)
                        zset_data[member_str] = float(score)
                elif isinstance(data, dict):
                    # data 本身就是 {member: score} 格式
                    zset_data = {}
                    for member, score in data.items():
                        if isinstance(member, (dict, list)):
                            member_str = json.dumps(member, ensure_ascii=False)
                        else:
                            member_str = str(member)
                        zset_data[member_str] = float(score)
                else:
                    raise ValueError("ZSet 类型需要提供 scores 参数或使用 {member: score} 格式的字典")
                
                if zset_data:
                    self.client.zadd(key, zset_data)
            
            else:
                # String 类型（默认）
                if isinstance(data, (dict, list)):
                    value = json.dumps(data, ensure_ascii=False)
                else:
                    value = str(data)
                
                if ttl:
                    self.client.setex(key, ttl, value)
                else:
                    self.client.set(key, value)
            
            # 设置过期时间（如果指定了 TTL）
            if ttl:
                self.client.expire(key, ttl)
            
            return True
        except Exception as e:
            raise Exception(f"写入 Redis 数据失败: {e}")

