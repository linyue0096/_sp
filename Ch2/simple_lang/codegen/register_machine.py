"""暫存器機代碼生成器 - 生成三地址碼"""

from typing import List
from ..ir import Quadruple


class RegisterMachineCodegen:
    """暫存器機代碼生成器

    指令格式: OP Rd, Rs, Rt (目的暫存器, 源暫存器1, 源暫存器2)
    或:       OP Rd, Rs     (單元運算)

    指令集:
        LOAD    Rd, addr    - 載入記憶體到暫存器
        STORE   addr, Rs    - 儲存暫存器到記憶體
        LI      Rd, imm     - 載入立即數
        MOVE    Rd, Rs      - 移動暫存器
        ADD     Rd, Rs, Rt  - 加
        SUB     Rd, Rs, Rt  - 減
        MUL     Rd, Rs, Rt  - 乘
        DIV     Rd, Rs, Rt  - 除
        AND     Rd, Rs, Rt  - 邏輯與
        OR      Rd, Rs, Rt  - 邏輯或
        XOR     Rd, Rs, Rt  - 邏輯異或
        NOT     Rd, Rs      - 邏輯非
        SLT     Rd, Rs, Rt  - 小於設定
        SLE     Rd, Rs, Rt  - 小於等於設定
        SEQ     Rd, Rs, Rt  - 等於設定
        SNE     Rd, Rs, Rt  - 不等於設定
        J       label       - 跳轉
        BEQ     Rs, Rt, label - 分支相等
        BNE     Rs, Rt, label - 分支不等於
        CALL    label       - 函數呼叫
        RET                 - 返回
        PARAM    Rs         - 參數
        PRINT    Rs         - 輸出
        HALT                - 停止
    """

    def __init__(self):
        self.instructions: List[str] = []
        self.register_counter = 0
        self.registers = ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]
        self.register_map = {}  # 變數到暫存器的映射
        self.next_register = 0

    def allocate_register(self, name: str = None) -> str:
        """分配暫存器"""
        if name and name in self.register_map:
            return self.register_map[name]

        if self.next_register >= len(self.registers):
            # 溢出處理：使用堆疊
            return f"MEM[{len(self.register_map)}]"

        reg = self.registers[self.next_register]
        self.next_register = (self.next_register + 1) % len(self.registers)

        if name:
            self.register_map[name] = reg

        return reg

    def generate(self, quadruples: List[Quadruple]) -> List[str]:
        """生成暫存器機指令"""
        for quad in quadruples:
            self.translate_quadruple(quad)

        return self.instructions

    def translate_quadruple(self, quad: Quadruple):
        """翻譯四元組為暫存器機指令"""
        op = quad.op.upper()

        if op == "FUNCTION":
            self.emit(f"# Function: {quad.arg1}")
            self.next_register = 0
            self.register_map.clear()

        elif op == "ENDFUNCTION":
            self.emit("RET")

        elif op == "PARAM":
            reg = self.allocate_register()
            self.emit(f"LI {reg}, {quad.arg1}")

        elif op == "CALL":
            func_name = quad.arg1
            dest = quad.result
            self.emit(f"CALL {func_name}")
            if dest:
                reg = self.allocate_register(dest)
                self.emit(f"MOVE {reg}, R0")

        elif op == "RETURN":
            if quad.arg1:
                reg = self.get_register(quad.arg1)
                self.emit(f"MOVE R0, {reg}")
            self.emit("RET")

        elif op == "=":
            src_reg = self.get_register(quad.arg1)
            dst_reg = self.allocate_register(quad.result)
            self.emit(f"MOVE {dst_reg}, {src_reg}")

        elif op == "+":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"ADD {rd}, {r1}, {r2}")

        elif op == "-":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"SUB {rd}, {r1}, {r2}")

        elif op == "*":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"MUL {rd}, {r1}, {r2}")

        elif op == "/":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"DIV {rd}, {r1}, {r2}")

        elif op == "<":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"SLT {rd}, {r1}, {r2}")

        elif op == ">":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"SLT {rd}, {r2}, {r1}")

        elif op == "<=":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"SLE {rd}, {r1}, {r2}")

        elif op == ">=":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"SLE {rd}, {r2}, {r1}")

        elif op == "==":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"SEQ {rd}, {r1}, {r2}")

        elif op == "!=":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"SNE {rd}, {r1}, {r2}")

        elif op == "AND":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"AND {rd}, {r1}, {r2}")

        elif op == "OR":
            r1 = self.get_register(quad.arg1)
            r2 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"OR {rd}, {r1}, {r2}")

        elif op == "NOT":
            r1 = self.get_register(quad.arg1)
            rd = self.allocate_register(quad.result)
            self.emit(f"NOT {rd}, {r1}")

        elif op == "GOTO":
            self.emit(f"J {quad.result}")

        elif op == "IFFALSE":
            r1 = self.get_register(quad.arg1)
            self.emit(f"BEQ {r1}, R0, {quad.result}")

        elif op == "LABEL":
            self.emit(f"{quad.arg1}:")

        elif op == "GETARRAY":
            r1 = self.get_register(quad.arg2)
            rd = self.allocate_register(quad.result)
            self.emit(f"LOAD {rd}, {quad.arg1}[{r1}]")

        elif op == "SETARRAY":
            r1 = self.get_register(quad.arg2)
            r2 = self.get_register(quad.result)
            self.emit(f"STORE {quad.arg1}[{r1}], {r2}")

        elif op == "END":
            self.emit("HALT")

    def get_register(self, name: str) -> str:
        """獲取或創建暫存器"""
        if name in self.register_map:
            return self.register_map[name]

        # 如果是數字常數，使用立即數
        if name.isdigit() or (name.startswith('"') and name.endswith('"')):
            reg = self.allocate_register()
            self.emit(f"LI {reg}, {name}")
            return reg

        return self.allocate_register(name)

    def emit(self, instruction: str):
        """發射指令"""
        self.instructions.append(instruction)

    def print_code(self):
        """打印暫存器機代碼"""
        print("\n=== 暫存器機代碼 (Register Machine Code) ===")
        for instr in self.instructions:
            print(instr)


def main():
    """測試暫存器機代碼生成"""
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

    codegen = RegisterMachineCodegen()
    code = codegen.generate(quadruples)
    codegen.print_code()


if __name__ == "__main__":
    main()