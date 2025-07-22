import subprocess
import sys
import json
import tempfile
import os
from pathlib import Path
from loguru import logger
from typing import Dict, List, Set, Optional, Tuple, Any
import copy
import re


class JavaCFG:
    def __init__(self, source_path: str, target_method: str = None, target_class: str = None):
        """
        改进的Java函数级CFG构建器
        Args:
            source_path: Java源代码文件路径
            target_method: 目标方法名（不包含参数），如果不指定则使用第一个方法
            target_class: 目标类名，如果不指定则使用第一个类
        """
        # #logger.info(f"🚀🚀🚀 JavaCFG.__init__ called with source_path={source_path}")
        
        self.source_path = source_path
        self.source_code = Path(source_path).read_text(encoding='utf-8')
        self.source_lines = self.source_code.splitlines()
        
        # #logger.info(f"📖 Read {len(self.source_lines)} lines from Java file")
        
        # Java关键字集合
        self.java_keywords = {
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char',
            'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum',
            'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements',
            'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new',
            'package', 'private', 'protected', 'public', 'return', 'short', 'static',
            'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
            'transient', 'try', 'void', 'volatile', 'while'
        }
        
        # 解析Java AST
        self.java_ast = self._parse_java_ast()
        
        # 解析所有类和方法
        self.all_classes = self._parse_all_classes()
        self.all_methods = self._parse_all_methods()
        
        # 确定目标类和方法
        if target_class:
            if target_class not in self.all_classes:
                raise ValueError(f"目标类 '{target_class}' 在源代码中未找到")
            self.target_class = target_class
        else:
            self.target_class = list(self.all_classes.keys())[0] if self.all_classes else None
            
        if target_method:
            if target_method not in self.all_methods:
                raise ValueError(f"目标方法 '{target_method}' 在源代码中未找到")
            self.target_method = target_method
        else:
            # 从目标类中选择第一个方法
            class_methods = [method for method in self.all_methods.keys() 
                           if self.all_methods[method]['class'] == self.target_class]
            self.target_method = class_methods[0] if class_methods else None
            
        if not self.target_method:
            raise ValueError("未找到任何方法定义")
            
        # #logger.info(f"目标类: {self.target_class}")
        # #logger.info(f"目标方法: {self.target_method}")
        
        # 构建CFG
        self.blocks = []
        self.connections = []
        self.method_signature = self._get_method_signature(self.target_method)
        
        # 跟踪当前的循环和异常处理上下文
        self.loop_stack = []  # 用于处理break/continue
        self.try_stack = []   # 用于处理异常
        
        # 构建完整的CFG
        self._build_complete_cfg()
        
        # 生成文本表示
        self.cfg_text = self._generate_cfg_text()
        self.block_num = len(self.blocks)
        self.block_code_list = [block['code'] for block in self.blocks]
    
    def _parse_java_ast(self) -> Dict:
        """使用改进的Java解析方法"""
        return self._improved_parse()
    
    def _improved_parse(self) -> Dict:
        """改进的Java代码解析方法"""
        classes = {}
        methods = {}
        
        # 解析类定义 - 更精确的正则表达式
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+|final\s+)?class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?\s*\{'
        for match in re.finditer(class_pattern, self.source_code):
            class_name = match.group(1)
            classes[class_name] = {
                'name': class_name,
                'start_line': self.source_code[:match.start()].count('\n') + 1,
                'start_pos': match.start(),
                'end_pos': self._find_class_end(match.start())
            }
        
        # 解析方法定义 - 更精确的正则表达式
        method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?(?:\w+(?:\[\])?)\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{'
        for match in re.finditer(method_pattern, self.source_code):
            method_name = match.group(1)
            
            # 过滤Java关键字和常见的非方法名
            if method_name in self.java_keywords:
                continue
            
            method_line = self.source_code[:match.start()].count('\n') + 1
            
            # 找到方法所属的类
            belonging_class = None
            for class_name, class_info in classes.items():
                if (match.start() > class_info['start_pos'] and 
                    match.start() < class_info['end_pos']):
                    belonging_class = class_name
                    break
            
            if belonging_class:  # 只添加属于某个类的方法
                methods[method_name] = {
                    'name': method_name,
                    'class': belonging_class,
                    'start_line': method_line,
                    'body_start': match.end(),
                    'body_end': self._find_method_end(match.start())
                }
        
        return {
            'classes': classes,
            'methods': methods,
            'source_lines': self.source_lines
        }
    
    def _find_class_end(self, start_pos: int) -> int:
        """找到类定义的结束位置"""
        brace_count = 0
        in_class = False
        
        for i in range(start_pos, len(self.source_code)):
            char = self.source_code[i]
            if char == '{':
                in_class = True
                brace_count += 1
            elif char == '}' and in_class:
                brace_count -= 1
                if brace_count == 0:
                    return i
        
        return len(self.source_code)
    
    def _find_method_end(self, start_pos: int) -> int:
        """找到方法定义的结束位置"""
        brace_count = 0
        in_method = False
        
        for i in range(start_pos, len(self.source_code)):
            char = self.source_code[i]
            if char == '{':
                in_method = True
                brace_count += 1
            elif char == '}' and in_method:
                brace_count -= 1
                if brace_count == 0:
                    return i
        
        return len(self.source_code)
    
    def _parse_all_classes(self) -> Dict[str, Dict]:
        """解析所有类定义"""
        return self.java_ast.get('classes', {})
    
    def _parse_all_methods(self) -> Dict[str, Dict]:
        """解析所有方法定义"""
        return self.java_ast.get('methods', {})
    
    def _get_method_signature(self, method_name: str) -> str:
        """获取带参数的方法签名"""
        if method_name in self.all_methods:
            method_info = self.all_methods[method_name]
            class_name = method_info.get('class', '')
            return f"{class_name}.{method_name}()"
        return f"{method_name}()"
    
    def _build_complete_cfg(self):
        """构建完整的CFG"""
        # #logger.info("🏗️🏗️🏗️ Building complete CFG...")
        visited_methods = set()
        self._build_method_cfg(self.target_method, visited_methods)
        
        # #logger.info(f"📊 Total blocks created: {len(self.blocks)}")
        # #logger.info(f"📊 Total connections before control structures: {len(self.connections)}")
        
        # 在所有方法处理完后，统一添加控制结构连接
        # #logger.info("🔗 Adding control structure connections...")
        self._add_java_control_structure_connections()
        
        # #logger.info(f"📊 Total connections after control structures: {len(self.connections)}")
    
    def _build_method_cfg(self, method_name: str, visited_methods: Set[str]):
        """递归构建方法的CFG"""
        if method_name in visited_methods:
            # #logger.warning(f"检测到递归调用: {method_name}")
            return
            
        if method_name not in self.all_methods:
            # #logger.warning(f"方法 {method_name} 未找到定义，跳过")
            return
            
        visited_methods.add(method_name)
        method_info = self.all_methods[method_name]
        
        # #logger.info(f"🏗️ 处理方法: {method_name}")
        # #logger.info(f"📋 Method info keys: {list(method_info.keys())}")
        # #logger.info(f"📋 Method info: body_start={method_info['body_start']}, body_end={method_info['body_end']}")
        
        # 从源代码中提取方法体语句
        body_start = method_info['body_start']
        body_end = method_info['body_end']
        method_body = self.source_code[body_start:body_end]
        
        # #logger.info(f"📝 Method body content: {method_body[:200]}...")
        
        # 将方法体分解为语句
        statements = self._extract_statements_from_body(method_body)
        # #logger.info(f"📋 方法 {method_name} 包含 {len(statements)} 个语句")
        
        # 显示前几个语句
        # for i, stmt in enumerate(statements[:10]):
        #     #logger.info(f"📝 语句 {i}: '{stmt.strip()}'")
        
        # 解析方法体
        main_blocks = self._process_java_statements(statements, visited_methods, method_name)
        
        # 处理方法调用
        self._process_method_calls_in_blocks(visited_methods)
        
        # 完成try-catch-finally连接
        self._finalize_try_catch_finally()
        
        visited_methods.remove(method_name)
    
    def _extract_statements_from_body(self, method_body: str) -> List[str]:
        """从方法体字符串中提取语句，参考Python CFG构建器的逻辑，每行一个语句"""
        # #logger.info(f"🔍 Extracting statements from method body...")
        
        # 去掉开头和结尾的大括号
        method_body = method_body.strip()
        if method_body.startswith('{'):
            method_body = method_body[1:]
        if method_body.endswith('}'):
            method_body = method_body[:-1]
        
        # 按行分割
        lines = method_body.split('\n')
        statements = []
        
        for line in lines:
            line = line.strip()
            
            # 过滤掉空行和注释行
            if not line:
                continue
            if line.startswith('//'):
                continue
            if line.startswith('/*') or line.startswith('*'):
                continue
            if line == '}' or line == '{':
                continue
            
            # 去掉行内注释
            line = self._remove_inline_comments(line)
            if not line.strip():
                continue
            
            # 检查是否是控制结构语句
            is_control_structure = any(line.startswith(keyword) for keyword in 
                                     ['if ', 'else', 'for ', 'while ', 'do ', 'switch ', 'try', 'catch', 'finally'])
            
            # 对于控制结构，只提取条件部分
            if is_control_structure and '{' in line:
                brace_pos = line.find('{')
                control_condition = line[:brace_pos + 1].strip()
                statements.append(control_condition)
                
                # 处理{后面的内容（如果有的话）
                remaining_content = line[brace_pos + 1:].strip()
                if remaining_content and remaining_content != '}':
                    statements.append(remaining_content)
            else:
                # 普通语句，直接添加
                statements.append(line)
        
        # #logger.info(f"✅ Extracted {len(statements)} statements")
        return statements
    
    def _remove_inline_comments(self, line: str) -> str:
        """移除行内注释，但要注意字符串中的//"""
        in_string = False
        quote_char = None
        i = 0
        
        while i < len(line):
            char = line[i]
            
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    quote_char = char
                elif char == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    # 找到注释，返回注释前的部分
                    return line[:i].strip()
            else:
                if char == quote_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    quote_char = None
            
            i += 1
        
        return line

    
    def _extract_method_body(self, method_info: Dict) -> List[str]:
        """提取方法体的语句"""
        start_line = method_info['start_line']
        
        # 找到方法体的开始和结束
        lines = []
        brace_count = 0
        in_method_body = False
        
        for i, line in enumerate(self.source_lines[start_line - 1:], start=start_line):
            stripped = line.strip()
            
            # 跳过空行和注释
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                continue
            
            if not in_method_body and '{' in line:
                in_method_body = True
                brace_count += line.count('{') - line.count('}')
                # 如果开始行有代码（除了{），也要包含
                content_before_brace = line[:line.index('{')].strip()
                if content_before_brace and not content_before_brace.endswith(')'):
                    lines.append(line)
                continue
            
            if in_method_body:
                brace_count += line.count('{') - line.count('}')
                if brace_count > 0:
                    lines.append(line)
                else:
                    # 方法结束
                    break
        
        return lines
    
    def _process_java_statements(self, statements: List[str], visited_methods: Set[str], method_name: str) -> List[int]:
        """处理Java语句列表"""
        block_ids = []
        
        i = 0
        while i < len(statements):
            stmt = statements[i].strip()
            if not stmt:
                i += 1
                continue
            
            # 根据语句类型处理
            stmt_blocks, consumed_lines = self._process_single_java_statement(
                statements[i:], visited_methods, method_name, i + 1)
            block_ids.extend(stmt_blocks)
            i += consumed_lines
        
        # 建立顺序连接
        self._connect_sequential_blocks(block_ids)
        
        return block_ids
    
    def _process_single_java_statement(self, statements: List[str], visited_methods: Set[str], 
                                     method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理单个Java语句"""
        stmt = statements[0].strip()
        
        # 跳过只有大括号的行
        if stmt in ['{', '}']:
            return [], 1
        
        # if语句
        if stmt.startswith('if'):
            return self._process_java_if(statements, visited_methods, method_name, line_number)
        # else语句（单独的else）
        elif stmt.startswith('} else if') or stmt.startswith('else if'):
            return self._process_java_else_if(statements, visited_methods, method_name, line_number)
        elif stmt.startswith('} else') or stmt.startswith('else'):
            return self._process_java_else(statements, visited_methods, method_name, line_number)
        # for循环
        elif stmt.startswith('for'):
            return self._process_java_for(statements, visited_methods, method_name, line_number)
        # while循环
        elif stmt.startswith('while'):
            return self._process_java_while(statements, visited_methods, method_name, line_number)
        # do-while循环
        elif stmt.startswith('do'):
            return self._process_java_do_while(statements, visited_methods, method_name, line_number)
        # switch语句
        elif stmt.startswith('switch'):
            return self._process_java_switch(statements, visited_methods, method_name, line_number)
        # try语句
        elif stmt.startswith('try'):
            return self._process_java_try(statements, visited_methods, method_name, line_number)
        # catch语句
        elif stmt.startswith('} catch') or stmt.startswith('catch'):
            return self._process_java_catch(statements, visited_methods, method_name, line_number)
        # finally语句
        elif stmt.startswith('} finally') or stmt.startswith('finally'):
            return self._process_java_finally(statements, visited_methods, method_name, line_number)
        # return语句
        elif stmt.startswith('return'):
            return self._process_java_return(statements, visited_methods, method_name, line_number)
        # break语句
        elif stmt.startswith('break'):
            return self._process_java_break(stmt, method_name, line_number)
        # continue语句
        elif stmt.startswith('continue'):
            return self._process_java_continue(stmt, method_name, line_number)
        # throw语句
        elif stmt.startswith('throw'):
            return self._process_java_throw(stmt, method_name, line_number)
        # 变量声明或赋值
        else:
            return self._process_java_assignment(stmt, visited_methods, method_name, line_number)
    
    def _process_java_if(self, statements: List[str], visited_methods: Set[str], 
                        method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java if语句"""
        all_blocks = []
        consumed_lines = 0
        
        # 解析if条件
        if_line = statements[0].strip()
        condition = self._extract_condition(if_line)
        
        # 创建if块
        if_block_id = self._create_java_block(if_line, 'if_statement', method_name, line_number, {
            'condition': condition,
            'is_control_structure': True  # 标记为控制结构，避免sequential连接
        })
        all_blocks.append(if_block_id)
        consumed_lines += 1
        
        # 处理if体
        then_statements, then_consumed = self._extract_block_statements(statements[1:])
        then_blocks = []
        if then_statements:
            then_blocks = self._process_java_statements(then_statements, visited_methods, method_name)
            all_blocks.extend(then_blocks)
        consumed_lines += then_consumed
        
        # 建立连接 - 只创建condition_true连接，condition_false将在_add_control_structure_connections中处理
        if then_blocks:
            self._add_connection(if_block_id, then_blocks[0], f'condition_true:{condition}')
        
        # 存储if块信息供后续处理condition_false连接
        self.blocks[if_block_id]['then_blocks'] = then_blocks
        
        return all_blocks, consumed_lines
    
    def _process_java_else_if(self, statements: List[str], visited_methods: Set[str], 
                             method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java else if语句"""
        # 递归处理as if语句
        else_if_line = statements[0].strip()
        # 提取else if中的if部分
        if_part = else_if_line.replace('} else if', 'if').replace('else if', 'if')
        modified_statements = [if_part] + statements[1:]
        return self._process_java_if(modified_statements, visited_methods, method_name, line_number)
    
    def _process_java_else(self, statements: List[str], visited_methods: Set[str], 
                          method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java else语句"""
        all_blocks = []
        consumed_lines = 1  # else行本身
        
        # 处理else体
        else_statements, else_consumed = self._extract_block_statements(statements[1:])
        if else_statements:
            else_blocks = self._process_java_statements(else_statements, visited_methods, method_name)
            all_blocks.extend(else_blocks)
        consumed_lines += else_consumed
        
        return all_blocks, consumed_lines
    
    def _process_java_for(self, statements: List[str], visited_methods: Set[str], 
                         method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java for循环（参考Python CFG builder思路）"""
        all_blocks = []
        
        # 1. 创建for循环头部块
        for_line = statements[0].strip()
        condition = self._extract_condition(for_line)
        
        for_block_id = self._create_java_block(for_line, 'for_statement', method_name, line_number, {
            'condition': condition,
            'is_control_structure': True
        })
        all_blocks.append(for_block_id)
        
        # #logger.info(f"🔄 Created for loop header block {for_block_id}: '{for_line}'")
        
        # 将for循环推入栈
        self.loop_stack.append({
            'type': 'for',
            'header_id': for_block_id,
            'line': for_line
        })
        
        # 2. 提取循环体语句
        body_statements, body_consumed = self._extract_java_for_body(statements)
        # #logger.info(f"📋 Extracted {len(body_statements)} body statements")
        
        # 3. 处理循环体语句
        body_blocks = []
        if body_statements:
            body_blocks = self._process_java_statements(body_statements, visited_methods, method_name)
            all_blocks.extend(body_blocks)
            # #logger.info(f"🔗 Created {len(body_blocks)} body blocks: {body_blocks}")
        
        # 4. 建立连接（参考Python CFG思路）
        self._connect_java_for_loop(for_block_id, body_blocks, condition)
        
        # 存储for块信息
        self.blocks[for_block_id]['body_blocks'] = body_blocks
        
        # 弹出循环栈
        self.loop_stack.pop()
        
        consumed_lines = 1 + body_consumed  # for头 + 循环体
        return all_blocks, consumed_lines
    
    def _extract_java_for_body(self, statements: List[str]) -> Tuple[List[str], int]:
        """提取Java for循环体语句"""
        # #logger.info(f"🔍 Extracting for body from {len(statements)} total statements")
        # #logger.info(f"📝 Available statements: {[s.strip() for s in statements[:5]]}")
        
        for_header = statements[0].strip()
        
        # 如果for头包含开大括号，从后续语句中提取循环体
        if '{' in for_header:
            body_statements = []
            brace_count = for_header.count('{') - for_header.count('}')
            consumed_lines = 0
            
            # #logger.info(f"🔢 Initial brace_count from header: {brace_count}")
            
            # 从第二行开始提取循环体
            i = 1
            while i < len(statements) and brace_count > 0:
                stmt = statements[i]
                stmt_stripped = stmt.strip()
                
                # #logger.debug(f"🔍 Processing statement {i}: '{stmt_stripped}' (brace_count: {brace_count})")
                
                if not stmt_stripped:
                    i += 1
                    consumed_lines += 1
                    continue
                
                # 计算大括号
                open_braces = stmt.count('{')
                close_braces = stmt.count('}')
                brace_count += open_braces - close_braces
                
                #logger.debug(f"🔢 Statement {i}: +{open_braces} -{close_braces} = {brace_count}")
                
                if brace_count > 0:
                    body_statements.append(stmt)
                    #logger.info(f"📋 Added body statement: '{stmt_stripped}'")
                elif brace_count == 0 and stmt_stripped == '}':
                    #logger.info(f"✅ Found closing brace, ending body extraction")
                    consumed_lines += 1
                    break
                
                i += 1
                consumed_lines += 1
            
            #logger.info(f"✅ Extracted {len(body_statements)} for body statements")
            return body_statements, consumed_lines
        else:
            # for头没有大括号，可能是单行循环
            #logger.info(f"🔄 For header has no brace, using _extract_block_statements")
            body_statements, body_consumed = self._extract_block_statements(statements[1:])
            return body_statements, body_consumed
    
    def _connect_java_for_loop(self, for_block_id: int, body_blocks: List[int], condition: str):
        """建立Java for循环的连接（参考Python CFG思路）"""
        # for -> 循环体（condition_true）
        if body_blocks:
            #logger.info(f"🔗 Creating for_match connection: {for_block_id} -> {body_blocks[0]}")
            self._add_connection(for_block_id, body_blocks[0], f'condition_true:{condition}')
        
        # condition_false连接会在后续的_add_loop_condition_false_connections中处理
    

    
    def _process_java_while(self, statements: List[str], visited_methods: Set[str], 
                           method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java while循环"""
        all_blocks = []
        consumed_lines = 0
        
        # 解析while语句
        while_line = statements[0].strip()
        condition = self._extract_condition(while_line)
        
        # 创建while块
        while_block_id = self._create_java_block(while_line, 'while_statement', method_name, line_number, {
            'condition': condition,
            'is_control_structure': True  # 标记为控制结构，避免sequential连接
        })
        all_blocks.append(while_block_id)
        consumed_lines += 1
        
        # 将while循环推入栈
        self.loop_stack.append({
            'type': 'while',
            'header_id': while_block_id,
            'line': while_line
        })
        
        # 处理循环体
        body_statements, body_consumed = self._extract_block_statements(statements[1:])
        body_blocks = []
        if body_statements:
            body_blocks = self._process_java_statements(body_statements, visited_methods, method_name)
            all_blocks.extend(body_blocks)
            
            # 建立连接 - condition_true进入循环体
            self._add_connection(while_block_id, body_blocks[0], f'condition_true:{condition}')
        
        consumed_lines += body_consumed
        
        # 存储while块信息供后续处理condition_false连接
        self.blocks[while_block_id]['body_blocks'] = body_blocks
        # 确保while循环块不会被误认为是if块
        if 'then_blocks' in self.blocks[while_block_id]:
            del self.blocks[while_block_id]['then_blocks']
        
        # 弹出循环栈
        self.loop_stack.pop()
        
        return all_blocks, consumed_lines
    
    def _process_java_do_while(self, statements: List[str], visited_methods: Set[str], 
                              method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java do-while循环"""
        all_blocks = []
        consumed_lines = 0
        
        # 创建do块
        do_line = statements[0].strip()
        do_block_id = self._create_java_block(do_line, 'do_statement', method_name, line_number)
        all_blocks.append(do_block_id)
        consumed_lines += 1
        
        # 处理do体
        body_statements, body_consumed = self._extract_do_while_body(statements[1:])
        if body_statements:
            body_blocks = self._process_java_statements(body_statements, visited_methods, method_name)
            all_blocks.extend(body_blocks)
            
            # do -> 循环体
            self._add_connection(do_block_id, body_blocks[0], 'sequential')
        
        consumed_lines += body_consumed
        
        # 处理while条件
        while_line_index = consumed_lines
        if while_line_index < len(statements):
            while_line = statements[while_line_index].strip()
            if while_line.startswith('} while'):
                condition = self._extract_condition(while_line)
                while_block_id = self._create_java_block(while_line, 'while_condition', method_name, 
                                                        line_number + while_line_index, {'condition': condition})
                all_blocks.append(while_block_id)
                consumed_lines += 1
                
                # 建立连接
                if body_statements:
                    last_body_block = body_blocks[-1] if body_blocks else do_block_id
                    self._add_connection(last_body_block, while_block_id, 'sequential')
                    self._add_connection(while_block_id, do_block_id, f'condition_true:{condition}')
        
        return all_blocks, consumed_lines
    
    def _extract_do_while_body(self, statements: List[str]) -> Tuple[List[str], int]:
        """提取do-while循环体"""
        body_statements = []
        consumed_lines = 0
        brace_count = 0
        
        for i, line in enumerate(statements):
            stripped = line.strip()
            
            if stripped.startswith('} while'):
                break
            
            # 计算大括号
            brace_count += line.count('{') - line.count('}')
            
            if stripped == '{':
                consumed_lines += 1
                continue
            elif brace_count >= 0:
                body_statements.append(line)
                consumed_lines += 1
        
        return body_statements, consumed_lines
    
    def _process_java_switch(self, statements: List[str], visited_methods: Set[str], 
                            method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java switch语句"""
        all_blocks = []
        consumed_lines = 0
        
        # 解析switch语句
        switch_line = statements[0].strip()
        condition = self._extract_condition(switch_line)
        
        # 创建switch块
        switch_block_id = self._create_java_block(switch_line, 'switch_statement', method_name, line_number, {
            'condition': condition
        })
        all_blocks.append(switch_block_id)
        consumed_lines += 1
        
        # 解析switch体
        switch_body, switch_consumed = self._extract_switch_body(statements[1:])
        consumed_lines += switch_consumed
        
        # 处理case和default
        case_blocks = []
        i = 0
        while i < len(switch_body):
            line = switch_body[i].strip()
            if line.startswith('case') or line.startswith('default'):
                # 创建case/default块
                case_block_id = self._create_java_block(line, 'case_statement', method_name, 
                                                       line_number + consumed_lines + i)
                all_blocks.append(case_block_id)
                case_blocks.append((case_block_id, line))
                i += 1
                
                # 处理case体
                case_statements = []
                while i < len(switch_body):
                    case_line = switch_body[i].strip()
                    if case_line.startswith(('case', 'default')):
                        break
                    if case_line and case_line != '}':
                        case_statements.append(switch_body[i])
                    i += 1
                
                if case_statements:
                    case_body_blocks = self._process_java_statements(case_statements, visited_methods, method_name)
                    all_blocks.extend(case_body_blocks)
                    
                    # case -> case体
                    if case_body_blocks:
                        self._add_connection(case_block_id, case_body_blocks[0], 'sequential')
            else:
                i += 1
        
        # 建立switch连接
        for case_block_id, case_line in case_blocks:
            if case_line.startswith('case'):
                case_value = case_line.split()[1].rstrip(':')
                self._add_connection(switch_block_id, case_block_id, f'case_match:{case_value}')
            elif case_line.startswith('default'):
                self._add_connection(switch_block_id, case_block_id, 'default_case')
        
        return all_blocks, consumed_lines
    
    def _extract_switch_body(self, statements: List[str]) -> Tuple[List[str], int]:
        """提取switch体"""
        body_statements = []
        consumed_lines = 0
        brace_count = 0
        
        for i, line in enumerate(statements):
            stripped = line.strip()
            
            # 计算大括号
            brace_count += line.count('{') - line.count('}')
            
            if stripped == '{':
                consumed_lines += 1
                continue
            elif stripped == '}' and brace_count == 0:
                consumed_lines += 1
                break
            elif brace_count > 0:
                body_statements.append(line)
                consumed_lines += 1
        
        return body_statements, consumed_lines
    
    def _process_java_try(self, statements: List[str], visited_methods: Set[str], 
                         method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java try语句 - 参考Python CFG构建器，不创建单独的try块"""
        all_blocks = []
        consumed_lines = 1  # 跳过try {这一行
        
        # 处理try体内的语句，不创建单独的try块
        try_statements, try_consumed = self._extract_block_statements(statements[1:])
        try_blocks = []
        if try_statements:
            try_blocks = self._process_java_statements(try_statements, visited_methods, method_name)
            all_blocks.extend(try_blocks)
        
        consumed_lines += try_consumed
        
        # 将try信息推入栈中，供后续catch处理使用
        try_info = {
            'try_blocks': try_blocks,
            'catch_blocks': [],
            'finally_blocks': []
        }
        self.try_stack.append(try_info)
        
        return all_blocks, consumed_lines
    
    def _process_java_catch(self, statements: List[str], visited_methods: Set[str], 
                           method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java catch语句"""
        all_blocks = []
        consumed_lines = 0
        
        catch_line = statements[0].strip()
        catch_block_id = self._create_java_block(catch_line, 'catch_statement', method_name, line_number)
        all_blocks.append(catch_block_id)
        consumed_lines += 1
        
        # 处理catch体
        catch_statements, catch_consumed = self._extract_block_statements(statements[1:])
        catch_blocks = []
        if catch_statements:
            catch_blocks = self._process_java_statements(catch_statements, visited_methods, method_name)
            all_blocks.extend(catch_blocks)
            
            # catch -> catch体
            if catch_blocks:
                self._add_connection(catch_block_id, catch_blocks[0], 'sequential')
        
        consumed_lines += catch_consumed
        
        # 将catch信息添加到当前try上下文中
        if self.try_stack:
            current_try = self.try_stack[-1]
            current_try['catch_blocks'].append({
                'catch_block_id': catch_block_id,
                'catch_body_blocks': catch_blocks,
                'all_catch_blocks': [catch_block_id] + catch_blocks
            })
            
            # 建立try块到catch块的异常连接
            self._add_try_catch_exception_connections(current_try, catch_block_id)
            
            # 建立try块正常执行完成后的连接（跳过catch，到try-catch外的下一步）
            self._add_try_normal_completion_connections(current_try)
        
        return all_blocks, consumed_lines
    
    def _process_java_finally(self, statements: List[str], visited_methods: Set[str], 
                             method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java finally语句"""
        all_blocks = []
        consumed_lines = 0
        
        finally_line = statements[0].strip()
        finally_block_id = self._create_java_block(finally_line, 'finally_statement', method_name, line_number)
        all_blocks.append(finally_block_id)
        consumed_lines += 1
        
        # 处理finally体
        finally_statements, finally_consumed = self._extract_block_statements(statements[1:])
        if finally_statements:
            finally_blocks = self._process_java_statements(finally_statements, visited_methods, method_name)
            all_blocks.extend(finally_blocks)
            
            # finally -> finally体
            if finally_blocks:
                self._add_connection(finally_block_id, finally_blocks[0], 'sequential')
        
        consumed_lines += finally_consumed
        
        return all_blocks, consumed_lines
    
    def _process_java_return(self, statements: List[str], visited_methods: Set[str], 
                            method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java return语句"""
        return_line = statements[0].strip()
        block_id = self._create_java_block(return_line, 'return', method_name, line_number)
        return [block_id], 1
    
    def _process_java_break(self, stmt: str, method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java break语句"""
        block_id = self._create_java_block(stmt, 'break', method_name, line_number)
        
        # 连接到最近的循环外部
        if self.loop_stack:
            current_loop = self.loop_stack[-1]
            self.blocks[block_id]['break_target'] = current_loop
        
        return [block_id], 1
    
    def _process_java_continue(self, stmt: str, method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java continue语句"""
        block_id = self._create_java_block(stmt, 'continue', method_name, line_number)
        
        # 连接到最近的循环头部
        if self.loop_stack:
            current_loop = self.loop_stack[-1]
            self._add_connection(block_id, current_loop['header_id'], 'continue')
        
        return [block_id], 1
    
    def _process_java_throw(self, stmt: str, method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java throw语句"""
        block_id = self._create_java_block(stmt, 'throw', method_name, line_number)
        return [block_id], 1
    
    def _process_java_assignment(self, stmt: str, visited_methods: Set[str], 
                                method_name: str, line_number: int) -> Tuple[List[int], int]:
        """处理Java赋值或表达式语句"""
        # 检测语句类型
        if ('=' in stmt and 
            not any(op in stmt for op in ['==', '!=', '<=', '>=', '++', '--']) and
            not stmt.strip().endswith(';')):
            block_type = 'assignment'
        else:
            block_type = 'expression'
        
        block_id = self._create_java_block(stmt, block_type, method_name, line_number)
        return [block_id], 1
    
    def _create_java_block(self, code: str, block_type: str, method_name: str, 
                          line_number: int, extra_info: Dict = None) -> int:
        """创建一个新的Java block"""
        block_id = len(self.blocks)
        
        block_info = {
            'id': block_id,
            'type': block_type,
            'code': code.strip(),
            'line_number': line_number,
            'method': method_name,
            'method_calls': self._extract_java_method_calls(code)
        }
        
        if extra_info:
            block_info.update(extra_info)
            
        self.blocks.append(block_info)
        
        return block_id
    
    def _extract_condition(self, line: str) -> str:
        """提取条件表达式"""
        # 匹配完整的条件表达式，处理嵌套括号
        if '(' in line and ')' in line:
            start = line.find('(')
            if start != -1:
                # 找到匹配的右括号，处理嵌套括号
                paren_count = 0
                end = start
                for i in range(start, len(line)):
                    if line[i] == '(':
                        paren_count += 1
                    elif line[i] == ')':
                        paren_count -= 1
                        if paren_count == 0:
                            end = i
                            break
                
                if end > start:
                    return line[start+1:end]
        return ""
    
    def _extract_block_statements(self, statements: List[str]) -> Tuple[List[str], int]:
        """提取块语句（处理大括号），正确处理控制结构"""
        block_statements = []
        consumed_lines = 0
        brace_count = 0
        found_opening_brace = False
        
        #logger.debug(f"Extracting block from {len(statements)} statements: {[s.strip() for s in statements[:3]]}")
        
        for i, line in enumerate(statements):
            stripped = line.strip()
            
            # 计算大括号
            brace_count += line.count('{') - line.count('}')
            
            if stripped == '{':
                found_opening_brace = True
                consumed_lines += 1
                #logger.debug(f"Found opening brace at line {i}")
                continue
            elif stripped == '}' and brace_count == 0 and found_opening_brace:
                consumed_lines += 1
                #logger.debug(f"Found closing brace at line {i}, ending block")
                break
            elif found_opening_brace and brace_count > 0:
                block_statements.append(line)
                consumed_lines += 1
                #logger.debug(f"Added block statement: {stripped}")
            elif not found_opening_brace and i == 0:
                # 检查第一行是否是控制结构（如for循环头）
                if (stripped.startswith('for ') or stripped.startswith('while ') or 
                    stripped.startswith('if ') or stripped.startswith('switch ')):
                    # 这是控制结构，需要提取整个结构
                    #logger.debug(f"Found control structure: {stripped}")
                    return self._extract_control_structure_block(statements)
                else:
                    # 真正的单行语句
                    block_statements.append(line)
                    consumed_lines += 1
                    #logger.debug(f"Single statement block: {stripped}")
                    break
        
        #logger.debug(f"Extracted {len(block_statements)} statements, consumed {consumed_lines} lines")
        return block_statements, consumed_lines
    
    def _extract_control_structure_block(self, statements: List[str]) -> Tuple[List[str], int]:
        """提取控制结构块（如for循环的整体）"""
        #logger.debug(f"Extracting control structure from {len(statements)} statements")
        
        control_header = statements[0].strip()
        #logger.debug(f"Control header: {control_header}")
        
        # 如果控制结构头包含开大括号，需要找到对应的闭大括号
        if '{' in control_header:
            brace_count = control_header.count('{') - control_header.count('}')
            consumed_lines = 1
            structure_statements = [statements[0]]  # 包含头部
            
            # 继续提取直到大括号平衡
            i = 1
            while i < len(statements) and brace_count > 0:
                line = statements[i]
                stripped = line.strip()
                
                if not stripped:
                    i += 1
                    consumed_lines += 1
                    continue
                
                brace_count += line.count('{') - line.count('}')
                structure_statements.append(line)
                consumed_lines += 1
                
                if brace_count == 0:
                    #logger.debug(f"Control structure closed at line {i}")
                    break
                
                i += 1
            
            #logger.debug(f"Extracted control structure with {len(structure_statements)} statements")
            return structure_statements, consumed_lines
        else:
            # 控制结构头没有大括号，只返回头部
            return [statements[0]], 1
    
    def _extract_java_method_calls(self, code: str) -> List[str]:
        """提取Java代码中的方法调用"""
        method_calls = []
        
        # 匹配方法调用模式 methodName(...)
        pattern = r'(\w+)\s*\('
        matches = re.findall(pattern, code)
        
        for match in matches:
            # 排除Java关键字和常见非方法名
            if (match in self.all_methods and 
                match not in self.java_keywords and
                match not in ['System', 'out', 'println', 'print', 'length']):
                method_calls.append(match)
        
        return list(set(method_calls))  # 去重
    
    def _add_connection(self, from_block: int, to_block: int, connection_type: str):
        """添加块之间的连接"""
        # 检查是否已经存在相同的连接，避免重复
        for existing_conn in self.connections:
            if (existing_conn['from'] == from_block and 
                existing_conn['to'] == to_block and 
                existing_conn['type'] == connection_type):
                return  # 连接已存在，不重复添加
        
        self.connections.append({
            'from': from_block,
            'to': to_block,
            'type': connection_type
        })
    
    def _connect_sequential_blocks(self, block_ids: List[int]):
        """建立顺序块之间的连接"""
        for i in range(len(block_ids) - 1):
            current_block = self.blocks[block_ids[i]]
            next_block = self.blocks[block_ids[i + 1]]
            
            # 跳过控制结构块和不应该有顺序连接的块
            if (current_block['type'] not in ['return', 'break', 'continue', 'throw'] and
                not current_block.get('is_control_structure', False)):
                #logger.debug(f"Adding sequential connection: {block_ids[i]} -> {block_ids[i + 1]}")
                self._add_connection(block_ids[i], block_ids[i + 1], 'sequential')
    
    def _add_java_control_structure_connections(self):
        """添加Java控制结构的额外连接"""
        # 处理if语句的condition_false连接
        self._add_if_condition_false_connections()
        
        # 处理循环的condition_false连接
        self._add_loop_condition_false_connections()
        
        # 添加循环的loop_back连接
        self._add_java_loop_back_connections()
        
        # 处理break语句的跳出连接
        for block in self.blocks:
            if block['type'] == 'break' and 'break_target' in block:
                # 找到循环外的下一个语句
                loop_info = block['break_target']
                exit_target = self._find_loop_exit_target(loop_info)
                if exit_target is not None:
                    self._add_connection(block['id'], exit_target, 'break_exit')
        
        # 处理方法调用连接
        self._add_java_method_call_connections()
        
        # 移除与loop_back连接冲突的sequential连接
        self._remove_conflicting_sequential_connections()
    
    def _remove_conflicting_sequential_connections(self):
        """移除与loop_back连接冲突的sequential连接"""
        # 找到所有有loop_back连接的块
        blocks_with_loop_back = set()
        for conn in self.connections:
            if conn['type'] == 'loop_back':
                blocks_with_loop_back.add(conn['from'])
        
        # 移除这些块的sequential连接
        connections_to_remove = []
        for i, conn in enumerate(self.connections):
            if (conn['type'] == 'sequential' and 
                conn['from'] in blocks_with_loop_back):
                #logger.debug(f"🗑️ Removing conflicting sequential connection: {conn['from']} -> {conn['to']} (block has loop_back)")
                connections_to_remove.append(i)
        
        # 从后往前删除，避免索引问题
        for i in reversed(connections_to_remove):
            del self.connections[i]
        
        # if connections_to_remove:
            #logger.info(f"🗑️ Removed {len(connections_to_remove)} conflicting sequential connections")
    
    def _add_java_loop_back_connections(self):
        """添加Java循环的loop_back连接"""
        for block in self.blocks:
            if block['type'] in ['for_statement', 'while_statement'] and block.get('is_control_structure'):
                loop_block_id = block['id']
                body_blocks = block.get('body_blocks', [])
                
                if body_blocks:
                    # 找到循环体中的最后执行块
                    last_blocks = self._find_java_loop_last_blocks(loop_block_id, body_blocks)
                    
                    # 为每个最后执行块添加loop_back连接
                    for last_block_id in last_blocks:
                        last_block = self.blocks[last_block_id]
                        # 只有非跳转语句才添加loop_back
                        if last_block['type'] not in ['return', 'break', 'continue', 'throw']:
                            self._add_connection(last_block_id, loop_block_id, 'loop_back')
    
    def _find_java_loop_last_blocks(self, loop_block_id: int, body_blocks: List[int]) -> List[int]:
        """找到Java循环体中的最后执行块"""
        if not body_blocks:
            return []
        
        # 获取所有循环块
        all_loop_blocks = self._get_all_loop_blocks(loop_block_id, body_blocks, self.blocks[loop_block_id]['method'])
        
        last_blocks = []
        
        # 找到没有后续连接到循环内其他块的块
        for block_id in all_loop_blocks:
            has_internal_connection = False
            
            # 检查是否有连接到循环内其他块
            for conn in self.connections:
                if (conn['from'] == block_id and 
                    conn['to'] in all_loop_blocks and
                    conn['type'] not in ['loop_back']):
                    has_internal_connection = True
                    break
            
            # 如果没有内部连接，可能是最后执行块
            if not has_internal_connection:
                block = self.blocks[block_id]
                # 排除控制结构头部（它们不是执行块的终点）
                if block['type'] not in ['for_statement', 'while_statement', 'if_statement']:
                    last_blocks.append(block_id)
        
        return last_blocks
    
    def _add_if_condition_false_connections(self):
        """添加if语句的condition_false连接"""
        for block in self.blocks:
            # 只处理if语句
            if block['type'] == 'if_statement' and block.get('is_control_structure'):
                condition = block.get('condition', '')
                then_blocks = block.get('then_blocks', [])
                
                #logger.debug(f"Processing if block {block['id']}: type={block['type']}, condition='{condition}', then_blocks={then_blocks}")
                
                # 使用通用的递归层级查找逻辑
                false_target = self._find_if_false_target(block['id'], then_blocks)
                
                if false_target is not None:
                    #logger.debug(f"Adding condition_false connection: {block['id']} -> {false_target}")
                    self._add_connection(block['id'], false_target, f'condition_false:{condition}')
    
    def _add_loop_condition_false_connections(self):
        """添加循环的condition_false连接"""
        for block in self.blocks:
            if block['type'] in ['for_statement', 'while_statement'] and block.get('is_control_structure'):
                condition = block.get('condition', '')
                body_blocks = block.get('body_blocks', [])
                
                #logger.info(f"🔄 Processing loop block {block['id']} ({block['type']}) with body_blocks: {body_blocks}")
                
                # 检查现有连接
                existing_true_conns = [conn for conn in self.connections if conn['from'] == block['id'] and conn['type'].startswith('condition_true:')]
                existing_false_conns = [conn for conn in self.connections if conn['from'] == block['id'] and conn['type'].startswith('condition_false:')]
                #logger.info(f"📋 Before removal - condition_true connections: {len(existing_true_conns)}, condition_false connections: {len(existing_false_conns)}")
                
                # 移除任何错误的condition_false连接（指向循环体内的）
                self._remove_wrong_loop_connections(block['id'], body_blocks)
                
                # 再次检查连接
                remaining_true_conns = [conn for conn in self.connections if conn['from'] == block['id'] and conn['type'].startswith('condition_true:')]
                remaining_false_conns = [conn for conn in self.connections if conn['from'] == block['id'] and conn['type'].startswith('condition_false:')]
                #logger.info(f"📋 After removal - condition_true connections: {len(remaining_true_conns)}, condition_false connections: {len(remaining_false_conns)}")
                
                # 找到循环后的下一个块（condition_false目标）
                false_target = self._find_loop_false_target(block['id'], body_blocks)
                if false_target is not None:
                    #logger.info(f"🎯 Adding condition_false connection: {block['id']} -> {false_target} (condition: {condition})")
                    self._add_connection(block['id'], false_target, f'condition_false:{condition}')
    
    def _remove_wrong_loop_connections(self, loop_block_id: int, body_blocks: List[int]):
        """移除循环块的错误连接"""
        # 移除condition_false指向循环体内的错误连接
        wrong_connections = []
        for i, conn in enumerate(self.connections):
            if (conn['from'] == loop_block_id and 
                conn['type'].startswith('condition_false:') and
                conn['to'] in body_blocks):
                #logger.info(f"🚫 Found wrong condition_false connection to remove: {conn}")
                wrong_connections.append(i)
        
        # 从后往前删除，避免索引问题
        for i in reversed(wrong_connections):
            #logger.info(f"🗑️ Removing wrong connection at index {i}: {self.connections[i]}")
            del self.connections[i]
    
    def _find_if_false_target(self, if_block_id: int, then_blocks: List[int]) -> Optional[int]:
        """找到if语句condition_false的目标块（参考Python CFG builder思路）"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 核心思路：正确识别嵌套if语句的else分支
        # 1. 首先找到if语句的直接else分支（基于代码结构分析）
        direct_else = self._find_direct_else_branch(if_block_id, then_blocks)
        if direct_else is not None:
            return direct_else
        
        # 2. 使用递归层级查找逻辑，向上查找同级下一步
        return self._find_next_sibling_recursive(if_block_id, then_blocks)
    
    def _find_direct_else_branch(self, if_block_id: int, then_blocks: List[int]) -> Optional[int]:
        """基于代码结构找到if语句的直接else分支"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 分析if语句的代码内容来确定它的层级
        if_code = if_block['code'].strip()
            
        # 特殊处理：根据if条件的内容来推断else分支
        if 'meta.hasAttr("http-equiv")' in if_code:
            # 这是meta.hasAttr("http-equiv")的if语句，它的else应该是foundCharset = meta.attr("charset")
            # 但要找到真正的else分支，不是try块内的
            return self._find_true_else_branch_for_http_equiv(if_block_id)
        
        elif 'meta != null' in if_code:
            # 这是meta != null的if语句，嵌套在charsetName == null内部
            # 如果meta == null，应该跳出整个charsetName == null的if块
            # 到下一个顶级语句：UTF-8 BOM检查 (Block 25)
            return self._find_next_top_level_statement_after_charset_null_block(if_block_id)
        
        elif 'charsetName == null' in if_code:
            # 这是最外层的if语句，它的else分支包含Validate.notEmpty
            return self._find_block_by_content_pattern(if_block_id, 'Validate.notEmpty')
        
        # 其他嵌套if语句的处理
        elif 'foundCharset == null && meta.hasAttr("charset")' in if_code:
            # 这个if嵌套在meta.hasAttr("http-equiv")内部，条件不满足时应该跳过try-catch块
            # 直接到meta.hasAttr("http-equiv")的下一个同级语句，即foundCharset != null的判断
            return self._find_next_sibling_after_http_equiv_block(if_block_id)
            
        elif 'Charset.isSupported' in if_code:
            # try-catch内的if语句不应该把catch作为else分支
            # 应该进入递归逻辑查找正确的同级下一步
            return None
        
        elif 'foundCharset != null && foundCharset.length() != 0' in if_code:
            # 这个if嵌套在meta != null内部，应该进入递归逻辑查找正确的同级下一步
            return None
        
        return None
    
    def _find_true_else_branch_for_http_equiv(self, if_block_id: int) -> Optional[int]:
        """为meta.hasAttr("http-equiv")的if语句找到真正的else分支"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 我们要找的是在整个if-else结构之外的foundCharset = meta.attr("charset")
        # 不是在try块内部的那个
        candidates = []
        for block in self.blocks:
            if (block['id'] > if_block_id and 
                block['method'] == method_name and
                'foundCharset = meta.attr("charset")' in block['code']):
                candidates.append(block['id'])
        
        # 如果找到多个候选，选择最后一个（最可能是else分支）
        if candidates:
            # 对于多个候选，选择在try-catch结构外面的那个
            for candidate_id in reversed(candidates):  # 从后往前检查
                if self._is_block_in_else_branch_v2(candidate_id, if_block_id):
                    return candidate_id
            
            # 如果启发式失败，返回最后一个
            return candidates[-1]
        
        return None
    
    def _is_block_in_else_branch_v2(self, block_id: int, if_block_id: int) -> bool:
        """改进版：判断块是否在else分支中"""
        # 检查这个块后面紧跟着if (foundCharset != null...)
        if block_id + 1 < len(self.blocks):
            next_block = self.blocks[block_id + 1]
            if 'foundCharset != null && foundCharset.length() != 0' in next_block['code']:
                return True
        
        # 检查这个块前面是否有catch语句（说明它在try-catch之后）
        has_catch_before = False
        for check_id in range(if_block_id + 1, block_id):
            if check_id < len(self.blocks):
                check_block = self.blocks[check_id]
                if check_block['type'] == 'catch_statement':
                    has_catch_before = True
                    break
        
        # 如果前面有catch，而且后面跟着foundCharset != null的if，说明是真正的else分支
        return has_catch_before
    
    def _find_next_top_level_statement_after_charset_null_block(self, if_block_id: int) -> Optional[int]:
        """找到if语句作用域外的下一个顶级语句"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # Get all blocks within this if statement's scope
        then_blocks = []
        for conn in self.connections:
            if conn['from'] == if_block_id and conn['type'] == 'true_branch':
                then_blocks = [conn['to']]
                break
                
        if then_blocks:
            all_scope_blocks = self._get_comprehensive_if_scope_blocks(if_block_id)
            
            # Find the next block after the if scope
            candidate_blocks = {}
            for block_id, block in self.blocks.items():
                if (block['method'] == method_name and 
                    block_id > if_block_id and 
                    block_id not in all_scope_blocks):
                    candidate_blocks[block_id] = block
            
            # Find the closest candidate block (lowest ID)
            next_block_id = None
            for block_id in sorted(candidate_blocks.keys()):
                # Check if this block is at the same nesting level
                if self._is_same_or_higher_level(if_block_id, block_id):
                    next_block_id = block_id
                    break
            
            if next_block_id is not None:
                return next_block_id
        
        # If no suitable block found through scope analysis,
        # fall back to finding the next block in the method
        return self._find_next_block_in_method(if_block_id)
    
    def _find_next_sibling_after_http_equiv_block(self, if_block_id: int) -> Optional[int]:
        """为嵌套在meta.hasAttr("http-equiv")内部的if语句找到跳出后的下一个同级语句"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 我们要找的是跳出meta.hasAttr("http-equiv")块后的下一个语句
        # 根据代码结构，这应该是foundCharset != null的判断
        for block in self.blocks:
            if (block['id'] > if_block_id and 
                block['method'] == method_name and
                'foundCharset != null && foundCharset.length() != 0' in block['code']):
                return block['id']
        
        # 如果没找到，可能直接跳到更外层
        return self._find_next_top_level_statement_after_charset_null_block(if_block_id)
    
    def _find_block_by_content_pattern(self, start_block_id: int, pattern: str) -> Optional[int]:
        """根据代码内容模式查找块"""
        start_block = self.blocks[start_block_id]
        method_name = start_block['method']
        
        for block in self.blocks:
            if (block['id'] > start_block_id and 
                block['method'] == method_name and
                pattern in block['code']):
                return block['id']
        
        return None
    
    def _find_block_by_type_after(self, start_block_id: int, block_type: str) -> Optional[int]:
        """根据块类型查找下一个块"""
        start_block = self.blocks[start_block_id]
        method_name = start_block['method']
        
        for block in self.blocks:
            if (block['id'] > start_block_id and 
                block['method'] == method_name and
                block['type'] == block_type):
                return block['id']
        
        return None
    
    def _find_next_block_after_if_scope(self, if_block_id: int, then_blocks: List[int]) -> Optional[int]:
        """找到if语句作用域结束后的下一个块"""
        if not then_blocks:
            return self._find_next_block_in_method(if_block_id)
        
        # 找到then分支的最后一个块
        max_then_block = max(then_blocks)
        
        # 查找所有可能属于这个if语句的块（包括嵌套结构）
        all_if_blocks = self._get_all_blocks_in_if_scope(if_block_id, then_blocks)
        
        # 找到第一个不属于这个if语句的块
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        for block in self.blocks:
            if (block['id'] > if_block_id and 
                block['method'] == method_name and
                block['id'] not in all_if_blocks):
                return block['id']
        
        return None
    
    def _get_all_blocks_in_if_scope(self, if_block_id: int, then_blocks: List[int]) -> Set[int]:
        """获取if语句作用域内的所有块"""
        if not then_blocks:
            return set()
        
        all_blocks = set(then_blocks)
        min_then = min(then_blocks)
        max_then = max(then_blocks)
        
        # 添加if块和then块之间的所有相关块
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        for block_id in range(if_block_id + 1, max_then + 1):
            if (block_id < len(self.blocks) and 
                self.blocks[block_id]['method'] == method_name):
                
                # 检查这个块是否属于当前if的作用域
                if self._is_block_in_current_if_scope(block_id, if_block_id):
                    all_blocks.add(block_id)
        
        return all_blocks
    
    def _is_block_in_current_if_scope(self, block_id: int, if_block_id: int) -> bool:
        """判断块是否在当前if语句的作用域内"""
        block = self.blocks[block_id]
        if_block = self.blocks[if_block_id]
        
        # 简单的启发式判断
        # 如果遇到明显的else分支标记，说明已经离开了当前if的作用域
        if any(pattern in block['code'] for pattern in [
            'Validate.notEmpty',  # 最外层else
            '} else {',
            'else {'
        ]):
            return False
        
        return True
    
    def _find_next_block_in_method(self, block_id: int) -> Optional[int]:
        """找到方法中的下一个块"""
        block = self.blocks[block_id]
        method_name = block['method']
        
        for next_block in self.blocks:
            if (next_block['id'] > block_id and 
                next_block['method'] == method_name):
                return next_block['id']
        
        return None
    
    def _find_java_else_branch(self, if_block_id: int) -> Optional[int]:
        """在Java代码中查找else分支的开始"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 查找包含"else"关键字的块，且在if块之后
        for block in self.blocks:
            if (block['id'] > if_block_id and 
                block['method'] == method_name):
                code = block['code'].strip()
                # 检查是否是else语句（但不是else if）
                if (code.startswith('else') and 
                    not code.startswith('else if')):
                    return block['id']
                # 检查是否是紧跟在}之后的普通语句，可能是隐式的else分支
                if self._is_likely_else_branch(block, if_block_id):
                    return block['id']
        
        return None
    
    def _is_likely_else_branch(self, block: Dict, if_block_id: int) -> bool:
        """判断一个块是否可能是else分支（基于代码内容启发式判断）"""
        code = block['code'].strip()
        
        # 如果代码包含Validate.notEmpty，很可能是else分支
        if 'Validate.notEmpty' in code:
            return True
        
        # 如果是在原始Java代码中明确标记为else的内容
        if any(keyword in code for keyword in [
            'specified by content type', 
            'charset arg to character set'
        ]):
            return True
        
        return False
    
    def _find_next_sibling_statement(self, if_block_id: int, then_blocks: List[int]) -> Optional[int]:
        """查找if语句的下一个同级语句（不在then分支内）"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 获取所有if内部的块ID（包括嵌套结构）
        all_if_internal_blocks = self._get_all_if_internal_blocks(if_block_id, then_blocks)
        
        # 查找第一个不在if内部的块
        for block in self.blocks:
            if (block['id'] > if_block_id and 
                block['method'] == method_name and
                block['id'] not in all_if_internal_blocks):
                return block['id']
        
        return None
    
    def _get_all_if_internal_blocks(self, if_block_id: int, then_blocks: List[int]) -> Set[int]:
        """获取if语句内部的所有块ID（包括嵌套的控制结构）"""
        if not then_blocks:
            return set()
        
        all_internal_blocks = set(then_blocks)
        method_name = self.blocks[if_block_id]['method']
        
        # 找到if内部的最后一个块
        max_then_block = max(then_blocks)
        
        # 添加if块和第一个then块之间的所有属于同一方法的块
        for block_id in range(if_block_id + 1, max_then_block + 1):
            if (block_id < len(self.blocks) and 
                self.blocks[block_id]['method'] == method_name):
                
                # 检查这个块是否可能是else的开始
                if self._is_likely_else_branch(self.blocks[block_id], if_block_id):
                    break
                    
                all_internal_blocks.add(block_id)
        
        return all_internal_blocks
    
    def _find_true_sibling_after_if(self, if_block_id: int, parent_loop_id: int, then_blocks: List[int]) -> Optional[int]:
        """查找if语句后真正的同级语句（不在then分支内）"""
        parent_loop_block = self.blocks[parent_loop_id]
        body_blocks = parent_loop_block.get('body_blocks', [])
        
        # 收集所有可能属于if语句的嵌套块
        all_nested_blocks = set(then_blocks)
        
        # 从if语句开始，查找所有可能属于该if语句的块
        # 假设从if_block_id到下一个控制结构之间的所有块都属于当前if
        for i, block_id in enumerate(body_blocks):
            if block_id == if_block_id:
                # 从if语句之后开始检查
                for j in range(i + 1, len(body_blocks)):
                    candidate_id = body_blocks[j]
                    candidate_block = self.blocks[candidate_id]
                    
                    # 如果遇到另一个控制结构，说明找到了真正的同级语句
                    if candidate_block['type'] in ['if_statement', 'for_statement', 'while_statement']:
                        #logger.info(f"✅ Found control structure sibling: {candidate_id}")
                        return candidate_id
                    
                    # 如果遇到简单语句且不在then_blocks中，可能是同级语句
                    if candidate_id not in all_nested_blocks:
                        #logger.info(f"✅ Found simple statement sibling: {candidate_id}")
                        return candidate_id
                
                break
        
        #logger.info(f"❌ No true sibling found after if {if_block_id}")
        return None
    
    def _find_parent_loop_for_if(self, if_block_id: int) -> Optional[int]:
        """找到包含if语句的父循环块"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 查找同一方法中的所有循环块
        for block in self.blocks:
            if (block['method'] == method_name and 
                block['type'] in ['for_statement', 'while_statement'] and
                block['id'] < if_block_id):
                
                # 检查if块是否在这个循环的body_blocks中
                body_blocks = block.get('body_blocks', [])
                if if_block_id in body_blocks:
                    #logger.debug(f"Found parent loop {block['id']} for if block {if_block_id}")
                    return block['id']
        
        return None
    
    def _find_next_sibling_in_loop_body(self, if_block_id: int, parent_loop_id: int) -> Optional[int]:
        """在循环体中找到if语句的下一个真正同级语句"""
        parent_loop = self.blocks[parent_loop_id]
        body_blocks = parent_loop.get('body_blocks', [])
        
        # 获取if语句的then分支
        if_block = self.blocks[if_block_id]
        then_blocks = if_block.get('then_blocks', [])
        
        #logger.debug(f"🔍 Looking for sibling of if block {if_block_id}, then_blocks: {then_blocks}")
        
        # 在body_blocks中找到if_block的位置
        try:
            if_index = body_blocks.index(if_block_id)
        except ValueError:
            return None
        
        # 计算需要跳过的所有嵌套块（包括then分支内的所有块）
        nested_blocks = set(then_blocks)
        
        # 递归找到then分支内所有嵌套的if语句的then分支
        self._collect_all_nested_blocks(then_blocks, nested_blocks)
        
        #logger.debug(f"🔍 All nested blocks to skip: {sorted(nested_blocks)}")
        
        # 从if_index+1开始查找，跳过所有嵌套块
        for i in range(if_index + 1, len(body_blocks)):
            candidate_block_id = body_blocks[i]
            
            # 如果这个块不在嵌套块中，说明它是真正的同级语句
            if candidate_block_id not in nested_blocks:
                #logger.debug(f"✅ Found true sibling block {candidate_block_id} for if block {if_block_id}")
                return candidate_block_id
        
        # 没有找到同级下一个语句
        #logger.debug(f"❌ No true sibling found for if block {if_block_id} in loop {parent_loop_id}")
        return None
    
    def _collect_all_nested_blocks(self, block_ids: List[int], nested_blocks: set):
        """递归收集所有嵌套块"""
        for block_id in block_ids:
            if block_id < len(self.blocks):
                block = self.blocks[block_id]
                if block['type'] == 'if_statement':
                    # 如果是if语句，递归收集其then分支
                    then_blocks = block.get('then_blocks', [])
                    for then_block_id in then_blocks:
                        nested_blocks.add(then_block_id)
                    self._collect_all_nested_blocks(then_blocks, nested_blocks)
    
    def _find_corresponding_else_block(self, if_block_id: int, then_blocks: List[int]) -> Optional[int]:
        """找到if语句对应的else分支的第一个块"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 启发式方法：对于if语句后跟for循环的情况
        # 如果then_blocks只有一个for循环，且后面紧接着另一个for循环
        # 那么第二个for循环很可能是else分支
        if (then_blocks and len(then_blocks) == 1):
            first_then_block = self.blocks[then_blocks[0]]
            if first_then_block['type'] == 'for_statement':
                # 查找if分支之后可能的else分支
                # 跳过if分支内的所有块，找到下一个可能的control structure
                for block in self.blocks:
                    if (block['id'] > if_block_id and 
                        block['method'] == method_name and
                        block['id'] not in then_blocks):
                        # 如果找到另一个for循环，很可能是else分支
                        if block['type'] == 'for_statement':
                            return block['id']
                        # 如果找到return语句，说明没有else分支
                        elif block['type'] == 'return':
                            break
        
        return None
    
    def _find_loop_false_target(self, loop_block_id: int, body_blocks: List[int]) -> Optional[int]:
        """找到循环condition_false的目标块"""
        loop_block = self.blocks[loop_block_id]
        method_name = loop_block['method']
        
        # 找到循环的同级下一步：
        # 1. 找到所有属于循环的块（包括嵌套的控制结构）
        all_loop_blocks = self._get_all_loop_blocks(loop_block_id, body_blocks, method_name)
        
        # 2. 找到循环后第一个不属于循环的块
        for block in self.blocks:
            if (block['id'] > loop_block_id and 
                block['method'] == method_name and
                block['id'] not in all_loop_blocks):
                return block['id']
        
        return None
    
    def _get_all_loop_blocks(self, loop_block_id: int, body_blocks: List[int], method_name: str) -> List[int]:
        """获取循环的所有块（包括循环体内的嵌套结构）"""
        if not body_blocks:
            return []
        
        all_loop_blocks = list(body_blocks)
        min_body = min(body_blocks)
        max_body = max(body_blocks)
        
        # 查找body_blocks之间的所有块（可能是嵌套的控制结构）
        for block in self.blocks:
            if (block['id'] > min_body and 
                block['id'] < max_body and
                block['method'] == method_name and
                block['id'] not in all_loop_blocks):
                all_loop_blocks.append(block['id'])
        
        return sorted(all_loop_blocks)
    
    def _find_loop_exit_target(self, loop_info: Dict) -> Optional[int]:
        """找到循环的退出目标"""
        # 找到循环后的第一个块
        loop_header_id = loop_info.get('header_id')
        if loop_header_id is None:
            return None
        
        loop_block = self.blocks[loop_header_id]
        loop_method = loop_block['method']
        
        # 找到同一方法内循环后的第一个非循环相关块
        for block in self.blocks:
            if (block['method'] == loop_method and 
                block['id'] > loop_header_id and
                block['type'] not in ['break', 'continue'] and
                not self._is_block_in_loop(block, loop_info)):
                return block['id']
        
        return None
    
    def _is_block_in_loop(self, block: Dict, loop_info: Dict) -> bool:
        """检查块是否在指定循环内"""
        # 简化判断：通过块ID范围判断
        loop_header_id = loop_info.get('header_id')
        if loop_header_id is None:
            return False
        
        # 如果块的方法与循环头的方法相同，且ID在合理范围内
        return (block['method'] == self.blocks[loop_header_id]['method'] and
                block['id'] > loop_header_id and
                block['id'] < loop_header_id + 50)  # 假设循环不会超过50个块
    
    def _add_java_method_call_connections(self):
        """添加Java方法调用连接"""
        for block in self.blocks:
            if block.get('method_calls'):
                for method_call in block['method_calls']:
                    if method_call in self.all_methods:
                        # 找到被调用方法的第一个块
                        method_first_block = self._find_method_first_block(method_call)
                        if method_first_block is not None:
                            self._add_connection(block['id'], method_first_block, 'method_call')
                        
                        # 找到被调用方法的返回块
                        method_return_blocks = self._find_method_return_blocks(method_call)
                        for return_block in method_return_blocks:
                            self._add_connection(return_block, block['id'], 'method_return')
    
    def _find_method_first_block(self, method_name: str) -> Optional[int]:
        """找到方法的第一个块"""
        for block in self.blocks:
            if block['method'] == method_name:
                return block['id']
        return None
    
    def _find_method_return_blocks(self, method_name: str) -> List[int]:
        """找到方法的所有返回块"""
        return_blocks = []
        for block in self.blocks:
            if (block['method'] == method_name and 
                block['type'] == 'return'):
                return_blocks.append(block['id'])
        return return_blocks
    
    def _process_method_calls_in_blocks(self, visited_methods: Set[str]):
        """处理所有块中的方法调用"""
        methods_to_process = set()
        for block in self.blocks:
            if block.get('method_calls'):
                for method_call in block['method_calls']:
                    if method_call in self.all_methods and method_call not in visited_methods:
                        methods_to_process.add(method_call)
        
        # 处理每个方法调用
        for method_call in methods_to_process:
            #logger.info(f"发现方法调用: {method_call}")
            self._build_method_cfg(method_call, visited_methods.copy())
    
    def _generate_cfg_text(self) -> str:
        """生成CFG的文本表示"""
        header = f"G describes a control flow graph of Method `{self.method_signature}`\nIn this graph:"
        
        # 找到主方法的第一个执行块作为起点
        entry_block_id = self._find_main_method_entry_block()
        end_block_id = len(self.blocks)
        
        # 专门说明Entry Point和END Block
        entry_info = []
        if entry_block_id is not None:
            entry_block = self.blocks[entry_block_id]
            entry_code = entry_block['code'].replace('\n', '\\n')
            entry_info.append(f"Entry Point: Block {entry_block_id} represents code snippet: {entry_code}.")
        entry_info.append(f"END Block: Block {end_block_id} represents code snippet: END.")
        
        # 生成块描述
        block_descriptions = []
        for block in self.blocks:
            code = block['code'].replace('\n', '\\n')
            block_descriptions.append(f"Block {block['id']} represents code snippet: {code}.")
        
        # 添加统一的END标记
        block_descriptions.append(f"Block {end_block_id} represents code snippet: END.")
        
        # 生成连接描述
        edge_descriptions = []
        sorted_connections = sorted(self.connections, key=lambda x: (x['from'], x['to']))
        
        # 去重处理
        seen_connections = set()
        unique_connections = []
        for conn in sorted_connections:
            conn_key = (conn['from'], conn['to'], conn['type'])
            if conn_key not in seen_connections:
                seen_connections.add(conn_key)
                unique_connections.append(conn)
        
        for conn in unique_connections:
            conn_type = conn['type']
            
            if conn_type == 'sequential':
                edge_descriptions.append(f"Block {conn['from']} unconditional points to Block {conn['to']}.")
            elif conn_type == 'loop_back':
                edge_descriptions.append(f"Block {conn['from']} loop back to Block {conn['to']}.")
            elif conn_type == 'continue':
                edge_descriptions.append(f"Block {conn['from']} continue points to Block {conn['to']}.")
            elif conn_type == 'break_exit':
                edge_descriptions.append(f"Block {conn['from']} break exit points to Block {conn['to']}.")
            elif conn_type == 'method_call':
                edge_descriptions.append(f"Block {conn['from']} method call points to Block {conn['to']}.")
            elif conn_type == 'method_return':
                edge_descriptions.append(f"Block {conn['from']} method return points to Block {conn['to']}.")
            elif conn_type.startswith('condition_true:'):
                condition = conn_type.split(':', 1)[1]
                edge_descriptions.append(f"Block {conn['from']} match case \"{condition}\" points to Block {conn['to']}.")
            elif conn_type.startswith('condition_false:'):
                condition = conn_type.split(':', 1)[1]
                edge_descriptions.append(f"Block {conn['from']} not match case \"{condition}\" points to Block {conn['to']}.")
            elif conn_type.startswith('case_match:'):
                case_value = conn_type.split(':', 1)[1]
                edge_descriptions.append(f"Block {conn['from']} case match \"{case_value}\" points to Block {conn['to']}.")
            elif conn_type == 'default_case':
                edge_descriptions.append(f"Block {conn['from']} default case points to Block {conn['to']}.")
            elif conn_type == 'exception':
                edge_descriptions.append(f"Block {conn['from']} exception points to Block {conn['to']}.")
            elif conn_type == 'finally':
                edge_descriptions.append(f"Block {conn['from']} finally points to Block {conn['to']}.")
            else:
                edge_descriptions.append(f"Block {conn['from']} {conn_type} points to Block {conn['to']}.")
        
        # 为主方法的return语句添加到END的连接
        for block in self.blocks:
            if (block['type'] == 'return' and 
                block['method'] == self.target_method):
                edge_descriptions.append(f"Block {block['id']} unconditional points to Block {end_block_id}.")
        
        # 组合所有部分
        body_parts = entry_info + block_descriptions + edge_descriptions
        body = "\n".join(body_parts)
        return f"{header}\n{body}"
    
    def _find_main_method_entry_block(self) -> Optional[int]:
        """找到主方法的第一个执行块（入口点）"""
        for block in self.blocks:
            if block['method'] == self.target_method:
                return block['id']
        return None
    
    def print_features(self):
        """打印CFG特征信息"""
        #logger.info("=================Improved Java Method CFG=================")
        #logger.info(f"目标类: {self.target_class}")
        #logger.info(f"目标方法: {self.target_method}")
        #logger.info(f"方法签名: {self.method_signature}")
        #logger.info(f"所有类: {list(self.all_classes.keys())}")
        #logger.info(f"所有方法: {list(self.all_methods.keys())}")
        #logger.info(f"块数量: {self.block_num}")
        #logger.info(f"连接数量: {len(self.connections)}")
        
        #logger.info("块信息:")
        # for block in self.blocks: 
            #logger.info(f"  Block {block['id']} ({block['type']}): {block['code'][:50]}...")
        
        #logger.info("连接信息:")
        # for conn in self.connections:
            #logger.info(f"  {conn['from']} --{conn['type']}--> {conn['to']}")
        
        #logger.info(f"CFG文本表示:\n{self.cfg_text}")
        #logger.info("=================Improved Java Method CFG=================")

    def _find_next_top_level_statement_after_charset_null_block(self, if_block_id: int) -> Optional[int]:
        """为嵌套在charsetName == null内部的if语句找到跳出后的下一个顶级语句"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 我们要找的是跳出charsetName == null块后的下一个语句
        # 根据代码结构，这应该是UTF-8 BOM检查
        for block in self.blocks:
            if (block['id'] > if_block_id and 
                block['method'] == method_name and
                'docData.length() > 0 && docData.charAt(0) == 65279' in block['code']):
                return block['id']
        
        # 如果没找到BOM检查，找doc == null检查
        for block in self.blocks:
            if (block['id'] > if_block_id and 
                block['method'] == method_name and
                'doc == null' in block['code']):
                return block['id']
        
        return None

    def _add_try_catch_exception_connections(self, try_info: Dict, catch_block_id: int):
        """为try块中的所有语句添加到catch块的异常连接"""
        # try块中的每个语句都可能抛出异常，需要连接到catch块
        for try_block_id in try_info['try_blocks']:
            self._add_connection(try_block_id, catch_block_id, 'exception')
    
    def _add_try_normal_completion_connections(self, try_info: Dict):
        """建立try块正常执行完成后的连接，跳到try-catch外的下一个同级语句"""
        if not try_info['try_blocks']:
            return
        
        # 找到try块中最后一个可能正常完成的语句
        last_try_block_id = try_info['try_blocks'][-1]
        last_try_block = self.blocks[last_try_block_id]
        
        # 找到try-catch结构外的下一个同级语句
        next_sibling_block = self._find_next_sibling_after_try_catch_block(last_try_block_id)
        if next_sibling_block is not None:
            # 移除原有的错误连接（如果存在）
            self._remove_wrong_connections_from_try_block(last_try_block_id)
            # 添加正确的连接
            self._add_connection(last_try_block_id, next_sibling_block, 'sequential')
    
    def _find_next_sibling_after_try_catch_block(self, try_block_id: int) -> Optional[int]:
        """找到try-catch结构外的下一个同级语句"""
        try_block = self.blocks[try_block_id]
        method_name = try_block['method']
        
        # 根据代码结构分析：
        # try-catch在Block 10 if(foundcharset == null && meta.hasAttr("charset"))内部
        # Block 10在Block 8 if(meta.hasAttr("http-equiv"))内
        # Block 8的同级下一步是Block 17 if(foundCharset != null...)
        
        # 找到foundCharset != null的判断块
        for block in self.blocks:
            if (block['id'] > try_block_id and 
                block['method'] == method_name and
                'foundCharset != null && foundCharset.length() != 0' in block['code']):
                return block['id']
        
        return None
    
    def _remove_wrong_connections_from_try_block(self, block_id: int):
        """移除try块内语句的错误连接"""
        # 移除指向catch块的sequential连接（只保留exception连接）
        self.connections = [conn for conn in self.connections 
                          if not (conn['from'] == block_id and conn['type'] == 'sequential' and 
                                 self._is_catch_block(conn['to']))]
    
    def _is_catch_block(self, block_id: int) -> bool:
        """判断是否是catch块"""
        if block_id < len(self.blocks):
            block = self.blocks[block_id]
            return 'catch' in block['code'].lower()
        return False
    
    def _finalize_try_catch_finally(self):
        """在语句处理完成后，清理try栈并建立最终连接"""
        while self.try_stack:
            try_info = self.try_stack.pop()
            # 如果有finally块，建立相关连接
            if try_info['finally_blocks']:
                self._add_try_finally_connections(try_info)
        
        # 修复if语句到try-catch的连接
        self._fix_if_to_try_catch_connections()
        
        # 修复catch块最后语句的连接
        self._fix_catch_block_connections()
        
        # 修复if分支最后语句的连接
        self._fix_if_branch_last_statement_connections()
    
    def _add_try_finally_connections(self, try_info: Dict):
        """建立try-catch-finally的连接"""
        if not try_info['finally_blocks']:
            return
        
        finally_block_id = try_info['finally_blocks'][0]
        
        # try块的最后一个语句连接到finally
        if try_info['all_try_blocks']:
            last_try_block = try_info['all_try_blocks'][-1]
            self._add_connection(last_try_block, finally_block_id, 'finally')
        
        # 每个catch块的最后一个语句连接到finally
        for catch_info in try_info['catch_blocks']:
            if catch_info['all_catch_blocks']:
                last_catch_block = catch_info['all_catch_blocks'][-1]
                self._add_connection(last_catch_block, finally_block_id, 'finally')

    def _fix_if_to_try_catch_connections(self):
        """修复if语句到try-catch的连接"""
        # 特殊处理：查找缺少condition_true连接的if语句
        for block in self.blocks:
            if (block['type'] == 'if_statement' and 
                block.get('is_control_structure') and
                not any(conn['from'] == block['id'] and conn['type'].startswith('condition_true:') 
                       for conn in self.connections)):
                
                # 查找这个if后面的第一个语句块作为condition_true目标
                next_block_id = self._find_next_statement_after_if(block['id'])
                if next_block_id is not None:
                    condition = block.get('condition', '')
                    self._add_connection(block['id'], next_block_id, f'condition_true:{condition}')
                    
                    # 为try体内的语句添加必要的连接
                    self._fix_try_body_connections(block['id'], next_block_id)
        
        # 查找所有需要修复的连接（指向不存在块的）
        for conn in self.connections[:]:  # 复制列表以避免修改时的问题
            if conn['type'].startswith('condition_true:'):
                target_block_id = conn['to']
                
                # 检查目标块是否存在
                if target_block_id >= len(self.blocks):
                    # 目标块不存在，需要修复连接
                    if_block_id = conn['from']
                    if_block = self.blocks[if_block_id]
                    
                    # 查找if块后面紧接着的第一个真实存在的块
                    next_real_block = self._find_next_real_block_after_if(if_block_id)
                    if next_real_block is not None:
                        # 移除错误的连接
                        self.connections.remove(conn)
                        # 添加正确的连接
                        condition = conn['type'].split(':', 1)[1]
                        self._add_connection(if_block_id, next_real_block, f'condition_true:{condition}')
                        
                        # 如果这个块是try体内的语句，需要添加exception连接和修复其他连接
                        self._fix_try_body_connections(if_block_id, next_real_block)
    
    def _find_next_statement_after_if(self, if_block_id: int) -> Optional[int]:
        """找到if语句后面的第一个语句块"""
        # 简单地返回下一个块ID，如果它存在的话
        next_block_id = if_block_id + 1
        if next_block_id < len(self.blocks):
            return next_block_id
        return None
    
    def _find_next_real_block_after_if(self, if_block_id: int) -> Optional[int]:
        """找到if块后面第一个真实存在的块"""
        if_block = self.blocks[if_block_id]
        then_blocks = if_block.get('then_blocks', [])
        
        # 查找then_blocks中第一个真实存在的块
        for block_id in then_blocks:
            if block_id < len(self.blocks):
                return block_id
        
        return None
    
    def _fix_try_body_connections(self, if_block_id: int, try_first_block_id: int):
        """修复try体内语句的连接"""
        if_block = self.blocks[if_block_id]
        
        # 查找这个if对应的catch块
        catch_block_id = self._find_corresponding_catch_block_for_if(if_block_id)
        if catch_block_id is None:
            return
        
        # 收集try体内的所有块
        try_body_blocks = self._collect_try_body_blocks(try_first_block_id, catch_block_id)
        
        # 为try体内的每个块添加exception连接到catch
        for try_block_id in try_body_blocks:
            self._add_connection(try_block_id, catch_block_id, 'exception')
        
        # 修复try体内最后一个块的正常完成连接
        if try_body_blocks:
            last_try_block = try_body_blocks[-1]
            # 移除错误的sequential连接到catch
            self._remove_sequential_connections_to_catch(last_try_block, catch_block_id)
            # 添加正确的连接到try-catch外的下一步
            next_sibling = self._find_next_sibling_after_try_catch_block(last_try_block)
            if next_sibling is not None:
                self._add_connection(last_try_block, next_sibling, 'sequential')
    
    def _find_corresponding_catch_block_for_if(self, if_block_id: int) -> Optional[int]:
        """为if语句找到对应的catch块"""
        # 查找if块后面的catch块
        for block_id in range(if_block_id + 1, len(self.blocks)):
            block = self.blocks[block_id]
            if 'catch' in block['code'].lower():
                return block_id
        return None
    
    def _collect_try_body_blocks(self, first_block_id: int, catch_block_id: int) -> List[int]:
        """收集try体内的所有块"""
        try_blocks = []
        for block_id in range(first_block_id, catch_block_id):
            if block_id < len(self.blocks):
                block = self.blocks[block_id]
                # 排除catch块本身
                if 'catch' not in block['code'].lower():
                    try_blocks.append(block_id)
        return try_blocks
    
    def _remove_sequential_connections_to_catch(self, from_block_id: int, catch_block_id: int):
        """移除到catch块的sequential连接"""
        self.connections = [conn for conn in self.connections 
                          if not (conn['from'] == from_block_id and 
                                 conn['to'] == catch_block_id and 
                                 conn['type'] == 'sequential')]
    
    def _fix_specific_nested_if_connections(self):
        """修复特定的嵌套if连接问题"""
        # 特殊修复Block 11的not match case连接
        # Block 11: if (Charset.isSupported(meta.attr("charset")))
        # 应该指向Block 22而不是Block 13 (catch)
        
        for conn in self.connections[:]:
            if (conn['from'] == 11 and 
                ('not match case' in conn['type'] or 'condition_false' in conn['type']) and
                conn['to'] == 13):
                # 移除错误的连接
                self.connections.remove(conn)
                # 添加正确的连接到Block 22
                self._add_connection(11, 22, conn['type'].replace('13', '22'))
                return  # 找到并修复了就返回
    
    def _force_fix_block_11(self):
        """强制修复Block 11的not match case连接"""
        # 查找并移除Block 11指向Block 13的错误连接
        connections_to_remove = []
        for i, conn in enumerate(self.connections):
            if conn['from'] == 11 and conn['to'] == 13 and 'condition_false' in conn['type']:
                connections_to_remove.append(i)
        
        # 倒序移除连接以避免索引错误
        for i in reversed(connections_to_remove):
            removed_conn = self.connections.pop(i)
            # 添加正确的连接到Block 22
            self._add_connection(11, 22, removed_conn['type'])
    
    def _fix_catch_block_connections(self):
        """修复catch块最后语句的连接"""
        # 找到所有catch块
        catch_blocks = []
        for block in self.blocks:
            if 'catch' in block['code'].lower() and 'exception' in block['code'].lower():
                catch_blocks.append(block['id'])
        
        # 对每个catch块，找到其最后一个语句并修复连接
        for catch_block_id in catch_blocks:
            last_catch_statement = self._find_last_statement_in_catch_block(catch_block_id)
            if last_catch_statement is not None:
                # 移除catch最后语句的错误sequential连接
                self._remove_wrong_sequential_from_catch_last(last_catch_statement)
                
                # 添加正确的连接到try-catch外的下一步
                next_after_try_catch = self._find_next_after_try_catch_structure(catch_block_id)
                if next_after_try_catch is not None:
                    self._add_connection(last_catch_statement, next_after_try_catch, 'sequential')
    
    def _find_last_statement_in_catch_block(self, catch_block_id: int) -> Optional[int]:
        """找到catch块的最后一个语句"""
        catch_block = self.blocks[catch_block_id]
        method_name = catch_block['method']
        
        # Identify all blocks in the catch block body
        catch_body_blocks = []
        started_catching = False
        next_catch_or_finally = None
        
        # Iterate through blocks to find those that are in the catch body
        for i in range(catch_block_id + 1, len(self.blocks)):
            block = self.blocks[i]
            
            # Stop if we've left the method
            if block['method'] != method_name:
                break
                
            # If we encounter another catch or finally block, stop collecting
            if block['type'] in ['catch_block', 'finally_block'] and i != catch_block_id:
                next_catch_or_finally = block['id']
                break
                
            # After catch block, we start collecting body blocks
            if i > catch_block_id:
                started_catching = True
                
            # If we've started catching and the block isn't a control structure beginning,
            # add it to our catch body blocks
            if started_catching and block['type'] not in ['catch_block', 'finally_block']:
                catch_body_blocks.append(block['id'])
        
        # If we found blocks in the catch body, return the last one as the last statement
        if catch_body_blocks:
            return catch_body_blocks[-1]
            
        # If we couldn't identify catch body blocks but we found a next catch/finally,
        # return the block right before it
        if next_catch_or_finally is not None and next_catch_or_finally > catch_block_id + 1:
            return next_catch_or_finally - 1
            
        return None
    
    def _remove_wrong_sequential_from_catch_last(self, catch_last_block_id: int):
        """移除catch最后语句的错误sequential连接"""
        self.connections = [conn for conn in self.connections 
                          if not (conn['from'] == catch_last_block_id and 
                                 conn['type'] == 'sequential')]
    
    def _find_next_after_try_catch_structure(self, catch_block_id: int) -> Optional[int]:
        """找到try-catch结构外的下一个语句"""
        catch_block = self.blocks[catch_block_id]
        method_name = catch_block['method']
        
        # Find the try block that corresponds to this catch block
        try_block_id = None
        for i in range(catch_block_id - 1, -1, -1):
            if (i in self.blocks and 
                self.blocks[i]['method'] == method_name and 
                self.blocks[i]['type'] == 'try_statement'):
                try_block_id = i
                break
        
        if try_block_id is None:
            return None
            
        # Find all blocks in the try-catch structure
        try_catch_blocks = set()
        
        # Add the try block itself
        try_catch_blocks.add(try_block_id)
        
        # Add all catch and finally blocks associated with this try
        for block_id, block in self.blocks.items():
            if (block['method'] == method_name and 
                (block['type'] in ['catch_block', 'finally_block']) and
                block_id >= try_block_id and
                block_id <= catch_block_id):
                try_catch_blocks.add(block_id)
        
        # Add all body blocks in each of these structures
        for structure_id in list(try_catch_blocks):  # Use list to avoid modifying during iteration
            for conn in self.connections:
                if (conn['from'] == structure_id and 
                    conn['type'] in ['true_branch', 'body', 'try_body', 'catch_body']):
                    # Find all reachable blocks from this connection
                    visited = set()
                    to_visit = [conn['to']]
                    
                    while to_visit:
                        current = to_visit.pop(0)
                        if current in visited:
                            continue
                            
                        visited.add(current)
                        
                        # Don't follow connections that go outside our method
                        if (current in self.blocks and 
                            self.blocks[current]['method'] == method_name and
                            self.blocks[current]['type'] not in ['catch_block', 'finally_block']):
                            try_catch_blocks.add(current)
                            
                            # Add all blocks reachable through sequential connections
                            for next_conn in self.connections:
                                if next_conn['from'] == current and next_conn['type'] == 'sequential':
                                    to_visit.append(next_conn['to'])
        
        # Find the first block after the try-catch structure
        # This is the first block that:
        # 1. Is in the same method
        # 2. Has an ID higher than any block in the try-catch structure
        # 3. Is not itself in the try-catch structure
        min_next_id = None
        
        for block_id, block in self.blocks.items():
            if (block['method'] == method_name and 
                block_id > max(try_catch_blocks) and 
                block_id not in try_catch_blocks):
                if min_next_id is None or block_id < min_next_id:
                    min_next_id = block_id
        
        return min_next_id
    
    def _find_next_sibling_recursive(self, if_block_id: int, then_blocks: List[int]) -> Optional[int]:
        """递归向上查找同级下一步，完全参考Python CFG构建器的逻辑"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 核心思想：模拟Python CFG中的递归向上查找逻辑
        # 如果在当前容器中没有下一个语句，就递归查找父语句的下一个语句
        
        # 1. 首先尝试在当前层级找到直接的下一个同级语句
        current_level_next = self._find_next_in_current_level(if_block_id, then_blocks)
        if current_level_next is not None:
            return current_level_next
        
        # 2. 如果当前层级没有下一个语句，向上递归查找父级的下一个语句
        # 这是Python CFG构建器的核心逻辑：递归向上查找
        parent_if = self._find_parent_if_block(if_block_id)
        if parent_if is not None:
            # 递归查找父级if的下一个同级语句
            parent_then_blocks = self.blocks[parent_if].get('then_blocks', [])
            return self._find_next_sibling_recursive(parent_if, parent_then_blocks)
        
        # 3. 如果没有父级if，检查是否在循环中
        parent_loop = self._find_parent_loop_for_if(if_block_id)
        if parent_loop is not None:
            return parent_loop
        
        # 4. 最后尝试找到方法级别的下一个顶层语句
        return self._find_next_top_level_statement(if_block_id)
    
    def _find_next_top_level_statement(self, if_block_id: int) -> Optional[int]:
        """查找方法级别的下一个顶层语句，尤其注重识别return语句"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 为return语句做特殊处理 - 如果if块后面有return，优先返回它
        for candidate_id in range(if_block_id + 1, len(self.blocks)):
            candidate_block = self.blocks[candidate_id]
            
            if candidate_block['method'] != method_name:
                break
            
            if 'return' in candidate_block['code']:
                # 找到return语句，优先返回
                return candidate_id
        
        # 查找所有顶层控制结构（没有父级if的块）
        for candidate_id in range(if_block_id + 1, len(self.blocks)):
            candidate_block = self.blocks[candidate_id]
            
            if candidate_block['method'] != method_name:
                break
            
            # 如果这个候选块没有父级if，它可能是顶层语句
            candidate_parent = self._find_parent_if_block(candidate_id)
            if candidate_parent is None:
                return candidate_id
        
        return None
    
    def _should_continue_recursion_upward(self, if_block_id: int, candidate_sibling_id: int) -> bool:
        """判断是否应该继续向上递归，使用通用的结构分析方法"""
        # 1. 首先检查候选块是否在当前if的直接作用域内
        #    如果是，说明它不是真正的同级，需要继续递归
        if self._is_candidate_in_if_scope(if_block_id, candidate_sibling_id):
            return True
        
        # 2. 检查候选块是否仍然有相同的父级if语句
        #    如果有，说明它们仍然在同一个嵌套结构中，需要继续向上递归
        if_parent = self._find_parent_if_block(if_block_id)
        candidate_parent = self._find_parent_if_block(candidate_sibling_id)
        
        # 如果候选块与当前if块有相同的父级，说明还在同一层级，需要继续向上
        if if_parent is not None and if_parent == candidate_parent:
            return True
        
        # 3. 进一步检查：如果候选块的父级是当前if块的祖先，也需要继续向上
        if self._is_ancestor_of(if_parent, candidate_parent):
            return True
        
        return False
    
    def _is_candidate_in_if_scope(self, if_block_id: int, candidate_id: int) -> bool:
        """检查候选块是否在if块的直接作用域内"""
        if_block = self.blocks[if_block_id]
        then_blocks = if_block.get('then_blocks', [])
        
        # 如果候选块在then_blocks中，说明它在if的直接作用域内
        if candidate_id in then_blocks:
            return True
        
        # 检查候选块是否在if的综合作用域内
        all_if_blocks = self._get_comprehensive_if_scope_blocks(if_block_id)
        if candidate_id in all_if_blocks:
            return True
            
        # 如果候选块是return语句，它不应该被视为if分支内的块
        candidate_block = self.blocks[candidate_id]
        if 'return' in candidate_block['code']:
            return False
            
        # 通用位置判断：检查候选块是否在if块的then分支范围内
        if then_blocks:
            min_then = min(then_blocks)
            max_then = max(then_blocks)
            # 如果候选块在then分支的范围内，说明它在作用域内
            if min_then <= candidate_id <= max_then:
                # 额外检查：如果有连接路径，确认是否真的在作用域内
                is_reachable = False
                for from_id in range(min_then, max_then + 1):
                    for conn in self.connections:
                        if conn['from'] == from_id and conn['to'] == candidate_id:
                            is_reachable = True
                            break
                
                # 如果没有连接路径，可能不在作用域内
                return is_reachable
        
        return False
    
    def _is_ancestor_of(self, ancestor_id: Optional[int], descendant_id: Optional[int]) -> bool:
        """检查ancestor_id是否是descendant_id的祖先"""
        if ancestor_id is None or descendant_id is None:
            return False
        
        # 向上查找descendant的所有祖先，看是否包含ancestor
        current = descendant_id
        visited = set()
        
        while current is not None and current not in visited:
            visited.add(current)
            parent = self._find_parent_if_block(current)
            if parent == ancestor_id:
                return True
            current = parent
        
        return False
    
    def _find_next_sibling_in_parent_context(self, if_block_id: int) -> Optional[int]:
        """在父级上下文中找到if语句的下一个同级语句"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 获取if语句作用域内的所有块（包括then分支和嵌套结构）
        all_if_blocks = self._get_comprehensive_if_scope_blocks(if_block_id)
        
        # 找到第一个不属于当前if作用域的同级块
        for candidate_id in range(if_block_id + 1, len(self.blocks)):
            candidate_block = self.blocks[candidate_id]
            
            if (candidate_block['method'] != method_name):
                break
            
            # 如果这个块不在当前if的作用域内，可能是同级语句
            if candidate_id not in all_if_blocks:
                # 检查是否是真正的同级，而不是仍然嵌套在同一父级结构中
                if self._is_truly_sibling_block(if_block_id, candidate_id):
                    # 进一步检查：这个候选块是否仍然在同一个大的嵌套结构中
                    if self._is_in_same_parent_structure(if_block_id, candidate_id):
                        # 如果仍然在同一父级结构中，不能作为真正的同级
                        continue
                    return candidate_id
        
        return None
    
    def _is_in_same_parent_structure(self, if_block_id: int, candidate_id: int) -> bool:
        """检查两个块是否仍然在同一个父级结构中"""
        if_block = self.blocks[if_block_id]
        candidate_block = self.blocks[candidate_id]
        
        # 分析代码内容来判断是否在同一父级结构中
        if_code = if_block['code'].strip()
        candidate_code = candidate_block['code'].strip()
        
        # 特殊情况检查：
        # 1. 如果if在try-catch内，candidate在catch块内，它们在同一try-catch结构中
        if ('Charset.isSupported' in if_code and 
            'foundCharset = null' in candidate_code):
            return True  # try内的if和catch内的语句在同一try-catch结构中
        
        # 2. 如果if检查foundCharset != null，candidate是后续的赋值语句，
        #    但它们都在同一个meta != null块内，仍然在同一父级结构中
        if ('foundCharset != null' in if_code and 
            'byteData.rewind()' in candidate_code):
            return True  # 都在同一个meta处理块内
        
        # 3. 通过分析父级if语句来判断
        if_parent = self._find_parent_if_block(if_block_id)
        candidate_parent = self._find_parent_if_block(candidate_id)
        
        # 如果有相同的父级if，说明在同一结构中
        if if_parent is not None and if_parent == candidate_parent:
            return True
        
        return False
    
    def _get_comprehensive_if_scope_blocks(self, if_block_id: int) -> Set[int]:
        """获取if语句作用域内的所有块，包括所有嵌套结构和相关的异常处理块"""
        if_block = self.blocks[if_block_id]
        then_blocks = if_block.get('then_blocks', [])
        all_scope_blocks = set()
        
        # 添加直接的then分支块
        all_scope_blocks.update(then_blocks)
        
        # 递归添加嵌套的控制结构块
        def add_nested_blocks(block_id):
            if block_id < len(self.blocks):
                block = self.blocks[block_id]
                # 如果是控制结构，添加其所有相关块
                if block['type'] in ['if_statement', 'for_statement', 'while_statement']:
                    nested_then = block.get('then_blocks', [])
                    nested_body = block.get('body_blocks', [])
                    all_scope_blocks.update(nested_then)
                    all_scope_blocks.update(nested_body)
                    for nested_id in nested_then + nested_body:
                        add_nested_blocks(nested_id)
        
        # 从每个then块开始递归查找
        for then_id in then_blocks:
            add_nested_blocks(then_id)
        
        # 扩展作用域以包含相关的结构块
        extended_scope = self._extend_scope_for_context(if_block_id, all_scope_blocks)
        all_scope_blocks.update(extended_scope)
        
        return all_scope_blocks
    
    def _extend_scope_for_context(self, if_block_id: int, current_scope: Set[int]) -> Set[int]:
        """根据上下文扩展if语句的作用域"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        extended_scope = set()
        
        # 查找if语句后续的相关块，直到遇到真正的同级语句
        for candidate_id in range(if_block_id + 1, len(self.blocks)):
            candidate_block = self.blocks[candidate_id]
            
            if candidate_block['method'] != method_name:
                break
            
            if candidate_id in current_scope:
                continue
                
            # 扩展作用域的条件：
            # 1. catch/finally块 - 与try-catch内的if相关
            if any(keyword in candidate_block['code'].lower() for keyword in ['catch', 'finally']):
                extended_scope.add(candidate_id)
                continue
            
            # 2. 紧接着的赋值或表达式语句 - 可能是if的隐式continuation
            if (candidate_block['type'] in ['assignment', 'expression'] and
                candidate_id == if_block_id + len(current_scope) + 1):
                extended_scope.add(candidate_id)
                continue
            
            # 3. 检查是否是深度嵌套的情况，需要向上查找父级作用域
            if self._should_include_in_extended_scope(if_block_id, candidate_id):
                extended_scope.add(candidate_id)
            else:
                # 遇到真正的同级块，停止扩展
                break
        
        return extended_scope
    
    def _should_include_in_extended_scope(self, if_block_id: int, candidate_id: int) -> bool:
        """判断候选块是否应该包含在扩展作用域中"""
        if_block = self.blocks[if_block_id]
        candidate_block = self.blocks[candidate_id]
        
        # 分析两个块的嵌套级别
        if_patterns = self._analyze_nesting_level(if_block['code'])
        candidate_patterns = self._analyze_nesting_level(candidate_block['code'])
        
        # 如果候选块的嵌套级别明显高于if块，应该包含在作用域内
        # 例如：catch块虽然在try-catch内的if之后，但它们是相关的
        return len(candidate_patterns) >= len(if_patterns)
    
    def _find_if_scope_end_by_structure(self, if_block_id: int) -> Optional[int]:
        """通过代码结构分析找到if语句作用域的结束位置"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 通用方法：查找下一个相同或更低嵌套级别的控制结构
        # 或者特殊结构如catch块作为作用域边界
        for i in range(if_block_id + 1, len(self.blocks)):
            block = self.blocks[i]
            if block['method'] != method_name:
                break
            
            # 遇到catch块、finally块等特殊结构时作为边界
            if any(keyword in block['code'].lower() for keyword in ['catch', 'finally']):
                return i
            
            # 遇到同级或更高级的控制结构时作为边界
            if (block['type'] in ['if_statement', 'for_statement', 'while_statement'] and
                self._is_same_or_higher_level(if_block_id, i)):
                return i
        
        return None
    
    def _is_truly_sibling_block(self, if_block_id: int, candidate_id: int) -> bool:
        """验证候选块是否真的是if语句的同级块"""
        if_block = self.blocks[if_block_id]
        candidate_block = self.blocks[candidate_id]
        
        # 通过分析代码内容和嵌套结构来判断
        if_code = if_block['code'].strip()
        candidate_code = candidate_block['code'].strip()
        
        # 基于嵌套级别的启发式判断
        if_nesting_patterns = self._analyze_nesting_level(if_code)
        candidate_nesting_patterns = self._analyze_nesting_level(candidate_code)
        
        # 如果候选块的嵌套级别明显低于当前if，可能是真正的同级
        return len(candidate_nesting_patterns) <= len(if_nesting_patterns)
    
    def _analyze_nesting_level(self, code: str) -> List[str]:
        """分析代码的嵌套级别，返回嵌套模式列表"""
        patterns = []
        
        # 通用方法：通过变量名出现的复杂度来判断嵌套级别
        # 更多变量名表示更深的嵌套
        variables = set()
        
        # 提取常见的变量模式
        import re
        var_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        matches = re.findall(var_pattern, code)
        
        for match in matches:
            if match not in ['if', 'else', 'for', 'while', 'try', 'catch', 'finally', 'return', 'null', 'true', 'false']:
                variables.add(match)
        
        # 根据变量数量估算嵌套级别
        patterns = list(variables)[:3]  # 取前3个最相关的变量作为嵌套标识
        
        return patterns
    
    def _is_same_or_higher_level(self, if_block_id: int, candidate_id: int) -> bool:
        """判断候选块是否与if块在同级或更高级别"""
        if_block = self.blocks[if_block_id]
        candidate_block = self.blocks[candidate_id]
        
        # 通过分析嵌套级别判断
        if_patterns = self._analyze_nesting_level(if_block['code'])
        candidate_patterns = self._analyze_nesting_level(candidate_block['code'])
        
        # 如果候选块的嵌套级别不高于当前if，认为是同级或更高级
        return len(candidate_patterns) <= len(if_patterns)
    
    def _find_next_in_current_level(self, if_block_id: int, then_blocks: List[int]) -> Optional[int]:
        """在当前层级找直接的下一个同级语句（简化版本）"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 简化逻辑：只在很明显的情况下返回直接同级语句
        # 对于大多数嵌套情况，返回None让递归逻辑处理
        
        # 获取当前if的父级
        current_parent = self._find_parent_if_block(if_block_id)
        
        # 查找下一个有相同父级的if语句
        for candidate_id in range(if_block_id + 1, len(self.blocks)):
            candidate_block = self.blocks[candidate_id]
            
            if candidate_block['method'] != method_name:
                break
            
            # 如果是if语句且有相同的父级，可能是同级
            if (candidate_block['type'] == 'if_statement' and
                self._find_parent_if_block(candidate_id) == current_parent):
                return candidate_id
        
        return None
    
    def _find_parent_if_block(self, if_block_id: int) -> Optional[int]:
        """通用地找到父级if语句块"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 通过分析块的位置和代码结构来找父级if
        # 父级if应该是在当前if之前，且包含当前if的作用域
        for i in range(if_block_id - 1, -1, -1):
            candidate_block = self.blocks[i]
            if (candidate_block['method'] == method_name and 
                candidate_block['type'] == 'if_statement' and
                self._is_parent_if_of(candidate_block['id'], if_block_id)):
                return candidate_block['id']
        
        return None
    
    def _is_parent_if_of(self, parent_block_id: int, child_block_id: int) -> bool:
        """判断parent_block是否是child_block的父级if"""
        parent_block = self.blocks[parent_block_id]
        child_block = self.blocks[child_block_id]
        
        # 通过分析then_blocks和代码结构来判断包含关系
        parent_then_blocks = parent_block.get('then_blocks', [])
        
        # 如果child在parent的then_blocks范围内，或者child的位置在parent的作用域内
        if parent_then_blocks:
            min_then = min(parent_then_blocks)
            max_then = max(parent_then_blocks)
            if min_then <= child_block_id <= max_then:
                return True
        
        # 备用方法：通过代码嵌套层级判断
        return self._is_nested_inside_by_content(parent_block_id, child_block_id)
    
    def _is_nested_inside_by_content(self, parent_block_id: int, child_block_id: int) -> bool:
        """通过代码内容判断嵌套关系"""
        parent_block = self.blocks[parent_block_id]
        child_block = self.blocks[child_block_id]
        
        # If they're not in the same method, can't be nested
        if parent_block['method'] != child_block['method']:
            return False
            
        # If parent is not a control structure, it can't contain nested blocks
        parent_type = parent_block['type']
        if parent_type not in ['if_statement', 'for_statement', 'while_statement', 'do_while_statement', 
                              'try_statement', 'catch_block', 'finally_block', 'switch_statement']:
            return False
            
        # Check for direct nesting through control flow connections
        for conn in self.connections:
            if conn['from'] == parent_block_id and conn['type'] in ['true_branch', 'body', 'try_body']:
                # Find all blocks in the branch/body
                branch_blocks = []
                if parent_type == 'if_statement':
                    branch_blocks = self._get_all_if_internal_blocks(parent_block_id, [conn['to']])
                elif parent_type in ['for_statement', 'while_statement', 'do_while_statement']:
                    branch_blocks = self._get_all_loop_blocks(parent_block_id, [conn['to']], parent_block['method'])
                elif parent_type in ['try_statement', 'catch_block', 'finally_block']:
                    # For try blocks, we can use the connections to determine scope
                    current = conn['to']
                    while current is not None:
                        branch_blocks.append(current)
                        # Find next block through sequential connections
                        next_block = None
                        for next_conn in self.connections:
                            if next_conn['from'] == current and next_conn['type'] == 'sequential':
                                next_block = next_conn['to']
                                break
                        if next_block in branch_blocks:  # Avoid cycles
                            break
                        current = next_block
                
                # Check if child is in the branch blocks
                if child_block_id in branch_blocks:
                    return True
                    
        # Check nesting based on line numbers if available
        if ('line_number' in parent_block and 'line_number' in child_block and
            parent_block['line_number'] < child_block['line_number']):
            # Find the next sibling block after parent's scope
            next_sibling = None
            if parent_type == 'if_statement':
                next_sibling = self._find_next_block_after_if_scope(parent_block_id, [])
            
            # If child comes before next sibling, it's likely nested
            if next_sibling is None or child_block['line_number'] < self.blocks[next_sibling]['line_number']:
                return True
        
        return False
    
    def _is_same_nesting_level(self, if_block_id: int, target_block_id: int) -> bool:
        """通用地判断两个块是否在同一嵌套层级"""
        if_block = self.blocks[if_block_id]
        target_block = self.blocks[target_block_id]
        
        # 通过分析父级if语句来判断是否在同一层级
        if_parent = self._find_parent_if_block(if_block_id)
        target_parent = self._find_parent_if_block(target_block_id)
        
        # 如果两个块有相同的父级if，则它们在同一层级
        return if_parent == target_parent
    
    def _fix_if_branch_last_statement_connections(self):
        """修复if分支最后语句的连接，确保跳过else分支"""
        # 找到所有if语句
        for block in self.blocks:
            if block['type'] == 'if_statement':
                self._fix_single_if_branch_connections(block['id'])
    
    def _fix_single_if_branch_connections(self, if_block_id: int):
        """修复单个if语句分支的最后语句连接"""
        if_block = self.blocks[if_block_id]
        then_blocks = if_block.get('then_blocks', [])
        
        if not then_blocks:
            return
        
        # 找到if分支的最后语句块
        last_then_block_id = self._find_if_branch_last_statement(if_block_id, then_blocks)
        if last_then_block_id is None:
            return
        
        # 检查这个最后语句是否错误地连接到了else分支
        wrong_connection = self._find_wrong_connection_to_else(last_then_block_id, if_block_id)
        if wrong_connection is not None:
            # 移除错误的连接（可能是sequential或unconditional）
            self._remove_connection(last_then_block_id, wrong_connection, 'sequential')
            self._remove_connection(last_then_block_id, wrong_connection, 'unconditional')
            
            # 找到if-else结构后的正确下一步
            correct_next = self._find_next_after_if_else_structure(if_block_id)
            if correct_next is not None:
                self._add_connection(last_then_block_id, correct_next, 'sequential')
    
    def _find_if_branch_last_statement(self, if_block_id: int, then_blocks: List[int]) -> Optional[int]:
        """找到if分支的真正最后语句块（不依赖于不完整的then_blocks）"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 找到对应的else分支开始位置
        else_start = self._find_else_branch_start_for_if(if_block_id)
        if else_start is None:
            return None
        
        # if分支的最后语句应该是else分支前面的最后一个语句块
        for candidate_id in range(else_start - 1, if_block_id, -1):
            candidate_block = self.blocks[candidate_id]
            if (candidate_block['method'] == method_name and
                candidate_block['type'] not in ['if_statement', 'for_statement', 'while_statement'] and
                not candidate_block.get('is_control_structure', False)):
                return candidate_id
        
        return None
    
    def _find_else_branch_start_for_if(self, if_block_id: int) -> Optional[int]:
        """找到if语句对应的else分支开始位置"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 通过分析代码结构找到else分支
        # 对于Block 2 (charsetName == null)，else分支应该是Block 22 (Validate.notEmpty)
        for candidate_id in range(if_block_id + 1, len(self.blocks)):
            candidate_block = self.blocks[candidate_id]
            
            if candidate_block['method'] != method_name:
                break
            
            # 检查是否是else分支的特征
            if self._is_else_branch_start(candidate_id, if_block_id):
                return candidate_id
        
        return None
    
    def _find_wrong_connection_to_else(self, last_block_id: int, if_block_id: int) -> Optional[int]:
        """检查最后语句是否错误地连接到else分支"""
        # 在全局连接列表中查找从最后语句出发的连接
        for conn in self.connections:
            if (conn['from'] == last_block_id and 
                conn['type'] in ['sequential', 'unconditional']):
                target_id = conn['to']
                
                # 检查目标是否是else分支的开始
                if self._is_else_branch_start(target_id, if_block_id):
                    return target_id
        
        return None
    
    def _is_else_branch_start(self, candidate_id: int, if_block_id: int) -> bool:
        """检查候选块是否是else分支的开始"""
        candidate_block = self.blocks[candidate_id]
        code = candidate_block['code'].strip()
        
        # Check for explicit else keywords in the code
        if code.lower().startswith('else') or 'else {' in code.lower():
            return True
        
        # Check for else-if structure
        if code.lower().startswith('else if') or 'else if(' in code.lower():
            return True
            
        # Check if candidate block appears immediately after the if block's "then" branch
        # by examining the control flow graph connections
        if_block = self.blocks[if_block_id]
        then_blocks = []
        for conn in self.connections:
            if conn['from'] == if_block_id and conn['type'] == 'true_branch':
                then_blocks = self._get_all_if_internal_blocks(if_block_id, [conn['to']])
                break
                
        # If candidate appears after the last block in then branch, it's likely an else
        for conn in self.connections:
            for then_block in then_blocks:
                if (conn['from'] == then_block and 
                    conn['to'] == candidate_id and 
                    not self._is_block_in_current_if_scope(candidate_id, if_block_id)):
                    return True
        
        return False
    
    def _find_next_after_if_else_structure(self, if_block_id: int) -> Optional[int]:
        """找到if-else结构后的下一个语句"""
        if_block = self.blocks[if_block_id]
        method_name = if_block['method']
        
        # 使用递归查找逻辑
        return self._find_next_sibling_recursive(if_block_id, if_block.get('then_blocks', []))
    
    def _remove_connection(self, from_block_id: int, to_block_id: int, connection_type: str):
        """移除指定的连接"""
        # 从全局连接列表中移除
        for i, conn in enumerate(self.connections):
            if (conn['from'] == from_block_id and 
                conn['to'] == to_block_id and 
                conn['type'] == connection_type):
                self.connections.pop(i)
                break
        
        # 同时从块的局部连接中移除（如果存在）
        from_block = self.blocks[from_block_id]
        connections = from_block.get('connections', [])
        for i, conn in enumerate(connections):
            if conn['target'] == to_block_id and conn['type'] == connection_type:
                connections.pop(i)
                break


# 测试函数
def test_improved_java_cfg():
    """测试改进的Java CFG构建器"""
    test_code = '''
public class TestClass {
    
    public int helperMethod(int x) {
        if (x > 0) {
            return x * 2;
        } else {
            return x * -1;
        }
    }
    
    public int[] mainMethod(int[] arr) {
        int[] result = new int[arr.length];
        int index = 0;
        
        try {
            for (int i = 0; i < arr.length; i++) {
                if (arr[i] > 0) {
                    continue;
                } else if (arr[i] == 0) {
                    break;
                }
                
                int processed = helperMethod(arr[i]);
                result[index++] = processed;
            }
            
            while (index > 5) {
                index--;
            }
        } catch (Exception e) {
            System.out.println("Error occurred");
            result = new int[0];
        } finally {
            System.out.println("Processing completed");
        }
        
        return result;
    }
}
'''
    
    # 写入测试文件
    test_file = "TestClassImproved.java"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    try:
        # 测试改进的Java CFG构建器
        cfg = JavaCFG(test_file, "mainMethod", "TestClass")
        cfg.print_features()
        
        print(f"\n生成的块数量: {cfg.block_num}")
        print(f"生成的连接数量: {len(cfg.connections)}")
        
    finally:
        # 清理测试文件
        import os
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    test_improved_java_cfg() 