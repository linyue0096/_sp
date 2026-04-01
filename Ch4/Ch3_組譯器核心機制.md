# 第三章 組譯器核心機制

## 3.1 兩遍掃描架構

組譯器通常採用兩遍掃描（Two-Pass）架構來處理組譯語言程式，這是因為組譯語言中可能存在向前參考（Forward Reference）的問題。

### 第一遍（Pass 1）

主要任務：
1. 識別所有標籤並建立符號表
2. 計算每個指令的位址
3. 處理巨集定義
4. 記錄段定義與屬性

```
第一遍掃描流程：
  初始化位址計數器
  迴圈：
    讀取下一行
    如果是指令：
      更新位址計數器
    如果是標籤：
      將標籤與目前位址存入符號表
    如果是巨集定義：
      暫存巨集定義
  直到檔案結束
```

### 第二遍（Pass 2）

主要任務：
1. 翻譯指令為機器碼
2. 解析符號引用
3. 產生目標檔案
4. 處理錯誤

```
第二遍掃描流程：
  初始化位址計數器
  迴圈：
    讀取下一行
    如果是指令：
      查詢符號表取得運算元位址
      產生機器碼
      更新位址計數器
  直到檔案結束
```

## 3.2 詞法分析

詞法分析器（Lexer）是組譯器的第一個元件，負責將輸入的文字流切割成記號（Token）。

### 記號類型

1. **標籤（Label）**：識別符號後接冒號
2. **指令（Instruction）**：操作碼助記符
3. **運算元（Operand）**：暫存器、立即值、位址
4. **指示（Directive）**：以句點開頭的控制指令
5. **註解（Comment）**：分號後的文字

### 詞法分析器範例

```python
import re

class Lexer:
    TOKEN_PATTERNS = [
        (r'^[a-zA-Z_][a-zA-Z0-9_]*:', 'LABEL'),
        (r'^(mov|add|sub|mul|div|jmp|je|jne|call|ret|push|pop)$', 'INSTRUCTION'),
        (r'^(db|dw|dd|dq|section|global|extern)$', 'DIRECTIVE'),
        (r'^(ax|bx|cx|dx|si|di|bp|sp|ah|al|bh|bl|ch|cl|dh|dl)$', 'REGISTER'),
        (r'^0x[0-9a-fA-F]+', 'IMMEDIATE_HEX'),
        (r'^[0-9]+', 'IMMEDIATE_DEC'),
        (r'^;.*', 'COMMENT'),
        (r'^\s+', 'WHITESPACE'),
    ]
    
    def tokenize(self, source):
        tokens = []
        lines = source.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.split(';')[0].strip()
            if not line:
                continue
                
            pos = 0
            while pos < len(line):
                matched = False
                
                for pattern, token_type in self.TOKEN_PATTERNS:
                    match = re.match(pattern, line[pos:])
                    if match:
                        value = match.group(0)
                        if token_type not in ('WHITESPACE', 'COMMENT'):
                            tokens.append({
                                'type': token_type,
                                'value': value,
                                'line': line_num
                            })
                        pos += len(value)
                        matched = True
                        break
                        
                if not matched:
                    raise SyntaxError(f'Unknown token at line {line_num}: {line[pos]}')
                    
        return tokens
```

## 3.3 符號表管理

符號表是組譯器的核心資料結構，用於儲存所有標籤與其相關資訊。

### 符號表結構

```python
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.current_section = None
        self.location_counter = 0
        
    def add_symbol(self, name, address, section, symbol_type='label'):
        self.symbols[name] = {
            'address': address,
            'section': section,
            'type': symbol_type,
            'defined': True
        }
        
    def add_forward_ref(self, name, section, line):
        if name not in self.symbols:
            self.symbols[name] = {
                'section': section,
                'type': 'unknown',
                'defined': False,
                'references': [line]
            }
        else:
            if 'references' not in self.symbols[name]:
                self.symbols[name]['references'] = []
            self.symbols[name]['references'].append(line)
            
    def resolve_symbol(self, name):
        if name in self.symbols:
            return self.symbols[name]['address']
        return None
    
    def is_defined(self, name):
        return name in self.symbols and self.symbols[name].get('defined', False)
```

### 符號表操作

1. **新增符號**：建立新的標籤項目
2. **查詢符號**：取得位址或屬性
3. **更新符號**：修正位址或屬性
4. **刪除符號**：移除未使用的項目

## 3.4 指令翻譯與目標碼生成

### 指令編碼基本原則

1. **操作碼映射**：將助記符號轉換為二進位操作碼
2. **運算元編碼**：處理不同類型的運算元
3. **位址模式**：處理各種位址指定方式

### 指令編碼表（簡化示例）

```python
OPCODES = {
    'mov': {
        ('reg8', 'imm8'): 0xB0,    # mov reg8, imm8
        ('reg16', 'imm16'): 0xB8,  # mov reg16, imm16
        ('mem', 'reg8'): 0x88,     # mov [mem], reg8
        ('reg8', 'mem'): 0x8A,     # mov reg8, [mem]
        ('reg16', 'reg16'): 0x89,  # mov reg16, reg16
    },
    'add': {
        ('reg8', 'imm8'): 0x00,
        ('reg16', 'imm16'): 0x01,
        ('reg16', 'reg16'): 0x01,
    },
    'jmp': {
        ('label'): 0xE9,           # near jump
        ('label8'): 0xEB,          # short jump
    }
}

REGISTER_CODES = {
    'al': 0, 'cl': 1, 'dl': 2, 'bl': 3,
    'ah': 4, 'ch': 5, 'dh': 6, 'bh': 7,
    'ax': 0, 'cx': 1, 'dx': 2, 'bx': 3,
    'sp': 4, 'bp': 5, 'si': 6, 'di': 7,
}
```

### 目標碼生成器

```python
class CodeGenerator:
    def __init__(self):
        self.opcodes = OPCODES
        self.reg_codes = REGISTER_CODES
        self.output = bytearray()
        
    def encode_instruction(self, instruction, operands, symbol_table):
        opcode = instruction.lower()
        
        if opcode == 'mov':
            return self.encode_mov(operands, symbol_table)
        elif opcode == 'add':
            return self.encode_add(operands, symbol_table)
        elif opcode == 'jmp':
            return self.encode_jmp(operands, symbol_table)
        else:
            raise ValueError(f'Unknown instruction: {instruction}')
            
    def encode_mov(self, operands, symbol_table):
        dest, src = operands
        result = bytearray()
        
        # 判斷運算元類型並編碼
        if dest in self.reg_codes and src in self.reg_codes:
            result.append(0x89)  # modrm
            modrm = 0xC0 | (self.reg_codes[dest] << 3) | self.reg_codes[src]
            result.append(modrm)
        elif dest in self.reg_codes and isinstance(src, int):
            result.append(0xB0 + self.reg_codes[dest])
            result.append(src & 0xFF)
            
        return result
```

## 3.5 位址解析

### 位址類型

1. **絕對位址**：實際記憶體位置
2. **相對位址**：相對於目前位置的位移
3. **間接位址**：位址指向的內容
4. **基底相對位址**：基底暫存器加上位移

### 位址解析方法

```python
class AddressResolver:
    def __init__(self, symbol_table, base_address=0):
        self.symbol_table = symbol_table
        self.base_address = base_address
        
    def resolve(self, operand, current_address):
        if isinstance(operand, int):
            return operand
            
        if operand in self.symbol_table:
            symbol = self.symbol_table[operand]
            return symbol['address']
            
        # 處理相對位址
        if isinstance(operand, dict) and operand.get('type') == 'rel':
            target = operand['target']
            if target in self.symbol_table:
                target_addr = self.symbol_table[target]['address']
                return target_addr - current_address - 2  # 相對位移
                
        raise ValueError(f'Cannot resolve address: {operand}')
        
    def calculate_relative_address(self, target, current):
        if target in self.symbol_table:
            return self.symbol_table[target]['address'] - current
        return None
```

### 重定位資訊

```python
class RelocationEntry:
    def __init__(self, offset, section, symbol, addend=0):
        self.offset = offset
        self.section = section
        self.symbol = symbol
        self.addend = addend
        
    def to_dict(self):
        return {
            'offset': self.offset,
            'section': self.section,
            'symbol': self.symbol,
            'addend': self.addend
        }
```