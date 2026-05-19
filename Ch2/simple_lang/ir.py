"""中間碼生成器 (IR Generator) - 生成四元組"""

from typing import List, Optional
from dataclasses import dataclass
from .parser import *


@dataclass
class Quadruple:
    """四元組 (op, arg1, arg2, result)"""
    op: str
    arg1: str = ""
    arg2: str = ""
    result: str = ""

    def __repr__(self):
        if self.arg2:
            return f"({self.op}, {self.arg1}, {self.arg2}, {self.result})"
        return f"({self.op}, {self.arg1}, -, {self.result})"


class IRGenerator:
    """中間碼生成器"""

    def __init__(self):
        self.quadruples: List[Quadruple] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.current_function = ""

    def generate(self, node: ProgramNode) -> List[Quadruple]:
        """生成中間碼"""
        for func in node.functions:
            self.generate_function(func)

        self.add_quadruple("END", "", "", "")
        return self.quadruples

    def new_temp(self) -> str:
        """生成臨時變數"""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def new_label(self) -> str:
        """生成標籤"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def add_quadruple(self, op: str, arg1: str = "", arg2: str = "", result: str = ""):
        """添加四元組"""
        self.quadruples.append(Quadruple(op, arg1, arg2, result))

    def generate_function(self, node: FunctionNode):
        """生成函數中間碼"""
        self.current_function = node.name
        self.add_quadruple("FUNCTION", node.name, "", "")

        # 生成參數
        for param in node.params:
            self.add_quadruple("PARAM", param.name, "", "")

        # 生成函數體
        for stmt in node.body:
            self.generate_statement(stmt)

        self.add_quadruple("ENDFUNCTION", node.name, "", "")

    def generate_statement(self, node: ASTNode):
        """生成語句中間碼"""
        if isinstance(node, VarDeclarationNode):
            self.generate_var_declaration(node)
        elif isinstance(node, AssignmentNode):
            self.generate_assignment(node)
        elif isinstance(node, IfNode):
            self.generate_if(node)
        elif isinstance(node, WhileNode):
            self.generate_while(node)
        elif isinstance(node, ForNode):
            self.generate_for(node)
        elif isinstance(node, ReturnNode):
            self.generate_return(node)
        elif isinstance(node, FunctionCallNode):
            self.generate_function_call(node)

    def generate_var_declaration(self, node: VarDeclarationNode):
        """生成變數宣告"""
        if node.init:
            result = self.generate_expression(node.init)
            self.add_quadruple("=", result, "", node.name)

    def generate_assignment(self, node: AssignmentNode):
        """生成賦值"""
        if isinstance(node.target, IdentifierNode):
            result = self.generate_expression(node.value)
            self.add_quadruple("=", result, "", node.target.name)
        elif isinstance(node.target, ArrayAccessNode):
            index = self.generate_expression(node.target.index)
            value = self.generate_expression(node.value)
            self.add_quadruple("SETARRAY", node.target.name, index, value)

    def generate_if(self, node: IfNode):
        """生成條件語句"""
        cond = self.generate_expression(node.condition)

        else_label = self.new_label()
        end_label = self.new_label()

        self.add_quadruple("IFFALSE", cond, "", else_label)

        for stmt in node.then_branch:
            self.generate_statement(stmt)

        self.add_quadruple("GOTO", "", "", end_label)

        self.add_quadruple("LABEL", else_label, "", "")

        if node.else_branch:
            for stmt in node.else_branch:
                self.generate_statement(stmt)

        self.add_quadruple("LABEL", end_label, "", "")

    def generate_while(self, node: WhileNode):
        """生成 while 迴圈"""
        start_label = self.new_label()
        end_label = self.new_label()

        self.add_quadruple("LABEL", start_label, "", "")

        cond = self.generate_expression(node.condition)
        self.add_quadruple("IFFALSE", cond, "", end_label)

        for stmt in node.body:
            self.generate_statement(stmt)

        self.add_quadruple("GOTO", "", "", start_label)
        self.add_quadruple("LABEL", end_label, "", "")

    def generate_for(self, node: ForNode):
        """生成 for 迴圈"""
        start_label = self.new_label()
        end_label = self.new_label()

        if node.init:
            self.generate_statement(node.init)

        self.add_quadruple("LABEL", start_label, "", "")

        if node.condition:
            cond = self.generate_expression(node.condition)
            self.add_quadruple("IFFALSE", cond, "", end_label)

        for stmt in node.body:
            self.generate_statement(stmt)

        if node.update:
            self.generate_statement(node.update)

        self.add_quadruple("GOTO", "", "", start_label)
        self.add_quadruple("LABEL", end_label, "", "")

    def generate_return(self, node: ReturnNode):
        """生成返回語句"""
        if node.value:
            result = self.generate_expression(node.value)
            self.add_quadruple("RETURN", result, "", "")
        else:
            self.add_quadruple("RETURN", "", "", "")

    def generate_function_call(self, node: FunctionCallNode):
        """生成函數呼叫"""
        # 生成參數
        for arg in node.args:
            result = self.generate_expression(arg)
            self.add_quadruple("PARAM", result, "", "")

        # 函數呼叫
        temp = self.new_temp()
        self.add_quadruple("CALL", node.name, "", temp)

        return temp

    def generate_expression(self, node: ExprNode) -> str:
        """生成表達式中間碼"""
        if isinstance(node, NumberNode):
            return str(node.value)

        if isinstance(node, StringNode):
            return f'"{node.value}"'

        if isinstance(node, BooleanNode):
            return "1" if node.value else "0"

        if isinstance(node, IdentifierNode):
            return node.name

        if isinstance(node, BinaryExprNode):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)
            result = self.new_temp()
            self.add_quadruple(node.operator, left, right, result)
            return result

        if isinstance(node, UnaryExprNode):
            operand = self.generate_expression(node.operand)
            result = self.new_temp()
            self.add_quadruple(node.operator, operand, "", result)
            return result

        if isinstance(node, FunctionCallNode):
            return self.generate_function_call(node)

        if isinstance(node, ArrayAccessNode):
            index = self.generate_expression(node.index)
            result = self.new_temp()
            self.add_quadruple("GETARRAY", node.name, index, result)
            return result

        return ""

    def print_quadruples(self):
        """打印四元組"""
        print("\n=== 四元組 (Quadruples) ===")
        print(f"{'OP':<12} {'ARG1':<15} {'ARG2':<15} {'RESULT':<15}")
        print("-" * 60)
        for q in self.quadruples:
            print(f"{q.op:<12} {q.arg1:<15} {q.arg2:<15} {q.result:<15}")


def main():
    """測試中間碼生成"""
    from lexer import Lexer
    from parser import Parser

    source = """
    function main() : int {
        var x : int = 10
        var y : int = 20
        if (x < y) {
            return x
        }
        return 0
    }
    """

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    ir = IRGenerator()
    quadruples = ir.generate(ast)
    ir.print_quadruples()


if __name__ == "__main__":
    main()