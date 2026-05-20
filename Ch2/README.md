# SimpleLang 編譯器

SimpleLang 是一款簡易程式語言編譯器，支援生成四元組中間碼、堆疊機、暫存器機及 LLVM IR 四種目標碼。

---

## 第一章 簡介

### 1.1 什麼是 SimpleLang
SimpleLang 是一款**強類型靜態編譯語言**，支援變數、函數、陣列、條件判斷與迴圈。

**開發背景**：本編譯器是基於課程設計需求，以 C 語言版本編譯器為基礎，改用 Python 重寫，並擴充支援多種目標碼輸出格式。

### 1.2 編譯器架構流程
```
原始碼 → 詞法分析(Lexer) → 語法分析(Parser) → 語義分析(Semantic) → 中間碼(IR) → 目標碼(CodeGen)
```

### 1.3 支援的目標碼
| 類型 | 說明 |
|------|------|
| 四元組 (Quadruple) | (op, arg1, arg2, result) 格式的中間表示 |
| 堆疊機 (Stack Machine) | 虛擬機位元組碼，基於堆疊操作 |
| 暫存器機 (Register Machine) | 三地址碼，基於暫存器分配 |
| LLVM IR | LLVM 中間表示，可進一步編譯為機器碼 |

---

## 第二章 安裝與使用

### 2.1 環境需求
- Python 3.8 以上
- 無需安裝額外依賴

### 2.2 安裝方式
```bash
cd Ch2
pip install -e .
```

### 2.3 編譯程式
```bash
python3 -m simple_lang.compiler <原始碼檔案> -o <輸出目錄>
```

### 2.4 執行範例
```bash
# 編譯測試程式
python3 -m simple_lang.compiler examples/test1.simple -o examples/output

# 查看輸出
cat examples/output/quadruples.txt
cat examples/output/llvm_ir.ll
```

---

## 第三章 語法規則 (EBNF/BNF)

### 3.1 程式結構
```ebnf
program         = { functionDefinition } ;
functionDefinition = "function" identifier "(" [ parameterList ] ")" ":" type block ;
parameterList   = identifier ":" type { "," identifier ":" type } ;
block           = "{" { statement } "}" ;
```

### 3.2 類型系統
```ebnf
type            = "int" | "float" | "bool" | "string" | arrayType ;
arrayType       = type "[" [ number ] "]" ;
variableDeclaration = "var" identifier ":" type [ "=" expression ] ";" ;
```

### 3.3 表達式與運算子
```ebnf
expression      = logicalOrExpression ;
logicalOrExpression = logicalAndExpression { "or" logicalAndExpression } ;
logicalAndExpression = relationalExpression { "and" relationalExpression } ;
relationalExpression = additiveExpression [ ( "<" | ">" | "<=" | ">=" | "==" | "!=" ) additiveExpression ] ;
additiveExpression = multiplicativeExpression { ("+" | "-") multiplicativeExpression } ;
multiplicativeExpression = unaryExpression { ("*" | "/") unaryExpression } ;
unaryExpression  = [ ("-" | "not") ] primaryExpression ;
```

### 3.4 強形態與弱形態特性

| 特性 | 強形態 | 弱形態 |
|------|--------|--------|
| 變數類型宣告 | 必須 (var x : int) | 可選 (支援推斷) |
| 隱式類型轉換 | 不允許 | 允許 |
| 陣列邊界檢查 | 必須 | 可選 |
| 編譯期類型推斷 | 支援 | 支援 |

**本編譯器採用強形態設計**：所有變數必須宣告類型，不允許隱式轉換，確保型別安全。

### 3.5 保留關鍵字
```
function, var, if, else, while, for, return,
int, float, bool, string, true, false, and, or, not
```

---

## 第四章 語言語法範例

### 4.1 變數宣告與賦值
```simple
var x : int = 10;
var y : int = 20;
var name : string = "hello";
```

### 4.2 函數定義
```simple
function add(a : int, b : int) : int {
    return a + b;
}

function fib(n : int) : int {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}
```

### 4.3 條件判斷
```simple
if (x < y) {
    return x;
} else {
    return y;
}
```

### 4.4 迴圈結構
```simple
// while 迴圈
while (i < 10) {
    i = i + 1;
}

// for 迴圈
for (j = 0; j < 5; j = j + 1) {
    sum = sum + j;
}
```

### 4.5 運算子優先級
| 優先級 | 運算子 | 結合性 |
|--------|--------|--------|
| 1 (最高) | `()` `[]` | 左到右 |
| 2 | `-` `not` | 右到左 |
| 3 | `*` `/` | 左到右 |
| 4 | `+` `-` | 左到右 |
| 5 | `<` `>` `<=` `>=` | 左到右 |
| 6 | `==` `!=` | 左到右 |
| 7 | `and` | 左到右 |
| 8 (最低) | `or` | 左到右 |

---

## 第五章 輸出檔案說明

### 5.1 四元組 (quadruples.txt)
**格式**：(op, arg1, arg2, result)

```
OP           ARG1            ARG2            RESULT
------------------------------------------------------------
FUNCTION     main
=            10                              x
+            x               y               t0
RETURN       t0
ENDFUNCTION  main
```

**用途**：中間表示，用於最佳化與目標碼生成。

### 5.2 堆疊機 (stack_machine.asm)
**指令集**：PUSH, POP, ADD, SUB, MUL, DIV, LOAD, STORE, JUMP, JUMPF, CALL, RET, HALT

```asm
FUNCTION main
PUSH 10
STORE x
POP R0
ADD R0, R1
JUMPF L0
RETURN
HALT
```

**特色**：基於堆疊操作，無需暫存器分配。

### 5.3 暫存器機 (register_machine.asm)
**指令集**：LI, MOVE, ADD, SUB, MUL, DIV, SLT, SEQ, J, BEQ, CALL, RET, HALT

```asm
# Function: main
LI R0, 10
MOVE R1, R0
SLT R4, R1, R3
BEQ R4, R0, L0
RET
HALT
```

**特色**：三地址碼格式，基於暫存器分配策略。

### 5.4 LLVM IR (llvm_ir.ll)
```llvm
; SimpleLang -> LLVM IR
define i32 @main() {
  %x = add i32 0, 10
  %y = add i32 0, 20
  %t0 = icmp slt i32 %x, %y
  br i1 %t0, label %L0, label %L0_else
  ret i32 %x
}
```

**用途**：可透過 LLVM 工具鏈編譯為原生機器碼。

### 5.5 專案目錄結構
```
Ch2/
├── simple_lang/           # 編譯器核心模組
│   ├── __init__.py
│   ├── lexer.py           # 詞法分析器
│   ├── parser.py          # 語法分析器 (建構AST)
│   ├── semantic.py        # 語義分析器 (類型檢查)
│   ├── ir.py              # 中間碼生成器 (四元組)
│   ├── compiler.py        # 主編譯器
│   └── codegen/           # 目標碼生成
│       ├── stack_machine.py    # 堆疊機代碼
│       ├── register_machine.py # 暫存器機代碼
│       └── llvm_ir.py          # LLVM IR生成
├── examples/              # 範例程式
│   ├── test1.simple       # 測試輸入
│   └── output/           # 編譯輸出
├── docs/                 # 語法規格文件
│   └── SIMPLELANG_SPEC.md
├── setup.py             # 安裝配置
└── README.md            # 說明文件
```

---

## 附加資訊

### 授權
MIT License

### 作者
SimpleLang Compiler Team

### 參考資料
- 基於 C 語言版本編譯器延伸
- EBNF/BNF 語法規格參照
- LLVM IR 格式標準