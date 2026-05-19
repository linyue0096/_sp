"""詞法分析器 (Lexer) - 將源代碼轉換為 Token 流"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List
import re


class TokenType(Enum):
    """Token 類型"""

    # 保留關鍵字
    FUNCTION = auto()
    VAR = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()

    # 類型
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    STRING = auto()

    # 字面量
    NUMBER = auto()
    STRING_LIT = auto()
    TRUE = auto()
    FALSE = auto()

    # 運算子
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    ASSIGN = auto()

    # 比較運算子
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    # 邏輯運算子
    AND = auto()
    OR = auto()
    NOT = auto()

    # 分隔符
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()

    # 識別符
    IDENTIFIER = auto()

    # 特殊
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """Token 結構"""
    type: TokenType
    lexeme: str
    value: Optional[any] = None
    line: int = 0
    column: int = 0

    def __repr__(self):
        return f"Token({self.type.name}, '{self.lexeme}', line={self.line})"


class Lexer:
    """詞法分析器"""

    KEYWORDS = {
        'function': TokenType.FUNCTION,
        'var': TokenType.VAR,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'return': TokenType.RETURN,
        'int': TokenType.INT,
        'float': TokenType.FLOAT,
        'bool': TokenType.BOOL,
        'string': TokenType.STRING,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        """執行詞法分析"""
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, '', line=self.line, column=self.column))
        return self.tokens

    def scan_token(self):
        """掃描單個 Token"""
        char = self.peek()

        # 空白字元
        if char.isspace():
            self.advance()
            return

        # 註釋
        if char == '/' and self.peek_next() == '/':
            while char != '\n' and not self.is_at_end():
                self.advance()
                char = self.peek()
            return

        # 識別符或關鍵字
        if char.isalpha() or char == '_':
            self.identifier()
            return

        # 數字
        if char.isdigit():
            self.number()
            return

        # 字串
        if char == '"':
            self.string()
            return

        # 單字元 Token
        self.single_char_token(char)

    def single_char_token(self, char: str):
        """處理單字元 Token"""
        token_map = {
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MUL,
            '/': TokenType.DIV,
        }

        if char in token_map:
            self.add_token(token_map[char])
            self.advance()
            return

        # 檢查多字元運算子
        if char == '=':
            self.advance()
            if self.peek() == '=':
                self.add_token(TokenType.EQ)
                self.advance()
            else:
                self.add_token(TokenType.ASSIGN)
            return

        if char == '!':
            self.advance()
            if self.peek() == '=':
                self.add_token(TokenType.NEQ)
                self.advance()
            else:
                self.add_token(TokenType.NOT)
            return

        if char == '<':
            self.advance()
            if self.peek() == '=':
                self.add_token(TokenType.LE)
                self.advance()
            else:
                self.add_token(TokenType.LT)
            return

        if char == '>':
            self.advance()
            if self.peek() == '=':
                self.add_token(TokenType.GE)
                self.advance()
            else:
                self.add_token(TokenType.GT)
            return

        # 未知字元
        self.error_token(f"Unknown character: {char}")

    def identifier(self):
        """識別符或關鍵字"""
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()

        text = self.source[self.start:self.current]
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    def number(self):
        """數值常"""
        while self.peek().isdigit():
            self.advance()

        # 小數點
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()

        text = self.source[self.start:self.current]
        value = float(text) if '.' in text else int(text)
        self.add_token(TokenType.NUMBER, value)

    def string(self):
        """字串常"""
        self.advance()  # 跳過 opening quote
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.error_token("Unterminated string")

        self.advance()  # 跳過 closing quote
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING_LIT, value)

    def add_token(self, token_type: TokenType, value=None):
        """添加 Token"""
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, value, self.line, self.column))

    def peek(self) -> str:
        """查看當前字元"""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        """查看下一個字元"""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def advance(self) -> str:
        """前進並返回當前字元"""
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def is_at_end(self) -> bool:
        """是否已到達末尾"""
        return self.current >= len(self.source)

    def error_token(self, message: str):
        """錯誤 Token"""
        print(f"Lexer Error at line {self.line}, column {self.column}: {message}")


def main():
    """測試詞法分析器"""
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

    print("=== Tokens ===")
    for token in tokens:
        print(f"{token.type.name:20} {token.lexeme:15} value={token.value}")


if __name__ == "__main__":
    main()