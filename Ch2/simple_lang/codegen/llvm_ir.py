"""LLVM IR 代碼生成器"""

from typing import List, Dict
from ..ir import Quadruple


class LLVMIRGenerator:
    """LLVM IR 代碼生成器

    生成的 LLVM IR 格式:
    - 模組定義
    - 全域變數
    - 函數定義
    - 基本塊與指令

    支援的類型: i32, i64, float, double, i1 (bool), i8* (string)
    """

    def __init__(self):
        self.instructions: List[str] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.current_function = ""
        self.local_vars: Dict[str, str] = {}  # 變數到 LLVM 值的映射

    def generate(self, quadruples: List[Quadruple]) -> List[str]:
        """生成 LLVM IR"""
        self.emit("; SimpleLang -> LLVM IR")
        self.emit("; Module")
        self.emit("")
        self.emit("define i32 @main() {")

        for quad in quadruples:
            if quad.op == "FUNCTION":
                self.current_function = quad.arg1
            elif quad.op != "ENDFUNCTION" and quad.op != "FUNCTION":
                self.translate_quadruple(quad)

        self.emit("}")

        return self.instructions

    def translate_quadruple(self, quad: Quadruple):
        """翻譯四元組為 LLVM IR"""
        op = quad.op.upper()

        if op == "PARAM":
            pass  # 參數處理

        elif op == "=":
            src = self.get_value(quad.arg1)
            dest = self.get_or_create_var(quad.result)
            self.emit(f"  {dest} = add i32 0, {src}")

        elif op == "+":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = add i32 {v1}, {v2}")

        elif op == "-":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = sub i32 {v1}, {v2}")

        elif op == "*":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = mul i32 {v1}, {v2}")

        elif op == "/":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = sdiv i32 {v1}, {v2}")

        elif op == "<":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = icmp slt i32 {v1}, {v2}")

        elif op == ">":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = icmp sgt i32 {v1}, {v2}")

        elif op == "<=":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = icmp sle i32 {v1}, {v2}")

        elif op == ">=":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = icmp sge i32 {v1}, {v2}")

        elif op == "==":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = icmp eq i32 {v1}, {v2}")

        elif op == "!=":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = icmp ne i32 {v1}, {v2}")

        elif op == "AND":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = and i1 {v1}, {v2}")

        elif op == "OR":
            v1 = self.get_value(quad.arg1)
            v2 = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = or i1 {v1}, {v2}")

        elif op == "NOT":
            v1 = self.get_value(quad.arg1)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = xor i1 {v1}, true")

        elif op == "GOTO":
            self.emit(f"  br label %{quad.result}")

        elif op == "IFFALSE":
            v1 = self.get_value(quad.arg1)
            self.emit(f"  br i1 {v1}, label %{quad.result}, label %{quad.result}_else")

        elif op == "LABEL":
            self.emit(f"{quad.arg1}:")

        elif op == "CALL":
            func_name = quad.arg1
            result = quad.result
            if result:
                temp = self.new_temp()
                self.local_vars[result] = temp
                self.emit(f"  {temp} = call i32 @{func_name}()")

        elif op == "RETURN":
            if quad.arg1:
                v = self.get_value(quad.arg1)
                self.emit(f"  ret i32 {v}")
            else:
                self.emit(f"  ret i32 0")

        elif op == "GETARRAY":
            idx = self.get_value(quad.arg2)
            result = self.new_temp()
            self.local_vars[quad.result] = result
            self.emit(f"  {result} = getelementptr i32, i32* {quad.arg1}, i32 {idx}")

        elif op == "SETARRAY":
            idx = self.get_value(quad.arg2)
            val = self.get_value(quad.result)
            self.emit(f"  store i32 {val}, i32* {quad.arg1}")

        elif op == "END":
            self.emit("  ret i32 0")

    def new_temp(self) -> str:
        """生成臨時值"""
        temp = f"%t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def new_label(self) -> str:
        """生成標籤"""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def get_or_create_var(self, name: str) -> str:
        """獲取或創建變數"""
        if name not in self.local_vars:
            self.local_vars[name] = f"%{name}"
        return self.local_vars[name]

    def get_value(self, name: str) -> str:
        """獲取值"""
        # 數字常數
        if name.isdigit():
            return name

        # 區域變數
        if name in self.local_vars:
            return self.local_vars[name]

        # 臨時變數
        if name.startswith('t'):
            return f"%{name}"

        return f"%{name}"

    def emit(self, instruction: str):
        """發射指令"""
        self.instructions.append(instruction)

    def print_code(self):
        """打印 LLVM IR"""
        print("\n=== LLVM IR ===")
        for instr in self.instructions:
            print(instr)


def main():
    """測試 LLVM IR 生成"""
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

    codegen = LLVMIRGenerator()
    code = codegen.generate(quadruples)
    codegen.print_code()


if __name__ == "__main__":
    main()