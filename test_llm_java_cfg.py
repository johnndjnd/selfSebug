#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from chat import generate_java_cfg_with_llm
import os
import sys

def read_java_file(file_path):
    """读取Java文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <java_file_path> [method_name] [class_name]")
        sys.exit(1)
    
    java_file = sys.argv[1]
    method_name = sys.argv[2] if len(sys.argv) > 2 else None
    class_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 读取Java代码
    java_code = read_java_file(java_file)
    
    # 使用LLM生成CFG
    cfg_text = generate_java_cfg_with_llm(java_code, method_name, class_name)
    
    # 输出结果
    print(cfg_text)

if __name__ == "__main__":
    main() 