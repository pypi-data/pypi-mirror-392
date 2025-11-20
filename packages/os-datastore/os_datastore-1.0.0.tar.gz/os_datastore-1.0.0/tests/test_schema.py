"""
Schema 验证测试
"""
import pytest
from datastore.schema import SchemaValidator


def test_schema_validator():
    """测试 Schema 验证器"""
    schema = {
        "type": "object",
        "required": ["thingid", "filepath", "time"],
        "properties": {
            "thingid": {
                "type": "string",
                "description": "事物的唯一标识符"
            },
            "filepath": {
                "type": "string",
                "description": "文件在系统中的路径"
            },
            "time": {
                "type": "string",
                "format": "date-time",
                "description": "时间信息，建议使用 ISO 8601 格式"
            }
        },
        "additionalProperties": False
    }
    
    validator = SchemaValidator(schema)
    
    # 测试有效数据
    valid_data = {
        "thingid": "device_001",
        "filepath": "/path/to/file.jpg",
        "time": "2025-01-18T10:00:00Z"
    }
    
    is_valid, error = validator.is_valid(valid_data)
    assert is_valid is True
    assert error is None
    
    # 测试无效数据（缺少必填字段）
    invalid_data = {
        "thingid": "device_001"
    }
    
    is_valid, error = validator.is_valid(invalid_data)
    assert is_valid is False
    assert error is not None
    
    # 测试获取必填字段
    required_fields = validator.get_required_fields()
    assert "thingid" in required_fields
    assert "filepath" in required_fields
    assert "time" in required_fields

