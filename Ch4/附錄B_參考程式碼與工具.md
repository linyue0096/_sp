# 附錄B：參考程式碼與工具

## B.1 參考程式碼

### B.1.1 簡單組譯器實作（C語言）

以下是一個簡化的組譯器核心實作，展示詞彙分析、語法分析與目標碼生成的基本結構：

```c
// assembler.h - 組譯器核心資料結構

#ifndef ASSEMBLER_H
#define ASSEMBLER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    TOKEN_INSTRUCTION,  // 指令助記符
    TOKEN_LABEL,        // 標籤
    TOKEN_REGISTER,     // 暫存器
    TOKEN_NUMBER,       // 數字常數
    TOKEN_STRING,       // 字串常數
    TOKEN_DIRECTIVE,    // 偽指令
    TOKEN_REGISTER8,   // 8位元暫存器
    TOKEN_SEGMENT,     // 區段暫存器
    TOKEN_END           // 檔案結尾
} TokenType;

typedef struct {
    TokenType type;
    char value[64];
    int line;
    int column;
} Token;

typedef enum {
    OP_MOV, OP_ADD, OP_SUB, OP_MUL, OP_DIV,
    OP_AND, OP_OR, OP_XOR, OP_NOT,
    OP_JMP, OP_JE, OP_JNE, OP_JG, OP_JL,
    OP_CALL, OP_RET, OP_PUSH, OP_POP,
    OP_CMP, OP_TEST,
    OP_NONE
} Opcode;

typedef struct {
    Opcode op;
    char operands[3][64];  // 最多3個運算元
    int operandCount;
    int address;          // 指令位址
} Instruction;

typedef struct {
    char name[64];
    int address;
    int isDefined;
} Symbol;

typedef struct {
    Symbol *symbols;
    int symbolCount;
    int capacity;
} SymbolTable;

typedef struct {
    Instruction *instructions;
    int instructionCount;
    int capacity;
} InstructionList;

// 詞彙分析器
Token* lexer(const char *filename);
Token* createToken(TokenType type, const char *value, int line, int col);
void freeTokens(Token *head);

// 語法分析器
InstructionList* parse(Token *tokens);
int parseInstruction(Token *tokens, Instruction *ins);
char* parseOperand(Token *tokens, char *operand);

// 符號表管理
SymbolTable* createSymbolTable();
void addSymbol(SymbolTable *table, const char *name, int address);
int getSymbolAddress(SymbolTable *table, const char *name);
void freeSymbolTable(SymbolTable *table);

// 目標碼生成
void generateObjectFile(InstructionList *list, SymbolTable *table, const char *filename);
void emitInstruction(FILE *fp, Instruction *ins);
void emitSymbolTable(FILE *fp, SymbolTable *table);

// 主程式
int assemble(const char *inputFile, const char *outputFile);

#endif
```

```c
// assembler.c - 組譯器實作

#include "assembler.h"

#define MAX_LINE_LENGTH 256
#define INITIAL_CAPACITY 1024

// 指令助記符表
typedef struct {
    const char *mnemonic;
    Opcode opcode;
} MnemonicEntry;

static const MnemonicEntry mnemonics[] = {
    {"mov", OP_MOV}, {"add", OP_ADD}, {"sub", OP_SUB},
    {"mul", OP_MUL}, {"div", OP_DIV}, {"and", OP_AND},
    {"or", OP_OR}, {"xor", OP_XOR}, {"not", OP_NOT},
    {"jmp", OP_JMP}, {"je", OP_JE}, {"jne", OP_JNE},
    {"jg", OP_JG}, {"jl", OP_JL},
    {"call", OP_CALL}, {"ret", OP_RET},
    {"push", OP_PUSH}, {"pop", OP_POP},
    {"cmp", OP_CMP}, {"test", OP_TEST},
    {NULL, OP_NONE}
};

// 暫存器表
static const char* registers[] = {
    "ax", "bx", "cx", "dx", "si", "di", "bp", "sp",
    "al", "bl", "cl", "dl", "ah", "bh", "ch", "dh",
    NULL
};

Token* createToken(TokenType type, const char *value, int line, int col) {
    Token *token = (Token*)malloc(sizeof(Token));
    token->type = type;
    strncpy(token->value, value, 63);
    token->line = line;
    token->column = col;
    return token;
}

Token* lexer(const char *filename) {
    FILE *fp = fopen(filename, "r");
    if (!fp) {
        fprintf(stderr, "Cannot open file: %s\n", filename);
        return NULL;
    }
    
    Token *head = NULL, *tail = NULL;
    char line[MAX_LINE_LENGTH];
    int lineNum = 0;
    
    while (fgets(line, MAX_LINE_LENGTH, fp)) {
        lineNum++;
        char *ptr = line;
        
        // 跳過空白
        while (*ptr == ' ' || *ptr == '\t') ptr++;
        
        // 跳過註解
        if (*ptr == ';' || *ptr == '\n' || *ptr == '\0') continue;
        
        // 處理標籤
        char *colon = strchr(ptr, ':');
        if (colon && *(colon+1) != ':') {
            *colon = '\0';
            Token *label = createToken(TOKEN_LABEL, ptr, lineNum, 0);
            if (!head) head = tail = label;
            else { tail->next = label; tail = label; }
            ptr = colon + 1;
            while (*ptr == ' ' || *ptr == '\t') ptr++;
            if (*ptr == '\n' || *ptr == '\0') continue;
        }
        
        // 解析助記符
        char word[64];
        int i = 0;
        while ((*ptr >= 'a' && *ptr <= 'z') || 
               (*ptr >= 'A' && *ptr <= 'Z') ||
               (*ptr >= '0' && *ptr <= '9')) {
            word[i++] = *ptr++;
        }
        word[i] = '\0';
        
        // 檢查是否為指令
        Opcode op = OP_NONE;
        for (int j = 0; mnemonics[j].mnemonic; j++) {
            if (strcasecmp(word, mnemonics[j].mnemonic) == 0) {
                op = mnemonics[j].opcode;
                break;
            }
        }
        
        Token *token;
        if (op != OP_NONE) {
            token = createToken(TOKEN_INSTRUCTION, word, lineNum, 0);
        } else {
            // 可能為數字
            if (word[0] >= '0' && word[0] <= '9') {
                token = createToken(TOKEN_NUMBER, word, lineNum, 0);
            } else {
                token = createToken(TOKEN_LABEL, word, lineNum, 0);
            }
        }
        
        if (!head) head = tail = token;
        else { tail->next = token; tail = token; }
    }
    
    fclose(fp);
    return head;
}

SymbolTable* createSymbolTable() {
    SymbolTable *table = (SymbolTable*)malloc(sizeof(SymbolTable));
    table->capacity = 128;
    table->symbolCount = 0;
    table->symbols = (Symbol*)malloc(table->capacity * sizeof(Symbol));
    return table;
}

void addSymbol(SymbolTable *table, const char *name, int address) {
    if (table->symbolCount >= table->capacity) {
        table->capacity *= 2;
        table->symbols = (Symbol*)realloc(table->symbols, 
            table->capacity * sizeof(Symbol));
    }
    Symbol *sym = &table->symbols[table->symbolCount++];
    strncpy(sym->name, name, 63);
    sym->address = address;
    sym->isDefined = 1;
}

int getSymbolAddress(SymbolTable *table, const char *name) {
    for (int i = 0; i < table->symbolCount; i++) {
        if (strcmp(table->symbols[i].name, name) == 0) {
            return table->symbols[i].address;
        }
    }
    return -1;
}

void generateObjectFile(InstructionList *list, SymbolTable *table, 
                        const char *filename) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        fprintf(stderr, "Cannot create output file: %s\n", filename);
        return;
    }
    
    // 輸出指令數量
    fwrite(&list->instructionCount, sizeof(int), 1, fp);
    
    // 輸出指令
    for (int i = 0; i < list->instructionCount; i++) {
        Instruction *ins = &list->instructions[i];
        fwrite(&ins->op, sizeof(Opcode), 1, fp);
        fwrite(&ins->operandCount, sizeof(int), 1, fp);
        for (int j = 0; j < ins->operandCount; j++) {
            int len = strlen(ins->operands[j]) + 1;
            fwrite(&len, sizeof(int), 1, fp);
            fwrite(ins->operands[j], 1, len, fp);
        }
    }
    
    // 輸出符號表
    fwrite(&table->symbolCount, sizeof(int), 1, fp);
    for (int i = 0; i < table->symbolCount; i++) {
        Symbol *sym = &table->symbols[i];
        int len = strlen(sym->name) + 1;
        fwrite(&len, sizeof(int), 1, fp);
        fwrite(sym->name, 1, len, fp);
        fwrite(&sym->address, sizeof(int), 1, fp);
    }
    
    fclose(fp);
}

int assemble(const char *inputFile, const char *outputFile) {
    // 第一遍：詞彙分析
    Token *tokens = lexer(inputFile);
    if (!tokens) return -1;
    
    // 建立符號表
    SymbolTable *table = createSymbolTable();
    
    // 建立指令列表
    InstructionList *list = (InstructionList*)malloc(sizeof(InstructionList));
    list->capacity = INITIAL_CAPACITY;
    list->instructionCount = 0;
    list->instructions = (Instruction*)malloc(list->capacity * sizeof(Instruction));
    
    // 處理token（簡化版本）
    Token *t = tokens;
    int currentAddress = 0;
    
    while (t) {
        if (t->type == TOKEN_LABEL) {
            addSymbol(table, t->value, currentAddress);
        } else if (t->type == TOKEN_INSTRUCTION) {
            // 找到指令
            // 這裡需要更完整的解析邏輯
            currentAddress += 4; // 假設每條指令4位元組
        }
        t = t->next;
    }
    
    // 生成目標檔案
    generateObjectFile(list, table, outputFile);
    
    // 清理資源
    freeTokens(tokens);
    freeSymbolTable(table);
    free(list->instructions);
    free(list);
    
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: %s <input.asm> <output.o>\n", argv[0]);
        return 1;
    }
    
    return assemble(argv[1], argv[2]);
}
```

### B.1.2 簡單虛擬機器

```c
// virtual_machine.c - 簡單堆疊式虛擬機器

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define STACK_SIZE 1024
#define MEMORY_SIZE 65536

typedef struct {
    uint32_t sp;        // 堆疊指標
    uint32_t pc;        // 程式計數器
    uint32_t registers[8];
    uint8_t memory[MEMORY_SIZE];
    uint32_t stack[STACK_SIZE];
} VM;

void vm_init(VM *vm) {
    vm->sp = 0;
    vm->pc = 0;
    memset(vm->registers, 0, sizeof(vm->registers));
    memset(vm->memory, 0, sizeof(vm->memory));
}

void vm_push(VM *vm, uint32_t value) {
    if (vm->sp >= STACK_SIZE) {
        fprintf(stderr, "Stack overflow!\n");
        exit(1);
    }
    vm->stack[vm->sp++] = value;
}

uint32_t vm_pop(VM *vm) {
    if (vm->sp == 0) {
        fprintf(stderr, "Stack underflow!\n");
        exit(1);
    }
    return vm->stack[--vm->sp];
}

void vm_execute(VM *vm, uint8_t *code, int size) {
    while (vm->pc < size) {
        uint8_t opcode = code[vm->pc++];
        
        switch (opcode) {
            case 0x01: { // LOAD
                uint8_t r = code[vm->pc++];
                uint32_t addr = code[vm->pc++];
                vm->registers[r] = vm->memory[addr];
                break;
            }
            case 0x02: { // STORE
                uint8_t r = code[vm->pc++];
                uint32_t addr = code[vm->pc++];
                vm->memory[addr] = vm->registers[r];
                break;
            }
            case 0x03: { // PUSH
                uint32_t val;
                memcpy(&val, &code[vm->pc], 4);
                vm->pc += 4;
                vm_push(vm, val);
                break;
            }
            case 0x04: // POP
                vm_pop(vm);
                break;
            case 0x05: { // ADD
                uint32_t b = vm_pop(vm);
                uint32_t a = vm_pop(vm);
                vm_push(vm, a + b);
                break;
            }
            case 0x06: { // SUB
                uint32_t b = vm_pop(vm);
                uint32_t a = vm_pop(vm);
                vm_push(vm, a - b);
                break;
            }
            case 0x07: { // MUL
                uint32_t b = vm_pop(vm);
                uint32_t a = vm_pop(vm);
                vm_push(vm, a * b);
                break;
            }
            case 0x08: { // DIV
                uint32_t b = vm_pop(vm);
                uint32_t a = vm_pop(vm);
                vm_push(vm, a / b);
                break;
            }
            case 0x09: // HALT
                return;
            default:
                fprintf(stderr, "Unknown opcode: %02x\n", opcode);
                exit(1);
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <program.bin>\n", argv[0]);
        return 1;
    }
    
    FILE *fp = fopen(argv[1], "rb");
    if (!fp) {
        fprintf(stderr, "Cannot open file: %s\n", argv[1]);
        return 1;
    }
    
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    
    uint8_t *code = (uint8_t*)malloc(size);
    fread(code, 1, size, fp);
    fclose(fp);
    
    VM vm;
    vm_init(&vm);
    vm_execute(&vm, code, size);
    
    printf("Execution complete. Stack top: %u\n", vm.stack[vm.sp-1]);
    
    free(code);
    return 0;
}
```

## B.2 推薦工具

### B.2.1 組譯器工具

| 名稱 | 平台 | 說明 |
|------|------|------|
| **NASM** | Linux/Windows/Mac | 流行的x86/x64組譯器，支援多種輸出格式 |
| **MASM** | Windows | Microsoft Assembly，Windows開發標準 |
| **FASM** | Linux/Windows/Mac | 快且功能豐富的組譯器 |
| **GAS** | Linux/Unix | GNU Assembler，GCC內建 |
| **YASM** | Linux/Windows/Mac | NASM相容的組譯器，支援更多架構 |
| **ARM ARM** | 跨平台 | ARM架構組譯器，嵌入式開發常用 |

### B.2.2 反組譯與除錯工具

| 名稱 | 平台 | 說明 |
|------|------|------|
| **objdump** | Linux | GNU工具，可反組譯目標檔案 |
| **IDA Pro** | Windows/Linux | 專業級反組譯與分析工具 |
| **Ghidra** | 跨平台 | NSA開發的開源逆向工程框架 |
| **x64dbg** | Windows | 開源x64/x86除錯器 |
| **OllyDbg** | Windows | 32位元程式除錯器 |

### B.2.3 整合開發環境

| 名稱 | 平台 | 說明 |
|------|------|------|
| **Visual Studio** | Windows | 支援MASM整合開發 |
| **VS Code + ASM** | 跨平台 | 輕量編輯器配合組譯擴展 |
| **Eclipse + ASM** | 跨平台 | 使用ASMTools外掛 |

### B.2.4 線上資源

- **NASM Documentation**: https://www.nasm.us/doc/
- **Intel x86 Reference**: https://software.intel.com/security/vulnerability-guidance
- **ARM Developer Docs**: https://developer.arm.com/documentation
- **O'Reilly Assembly Language Books**: 經典學習資源

## B.3 練習專案建議

1. **實作簡單組譯器**：從支援基本指令開始，逐步擴展功能
2. **實作虛擬機器**：設計簡單的位元組碼格式並實作執行器
3. **最佳化分析工具**：分析組譯程式的效能瓶頸
4. **反向工程練習**：使用反組譯工具分析現有程式
5. **嵌入式系統專案**：開發ARM微控制器的開機程式