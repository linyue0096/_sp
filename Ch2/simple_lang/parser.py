"""語法分析器 (Parser) - 將 Token 流轉換為 AST"""

from typing import List, Optional
from dataclasses import dataclass, field
from .lexer import Token, TokenType


# ===== AST 節點 =====

@dataclass
class ASTNode:
    """AST 基類"""
    line: int = 0


@dataclass
class ProgramNode(ASTNode):
    """程式節點"""
    functions: List['FunctionNode'] = field(default_factory=list)


@dataclass
class FunctionNode:
    """函數定義節點"""
    name: str
    params: List['ParameterNode']
    return_type: str
    body: List[ASTNode]
    line: int = 0


@dataclass
class ParameterNode:
    """參數節點"""
    name: str
    type: str
    line: int = 0


@dataclass
class VarDeclarationNode:
    """變數宣告節點"""
    name: str
    var_type: str
    init: Optional['ExprNode'] = None
    line: int = 0


@dataclass
class AssignmentNode:
    """賦值語句節點"""
    target: 'ExprNode'
    value: 'ExprNode'
    line: int = 0


@dataclass
class ArrayAssignmentNode:
    """陣列賦值節點"""
    name: str
    index: 'ExprNode'
    value: 'ExprNode'
    line: int = 0


@dataclass
class IfNode:
    """條件語句節點"""
    condition: 'ExprNode'
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None
    line: int = 0


@dataclass
class WhileNode:
    """while 迴圈節點"""
    condition: 'ExprNode'
    body: List[ASTNode]
    line: int = 0


@dataclass
class ForNode:
    """for 迴圈節點"""
    init: Optional[ASTNode]
    condition: Optional['ExprNode']
    update: Optional[ASTNode]
    body: List[ASTNode]
    line: int = 0


@dataclass
class ReturnNode:
    """返回語句節點"""
    value: Optional['ExprNode'] = None
    line: int = 0


@dataclass
class ExprNode:
    """表達式基類"""
    line: int = 0


@dataclass
class BinaryExprNode:
    """二元運算表達式"""
    operator: str
    left: ExprNode
    right: ExprNode
    line: int = 0


@dataclass
class UnaryExprNode:
    """一元運算表達式"""
    operator: str
    operand: ExprNode
    line: int = 0


@dataclass
class IdentifierNode:
    """識別符表達式"""
    name: str
    line: int = 0


@dataclass
class NumberNode:
    """數值常"""
    value: any
    line: int = 0


@dataclass
class StringNode:
    """字串常"""
    value: str
    line: int = 0


@dataclass
class BooleanNode:
    """布林常"""
    value: bool
    line: int = 0


@dataclass
class ArrayAccessNode:
    """陣列存取"""
    name: str
    index: ExprNode
    line: int = 0


@dataclass
class FunctionCallNode:
    """函數呼叫"""
    name: str
    args: List[ExprNode]
    line: int = 0


# ===== Parser =====

class Parser:
    """語法分析器"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> ProgramNode:
        """執行語法分析"""
        program = ProgramNode(functions=[], line=1)

        while not self.is_at_end():
            if self.check(TokenType.FUNCTION):
                program.functions.append(self.function())
            else:
                self.advance()

        return program

    # ===== 輔助方法 =====

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        self.error(message)

    def error(self, message: str):
        token = self.peek()
        print(f"Parser Error at line {token.line}: {message}")
        raise Exception(message)

    # ===== 語法規則 =====

    def function(self) -> FunctionNode:
        """function ID(params) : type block"""
        self.consume(TokenType.FUNCTION, "Expected 'function'")
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").lexeme

        self.consume(TokenType.LPAREN, "Expected '(' after function name")

        params = []
        if not self.check(TokenType.RPAREN):
            params.append(self.parameter())
            while self.check(TokenType.COMMA):
                self.advance()
                params.append(self.parameter())

        self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        self.consume(TokenType.COLON, "Expected ':' before return type")

        return_type = self.consume(TokenType.INT, "Expected return type").lexeme
        if return_type == 'int':
            return_type = 'int'
        elif return_type == 'float':
            return_type = 'float'
        elif return_type == 'bool':
            return_type = 'bool'
        elif return_type == 'string':
            return_type = 'string'

        body = self.block()

        return FunctionNode(
            name=name,
            params=params,
            return_type=return_type,
            body=body,
            line=self.previous().line
        )

    def parameter(self) -> ParameterNode:
        """ID : type"""
        name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").lexeme
        self.consume(TokenType.COLON, "Expected ':' after parameter name")

        param_type = self.consume(TokenType.INT, "Expected parameter type").lexeme
        return ParameterNode(name=name, type=param_type, line=self.previous().line)

    def block(self) -> List[ASTNode]:
        """{ statement* }"""
        self.consume(TokenType.LBRACE, "Expected '{'")
        statements = []

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.statement())

        self.consume(TokenType.RBRACE, "Expected '}'")
        return statements

    def statement(self) -> ASTNode:
        """statement ::= varDecl | assignment | ifStmt | whileStmt | forStmt | returnStmt"""
        if self.check(TokenType.VAR):
            return self.var_declaration()

        if self.check(TokenType.IF):
            return self.if_statement()

        if self.check(TokenType.WHILE):
            return self.while_statement()

        if self.check(TokenType.FOR):
            return self.for_statement()

        if self.check(TokenType.RETURN):
            return self.return_statement()

        # 可能是賦值或表達式
        return self.expression_statement()

    def var_declaration(self) -> VarDeclarationNode:
        """var ID : type [= expr] ;"""
        self.consume(TokenType.VAR, "Expected 'var'")
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").lexeme
        self.consume(TokenType.COLON, "Expected ':' after variable name")

        var_type = self.consume(TokenType.INT, "Expected type").lexeme

        init = None
        if self.check(TokenType.ASSIGN):
            self.advance()
            # 解析簡單表達式（數字、識別符、或帶運算符的二元式）
            init = self.simple_expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")

        return VarDeclarationNode(name=name, var_type=var_type, init=init, line=self.previous().line)

    def if_statement(self) -> IfNode:
        """if ( expr ) block [ else block ]"""
        self.consume(TokenType.IF, "Expected 'if'")
        self.consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")

        then_branch = self.block()

        else_branch = None
        if self.check(TokenType.ELSE):
            self.advance()
            else_branch = self.block()

        return IfNode(condition=condition, then_branch=then_branch, else_branch=else_branch, line=self.previous().line)

    def while_statement(self) -> WhileNode:
        """while ( expr ) block"""
        self.consume(TokenType.WHILE, "Expected 'while'")
        self.consume(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")
        body = self.block()

        return WhileNode(condition=condition, body=body, line=self.previous().line)

    def for_statement(self) -> ForNode:
        """for ( [stmt] ; [expr] ; [stmt] ) block"""
        self.consume(TokenType.FOR, "Expected 'for'")
        self.consume(TokenType.LPAREN, "Expected '(' after 'for'")

        init = None
        if not self.check(TokenType.SEMICOLON):
            init = self.statement()

        self.consume(TokenType.SEMICOLON, "Expected ';'")

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';'")

        update = None
        if not self.check(TokenType.RPAREN):
            update = self.statement()

        self.consume(TokenType.RPAREN, "Expected ')'")
        body = self.block()

        return ForNode(init=init, condition=condition, update=update, body=body, line=self.previous().line)

    def return_statement(self) -> ReturnNode:
        """return [expr] ;"""
        self.consume(TokenType.RETURN, "Expected 'return'")

        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after return value")

        return ReturnNode(value=value, line=self.previous().line)

    def expression_statement(self) -> ASTNode:
        """expr ; 或 assignment ;"""
        expr = self.expression()

        # 檢查是否為賦值
        if self.check(TokenType.ASSIGN):
            self.advance()
            value = self.expression()
            if isinstance(expr, IdentifierNode):
                result = AssignmentNode(target=expr, value=value, line=expr.line)
            else:
                result = AssignmentNode(target=expr, value=value, line=expr.line)
            self.consume(TokenType.SEMICOLON, "Expected ';'")
            return result

        self.consume(TokenType.SEMICOLON, "Expected ';'")
        return expr

    # ===== 表達式 =====

    def expression(self) -> ExprNode:
        """expression ::= orExpr"""
        return self.or_expression()

    def or_expression(self) -> ExprNode:
        """orExpr ::= andExpr { or andExpr }"""
        left = self.and_expression()

        while self.check(TokenType.OR):
            operator = self.advance().lexeme
            right = self.and_expression()
            left = BinaryExprNode(operator=operator, left=left, right=right, line=self.previous().line)

        return left

    def and_expression(self) -> ExprNode:
        """andExpr ::= equalityExpr { and equalityExpr }"""
        left = self.equality_expression()

        while self.check(TokenType.AND):
            operator = self.advance().lexeme
            right = self.equality_expression()
            left = BinaryExprNode(operator=operator, left=left, right=right, line=self.previous().line)

        return left

    def equality_expression(self) -> ExprNode:
        """equalityExpr ::= comparisonExpr { (== | !=) comparisonExpr }"""
        left = self.comparison_expression()

        while self.check(TokenType.EQ) or self.check(TokenType.NEQ):
            operator = self.advance().lexeme
            right = self.comparison_expression()
            left = BinaryExprNode(operator=operator, left=left, right=right, line=self.previous().line)

        return left

    def comparison_expression(self) -> ExprNode:
        """comparisonExpr ::= additiveExpr { (< | > | <= | >=) additiveExpr }"""
        left = self.additive_expression()

        while self.check(TokenType.LT) or self.check(TokenType.LE) or \
                self.check(TokenType.GT) or self.check(TokenType.GE):
            operator = self.advance().lexeme
            right = self.additive_expression()
            left = BinaryExprNode(operator=operator, left=left, right=right, line=self.previous().line)

        return left

    def additive_expression(self) -> ExprNode:
        """additiveExpr ::= multiplicativeExpr { (+ | -) multiplicativeExpr }"""
        left = self.multiplicative_expression()

        while self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
            operator = self.advance().lexeme
            right = self.multiplicative_expression()
            left = BinaryExprNode(operator=operator, left=left, right=right, line=self.previous().line)

        return left

    def multiplicative_expression(self) -> ExprNode:
        """multiplicativeExpr ::= unaryExpr { (* | /) unaryExpr }"""
        left = self.unary_expression()

        while self.check(TokenType.MUL) or self.check(TokenType.DIV):
            operator = self.advance().lexeme
            right = self.unary_expression()
            left = BinaryExprNode(operator=operator, left=left, right=right, line=self.previous().line)

        return left

    def unary_expression(self) -> ExprNode:
        """unaryExpr ::= (- | not) unaryExpr | primaryExpr"""
        if self.check(TokenType.MINUS):
            operator = self.advance().lexeme
            operand = self.unary_expression()
            return UnaryExprNode(operator=operator, operand=operand, line=self.previous().line)

        if self.check(TokenType.NOT):
            operator = self.advance().lexeme
            operand = self.unary_expression()
            return UnaryExprNode(operator=operator, operand=operand, line=self.previous().line)

        return self.primary_expression()

    def primary_expression(self) -> ExprNode:
        """primaryExpr ::= number | string | bool | ID | ID [expr] | ( expr ) | functionCall"""
        if self.check(TokenType.NUMBER):
            value = self.advance().value
            return NumberNode(value=value, line=self.previous().line)

        if self.check(TokenType.STRING_LIT):
            value = self.advance().value
            return StringNode(value=value, line=self.previous().line)

        if self.check(TokenType.TRUE):
            self.advance()
            return BooleanNode(value=True, line=self.previous().line)

        if self.check(TokenType.FALSE):
            self.advance()
            return BooleanNode(value=False, line=self.previous().line)

        if self.check(TokenType.IDENTIFIER):
            name = self.advance().lexeme

            # 函數呼叫
            if self.check(TokenType.LPAREN):
                return self.function_call(name)

            # 陣列存取
            if self.check(TokenType.LBRACKET):
                self.advance()
                index = self.expression()
                self.consume(TokenType.RBRACKET, "Expected ']'")
                return ArrayAccessNode(name=name, index=index, line=self.previous().line)

            return IdentifierNode(name=name, line=self.previous().line)

        if self.check(TokenType.LPAREN):
            self.advance()
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')'")
            return expr

        self.error("Expected expression")
        return None

    def function_call(self, name: str) -> FunctionCallNode:
        """ID ( args )"""
        self.consume(TokenType.LPAREN, "Expected '('")

        args = []
        if not self.check(TokenType.RPAREN):
            args.append(self.expression())
            while self.check(TokenType.COMMA):
                self.advance()
                args.append(self.expression())

        self.consume(TokenType.RPAREN, "Expected ')'")

        return FunctionCallNode(name=name, args=args, line=self.previous().line)

    def simple_expression(self) -> ExprNode:
        """簡單表達式 - 用於 var 初始化，遇到 ; 或 } 停止"""
        return self.or_expression()

    def is_statement_end(self) -> bool:
        """檢查是否為語句結束標記"""
        t = self.peek().type
        return t in [TokenType.SEMICOLON, TokenType.RBRACE]


def print_ast(node: ASTNode, indent: int = 0):
    """打印 AST"""
    prefix = "  " * indent
    print(f"{prefix}{node.__class__.__name__}")
    for field_name in dir(node):
        if field_name.startswith('_'):
            continue
        field_value = getattr(node, field_name, None)
        if isinstance(field_value, list):
            for item in field_value:
                if isinstance(item, ASTNode):
                    print(f"{prefix}  {field_name}:")
                    print_ast(item, indent + 2)
        elif isinstance(field_value, ASTNode):
            print(f"{prefix}  {field_name}:")
            print_ast(field_value, indent + 2)
        elif field_value is not None and not callable(field_value):
            print(f"{prefix}  {field_name}: {field_value}")


def main():
    """測試語法分析器"""
    from lexer import Lexer

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

    print("=== AST ===")
    print_ast(ast)


if __name__ == "__main__":
    main()