"""
Schema 验证模块
"""
import json
from typing import Dict, Any, List, Optional, Tuple
from jsonschema import validate, ValidationError, Draft7Validator


class SchemaValidator:
    """Schema 验证器"""
    
    def __init__(self, schema: Dict[str, Any]):
        """
        初始化 Schema 验证器
        
        Args:
            schema: JSON Schema 字典
        """
        self.schema = schema
        self.validator = Draft7Validator(schema)
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        验证数据是否符合 schema
        
        Args:
            data: 要验证的数据字典
            
        Returns:
            True 如果验证通过
            
        Raises:
            ValidationError: 如果验证失败
        """
        validate(instance=data, schema=self.schema)
        return True
    
    def is_valid(self, data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        检查数据是否有效，不抛出异常
        
        Args:
            data: 要验证的数据字典
            
        Returns:
            (is_valid, error_message) 元组
        """
        errors = list(self.validator.iter_errors(data))
        if errors:
            error_messages = [str(error) for error in errors]
            return False, "; ".join(error_messages)
        return True, None
    
    def get_required_fields(self) -> List[str]:
        """
        获取必填字段列表
        
        Returns:
            必填字段名称列表
        """
        return self.schema.get("required", [])
    
    def get_properties(self) -> Dict[str, Any]:
        """
        获取属性定义
        
        Returns:
            属性定义字典
        """
        return self.schema.get("properties", {})

