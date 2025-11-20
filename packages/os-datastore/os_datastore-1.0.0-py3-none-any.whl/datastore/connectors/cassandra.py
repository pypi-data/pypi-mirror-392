"""
Cassandra 连接器
"""
from typing import Dict, Any, List, Optional
from cassandra.cluster import Cluster, DCAwareRoundRobinPolicy
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement

from datastore.connectors.base import BaseConnector


class CassandraConnector(BaseConnector):
    """Cassandra 数据库连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cluster: Optional[Cluster] = None
        self.session = None
        self.keyspace = config.get("keyspace", "")
        self.datacenter = config.get("datacenter")
        self.default_table = config.get("table")
        
        # 验证必需的配置
        if not self.keyspace:
            raise ValueError("Cassandra 配置中缺少 keyspace")
        if not self.datacenter:
            raise ValueError("Cassandra 配置中缺少 datacenter")
        if not self.default_table:
            raise ValueError("Cassandra 配置中缺少 table")
    
    def connect(self) -> None:
        """连接 Cassandra"""
        contact_points = [self.config['host']]
        port = self.config.get('port', 9042)
        
        username = self.config.get("username", "")
        password = self.config.get("password", "")
        
        cluster_kwargs = {
            'contact_points': contact_points,
            'port': port
        }
        
        # 如果指定了 datacenter，使用 DCAwareRoundRobinPolicy
        if self.datacenter:
            cluster_kwargs['load_balancing_policy'] = DCAwareRoundRobinPolicy(local_dc=self.datacenter)
        
        if username and password:
            auth_provider = PlainTextAuthProvider(username=username, password=password)
            cluster_kwargs['auth_provider'] = auth_provider
        
        self.cluster = Cluster(**cluster_kwargs)
        self.session = self.cluster.connect(self.keyspace)
        self._connected = True
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()
        self.session = None
        self.cluster = None
        self._connected = False
    
    def read(self, table: Optional[str] = None, where_clause: str = "", limit: int = 100, **kwargs) -> List[Dict[str, Any]]:
        """
        读取数据
        
        Args:
            table: 表名（如果为 None，使用 URL 中指定的默认表名）
            where_clause: WHERE 子句（不包含 WHERE 关键字）
            limit: 限制返回行数
            **kwargs: 其他参数
            
        Returns:
            数据行列表
        """
        if not self._connected:
            self.connect()
        
        # 如果没有指定表名，使用默认表名（从 URL 解析得到）
        if not table:
            table = self.default_table
        
        if not table:
            raise ValueError("必须指定表名，可以通过 table 参数或 URL 中的表名指定")
        
        query = f"SELECT * FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            statement = SimpleStatement(query)
            rows = self.session.execute(statement)
            # Cassandra Row 对象不能直接用 dict() 转换，需要使用 _fields 属性
            result = []
            for row in rows:
                # 方法1: 使用 _fields 和 getattr
                row_dict = {field: getattr(row, field) for field in row._fields}
                result.append(row_dict)
            return result
        except Exception as e:
            raise Exception(f"读取 Cassandra 数据失败: {e}")
    
    def write(self, data: Dict[str, Any], table: Optional[str] = None, **kwargs) -> bool:
        """
        写入数据
        
        Args:
            data: 要写入的数据字典
            table: 表名（如果为 None，使用 URL 中指定的默认表名）
            **kwargs: 其他参数
            
        Returns:
            True 如果写入成功
        """
        if not self._connected:
            self.connect()
        
        # 如果没有指定表名，使用默认表名（从 URL 解析得到）
        if not table:
            table = self.default_table
        
        if not table:
            raise ValueError("必须指定表名，可以通过 table 参数或 URL 中的表名指定")
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            # Cassandra 使用 PreparedStatement 进行参数化查询
            prepared = self.session.prepare(query)
            self.session.execute(prepared, values)
            return True
        except Exception as e:
            raise Exception(f"写入 Cassandra 数据失败: {e}")

