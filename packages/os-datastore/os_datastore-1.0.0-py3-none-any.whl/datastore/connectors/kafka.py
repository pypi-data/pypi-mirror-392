"""
Kafka 连接器
"""
from typing import Dict, Any, List, Optional, Iterator
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError
import json
import time

from datastore.connectors.base import BaseConnector


class KafkaConnector(BaseConnector):
    """Kafka 消息队列连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.producer: Optional[KafkaProducer] = None
        self.consumer: Optional[KafkaConsumer] = None
        self.current_group_id: Optional[str] = None
        self.topic = config.get("topic", "")
        self.bootstrap_servers = f"{config['host']}:{config.get('port', 9092)}"
    
    def connect(self) -> None:
        """连接 Kafka"""
        # Kafka 连接是延迟的，这里只标记为已连接
        self._connected = True
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.producer:
            try:
                self.producer.close()
            except Exception:
                pass
        if self.consumer:
            try:
                self.consumer.close()
            except Exception:
                pass
        self.producer = None
        self.consumer = None
        self.current_group_id = None
        self._connected = False
    
    def _get_producer(self) -> KafkaProducer:
        """获取或创建 Producer"""
        if not self.producer:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
            )
        return self.producer
    
    def _get_consumer(self, group_id: str = "datastore-consumer", auto_offset_reset: str = "latest") -> KafkaConsumer:
        """
        获取或创建 Consumer
        
        Args:
            group_id: Consumer Group ID（如果为 None，则不使用 consumer group）
            auto_offset_reset: offset 重置策略
                - "earliest": 从最早的消息开始（如果没有保存的 offset）
                - "latest": 从最新的消息开始（如果没有保存的 offset）
                注意：如果有 consumer group 且有保存的 offset，会从保存的 offset 开始消费
        """
        # 如果 consumer 不存在，或者 group_id 发生变化，需要重新创建
        if not self.consumer or self.current_group_id != group_id:
            # 关闭旧的 consumer
            if self.consumer:
                try:
                    self.consumer.close()
                except Exception:
                    pass
            
            consumer_config = {
                'bootstrap_servers': self.bootstrap_servers,
                'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
                'enable_auto_commit': False,  # 禁用自动提交，使用手动提交
                'consumer_timeout_ms': 1000,
                'auto_offset_reset': auto_offset_reset,  # earliest 或 latest
            }
            
            # 如果提供了 group_id，则使用 consumer group
            if group_id:
                consumer_config['group_id'] = group_id
            
            self.consumer = KafkaConsumer(
                self.topic,
                **consumer_config
            )
            self.current_group_id = group_id
            
            # 等待分区分配完成
            timeout = 5  # 5秒超时
            start_time = time.time()
            while not self.consumer.assignment() and (time.time() - start_time) < timeout:
                self.consumer.poll(timeout_ms=100)
                time.sleep(0.1)
        
        return self.consumer
    
    def commit_offset(self, **kwargs) -> bool:
        """
        手动提交偏移量
        
        Args:
            **kwargs: 可选参数
                - offsets: 要提交的偏移量字典 {TopicPartition: OffsetAndMetadata}（默认提交所有分区）
                - async: 是否异步提交（默认 False，同步提交）
        
        Returns:
            True 如果提交成功
            
        Raises:
            RuntimeError: 如果 Consumer 未初始化或没有 consumer group
        """
        if not self.consumer:
            raise RuntimeError("Consumer 未初始化，无法提交偏移量")
        
        # 检查是否有 consumer group（没有 consumer group 无法提交偏移量）
        if not self.current_group_id:
            raise RuntimeError("没有 consumer group，无法提交偏移量。请在使用 read() 或 readstream() 时指定 group_id")
        
        try:
            offsets = kwargs.get("offsets", None)
            async_commit = kwargs.get("async", False)
            
            if async_commit:
                # 异步提交
                if offsets:
                    self.consumer.commit_async(offsets=offsets)
                else:
                    self.consumer.commit_async()
            else:
                # 同步提交
                if offsets:
                    self.consumer.commit(offsets=offsets)
                else:
                    self.consumer.commit()
            
            return True
        except Exception as e:
            raise Exception(f"提交偏移量失败: {e}")
    
    def read(self, timeout_ms: int = 1000, max_records: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        读取消息
        
        Args:
            timeout_ms: 超时时间（毫秒）
            max_records: 最大记录数
            **kwargs: 其他参数
                - group_id: Consumer Group ID（默认 "datastore-consumer"，None 表示不使用 consumer group）
                - auto_offset_reset: offset 重置策略（"earliest" 或 "latest"，默认 "latest"）
                    - 如果有 consumer group 且有保存的 offset，会从保存的 offset 开始消费
                    - 如果没有保存的 offset，则根据此参数决定从 earliest 或 latest 开始
                - seek_to_end: 是否先定位到末尾（用于只读取之后的新消息，默认 False）
                - auto_commit: 是否自动提交偏移量（默认 False，需要手动调用 commit_offset）
            
        Returns:
            消息列表
        """
        if not self._connected:
            self.connect()
        
        try:
            group_id = kwargs.get("group_id", "datastore-consumer")
            auto_offset_reset = kwargs.get("auto_offset_reset", "latest")
            seek_to_end = kwargs.get("seek_to_end", False)
            auto_commit = kwargs.get("auto_commit", False)
            
            consumer = self._get_consumer(group_id, auto_offset_reset=auto_offset_reset)
            messages = []
            
            # 如果 seek_to_end 为 True，先定位到末尾（用于只读取之后的新消息）
            if seek_to_end:
                try:
                    # 等待分区分配
                    partitions = consumer.assignment()
                    if partitions:
                        consumer.seek_to_end()
                except Exception:
                    pass
            
            # 使用 poll 方法读取消息
            # 可能需要多次 poll 才能获取到消息
            total_timeout = timeout_ms
            poll_timeout = min(1000, timeout_ms)  # 每次 poll 的超时时间
            
            while total_timeout > 0 and len(messages) < max_records:
                msg_pack = consumer.poll(timeout_ms=poll_timeout)
                
                # 收集消息
                for topic_partition, records in msg_pack.items():
                    for record in records:
                        if len(messages) >= max_records:
                            break
                        messages.append(record.value)
                    if len(messages) >= max_records:
                        break
                
                # 如果已经获取到消息，可以提前退出
                if messages:
                    break
                
                total_timeout -= poll_timeout
            
            # 如果启用了自动提交，则提交偏移量
            if auto_commit and messages and group_id:
                try:
                    # 只有在有 consumer group 时才能提交
                    consumer.commit()
                except Exception:
                    pass
            
            return messages
        except Exception as e:
            raise Exception(f"读取 Kafka 消息失败: {e}")
    
    def write(self, data: Dict[str, Any], key: Optional[str] = None, **kwargs) -> bool:
        """
        写入消息
        
        Args:
            data: 要写入的数据字典
            key: 消息 key（可选）
            **kwargs: 其他参数
            
        Returns:
            True 如果写入成功
        """
        if not self._connected:
            self.connect()
        
        try:
            producer = self._get_producer()
            future = producer.send(self.topic, value=data, key=key.encode() if key else None)
            # 等待发送完成
            record_metadata = future.get(timeout=10)
            return True
        except KafkaError as e:
            raise Exception(f"写入 Kafka 消息失败: {e}")
    
    def readstream(self, poll_timeout_ms: int = 1000, **kwargs) -> Iterator[Dict[str, Any]]:
        """
        持续读取消息流（生成器）
        
        一旦 Kafka 主题有新数据，就会立即读取并 yield。
        这是一个生成器方法，会持续运行直到被停止（如 KeyboardInterrupt）。
        
        Args:
            poll_timeout_ms: 每次 poll 的超时时间（毫秒），默认 1000ms
            **kwargs: 其他参数
                - group_id: Consumer Group ID（默认 "datastore-consumer-stream"，None 表示不使用 consumer group）
                - auto_offset_reset: offset 重置策略（"earliest" 或 "latest"，默认 "latest"）
                    - 如果有 consumer group 且有保存的 offset，会从保存的 offset 开始消费
                    - 如果没有保存的 offset，则根据此参数决定从 earliest 或 latest 开始
                - seek_to_end: 是否先定位到末尾（用于只读取新消息，默认 False）
                - max_messages: 最大消息数量，达到后停止（默认 None，无限制）
                - stop_on_empty: 如果 poll 返回空是否停止（默认 False，继续等待）
                - auto_commit: 是否自动提交偏移量（默认 False，需要手动调用 commit_offset）
            
        Yields:
            消息字典
            
        Example:
            >>> for message in connector.readstream():
            ...     print(f"收到消息: {message}")
            ...     # 处理消息
            ...     connector.commit_offset()  # 手动提交偏移量
        """
        if not self._connected:
            self.connect()
        
        try:
            group_id = kwargs.get("group_id", "datastore-consumer-stream")
            auto_offset_reset = kwargs.get("auto_offset_reset", "latest")
            seek_to_end = kwargs.get("seek_to_end", False)
            max_messages = kwargs.get("max_messages", None)
            stop_on_empty = kwargs.get("stop_on_empty", False)
            auto_commit = kwargs.get("auto_commit", False)
            
            consumer = self._get_consumer(group_id, auto_offset_reset=auto_offset_reset)
            
            # 如果 seek_to_end 为 True，先定位到末尾（用于只读取之后的新消息）
            if seek_to_end:
                try:
                    partitions = consumer.assignment()
                    if partitions:
                        consumer.seek_to_end()
                except Exception:
                    pass
            
            message_count = 0
            
            # 持续读取消息
            while True:
                try:
                    # Poll 消息
                    msg_pack = consumer.poll(timeout_ms=poll_timeout_ms)
                    
                    # 如果没有消息
                    if not msg_pack:
                        if stop_on_empty:
                            # 如果设置了 stop_on_empty，且没有消息，则停止
                            break
                        # 否则继续等待
                        continue
                    
                    # 处理收到的消息
                    for topic_partition, records in msg_pack.items():
                        for record in records:
                            message_count += 1
                            
                            # 如果达到最大消息数，停止
                            if max_messages and message_count > max_messages:
                                return
                            
                            # Yield 消息
                            yield record.value
                            
                            # 如果启用了自动提交，则提交偏移量
                            if auto_commit and group_id:
                                try:
                                    # 只有在有 consumer group 时才能提交
                                    consumer.commit()
                                except Exception:
                                    pass
                            
                except KeyboardInterrupt:
                    # 用户中断（Ctrl+C）
                    break
                except Exception as e:
                    # 其他异常，记录但继续尝试
                    raise Exception(f"读取 Kafka 消息流失败: {e}")
                    
        except Exception as e:
            raise Exception(f"Kafka 消息流读取失败: {e}")

