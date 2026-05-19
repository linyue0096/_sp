"""SimpleLang - 简单编程语言编译器

支持生成:
- 四元组中间码
- 堆叠机字节码
- 暂存器机代码
- LLVM IR
"""

__version__ = "1.0.0"
__author__ = "SimpleLang Compiler"

from .lexer import Lexer, Token, TokenType
from .parser import Parser
from .semantic import SemanticAnalyzer
from .ir import IRGenerator, Quadruple
from .codegen.stack_machine import StackMachineCodegen
from .codegen.register_machine import RegisterMachineCodegen
from .codegen.llvm_ir import LLVMIRGenerator
from .compiler import Compiler

__all__ = [
    'Lexer', 'Token', 'TokenType',
    'Parser',
    'SemanticAnalyzer',
    'IRGenerator', 'Quadruple',
    'StackMachineCodegen',
    'RegisterMachineCodegen',
    'LLVMIRGenerator',
    'Compiler'
]