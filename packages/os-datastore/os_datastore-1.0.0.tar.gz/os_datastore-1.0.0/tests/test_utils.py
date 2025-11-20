"""
工具函数测试
"""
import pytest
from datastore.utils import parse_datasource_url


def test_parse_kafka_url():
    """测试解析 Kafka URL"""
    url = "kafka://192.168.2.123:9092/os.iot.rotary_wheel_image?authInfo=&mechanism=&securityProtocol="
    config = parse_datasource_url(url)
    
    assert config["scheme"] == "kafka"
    assert config["host"] == "192.168.2.123"
    assert config["port"] == 9092
    assert config["topic"] == "os.iot.rotary_wheel_image"


def test_parse_minio_url():
    """测试解析 MinIO URL"""
    url = "minio://192.168.2.123:9000/my-bucket?accessKey=minioadmin&secretKey=minioadmin&secure=false"
    config = parse_datasource_url(url)
    
    assert config["scheme"] == "minio"
    assert config["host"] == "192.168.2.123"
    assert config["port"] == 9000
    assert config["bucket"] == "my-bucket"
    assert config["access_key"] == "minioadmin"
    assert config["secret_key"] == "minioadmin"


def test_parse_postgres_url():
    """测试解析 PostgreSQL URL"""
    url = "postgres://localhost:5432/mydb?username=user&password=pass"
    config = parse_datasource_url(url)
    
    assert config["scheme"] == "postgres"
    assert config["host"] == "localhost"
    assert config["port"] == 5432
    assert config["database"] == "mydb"
    assert config["username"] == "user"
    assert config["password"] == "pass"


def test_parse_redis_url():
    """测试解析 Redis URL"""
    url = "redis://localhost:6379/0?password=mypass"
    config = parse_datasource_url(url)
    
    assert config["scheme"] == "redis"
    assert config["host"] == "localhost"
    assert config["port"] == 6379
    assert config["db"] == 0
    assert config["password"] == "mypass"


def test_parse_http_url():
    """测试解析 HTTP URL"""
    url = "http://192.168.2.123:8067/v1/phm/assets"
    config = parse_datasource_url(url)
    
    assert config["scheme"] == "http"
    assert config["host"] == "192.168.2.123"
    assert config["port"] == 8067
    assert config["path"] == "/v1/phm/assets"
    assert "base_url" in config

