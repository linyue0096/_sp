"""語義分析器 (Semantic Analyzer) - 類型檢查與作用域"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from .parser import *


@dataclass
class Symbol:
    """符號表項"""
    name: str
    type: str
    kind: str  # variable, function, parameter
    line: int = 0


@dataclass
class FunctionSymbol:
    """函數符號"""
    name: str
    params: List[str]
    return_type: str


class SymbolTable:
    """符號表"""

    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]
        self.functions: Dict[str, FunctionSymbol] = {}

    def enter_scope(self):
        """進入新作用域"""
        self.scopes.append({})

    def exit_scope(self):
        """退出作用域"""
        if len(self.scopes) > 1:
            self.scopes.pop()

    def define(self, symbol: Symbol):
        """定義符號"""
        self.scopes[-1][symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """查詢符號"""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def define_function(self, func: FunctionSymbol):
        """定義函數"""
        self.functions[func.name] = func

    def lookup_function(self, name: str) -> Optional[FunctionSymbol]:
        """查詢函數"""
        return self.functions.get(name)


class SemanticAnalyzer:
    """語義分析器"""

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[str] = []
        self.current_function: Optional[str] = None

    def analyze(self, node: ProgramNode):
        """執行語義分析"""
        # 第一次遍歷：收集函數宣告
        for func in node.functions:
            self.collect_function(func)

        # 第二次遍歷：分析函數體
        for func in node.functions:
            self.analyze_function(func)

        return len(self.errors) == 0

    def collect_function(self, node: FunctionNode):
        """收集函數訊息"""
        params = [p.type for p in node.params]
        func_symbol = FunctionSymbol(
            name=node.name,
            params=params,
            return_type=node.return_type
        )
        self.symbol_table.define_function(func_symbol)

    def analyze_function(self, node: FunctionNode):
        """分析函數"""
        self.current_function = node.name
        self.symbol_table.enter_scope()

        # 定義參數
        for param in node.params:
            symbol = Symbol(name=param.name, type=param.type, kind='parameter', line=param.line)
            self.symbol_table.define(symbol)

        # 分析函數體
        for stmt in node.body:
            self.analyze_statement(stmt)

        self.symbol_table.exit_scope()
        self.current_function = None

    def analyze_statement(self, node: ASTNode):
        """分析語句"""
        if isinstance(node, VarDeclarationNode):
            self.analyze_var_declaration(node)
        elif isinstance(node, AssignmentNode):
            self.analyze_assignment(node)
        elif isinstance(node, IfNode):
            self.analyze_if(node)
        elif isinstance(node, WhileNode):
            self.analyze_while(node)
        elif isinstance(node, ForNode):
            self.analyze_for(node)
        elif isinstance(node, ReturnNode):
            self.analyze_return(node)
        elif isinstance(node, BinaryExprNode):
            self.analyze_expression(node)
        elif isinstance(node, FunctionCallNode):
            self.analyze_expression(node)

    def analyze_var_declaration(self, node: VarDeclarationNode):
        """分析變數宣告"""
        symbol = Symbol(name=node.name, type=node.var_type, kind='variable', line=node.line)
        self.symbol_table.define(symbol)

        if node.init:
            init_type = self.get_expression_type(node.init)
            if init_type and not self.type_compatible(node.var_type, init_type):
                self.error(f"Type mismatch: cannot assign {init_type} to {node.var_type}", node.line)

    def analyze_assignment(self, node: AssignmentNode):
        """分析賦值"""
        if isinstance(node.target, IdentifierNode):
            symbol = self.symbol_table.lookup(node.target.name)
            if not symbol:
                self.error(f"Undefined variable: {node.target.name}", node.target.line)

            target_type = symbol.type
            value_type = self.get_expression_type(node.value)

            if value_type and not self.type_compatible(target_type, value_type):
                self.error(f"Type mismatch: cannot assign {value_type} to {target_type}", node.line)

    def analyze_if(self, node: IfNode):
        """分析條件語句"""
        cond_type = self.get_expression_type(node.condition)
        if cond_type and cond_type != 'bool':
            self.error(f"Condition must be boolean, got {cond_type}", node.condition.line)

        for stmt in node.then_branch:
            self.analyze_statement(stmt)

        if node.else_branch:
            for stmt in node.else_branch:
                self.analyze_statement(stmt)

    def analyze_while(self, node: WhileNode):
        """分析 while 迴圈"""
        cond_type = self.get_expression_type(node.condition)
        if cond_type and cond_type != 'bool':
            self.error(f"Condition must be boolean, got {cond_type}", node.condition.line)

        for stmt in node.body:
            self.analyze_statement(stmt)

    def analyze_for(self, node: ForNode):
        """分析 for 迴圈"""
        if node.init:
            self.analyze_statement(node.init)

        if node.condition:
            cond_type = self.get_expression_type(node.condition)
            if cond_type and cond_type != 'bool':
                self.error(f"Condition must be boolean, got {cond_type}", node.condition.line)

        if node.update:
            self.analyze_statement(node.update)

        for stmt in node.body:
            self.analyze_statement(stmt)

    def analyze_return(self, node: ReturnNode):
        """分析返回語句"""
        func = self.symbol_table.lookup_function(self.current_function)
        if not func:
            return

        if node.value:
            return_type = self.get_expression_type(node.value)
            if return_type and not self.type_compatible(func.return_type, return_type):
                self.error(f"Return type mismatch: expected {func.return_type}, got {return_type}", node.line)
        else:
            if func.return_type != 'int':
                self.error(f"Expected return value, got nothing", node.line)

    def analyze_expression(self, node: ExprNode) -> str:
        """分析表達式並返回類型"""
        if isinstance(node, NumberNode):
            return 'int' if isinstance(node.value, int) else 'float'

        if isinstance(node, StringNode):
            return 'string'

        if isinstance(node, BooleanNode):
            return 'bool'

        if isinstance(node, IdentifierNode):
            symbol = self.symbol_table.lookup(node.name)
            if not symbol:
                self.error(f"Undefined variable: {node.name}", node.line)
            return symbol.type

        if isinstance(node, BinaryExprNode):
            left_type = self.analyze_expression(node.left)
            right_type = self.analyze_expression(node.right)

            if node.operator in ['+', '-', '*', '/']:
                if left_type == 'float' or right_type == 'float':
                    return 'float'
                return 'int'

            if node.operator in ['and', 'or']:
                return 'bool'

            if node.operator in ['<', '>', '<=', '>=', '==', '!=']:
                return 'bool'

            return 'int'

        if isinstance(node, UnaryExprNode):
            operand_type = self.analyze_expression(node.operand)
            if node.operator == '-':
                return operand_type
            if node.operator == 'not':
                return 'bool'
            return operand_type

        if isinstance(node, FunctionCallNode):
            func = self.symbol_table.lookup_function(node.name)
            if not func:
                self.error(f"Undefined function: {node.name}", node.line)
                return 'int'

            if len(node.args) != len(func.params):
                self.error(f"Argument count mismatch for {node.name}", node.line)

            return func.return_type

        if isinstance(node, ArrayAccessNode):
            symbol = self.symbol_table.lookup(node.name)
            if not symbol:
                self.error(f"Undefined array: {node.name}", node.line)
            return 'int'

        return 'int'

    def get_expression_type(self, node: ExprNode) -> Optional[str]:
        """獲取表達式類型"""
        return self.analyze_expression(node)

    def type_compatible(self, target: str, source: str) -> bool:
        """檢查類型兼容性"""
        if target == source:
            return True

        # int 可以轉換為 float
        if target == 'float' and source == 'int':
            return True

        return False

    def error(self, message: str, line: int):
        """報告錯誤"""
        self.errors.append(f"Line {line}: {message}")
        print(f"Semantic Error: {message}")

    def has_errors(self) -> bool:
        return len(self.errors) > 0


def main():
    """測試語義分析器"""
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

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    if analyzer.has_errors():
        print("\n=== Semantic Errors ===")
        for error in analyzer.errors:
            print(error)
    else:
        print("Semantic analysis passed!")


if __name__ == "__main__":
    main()