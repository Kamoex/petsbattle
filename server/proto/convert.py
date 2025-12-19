#!/usr/bin/env python3
"""
Proto JSON to Python Class Converter
将 proto.json 转换为 Python 类定义
"""

import json
import re
from typing import Any, Dict, List, Set, Tuple, Optional


def parse_type(value: Any) -> Tuple[str, bool, Optional[str]]:
    """
    解析字段类型
    返回: (python_type, is_array, sub_class_name)
    """
    if isinstance(value, dict):
        # 嵌套对象
        return ('dict', False, None)
    elif isinstance(value, list):
        if len(value) > 0 and isinstance(value[0], dict):
            # 数组元素是对象
            return ('list_dict', True, None)
        elif len(value) > 0 and isinstance(value[0], str):
            # 数组元素是字符串，需要解析类型
            type_desc = value[0]
            if 'int' in type_desc:
                return ('List[int]', False, None)
            else:
                return ('List[str]', False, None)
        else:
            return ('List[Any]', False, None)
    elif isinstance(value, str):
        # 字符串类型描述，解析类型
        if 'int' in value.lower():
            return ('int', False, None)
        else:
            return ('str', False, None)
    elif isinstance(value, int):
        return ('int', False, None)
    else:
        return ('Any', False, None)


def generate_sub_class_name(parent_name: str, path: List[str]) -> str:
    """生成子类名称"""
    return parent_name + '_' + '_'.join(path)


def collect_classes(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    收集所有需要生成的类
    返回: {class_name: class_definition}
    """
    classes = {}
    
    for message_name, message_data in data.items():
        if not isinstance(message_data, dict):
            continue
        
        # 收集主类
        class_def = {
            'name': message_name,
            'fields': {},
            'id': None,
            'nested_classes': []
        }
        
        # 提取 id
        if 'id' in message_data:
            class_def['id'] = message_data['id']
        
        # 处理字段
        for key, value in message_data.items():
            if key in ['desc', 'id']:
                continue
            
            python_type, is_array, _ = parse_type(value)
            
            if python_type == 'dict':
                # 嵌套对象，需要生成子类
                sub_class_name = generate_sub_class_name(message_name, [key])
                class_def['fields'][key] = sub_class_name
                # 递归收集嵌套类
                nested_classes = collect_nested_classes(message_name, [key], value)
                class_def['nested_classes'].extend(nested_classes)
            elif python_type == 'list_dict':
                # 数组元素是对象
                sub_class_name = generate_sub_class_name(message_name, [key])
                class_def['fields'][key] = f'List[{sub_class_name}]'
                # 生成数组元素的类
                if len(value) > 0:
                    nested_classes = collect_nested_classes(message_name, [key], value[0])
                    class_def['nested_classes'].extend(nested_classes)
            else:
                class_def['fields'][key] = python_type
        
        classes[message_name] = class_def
    
    return classes


def collect_nested_classes(parent_name: str, path: List[str], data: Any) -> List[Dict[str, Any]]:
    """
    递归收集嵌套类
    """
    nested_classes = []
    
    if not isinstance(data, dict):
        return nested_classes
    
    current_class_name = generate_sub_class_name(parent_name, path)
    current_class = {
        'name': current_class_name,
        'fields': {},
        'id': None,
        'nested_classes': []
    }
    
    for key, value in data.items():
        if key in ['desc']:
            continue
        
        python_type, is_array, _ = parse_type(value)
        
        if python_type == 'dict':
            # 继续嵌套
            sub_class_name = generate_sub_class_name(parent_name, path + [key])
            current_class['fields'][key] = sub_class_name
            nested = collect_nested_classes(parent_name, path + [key], value)
            current_class['nested_classes'].extend(nested)
        elif python_type == 'list_dict':
            # 数组元素是对象
            sub_class_name = generate_sub_class_name(parent_name, path + [key])
            current_class['fields'][key] = f'List[{sub_class_name}]'
            if len(value) > 0:
                nested = collect_nested_classes(parent_name, path + [key], value[0])
                current_class['nested_classes'].extend(nested)
        else:
            current_class['fields'][key] = python_type
    
    nested_classes.append(current_class)
    nested_classes.extend(current_class['nested_classes'])
    
    return nested_classes


def get_default_value(field_type: str, all_classes: Set[str]) -> str:
    """
    获取字段的默认值
    """
    if field_type.startswith('List['):
        return '[]'
    elif field_type in all_classes:
        # 嵌套对象
        return 'None'
    elif field_type == 'int':
        return '-1'
    elif field_type == 'str':
        return '""'
    else:
        return 'None'


def generate_class_code(class_def: Dict[str, Any], all_classes: Set[str]) -> str:
    """
    生成类代码
    """
    class_name = class_def['name']
    fields = class_def['fields']
    class_id = class_def['id']
    
    lines = []
    lines.append(f"class {class_name}:")
    
    # 添加类属性 id
    if class_id is not None:
        lines.append(f"    id: int = {class_id}")
        lines.append("")
    
    # 检查是否有 code 和 message 字段
    has_code = 'code' in fields
    has_message = 'message' in fields
    has_code_and_message = has_code and has_message
    
    # 生成 __init__ 方法
    if has_code_and_message:
        # 有 code 和 message，作为参数
        lines.append("    def __init__(self, code: int = -1, message: str = \"\"):")
        lines.append("        self.code: int = code")
        lines.append("        self.message: str = message")
        
        # 初始化其他字段
        for field_name, field_type in fields.items():
            if field_name not in ['code', 'message']:
                default_value = get_default_value(field_type, all_classes)
                lines.append(f"        self.{field_name}: {field_type} = {default_value}")
    else:
        # 没有 code 和 message，无参数构造函数
        lines.append("    def __init__(self):")
        
        # 初始化所有字段
        for field_name, field_type in fields.items():
            default_value = get_default_value(field_type, all_classes)
            lines.append(f"        self.{field_name}: {field_type} = {default_value}")
    
    if not fields and class_id is None:
        lines.append("    pass")
    
    lines.append("")
    
    # 生成 to_dict 方法
    lines.append("    def to_dict(self) -> dict:")
        
    if class_id is not None or fields:
        lines.append("        result = {}")
        
        # 添加 id
        if class_id is not None:
            lines.append("        result['id'] = self.id")
        
        # 添加其他字段
        for field_name, field_type in fields.items():
            if field_type.startswith('List['):
                # 处理列表
                inner_type = field_type[5:-1]  # 提取 List[T] 中的 T
                if inner_type in all_classes:
                    # 列表元素是自定义类
                    lines.append(f"        result['{field_name}'] = [item.to_dict() for item in self.{field_name}] if self.{field_name} is not None else None")
                else:
                    # 列表元素是基本类型
                    lines.append(f"        result['{field_name}'] = self.{field_name}")
            elif field_type in all_classes:
                # 嵌套对象
                lines.append(f"        result['{field_name}'] = self.{field_name}.to_dict() if self.{field_name} is not None else None")
            else:
                # 基本类型
                lines.append(f"        result['{field_name}'] = self.{field_name}")
        
        lines.append("        return result")
    else:
        lines.append("        return {}")
    
    return '\n'.join(lines)


def main():
    # 读取 proto.json
    with open('/home/ubuntu/workspace/petsbattle/server/proto/proto.json', 'r', encoding='utf-8') as f:
        proto_data = json.load(f)
    
    # 收集所有类
    classes = collect_classes(proto_data)
    
    # 收集所有类名（包括嵌套类）
    all_class_names = set()
    for class_def in classes.values():
        all_class_names.add(class_def['name'])
        for nested in class_def['nested_classes']:
            all_class_names.add(nested['name'])
    
    # 生成代码
    output_lines = []
    output_lines.append('"""')
    output_lines.append('自动生成的协议类')
    output_lines.append('由 convert.py 从 proto.json 生成')
    output_lines.append('"""')
    output_lines.append('')
    output_lines.append('from __future__ import annotations')
    output_lines.append('from typing import List, Any, Optional')
    output_lines.append('')
    output_lines.append('')
    
    # 先生成所有嵌套类（因为主类可能依赖它们）
    nested_classes_generated = set()
    for class_def in classes.values():
        for nested in class_def['nested_classes']:
            if nested['name'] not in nested_classes_generated:
                output_lines.append(generate_class_code(nested, all_class_names))
                output_lines.append('')
                output_lines.append('')
                nested_classes_generated.add(nested['name'])
    
    # 生成主类
    for class_def in classes.values():
        output_lines.append(generate_class_code(class_def, all_class_names))
        output_lines.append('')
        output_lines.append('')
    
    # 写入文件
    output_code = '\n'.join(output_lines)
    with open('/home/ubuntu/workspace/petsbattle/server/proto/proto.py', 'w', encoding='utf-8') as f:
        f.write(output_code)
    
    print("转换完成！生成的文件：/home/ubuntu/workspace/petsbattle/server/proto/proto.py")
    print(f"共生成 {len(classes)} 个主类，{len(nested_classes_generated)} 个嵌套类")


if __name__ == '__main__':
    main()

