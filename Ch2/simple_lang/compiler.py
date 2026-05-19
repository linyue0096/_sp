"""SimpleLang 編譯器主程式"""

import sys
import argparse
from pathlib import Path

from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .ir import IRGenerator
from .codegen.stack_machine import StackMachineCodegen
from .codegen.register_machine import RegisterMachineCodegen
from .codegen.llvm_ir import LLVMIRGenerator


class Compiler:
    """SimpleLang 編譯器"""

    def __init__(self):
        self.lexer = None
        self.parser = None
        self.analyzer = None
        self.ir_generator = None

    def compile(self, source_file: str, output_dir: str = "."):
        """編譯源代碼"""
        print(f"Compiling: {source_file}")

        # 讀取源代碼
        with open(source_file, 'r', encoding='utf-8') as f:
            source = f.read()

        # 1. 詞法分析
        print("\n[1] Lexical Analysis...")
        self.lexer = Lexer(source)
        tokens = self.lexer.tokenize()
        print(f"    Token count: {len(tokens) - 1}")

        # 2. 語法分析
        print("\n[2] Syntax Analysis...")
        self.parser = Parser(tokens)
        ast = self.parser.parse()
        print(f"    Functions: {len(ast.functions)}")

        # 3. 語義分析
        print("\n[3] Semantic Analysis...")
        self.analyzer = SemanticAnalyzer()
        success = self.analyzer.analyze(ast)
        if not success:
            print("    Semantic errors found!")
            return False
        print("    Semantic analysis passed!")

        # 4. 中間碼生成
        print("\n[4] IR Generation...")
        self.ir_generator = IRGenerator()
        quadruples = self.ir_generator.generate(ast)
        print(f"    Quadruples: {len(quadruples)}")

        # 5. 目標碼生成
        print("\n[5] Code Generation...")

        # 5.1 四元組
        self.save_output(f"{output_dir}/quadruples.txt", self.format_quadruples(quadruples))

        # 5.2 堆疊機代碼
        stack_codegen = StackMachineCodegen()
        stack_code = stack_codegen.generate(quadruples)
        self.save_output(f"{output_dir}/stack_machine.asm", stack_code)

        # 5.3 暫存器機代碼
        register_codegen = RegisterMachineCodegen()
        register_code = register_codegen.generate(quadruples)
        self.save_output(f"{output_dir}/register_machine.asm", register_code)

        # 5.4 LLVM IR
        llvm_codegen = LLVMIRGenerator()
        llvm_code = llvm_codegen.generate(quadruples)
        self.save_output(f"{output_dir}/llvm_ir.ll", llvm_code)

        print("\n[6] Output files generated!")
        print(f"    - {output_dir}/quadruples.txt")
        print(f"    - {output_dir}/stack_machine.asm")
        print(f"    - {output_dir}/register_machine.asm")
        print(f"    - {output_dir}/llvm_ir.ll")

        print("\n=== Compilation Successful ===")
        return True

    def format_quadruples(self, quadruples) -> list:
        """格式化四元組"""
        lines = ["=== Quadruples ===", ""]
        lines.append(f"{'OP':<12} {'ARG1':<15} {'ARG2':<15} {'RESULT':<15}")
        lines.append("-" * 60)
        for q in quadruples:
            lines.append(f"{q.op:<12} {q.arg1:<15} {q.arg2:<15} {q.result:<15}")
        return lines

    def save_output(self, filename: str, content: list):
        """保存輸出"""
        with open(filename, 'w', encoding='utf-8') as f:
            for line in content:
                f.write(f"{line}\n")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(description="SimpleLang Compiler")
    parser.add_argument("input", help="Input source file")
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        return 1

    compiler = Compiler()
    success = compiler.compile(args.input, args.output)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())