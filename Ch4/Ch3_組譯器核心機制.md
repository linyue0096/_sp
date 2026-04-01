# 第三章 組譯器核心機制

## 3.1 詞彙分析器設計

詞彙分析器（Lexer）是組譯器的第一個處理階段，負責將原始程式碼轉換為一連串的詞彙單元（Token）。詞彙分析器的主要任務包括：

### 詞彙單元類型

組譯語言中的詞彙單元可分為以下類別：

1. **指令助記符**：如 `MOV`、`ADD`、`JMP` 等操作碼
2. **標籤**：用於標示程式位置的符號
3. **暫存器名稱**：如 `AX`、`BX`、`R0`、`R1` 等
4. **常數**：包括數值常數與字串常數
5. **偽指令**：如 `DB`、`DW`、`EQU`、`ORG` 等
6. **分隔符號**：如逗號、括號、冒號等

### 詞彙分析演算法

詞彙分析器通常採用有限狀態機（Finite State Machine）來識別各類型的詞彙單元：

```c
typedef enum {
    TOKEN_INSTRUCTION,
    TOKEN_LABEL,
    TOKEN_REGISTER,
    TOKEN_NUMBER,
    TOKEN_STRING,
    TOKEN_DIRECTIVE,
    TOKEN_SEPARATOR
} TokenType;

typedef struct {
    TokenType type;
    char value[256];
    int line;
    int column;
} Token;
```

### 狀態轉移圖

詞彙分析器透過狀態轉移來識別不同的詞彙單元：
- 初始狀態 → 識別空白與註解
- 識別字母開頭 → 可能為指令或標籤
- 識別數字開頭 → 可能為常數
- 識別特殊符號 → 為分隔符號或運算子

## 3.2 語法分析器設計

語法分析器（Parser）負責驗證詞彙單元序列是否符合組譯語言的語法規則，並建立語法樹（Syntax Tree）來表示程式的結構。

### 語法規則定義

組譯語言的語法通常以上下文無關文法（Context-Free Grammar）來描述：

```
instruction ::= label? opcode operands?
operands    ::= operand (',' operand)*
operand     ::= register | immediate | memory | label
memory      ::= '[' address ']'
address     ::= register ('+' number)? | number
```

### 語法分析方法

常用的語法分析方法包括：

1. **遞迴下降分析法**：適用於簡單的語法結構
2. **LR分析法**：適用於較複雜的語法結構
3. **LL(k)分析法**：從左到右、最左推導

### 語法樹結構

語法樹的節點類型包括：

```c
typedef enum {
    NODE_INSTRUCTION,
    NODE_LABEL,
    NODE_OPERAND,
    NODE_EXPRESSION
} NodeType;

typedef struct ASTNode {
    NodeType type;
    char *value;
    struct ASTNode **children;
    int childCount;
} ASTNode;
```

## 3.3 符號表管理

符號表（Symbol Table）是組譯器用於管理程式碼中所有符號的資料結構，包括標籤、巨集定義、與常數等。

### 符號表結構

符號表通常以雜湊表（Hash Table）實現，以提供高效的查詢效能：

```c
typedef struct Symbol {
    char *name;
    SymbolType type;          // 標籤、常數、巨集等
    Address value;           // 位址或數值
    int scope;               // 作用域層級
    struct Symbol *next;     // 衝突鏈結
} Symbol;

typedef struct SymbolTable {
    Symbol **buckets;
    int size;
    struct SymbolTable *parent;  // 父作用域
} SymbolTable;
```

### 符號類型

符號表中的符號可分為多種類型：

1. **標籤（Label）**：代表程式碼或資料的位址
2. **常數（Constant）**：使用 `EQU` 或 `SET` 定義的常數
3. **巨集（Macro）**：巨集定義的名稱
4. **外部符號（External Symbol）**：用於跨模組引用

### 作用域管理

組譯器需要支援區域與全域作用域：

```c
void enterScope(SymbolTable *table) {
    SymbolTable *newScope = createSymbolTable();
    newScope->parent = table;
    currentScope = newScope;
}

void exitScope(SymbolTable *table) {
    currentScope = table->parent;
}
```

## 3.4 位址解析與重定位

位址解析（Address Resolution）是將符號參照轉換為實際位址的過程，而重定位（Relocation）則是調整位址以適應不同的載入位置。

### 相對位址與絕對位址

組譯器需要處理兩種類型的位址：

1. **絕對位址**：固定的記憶體位置
2. **相對位址**：相對於目前位置的偏移量

### 重定位表

目標檔案中包含重定位資訊，供連結器使用：

```c
typedef struct RelocationEntry {
    char *symbol;         // 需要重定位的符號
    int offset;           // 在目標碼中的偏移量
    RelocationType type;  // 重定位類型
} RelocationEntry;
```

### 位址計算

位址解析的過程包括：

1. **計算標籤位址**：根據標籤出現的位置計算其位址
2. **計算相對位址**：計算跳躍指令的相對偏移量
3. **處理外部參照**：解析跨模組的符號引用

## 3.5 產生目標檔案

目標檔案（Object File）是組譯器的輸出，包含可被連結器處理的機器碼與相關資訊。

### 常見目標檔案格式

1. **COFF（Common Object File Format）**：Windows 環境常用
2. **ELF（Executable and Linkable Format）**：Unix/Linux 環境標準
3. **Mach-O**：macOS 環境使用

### 目標檔案結構

目標檔案通常包含以下區段：

```
+------------------+
|  檔案頭部         |
+------------------+
|  區段表          |
+------------------+
|  .text 區段      |  (程式碼)
+------------------+
|  .data 區段      |  (已初始化資料)
+------------------+
|  .bss 區段       |  (未初始化資料)
+------------------+
|  符號表          |
+------------------+
|  重定位表        |
+------------------+
```

### 輸出目標碼

產生目標碼的過程：

```c
void emitInstruction(FILE *output, Instruction *ins) {
    // 將助記符轉換為機器碼
    uint32_t machineCode = encodeInstruction(ins);
    fwrite(&machineCode, sizeof(uint32_t), 1, output);
}

void emitRelocation(FILE *output, Symbol *sym, int offset) {
    RelocationEntry rel = {
        .symbol = sym->name,
        .offset = offset,
        .type = REL_ABSOLUTE
    };
    fwrite(&rel, sizeof(RelocationEntry), 1, output);
}
```