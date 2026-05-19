# SimpleLang 編程語言規格說明書

## 1. 語言概述

**語言名稱**: SimpleLang
**版本**: 1.0
**類型**: 強類型靜態編譯語言

---

## 2. EBNF 語法定義

### 2.1 程式結構

```ebnf
program         = { functionDefinition } ;

functionDefinition = "function" identifier "(" [ parameterList ] ")" ":" type block ;

parameterList   = identifier ":" type { "," identifier ":" type } ;

block           = "{" { statement } "}" ;

statement       = variableDeclaration
                | assignmentStatement
                | arrayAssignmentStatement
                | ifStatement
                | whileStatement
                | forStatement
                | returnStatement
                | functionCallStatement
                ;
```

### 2.2 類型系統

```ebnf
type            = "int" | "float" | "bool" | "string" | arrayType ;

arrayType       = type "[" [ number ] "]" ;

variableDeclaration = "var" identifier ":" type [ "=" expression ] ";" ;
```

### 2.3 表達式

```ebnf
expression      = logicalOrExpression ;

logicalOrExpression = logicalAndExpression { "or" logicalAndExpression } ;

logicalAndExpression = relationalExpression { "and" relationalExpression } ;

relationalExpression = additiveExpression [ ( "<" | ">" | "<=" | ">=" | "==" | "!=" ) additiveExpression ] ;

additiveExpression = multiplicativeExpression { ("+" | "-") multiplicativeExpression } ;

multiplicativeExpression = unaryExpression { ("*" | "/") unaryExpression } ;

unaryExpression  = [ ("-" | "not") ] primaryExpression ;

primaryExpression = identifier
                   | number
                   | stringLiteral
                   | booleanLiteral
                   | arrayLiteral
                   | "(" expression ")"
                   | functionCall
                   | arrayAccess
                   ;
```

### 2.4 語句

```ebnf
assignmentStatement = identifier "=" expression ";" ;

arrayAssignmentStatement = identifier "[" expression "]" "=" expression ";" ;

ifStatement      = "if" "(" expression ")" block [ "else" block ] ;

whileStatement    = "while" "(" expression ")" block ;

forStatement      = "for" "(" [ assignmentStatement ] ";" [ expression ] ";" [ assignmentStatement ] ")" block ;

returnStatement  = "return" [ expression ] ";" ;

functionCallStatement = functionCall ";" ;

functionCall     = identifier "(" [ argumentList ] ")" ;

argumentList     = expression { "," expression } ;

arrayAccess      = identifier "[" expression "]" ;
```

### 2.5 基礎元素

```ebnf
identifier      = letter { letter | digit | "_" } ;

number           = digit { digit } [ "." digit { digit } ] ;

stringLiteral    = '"' { anyCharacterExceptQuote } '"' ;

booleanLiteral   = "true" | "false" ;

arrayLiteral     = "[" [ expression { "," expression } ] "]" ;

letter           = "A".."Z" | "a".."z" ;

digit            = "0".."9" ;
```

---

## 3. BNF 等價表示

```bnf
<program> ::= <functionDefinition>*

<functionDefinition> ::= function <identifier> ( <parameterList> ) : <type> <block>

<parameterList> ::= <identifier> : <type> | <parameterList> , <identifier> : <type>

<block> ::= { <statement> }

<statement> ::= <variableDeclaration> | <assignmentStatement> | <ifStatement> | <whileStatement> | <forStatement> | <returnStatement>

<type> ::= int | float | bool | string | <type> [ <number> ]

<expression> ::= <logicalOrExpression>

<logicalOrExpression> ::= <logicalAndExpression> | <logicalOrExpression> or <logicalAndExpression>

<logicalAndExpression> ::= <relationalExpression> | <logicalAndExpression> and <relationalExpression>

<relationalExpression> ::= <additiveExpression> | <relationalExpression> <relationalOp> <additiveExpression>

<additiveExpression> ::= <multiplicativeExpression> | <additiveExpression> <addOp> <multiplicativeExpression>

<multiplicativeExpression> ::= <unaryExpression> | <multiplicativeExpression> <mulOp> <unaryExpression>

<unaryExpression> ::= <primaryExpression> | - <unaryExpression> | not <unaryExpression>

<primaryExpression> ::= <identifier> | <number> | <stringLiteral> | <booleanLiteral> | ( <expression> ) | <functionCall> | <arrayAccess>

<identifier> ::= <letter> | <identifier> <letter> | <identifier> <digit> | <identifier> _
```

---

## 4. 強形態與弱形態

### 4.1 強形態 (Strong Typing)

1. **靜態類型檢查**: 所有變數必須宣告類型，編譯時進行類型檢查
2. **類型安全**: 不允許隱式類型轉換，必須明確強制轉換
3. **記憶體安全**: 陣列邊界檢查，防止緩衝區溢位
4. **編譯時錯誤**: 大多數錯誤在編譯期檢測，而非執行期

### 4.2 弱形態 (Weak Typing)

1. **彈性陣列大小**: 允許動態陣列（不明確指定大小）
2. **函數過載**: 允許同名函數不同參數類型
3. **推斷類型**: 支援 `var` 關鍵字進行類型推斷

### 4.3 語言特性矩陣

| 特性 | 強形態 | 弱形態 |
|------|--------|--------|
| 變數類型宣告 | 必須 | 可選 |
| 隱式類型轉換 | 不允許 | 允許 |
| 陣列邊界檢查 | 必須 | 可選 |
| 空指標檢查 | 強制 | 可選 |
| 編譯期類型推斷 | 支援 | 支援 |

---

## 5. 範例程式

```simple
function main() : int {
    var x : int = 10
    var y : int = 20
    var arr : int[5]

    arr[0] = x + y

    if (x < y) {
        return x
    } else {
        return y
    }
}

function fib(n : int) : int {
    if (n <= 1) {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}
```

---

## 6. 運算子優先級

| 優先級 | 運算子 | 結合性 |
|--------|--------|--------|
| 1 (最高) | `()` `[]` | 左到右 |
| 2 | `-` (負號) `not` | 右到左 |
| 3 | `*` `/` | 左到右 |
| 4 | `+` `-` | 左到右 |
| 5 | `<` `>` `<=` `>=` | 左到右 |
| 6 | `==` `!=` | 左到右 |
| 7 | `and` | 左到右 |
| 8 (最低) | `or` | 左到右 |

---

## 7. 保留關鍵字

```
function, var, if, else, while, for, return,
int, float, bool, string,
true, false, and, or, not
```

---

## 8. 語言語法圖摘要

```
Program: functionDefinition*

Function: function ID(params) : type Block

Statement:
  - var ID : type [= expr] ;
  - ID = expr ;
  - if (expr) Block [else Block]
  - while (expr) Block
  - for (; expr; ) Block
  - return [expr] ;
```