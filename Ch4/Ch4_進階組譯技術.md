# 第四章 進階組譯技術

## 4.1 條件式組譯與巨集處理

### 條件組譯指令

條件式組譯允許程式碼根據特定條件進行選擇性組譯，這在開發不同平台版本或偵錯版本時特別有用。

```assembly
; 根據不同的目標平台進行條件組譯
IF PLATFORM = 'WINDOWS'
    MOV AX, 4Ch         ; Windows 系統呼叫
    INT 21h
ELSE IF PLATFORM = 'LINUX'
    MOV EAX, 1         ; Linux exit 系統呼叫
    INT 80h
ENDIF

; 根據偵錯模式進行條件組譯
IFDEF DEBUG
    ; 輸出偵錯資訊
    LEA DX, debugMsg
    MOV AH, 09h
    INT 21h
ENDIF
```

### 巨集定義與展開

巨集是組譯語言中的重要抽象機制，可以將重複的程式碼片段定義為可重複使用的單元：

```assembly
; 定義巨集
MACRO PUSH_REGS
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
ENDMACRO

MACRO POP_REGS
    POP DX
    POP CX
    POP BX
    POP AX
ENDMACRO

; 使用巨集
PUSH_REGS
; ... 主要程式碼 ...
POP_REGS
```

### 帶參數的巨集

進階巨集可以接受參數，使程式碼更加靈活：

```assembly
MACRO LOAD_REG reg, value
    MOV reg, value
ENDMACRO

; 呼叫巨集
LOAD_REG AX, 100
LOAD_REG BX, 200
```

## 4.2 多模組連結與符號解析

### 模組化程式設計

大型程式通常分割為多個原始檔案，分別組譯後再連結成單一執行檔：

```assembly
; === main.asm ===
EXTERN init_display   ; 宣告外部符號
EXTERN draw_pixel

global _start
_start:
    CALL init_display
    MOV CX, 100
loop:
    CALL draw_pixel
    LOOP loop
    RET

; === display.asm ===
public init_display
init_display:
    MOV AX, 13h
    INT 10h
    RET

public draw_pixel
draw_pixel:
    ; 繪製像素的程式碼
    RET
```

### 符號解析機制

連結器需要解析跨模組的符號引用：

1. **強符號與弱符號**：強符號優先於弱符號
2. **未定義符號**：需要在其他模組中查找定義
3. **多重定義**：需要處理符號重複定義的情況

### 區段與連結

不同模組的區段需要在連結階段合併：

```
模組A: .text, .data, .bss
模組B: .text, .data, .bss
                ↓ 連結
最終輸出: .text, .data, .bss (合併)
```

## 4.3 指令最佳化技術

### 常見最佳化策略

組譯器可以實施多種指令最佳化：

1. **指令序列簡化**：消除冗餘指令
   ```assembly
   ; 最佳化前
   MOV AX, 0
   ADD AX, BX
   
   ; 最佳化後
   MOV AX, BX
   ```

2. **定址模式優化**：使用更高效的定址方式
   ```assembly
   ; 最佳化前
   MOV AX, [BX]
   ADD AX, [BX+2]
   
   ; 最佳化後 (使用索引)
   LEA SI, [BX]
   LODSW
   ADD AX, [SI]
   ```

3. **跳躍目標最佳化**：縮短跳躍距離
   ```assembly
   ; 重新排列程式碼以縮短跳躍距離
   ```

### 指令排程

指令排程可以提高管線效率：

```assembly
; 避免管線停滯
; 最佳化前
MOV AX, [BX]
ADD CX, AX
MOV [DX], AX

; 最佳化後 - 插入無關指令填補延遲
MOV AX, [BX]
MOV SI, offset
ADD CX, AX
```

## 4.4 指令編碼與解碼

### 指令編碼格式

不同架構的指令編碼格式各異，以x86為例：

```
[前綴] [運碼] [ModR/M] [SIB] [位移] [立即值]
```

- **前綴**：可選的修飾前綴
- **運碼**：主要操作碼（1-3位元組）
- **ModR/M**：運算元指定
- **SIB**：縮放索引基底
- **位移**：記憶體位址偏移
- **立即值**：常數運算元

### 編碼範例

```c
// x86 指令編碼範例
uint8_t encode_mov_rm32_imm32(uint8_t modrm, uint32_t imm) {
    uint8_t opcode[] = {0xB8 + (modrm & 0x38) >> 3}; // MOV r32, imm32
    // ... 組合位元組序列
}
```

### 反組譯

反組譯是將機器碼轉換回組譯語言的過程：

```c
void disassemble(uint8_t *code, int length) {
    while (length > 0) {
        Instruction ins = decode_instruction(code);
        printf("%s ", ins.mnemonic);
        print_operands(&ins);
        printf("\n");
        code += ins.length;
        length -= ins.length;
    }
}
```

## 4.5 錯誤處理與偵錯資訊

### 錯誤類型

組譯過程中可能發生的錯誤包括：

1. **語法錯誤**：指令格式不正確
2. **語意錯誤**：操作數類型不符或位址無效
3. **符號錯誤**：未定義的符號或重複定義
4. **範圍錯誤**：數值超出有效範圍

### 錯誤報告機制

```c
void error(int line, int column, ErrorType type, char *message) {
    fprintf(stderr, "Error at line %d, column %d: %s\n", line, column, message);
    errorCount++;
}

void warning(int line, int column, char *message) {
    fprintf(stderr, "Warning at line %d, column %d: %s\n", line, column, message);
}
```

### 偵錯資訊產生

組譯器可以產生偵錯資訊供偵錯器使用：

```assembly
; 產生行號資訊
.line 10
    MOV AX, 10

; 產生區段資訊
.section .text,"x"
.debug_line
    ; 行號表
```

### DWARF 格式

現代Unix系統使用DWARF格式作為偵錯資訊標準：

- **CU（Compilation Unit）**：編譯單元資訊
- **.line**：行號資訊
- **.debug_info**：型別與範圍資訊
- **.debug_abbrev**：縮寫表