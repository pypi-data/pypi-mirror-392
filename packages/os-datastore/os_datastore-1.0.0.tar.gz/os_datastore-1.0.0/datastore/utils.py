"""
工具函数模块
"""
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs


def parse_datasource_url(url: str) -> Dict[str, any]:
    """
    解析数据源 URL，返回连接信息字典
    
    支持的格式：
    - kafka://host:port/topic?authInfo=&mechanism=&securityProtocol=
    - minio://host:port/bucket?username=&password=
    - cassandra://host:port/datacenter/keyspace/table?username=&password=
    - redis://host:port/db?password=
    - http://host:port/path
    
    Args:
        url: 数据源 URL
        
    Returns:
        包含连接信息的字典
    """
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    
    result = {
        "scheme": scheme,
        "host": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path.lstrip("/"),
        "query": parse_qs(parsed.query),
    }
    
    # 根据不同的 scheme 解析特定参数
    if scheme == "kafka":
        result["topic"] = result["path"]
        result["auth_info"] = result["query"].get("authInfo", [""])[0]
        result["mechanism"] = result["query"].get("mechanism", [""])[0]
        result["security_protocol"] = result["query"].get("securityProtocol", [""])[0]
        
    elif scheme == "minio":
        result["bucket"] = result["path"]
        result["username"] = result["query"].get("username", [""])[0]
        result["password"] = result["query"].get("password", [""])[0]
        result["secure"] = result["query"].get("secure", ["false"])[0].lower() == "true"
        
    elif scheme == "cassandra":
        # 支持格式: cassandra://host:port/datacenter/keyspace/table?username=&password=
        path_parts = result["path"].split("/")
        if len(path_parts) >= 3:
            # 格式: datacenter/keyspace/table
            result["datacenter"] = path_parts[0]
            result["keyspace"] = path_parts[1]
            result["table"] = "/".join(path_parts[2:])  # 支持表名中包含斜杠
        else:
            raise ValueError(
                f"Cassandra URL 格式错误: {url}\n"
                f"正确格式应为: cassandra://host:port/datacenter/keyspace/table?username=&password="
            )
        result["username"] = result["query"].get("username", [""])[0]
        result["password"] = result["query"].get("password", [""])[0]
        
    elif scheme == "redis":
        # Redis URL 格式: redis://host:port/db?password=
        # db 在路径中，如果路径为空或无效，默认为 0
        if result["path"]:
            try:
                result["db"] = int(result["path"])
            except ValueError:
                result["db"] = 0
        else:
            result["db"] = 0
        result["password"] = result["query"].get("password", [""])[0]
        
    elif scheme == "http" or scheme == "https":
        result["path"] = parsed.path
        result["base_url"] = f"{scheme}://{parsed.hostname}"
        if parsed.port:
            result["base_url"] += f":{parsed.port}"
    
    return result

