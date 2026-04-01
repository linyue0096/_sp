# 第四章 進階組譯技術

## 4.1 巨集處理器

巨集處理器是組譯器的重要擴展功能，允許定義可重複使用的程式碼片段，提高程式碼的可維護性與可讀性。

### 巨集的定義與呼叫

```asm
; 巨集定義
%macro PRINT_STRING 1
    mov dx, %1
    mov ah, 09h
    int 21h
%endmacro

; 巨集呼叫
PRINT_STRING msg_buffer
```

### 巨集處理器架構

```python
class MacroProcessor:
    def __init__(self):
        self.macros = {}
        self.current_macro = None
        self.expansion_buffer = []
        
    def define_macro(self, name, params, body):
        self.macros[name] = {
            'params': params,
            'body': body,
            'local_labels': []
        }
        
    def expand_macro(self, name, args):
        if name not in self.macros:
            raise ValueError(f'Undefined macro: {name}')
            
        macro = self.macros[name]
        
        # 建立參數映射
        param_map = dict(zip(macro['params'], args))
        
        # 展開巨集主體
        expanded = []
        for line in macro['body']:
            expanded_line = line
            for param, value in param_map.items():
                expanded_line = expanded_line.replace(param, value)
            expanded.append(expanded_line)
            
        return expanded
```

### 巢狀巨集與遞迴巨集

```asm
; 巢狀巨集範例
%macro PUSH_REGS 0
    push ax
    push bx
    push cx
    push dx
%endmacro

%macro POP_REGS 0
    pop dx
    pop cx
    pop bx
    pop ax
%endmacro

%macro SAVE_CONTEXT 0
    PUSH_REGS
%endmacro

%macro RESTORE_CONTEXT 0
    POP_REGS
%endmacro
```

## 4.2 條件組譯

條件組譯允許根據特定條件選擇性地包含或排除程式碼區塊。

### 條件指示

```asm
%ifdef DEBUG
    mov dx, debug_msg
    mov ah, 09h
    int 21h
%endif

%ifndef RELEASE
    ; 開發專用程式碼
%endif

%if ARCH == 32
    ; 32位元特定程式碼
%elif ARCH == 64
    ; 64位元特定程式碼
%else
    ; 其他架構
%endif
```

### 條件組譯實作

```python
class ConditionalAssembler:
    def __init__(self):
        self.conditions = {
            'DEBUG': False,
            'RELEASE': True,
            'ARCH': 32
        }
        
    def process_conditional(self, lines):
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('%ifdef'):
                symbol = line.split()[1]
                self.process_ifdef(symbol, lines, i)
            elif line.startswith('%ifndef'):
                symbol = line.split()[1]
                self.process_ifndef(symbol, lines, i)
            elif line.startswith('%if'):
                condition = line[3:].strip()
                self.process_if(condition, lines, i)
            elif line.startswith('%endif'):
                pass
            else:
                result.append(line)
                
            i += 1
            
        return result
        
    def evaluate_condition(self, condition):
        # 簡化的條件表達式評估
        if '==' in condition:
            left, right = condition.split('==')
            return self.conditions.get(left.strip(), 0) == int(right.strip())
        elif '!=' in condition:
            left, right = condition.split('!=')
            return self.conditions.get(left.strip(), 0) != int(right.strip())
        return condition.strip() in self.conditions
```

## 4.3 段式記憶體管理

段（Section）是組織程式碼與資料的基本單位，不同的段具有不同的屬性與用途。

### 常見區段

```asm
section .data               ; 已初始化資料段
    message db "Hello$"
    number  dw 1234
    buffer  resb 256         ; 預留空間

section .bss                ; 未初始化資料段
    temp_buffer resb 64
    counter    resw 1

section .text                ; 程式碼段
    global _start
_start:
    mov ax, message
```

### 區段屬性

```asm
section .text progbits alloc exec nowrite

section .data write

section .bss nobits alloc nowrite
```

### 多段程式範例

```asm
section .data
    msg db "Enter number:", "$"
    result db "Result: $"

section .bss
    input_buffer resb 10
    output_buffer resb 20

section .text
    global main
main:
    mov dx, msg
    mov ah, 09h
    int 21h
    
    mov dx, input_buffer
    mov ah, 0Ah
    int 21h
    
    ; 處理輸入
    ; ...
    
    mov dx, result
    mov ah, 09h
    int 21h
```

## 4.4 連結器基礎

連結器（Linker）負責將多個目標檔案合併成單一可執行檔，並處理符號解析與位址重定位。

### 連結器的主要功能

1. **符號解析**：解析跨檔案的符號引用
2. **段合併**：合併相同類型的區段
3. **位址重定位**：調整相對位址
4. **符號綁定**：解析外部符號

### 連結腳本範例

```
INPUT(test.o library.o)
OUTPUT(test.elf)

SECTIONS
{
    .text 0x1000 : {
        *(.text)
    }
    
    .data 0x2000 : {
        *(.data)
    }
    
    .bss 0x3000 : {
        *(.bss)
    }
}
```

### 簡單連結器實作

```python
class Linker:
    def __init__(self):
        self.object_files = []
        self.sections = {}
        self.symbols = {}
        
    def add_object_file(self, obj_file):
        self.object_files.append(obj_file)
        
    def link(self, output_file):
        # 合併區段
        self.merge_sections()
        
        # 解析符號
        self.resolve_symbols()
        
        # 執行重定位
        self.relocate()
        
        # 寫出輸出檔案
        self.write_output(output_file)
        
    def merge_sections(self):
        base_address = 0x1000
        
        for obj in self.object_files:
            for section_name, section_data in obj.sections.items():
                if section_name not in self.sections:
                    self.sections[section_name] = bytearray()
                    
                offset = len(self.sections[section_name])
                self.sections[section_name].extend(section_data)
                
    def resolve_symbols(self):
        # 解析外部符號
        for obj in self.object_files:
            for symbol_name, symbol_ref in obj.unresolved_symbols.items():
                if symbol_name in self.symbols:
                    # 更新引用位址
                    pass
```

## 4.5 交叉組譯

交叉組譯（Cross-Assembly）是指在一种平台上产生另一种平台的可执行代码。

### 交叉組譯的用途

1. **嵌入式系統開發**：在PC上為嵌入式設備編譯
2. **作業系統開發**：為新架構編譯系統軟體
3. **測試與模擬**：在不同環境下測試程式

### 交叉組譯工具鏈

```bash
# ARM 交叉編譯
arm-none-eabi-as -o output.o input.s
arm-none-eabi-ld -o output.elf output.o
arm-none-eabi-objcopy -O binary output.elf output.bin

# MIPS 交叉編譯
mips-elf-as -o output.o input.s
mips-elf-ld -o output.elf output.o

# RISC-V 交叉編譯
riscv64-unknown-elf-as -o output.o input.s
riscv64-unknown-elf-ld -o output.elf output.o
```

### 目標碼格式轉換

```bash
# 從 ELF 提取二進位
objcopy -O binary input.elf output.bin

# 查看目標檔案內容
objdump -d input.o
objdump -h input.o

# 反組譯
objdump -d -M intel input.elf
```

### 目標檔案格式

```python
# ELF 檔案結構
class ELFFile:
    def __init__(self):
        self.header = {
            'e_ident': b'\x7fELF',
            'e_type': 2,           # ET_EXEC
            'e_machine': 0x3E,     # EM_X86_64
            'e_entry': 0x1000,
            'e_phoff': 64,
            'e_shoff': 0,
            'e_flags': 0,
            'e_ehsize': 64,
            'e_phentsize': 56,
            'e_phnum': 2,
        }
        self.program_headers = []
        self.sections = []
```