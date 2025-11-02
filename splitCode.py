# flattener.py
from pathlib import Path
import libcst as cst
from typing import List

class ExpressionFlattener:
    def __init__(self):
        self.temp_index = 1
        self.lines: List[str] = []
        self.indent = "    "

    def new_temp(self) -> str:
        name = f"x{self.temp_index}"
        self.temp_index += 1
        return name

    # ---------- operator mappings ----------
    def get_op(self, op_node) -> str:
        mapping = {
            cst.Add: "+", cst.Subtract: "-", cst.Multiply: "*",
            cst.Divide: "/", cst.Modulo: "%", cst.Power: "**",
            cst.FloorDivide: "//",
        }
        for cls, symbol in mapping.items():
            if isinstance(op_node, cls):
                return symbol
        raise NotImplementedError(f"不支持的二元运算符: {type(op_node)}")

    def get_unary_op(self, node) -> str:
        mapping = {
            cst.Minus: "-",
            cst.Plus: "+",
            cst.Not: "not ",
        }
        for cls, symbol in mapping.items():
            if isinstance(node, cls):
                return symbol
        raise NotImplementedError(f"不支持的单目运算符: {type(node)}")

    def get_comp_op(self, node) -> str:
        mapping = {
            cst.LessThan: "<",
            cst.GreaterThan: ">",
            cst.LessThanEqual: "<=",
            cst.GreaterThanEqual: ">=",
            cst.Equal: "==",
            cst.NotEqual: "!=",
            cst.Is: "is",
            cst.IsNot: "is not",
            cst.In: "in",
            cst.NotIn: "not in",
        }
        for cls, symbol in mapping.items():
            if isinstance(node, cls):
                return symbol
        raise NotImplementedError(f"不支持的比较运算符: {type(node)}")

    def get_bool_op(self, node) -> str:
        if isinstance(node, cst.And):
            return "and"
        if isinstance(node, cst.Or):
            return "or"
        raise NotImplementedError(f"不支持的布尔运算符: {type(node)}")

    # ---------- helpers ----------
    def get_func_name(self, node, indent="    ") -> str:
        if isinstance(node, cst.Name):
            return node.value
        if isinstance(node, cst.Attribute):
            base = self.get_func_name(node.value, indent)
            return f"{base}.{node.attr.value}"        
        if isinstance(node, cst.Subscript):
            return self.flatten_expr(node, indent)
        if isinstance(node, cst.Call):
            return self.flatten_expr(node, indent)
        if isinstance(node, cst.SimpleString):
            return node.value
        raise NotImplementedError(f"不支持的函数名类型: {type(node)}")

    # ---------- expression flattener ----------
    def flatten_expr(self, node, indent="    ") -> str:
        """递归分解表达式"""
        if isinstance(node, cst.BinaryOperation):
            left = self.flatten_expr(node.left, indent)
            right = self.flatten_expr(node.right, indent)
            op = self.get_op(node.operator)
            tmp = self.new_temp()
            self.lines.append(f"{indent}{tmp} = {left} {op} {right}")
            return tmp
        
        if isinstance(node, cst.List):
            # 处理列表字面量
            elements = [self.flatten_expr(e.value, indent) for e in node.elements]
            tmp = self.new_temp()
            self.lines.append(f"{indent}{tmp} = [{', '.join(elements)}]")
            return tmp
        
        if isinstance(node, cst.ListComp):
            result_tmp = self.new_temp()
            self.lines.append(f"{indent}{result_tmp} = []")

            def emit_comp(comp_node, current_indent):
                iter_tmp = self.flatten_expr(comp_node.iter, current_indent)
                target_src = cst.Module([]).code_for_node(comp_node.target).strip()
                self.lines.append(f"{current_indent}for {target_src} in {iter_tmp}:")
                body_indent = current_indent + "    "
                for if_clause in comp_node.ifs:
                    test_tmp = self.flatten_expr(if_clause.test, body_indent)
                    self.lines.append(f"{body_indent}if {test_tmp}:")
                    body_indent += "    "
                inner = getattr(comp_node, "inner_for", None)
                if inner:
                    emit_comp(inner, body_indent)
                else:
                    elt_tmp = self.flatten_expr(node.elt, body_indent)
                    self.lines.append(f"{body_indent}{result_tmp}.append({elt_tmp})")

            emit_comp(node.for_in, indent)
            return result_tmp
        
        if isinstance(node, cst.Subscript):
            value = self.flatten_expr(node.value, indent)
            
            # 辅助函数，用于智能处理切片边界
            def get_slice_part_str(part_node):
                if part_node is None:
                    return ""
                # 如果是简单类型，直接返回值；否则分解表达式
                if isinstance(part_node, (cst.Integer, cst.Name)) or \
                   (isinstance(part_node, cst.UnaryOperation) and isinstance(part_node.expression, cst.Integer)):
                    return cst.Module([]).code_for_node(part_node).strip()
                return self.flatten_expr(part_node, indent)

            indices = []
            for el in node.slice:
                s = el.slice
                if isinstance(s, cst.Index):
                    indices.append(self.flatten_expr(s.value, indent))
                elif isinstance(s, cst.Slice):
                    # 更健壮的切片构建逻辑，能处理所有情况
                    lower = get_slice_part_str(s.lower)
                    upper = get_slice_part_str(s.upper)
                    
                    # 只有当存在 step 或者 upper/lower 都为空时，才需要第三个冒号
                    if s.step:
                        step = get_slice_part_str(s.step)
                        slice_text = f"{lower}:{upper}:{step}"
                    else:
                        slice_text = f"{lower}:{upper}"

                    indices.append(slice_text)
                else:
                    # 对于未知类型，回退到原始方法
                    code = cst.Module([]).code_for_node(s)
                    indices.append(code.strip())
        
            tmp = self.new_temp()
            self.lines.append(f"{indent}{tmp} = {value}[{', '.join(indices)}]")
            return tmp

        if isinstance(node, cst.UnaryOperation):
            operand = self.flatten_expr(node.expression, indent)
            op = self.get_unary_op(node.operator)
            tmp = self.new_temp()
            self.lines.append(f"{indent}{tmp} = {op}{operand}")
            return tmp

        if isinstance(node, cst.Call):
            func_name = self.get_func_name(node.func, indent)
            args = []
            for arg in node.args:
                val = self.flatten_expr(arg.value, indent)
                if arg.keyword:
                    key = cst.Module([]).code_for_node(arg.keyword).strip()
                    args.append(f"{key}={val}")
                else:
                    args.append(val)
            tmp = self.new_temp()
            self.lines.append(f"{indent}{tmp} = {func_name}({', '.join(args)})")
            return tmp

        if isinstance(node, cst.Attribute):
            base = self.flatten_expr(node.value, indent)
            return f"{base}.{node.attr.value}"
        if isinstance(node, cst.Subscript):
            return self.flatten_expr(node, indent)
        
        # Parenthesized expression node class name may differ between libcst versions;
        # try several possible names for compatibility.
        if (hasattr(cst, "ParenthesizedExpression") and isinstance(node, getattr(cst, "ParenthesizedExpression"))) or \
           (hasattr(cst, "Parenthesized") and isinstance(node, getattr(cst, "Parenthesized"))) or \
           (hasattr(cst, "ParenthesizedNode") and isinstance(node, getattr(cst, "ParenthesizedNode"))):
            return self.flatten_expr(node.expression, indent)

        if isinstance(node, cst.Name):
            return node.value
        if isinstance(node, (cst.Integer, cst.Float, cst.SimpleString)):
            return node.value

        if isinstance(node, cst.Comparison):
            left = self.flatten_expr(node.left, indent)
            prev = left
            temps = []
            for comp in node.comparisons:
                right = self.flatten_expr(comp.comparator, indent)
                op = self.get_comp_op(comp.operator)
                t = self.new_temp()
                self.lines.append(f"{indent}{t} = {prev} {op} {right}")
                temps.append(t)
                prev = right
            if len(temps) == 1:
                return temps[0]
            cur = temps[0]
            for other in temps[1:]:
                t2 = self.new_temp()
                self.lines.append(f"{indent}{t2} = {cur} and {other}")
                cur = t2
            return cur

        if isinstance(node, cst.BooleanOperation):
            left = self.flatten_expr(node.left, indent)
            right = self.flatten_expr(node.right, indent)
            op = self.get_bool_op(node.operator)
            t = self.new_temp()
            self.lines.append(f"{indent}{t} = {left} {op} {right}")
            return t

        if isinstance(node, cst.IfExp):
            body = self.flatten_expr(node.body, indent)
            test = self.flatten_expr(node.test, indent)
            orelse = self.flatten_expr(node.orelse, indent)
            t = self.new_temp()
            self.lines.append(f"{indent}{t} = {body} if {test} else {orelse}")
            return t

        if isinstance(node, cst.Tuple):
            elts = [self.flatten_expr(e.value, indent) for e in node.elements]
            tmp = self.new_temp()
            self.lines.append(f"{indent}{tmp} = ({', '.join(elts)})")
            return tmp
        
        if isinstance(node, cst.Lambda):
            lambda_code = cst.Module([]).code_for_node(node).strip()
            tmp = self.new_temp()
            self.lines.append(f"{indent}{tmp} = {lambda_code}")
            return tmp
        
        if isinstance(node, cst.Dict):
            return cst.Module([]).code_for_node(node).strip()
        
        if isinstance(node, cst.Set):
            return cst.Module([]).code_for_node(node).strip()
            

        if isinstance(node, cst.GeneratorExp):
            results_tmp = self.new_temp()
            self.lines.append(f"{indent}{results_tmp} = []")

            def emit_comp(comp_node, current_indent):
                iter_tmp = self.flatten_expr(comp_node.iter, current_indent)
                target_src = cst.Module([]).code_for_node(comp_node.target).strip()
                self.lines.append(f"{current_indent}for {target_src} in {iter_tmp}:")
                body_indent = current_indent + "    "
                for if_clause in comp_node.ifs:
                    cond_tmp = self.flatten_expr(if_clause.test, body_indent)
                    self.lines.append(f"{body_indent}if {cond_tmp}:")
                    body_indent += "    "
                inner = getattr(comp_node, "inner_for", None)
                if inner:
                    emit_comp(inner, body_indent)
                else:
                    elt_tmp = self.flatten_expr(node.elt, body_indent)
                    self.lines.append(f"{body_indent}{results_tmp}.append({elt_tmp})")

            emit_comp(node.for_in, indent)
            iter_var = self.new_temp()
            gen_tmp = self.new_temp()
            self.lines.append(f"{indent}{gen_tmp} = ({iter_var} for {iter_var} in {results_tmp})")
            return gen_tmp

        raise NotImplementedError(f"不支持的表达式类型: {type(node)}")
    
    def flatten_augassign(self, s, indent):
        op_map = {
            "AddAssign": "+",
            "SubtractAssign": "-",
            "MultiplyAssign": "*",
            "DivideAssign": "/",
            "ModuloAssign": "%",
            "PowerAssign": "**",
            "FloorDivideAssign": "//",
        } 
        target = self.flatten_expr(s.target, indent)
        val = self.flatten_expr(s.value, indent)
        op = op_map.get(type(s.operator).__name__, "?")
        self.lines.append(f"{indent}{target} = {target} {op} {val}")

    # ---------- statement flatten ----------
    def flatten_stmt(self, stmt, indent=None):
        if indent is None:
            indent = self.indent

        if isinstance(stmt, cst.SimpleStatementLine):
            for s in stmt.body:
                try:
                    if isinstance(s, cst.Assign):
                        self.flatten_assign(s, indent)
                    elif isinstance(s, cst.AugAssign):
                        self.flatten_augassign(s, indent)
                    elif isinstance(s, cst.Expr):
                        expr_node = s.value
                        # 如果表达式是一个调用，直接分解它，不创建赋值
                        if isinstance(expr_node, cst.Call):
                            func_name = self.get_func_name(expr_node.func, indent)
                            args = []
                            for arg in expr_node.args:
                                val = self.flatten_expr(arg.value, indent)
                                if arg.keyword:
                                    key = cst.Module([]).code_for_node(arg.keyword).strip()
                                    args.append(f"{key}={val}")
                                else:
                                    args.append(val)
                            self.lines.append(f"{indent}{func_name}({', '.join(args)})")
                        else:
                            # 对于其他类型的表达式语句，保留原有逻辑或进行分解
                            try:
                                self.flatten_expr(expr_node, indent)
                            except NotImplementedError:
                                code_text = cst.Module([]).code_for_node(expr_node).strip()
                                self.lines.append(f"{indent}{code_text}")

                    elif isinstance(s, cst.Return):
                        if s.value:
                            val = self.flatten_expr(s.value, indent)
                            self.lines.append(f"{indent}return {val}")
                        else:
                            self.lines.append(f"{indent}return")
                    else:
                        code = cst.Module([]).code_for_node(s).strip()
                        self.lines.append(f"{indent}{code}")
                except Exception as e:
                    code = cst.Module([]).code_for_node(s).strip()
                    self.lines.append(f"{indent}# 出错行保留")
                    self.lines.append(f"{indent}{code}")

        elif isinstance(stmt, cst.FunctionDef):
            self.flatten_function_def(stmt, indent)

        elif isinstance(stmt, cst.Expr):
            expr_node = stmt.value
            try:
                tmp = self.flatten_expr(expr_node, indent)
                # 如果是函数调用或表达式，无需赋值
                code_text = cst.Module([]).code_for_node(expr_node).strip()
                # 如果 flatten_expr 已经生成中间步骤，不重复生成最终语句
                if not isinstance(expr_node, (cst.Call, cst.BooleanOperation, cst.BinaryOperation)):
                    self.lines.append(f"{indent}{code_text}")
                else:
                    # 函数调用时，可以用最后的临时变量来触发副作用
                    self.lines.append(f"{indent}# 调用结果: {tmp}")
            except Exception:
                code_text = cst.Module([]).code_for_node(expr_node).strip()
                self.lines.append(f"{indent}# 出错行保留")
                self.lines.append(f"{indent}{code_text}")

        elif isinstance(stmt, cst.BaseSmallStatement):
            try:
                if isinstance(stmt, cst.Assign):
                    self.flatten_assign(stmt, indent)
                elif isinstance(stmt, cst.AugAssign):
                    target = self.flatten_expr(stmt.target, indent)
                    val = self.flatten_expr(stmt.value, indent)
                    try:
                        op = self.get_op(stmt.operator)
                    except NotImplementedError:
                        op_text = cst.Module([]).code_for_node(stmt.operator).strip()
                        op = op_text[:-1] if op_text.endswith('=') else op_text
                    self.lines.append(f"{indent}{target} = {target} {op} {val}")
                elif isinstance(stmt, cst.Return):
                    val = self.flatten_expr(stmt.value, indent) if stmt.value else ""
                    self.lines.append(f"{indent}return {val}".rstrip())
                else:
                    code = cst.Module([]).code_for_node(stmt)
                    self.lines.append(f"{indent}# 未处理语句: {code.strip()}")
                    self.lines.append(f"{indent}{code.strip()}")
            except Exception:
                code = cst.Module([]).code_for_node(stmt)
                self.lines.append(f"{indent}# 出错行保留")
                self.lines.append(f"{indent}{code.strip()}")


        elif isinstance(stmt, cst.If):
            self.flatten_if_chain(stmt, indent)



        elif isinstance(stmt, cst.While):
            # 修正：将 while 条件的分解移到循环内部，以确保每次迭代都重新求值
            self.lines.append(f"{indent}while True:")
            test = self.flatten_expr(stmt.test, indent + "    ")
            self.lines.append(f"{indent}    if not {test}:")
            self.lines.append(f"{indent}        break")

            # 处理 while body
            body_items = list(getattr(stmt.body, "body", []))
            if not body_items and isinstance(stmt.body, cst.SimpleStatementSuite):
                body_items = list(stmt.body.body)

            for sub in body_items:
                self.flatten_stmt(sub, indent + "    ")

            # 处理 else 子句
            orelse = stmt.orelse
            if orelse:
                self.lines.append(f"{indent}else:")
                orelse_body = list(getattr(orelse.body, "body", []))
                if not orelse_body and isinstance(orelse.body, cst.SimpleStatementSuite):
                    orelse_body = list(orelse.body.body)
                for sub in orelse_body:
                    self.flatten_stmt(sub, indent + "    ")

        elif isinstance(stmt, cst.For):
            target_code = cst.Module([]).code_for_node(stmt.target).strip()
            iter_code = self.flatten_expr(stmt.iter, indent)
            self.lines.append(f"{indent}for {target_code} in {iter_code}:")
            body_nodes = list(getattr(stmt.body, "body", []))
            if not body_nodes and isinstance(stmt.body, cst.SimpleStatementSuite):
                body_nodes = list(stmt.body.body)
            for sub in body_nodes:
                self.flatten_stmt(sub, indent + "    ")
            if stmt.orelse:
                self.lines.append(f"{indent}else:")
                orelse_nodes = list(getattr(stmt.orelse.body, "body", []))
                if not orelse_nodes and isinstance(stmt.orelse.body, cst.SimpleStatementSuite):
                    orelse_nodes = list(stmt.orelse.body.body)
                for sub in orelse_nodes:
                    self.flatten_stmt(sub, indent + "    ")

        elif isinstance(stmt, cst.Try):
            self.flatten_try(stmt, indent)

                    
    def flatten_if_chain(self, stmt, indent="    "):
            test = self.flatten_expr(stmt.test, indent)
            self.lines.append(f"{indent}if {test}:")
            body_items = list(getattr(stmt.body, "body", []))
            if not body_items and isinstance(stmt.body, cst.SimpleStatementSuite):
                body_items = list(stmt.body.body)
            for sub in body_items:
                self.flatten_stmt(sub, indent + "    ")

            orelse = getattr(stmt, "orelse", None)
            if not orelse:
                return

            elif_branch = isinstance(orelse, cst.If) or (
                hasattr(cst, "Elif") and isinstance(orelse, getattr(cst, "Elif"))
            )
            if elif_branch:
                self.lines.append(f"{indent}else:")
                self.flatten_if_chain(orelse, indent + "    ")
                return

            if isinstance(orelse, cst.Else):
                self.lines.append(f"{indent}else:")
                orelse_body = list(getattr(orelse.body, "body", []))
                if not orelse_body and isinstance(orelse.body, cst.SimpleStatementSuite):
                    orelse_body = list(orelse.body.body)
                for sub in orelse_body:
                    self.flatten_stmt(sub, indent + "    ")
                return

            code = cst.Module([]).code_for_node(orelse).strip()
            self.lines.append(f"{indent}# 未处理的 else 分支: {code}")
            self.lines.append(f"{indent}{code}")

    def _flatten_body(self, body, indent):
        if body is None:
            return
        body_nodes = list(getattr(body, "body", []))
        if not body_nodes and isinstance(body, cst.SimpleStatementSuite):
            body_nodes = list(body.body)
        for sub in body_nodes:
            self.flatten_stmt(sub, indent)

    def _build_except_clause(self, handler):
        clause = "except"
        if handler.type:
            type_code = cst.Module([]).code_for_node(handler.type).strip()
            clause += f" {type_code}"
        if handler.name:
            name_code = cst.Module([]).code_for_node(handler.name).strip()
            clause += f" {name_code}"
        return clause

    def flatten_try(self, try_stmt, indent="    "):
        self.lines.append(f"{indent}try:")
        self._flatten_body(try_stmt.body, indent + "    ")

        for handler in try_stmt.handlers:
            clause = self._build_except_clause(handler)
            self.lines.append(f"{indent}{clause}:")
            self._flatten_body(handler.body, indent + "    ")

        if try_stmt.orelse:
            self.lines.append(f"{indent}else:")
            self._flatten_body(try_stmt.orelse.body, indent + "    ")

        if try_stmt.finalbody:
            self.lines.append(f"{indent}finally:")
            self._flatten_body(try_stmt.finalbody.body, indent + "    ")

    def flatten_assign(self, stmt, indent="    "):
        start_len = len(self.lines)
        value = self.flatten_expr(stmt.value, indent)

        single_name_target = (
            len(stmt.targets) == 1 and isinstance(stmt.targets[0].target, cst.Name)
        )
        if (
            single_name_target
            and value.startswith("x")
            and value[1:].isdigit()
            and len(self.lines) > start_len
        ):
            last_line = self.lines[-1]
            expected_prefix = f"{indent}{value} = "
            if last_line.startswith(expected_prefix):
                rhs = last_line[len(expected_prefix):]
                target_name = stmt.targets[0].target.value
                self.lines[-1] = f"{indent}{target_name} = {rhs}"
                return

        for assign_target in stmt.targets:
            target_node = assign_target.target
            if isinstance(target_node, cst.Name):
                target = target_node.value
            elif isinstance(target_node, cst.Attribute):
                base = self.flatten_expr(target_node.value, indent)
                target = f"{base}.{target_node.attr.value}"
            elif isinstance(target_node, cst.Subscript):
                base = self.flatten_expr(target_node.value, indent)
                slice_code = cst.Module([]).code_for_node(target_node.slice[0].slice).strip()
                target = f"{base}[{slice_code}]"
            else:
                target = cst.Module([]).code_for_node(target_node)
            self.lines.append(f"{indent}{target} = {value}")

    def flatten_function_def(self, func_def, indent=""):
        params_code = cst.Module([]).code_for_node(func_def.params).strip()
        if params_code.startswith("(") and params_code.endswith(")"):
            params_code = params_code[1:-1]
        self.lines.append(f"{indent}def {func_def.name.value}({params_code}):")
        body_items = list(getattr(func_def.body, "body", []))
        if not body_items and isinstance(func_def.body, cst.SimpleStatementSuite):
            body_items = list(func_def.body.body)
        if not body_items:
            self.lines.append(f"{indent}    pass")
            return
        for sub in body_items:
            self.flatten_stmt(sub, indent + "    ")

    def flatten_code(self, code: str) -> str:
        module = cst.parse_module(code)
        self.lines = []
        self.temp_index = 1

        for stmt in module.body:
            if isinstance(stmt, cst.FunctionDef):
                self.flatten_function_def(stmt)

            elif (
                isinstance(stmt, cst.If)
                and isinstance(stmt.test, cst.Comparison)
                and isinstance(stmt.test.left, cst.Name)
                and stmt.test.left.value == "__name__"
                and len(stmt.test.comparisons) == 1
                and isinstance(stmt.test.comparisons[0].comparator, cst.SimpleString)
                and "__main__" in stmt.test.comparisons[0].comparator.value
            ):
                code_text = cst.Module([]).code_for_node(stmt).strip()
                self.lines.append(f"# 跳过主入口: {code_text}")
                for s in stmt.body.body:
                    self.flatten_stmt(s, self.indent)

            else:
                # 其他顶层语句（可根据需要分解或跳过）
                code_text = cst.Module([]).code_for_node(stmt).strip()
                self.lines.append(f"{code_text}   # 未分解语句")

        #将selfLines合并为一个字符串返回
        return "\n".join(self.lines)


# ---------------- demo ----------------
if __name__ == "__main__":
    fl = ExpressionFlattener()
    code = Path("buggy_code.py").read_text(encoding='utf-8')

    print("\n原始代码:\n" + code)
    print("\n分解结果:")
    try:
        out = fl.flatten_code(code)
        print(out)    
    except Exception as e:
        print("[Error]", e)
