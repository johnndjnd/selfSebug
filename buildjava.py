# filepath: buildjava.py
import tree_sitter
import tree_sitter_java
from tree_sitter import Parser
# 构造Java语言对象
java_language = tree_sitter.Language(tree_sitter_java.language())

# 构造解析器
parser = Parser(java_language)
# 解析Java代码
file = open("test.java", "r", encoding="utf-8")
code = file.read()
tree = parser.parse(bytes(code, "utf8"))
root_node = tree.root_node
# print(root_node.sexp())

# ---- 2. 工具函数 ----
def get_node_text(code_bytes, node):
    """提取语法树节点对应的源码片段"""
    return code_bytes[node.start_byte:node.end_byte].decode("utf-8")


# ---- 3. 表达式分解器 ----
class JavaExpressionFlattener:
    def __init__(self):
        self.temp_counter = 1
        self.lines = []

    def new_temp(self):
        name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return name

    def flatten_expr(self, code_bytes, node):
        """
        递归分解 binary_expression 节点。
        返回 (变量名, 代码列表)
        """
        if node.type == "binary_expression":
            # 左右子节点
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            operator = get_node_text(code_bytes, node.child_by_field_name("operator"))

            left_var = self.flatten_expr(code_bytes, left)
            right_var = self.flatten_expr(code_bytes, right)

            temp_name = self.new_temp()
            self.lines.append(f"int {temp_name} = {left_var} {operator} {right_var};")
            return temp_name

        elif node.type in ("identifier", "decimal_integer_literal", "parenthesized_expression"):
            return get_node_text(code_bytes, node)

        else:
            return get_node_text(code_bytes, node)

    def flatten_assignment(self, code_bytes, assign_node):
        """
        分解赋值语句 int x = a + b * (c - d);
        """
        declarator = assign_node.children[0]
        for child in assign_node.children:
            if child.type == "variable_declarator":
                declarator = child
                break

        var_name = get_node_text(code_bytes, declarator.child_by_field_name("name"))
        value_node = declarator.child_by_field_name("value")
        value_var = self.flatten_expr(code_bytes, value_node)
        self.lines.append(f"int {var_name} = {value_var};")

    def flatten_assignment(self, code_bytes, assign_node):
        """
        分解赋值语句 int x = a + b * (c - d);
        """
        declarator = None
        cursor = assign_node.walk()  # 获取游标
        if cursor.goto_first_child():  # 移动到第一个子节点
            while True:
                child = cursor.node
                if child.type == "variable_declarator":
                    declarator = child
                    break
                if not cursor.goto_next_sibling():  # 移动到下一个兄弟节点
                    break

        if declarator:
            var_name = get_node_text(code_bytes, declarator.child_by_field_name("name"))
            value_node = declarator.child_by_field_name("value")
            value_var = self.flatten_expr(code_bytes, value_node)
            self.lines.append(f"int {var_name} = {value_var};")

    def flatten(self, code):
        code_bytes = code.encode("utf-8")
        tree = parser.parse(code_bytes)
        root = tree.root_node

        # 找到所有局部变量声明
        for node in root.walk():
            if node.type == "local_variable_declaration":
                self.flatten_assignment(code_bytes, node)

        return "\n".join(self.lines)


# ---- 4. 测试示例 ----
if __name__ == "__main__":
    code = """
    class Test {
        void func() {
            int x = a + b * (c - d);
        }
    }
    """
    flattener = JavaExpressionFlattener()
    result = flattener.flatten(code)
    print(result)