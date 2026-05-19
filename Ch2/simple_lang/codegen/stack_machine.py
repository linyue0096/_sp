"""堆疊機代碼生成器 - 生成虛擬機字節碼"""

from typing import List
from ..ir import Quadruple


class StackMachineCodegen:
    """堆疊機代碼生成器

    指令集:
        LOAD    value   - 載入常數到堆疊
        LOADV   name    - 載入變數到堆疊
        STORE   name    - 儲存堆疊頂端到變數
        ADD             - 彈出兩個值相加,結果推入堆疊
        SUB             - 彈出兩個值相減
        MUL             - 彈出兩個值相乘
        DIV             - 彈出兩個值相除
        AND             - 邏輯 AND
        OR              - 邏輯 OR
        NOT             - 邏輯 NOT
        GT              - 大於
        LT              - 小於
        GE              - 大於等於
        LE              - 小於等於
        EQ              - 等於
        NEQ             - 不等於
        JUMP    label   - 無條件跳轉
        JUMPF   label   - 條件為假跳轉
        LABEL   label   - 定義標籤
        CALL    name    - 呼叫函數
        PARAM   n       - 設定參數
        RET             - 返回
        PRINT           - 輸出
        HALT            - 停止
    """

    def __init__(self):
        self.instructions: List[str] = []
        self.label_counter = 0

    def generate(self, quadruples: List[Quadruple]) -> List[str]:
        """生成堆疊機指令"""
        for quad in quadruples:
            self.translate_quadruple(quad)

        return self.instructions

    def translate_quadruple(self, quad: Quadruple):
        """翻譯四元組為堆疊機指令"""
        op = quad.op.upper()

        if op == "FUNCTION":
            self.emit(f"FUNCTION {quad.arg1}")

        elif op == "ENDFUNCTION":
            self.emit("RETURN")

        elif op == "PARAM":
            self.emit(f"PUSH {quad.arg1}")

        elif op == "CALL":
            self.emit(f"CALL {quad.arg1}")

        elif op == "RETURN":
            if quad.arg1:
                self.emit("PUSH R0")
                self.emit("STORE R0")
            self.emit("RETURN")

        elif op == "=":
            self.emit(f"PUSH {quad.arg1}")
            self.emit(f"STORE {quad.result}")

        elif op == "+":
            self.emit("POP R1")
            self.emit("POP R0")
            self.emit("ADD R0, R1")
            self.emit("PUSH R0")

        elif op == "-":
            self.emit("POP R1")
            self.emit("POP R0")
            self.emit("SUB R0, R1")
            self.emit("PUSH R0")

        elif op == "*":
            self.emit("POP R1")
            self.emit("POP R0")
            self.emit("MUL R0, R1")
            self.emit("PUSH R0")

        elif op == "/":
            self.emit("POP R1")
            self.emit("POP R0")
            self.emit("DIV R0, R1")
            self.emit("PUSH R0")

        elif op in ["<", ">", "<=", ">=", "==", "!="]:
            self.emit("POP R1")
            self.emit("POP R0")
            op_map = {
                "<": "LT", ">": "GT", "<=": "LE", ">=": "GE",
                "==": "EQ", "!=": "NEQ"
            }
            self.emit(f"{op_map[op]} R0, R1")
            self.emit("PUSH R0")

        elif op == "AND":
            self.emit("POP R1")
            self.emit("POP R0")
            self.emit("AND R0, R1")
            self.emit("PUSH R0")

        elif op == "OR":
            self.emit("POP R1")
            self.emit("POP R0")
            self.emit("OR R0, R1")
            self.emit("PUSH R0")

        elif op == "NOT":
            self.emit("POP R0")
            self.emit("NOT R0")
            self.emit("PUSH R0")

        elif op == "GOTO":
            self.emit(f"JUMP {quad.result}")

        elif op == "IFFALSE":
            self.emit("POP R0")
            self.emit(f"JUMPF {quad.result}")

        elif op == "LABEL":
            self.emit(f"LABEL {quad.arg1}")

        elif op == "GETARRAY":
            self.emit(f"LOADARRAY {quad.arg1} {quad.arg2} {quad.result}")

        elif op == "SETARRAY":
            self.emit(f"STOREARRAY {quad.arg1} {quad.arg2} {quad.result}")

        elif op == "END":
            self.emit("HALT")

    def emit(self, instruction: str):
        """發射指令"""
        self.instructions.append(instruction)

    def print_code(self):
        """打印堆疊機代碼"""
        print("\n=== 堆疊機字節碼 (Stack Machine Bytecode) ===")
        for i, instr in enumerate(self.instructions):
            print(f"{i:4d}:  {instr}")


def main():
    """測試堆疊機代碼生成"""
    from ..lexer import Lexer
    from ..parser import Parser
    from ..ir import IRGenerator

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

    codegen = StackMachineCodegen()
    code = codegen.generate(quadruples)
    codegen.print_code()


if __name__ == "__main__":
    main()