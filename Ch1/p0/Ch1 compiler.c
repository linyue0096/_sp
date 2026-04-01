#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// ==========================================
// 1. 定義 Token 種類
// ==========================================
typedef enum {
    TK_WHILE, TK_ID, TK_NUM, TK_ASSIGN, TK_LT, TK_PLUS,
    TK_LPAREN, TK_RPAREN, TK_LBRACE, TK_RBRACE, TK_EOF
} TokenType;

typedef struct {
    TokenType type;
    int value;         // 用於儲存數字
    char name[32];     // 用於儲存變數名稱
} Token;

const char* src;
Token current_token;

// ==========================================
// 2. 定義 AST (抽象語法樹) 節點
// ==========================================
typedef enum {
    AST_WHILE, AST_ASSIGN, AST_BINOP_LT, AST_BINOP_PLUS,
    AST_VAR, AST_NUM, AST_BLOCK
} ASTNodeType;

typedef struct ASTNode {
    ASTNodeType type;
    int value;                  // 用於 AST_NUM
    char name[32];              // 用於 AST_VAR
    struct ASTNode *left;       // 左子節點 (用於二元運算、賦值)
    struct ASTNode *right;      // 右子節點
    struct ASTNode *cond;       // 條件節點 (用於 while)
    struct ASTNode *body;       // 主體節點 (用於 while)
    struct ASTNode *next;       // 鏈結下一個陳述句 (用於 Block)
} ASTNode;

ASTNode* create_node(ASTNodeType type) {
    ASTNode* node = (ASTNode*)malloc(sizeof(ASTNode));
    memset(node, 0, sizeof(ASTNode));
    node->type = type;
    return node;
}

// ==========================================
// 3. 詞法分析器 (Lexer)
// ==========================================
void next_token() {
    while (isspace(*src)) src++;

    if (*src == '\0') {
        current_token.type = TK_EOF;
        return;
    }

    if (strncmp(src, "while", 5) == 0 && !isalnum(src[5])) {
        current_token.type = TK_WHILE;
        src += 5;
    } else if (isalpha(*src)) {
        int i = 0;
        while (isalnum(*src)) current_token.name[i++] = *src++;
        current_token.name[i] = '\0';
        current_token.type = TK_ID;
    } else if (isdigit(*src)) {
        int val = 0;
        while (isdigit(*src)) val = val * 10 + (*src++ - '0');
        current_token.value = val;
        current_token.type = TK_NUM;
    } else if (*src == '=') { current_token.type = TK_ASSIGN; src++; }
      else if (*src == '<') { current_token.type = TK_LT; src++; }
      else if (*src == '+') { current_token.type = TK_PLUS; src++; }
      else if (*src == '(') { current_token.type = TK_LPAREN; src++; }
      else if (*src == ')') { current_token.type = TK_RPAREN; src++; }
      else if (*src == '{') { current_token.type = TK_LBRACE; src++; }
      else if (*src == '}') { current_token.type = TK_RBRACE; src++; }
      else {
        printf("Lexer Error: Unknown char '%c'\n", *src);
        exit(1);
    }
}

void match(TokenType expected) {
    if (current_token.type == expected) next_token();
    else { printf("Syntax Error!\n"); exit(1); }
}

// ==========================================
// 4. 語法分析器 (Parser) -> 建立 AST
// ==========================================
ASTNode* parse_expression() {
    ASTNode* left = create_node(0);
    // 簡單解析變數或數字
    if (current_token.type == TK_ID) {
        left->type = AST_VAR;
        strcpy(left->name, current_token.name);
        match(TK_ID);
    } else if (current_token.type == TK_NUM) {
        left->type = AST_NUM;
        left->value = current_token.value;
        match(TK_NUM);
    }

    // 處理運算符號 (< 或 +)
    if (current_token.type == TK_LT || current_token.type == TK_PLUS) {
        ASTNode* op_node = create_node(current_token.type == TK_LT ? AST_BINOP_LT : AST_BINOP_PLUS);
        match(current_token.type);
        ASTNode* right = parse_expression(); // 遞迴解析右邊
        op_node->left = left;
        op_node->right = right;
        return op_node;
    }
    return left;
}

ASTNode* parse_statement() {
    if (current_token.type == TK_WHILE) {
        ASTNode* node = create_node(AST_WHILE);
        match(TK_WHILE);
        match(TK_LPAREN);
        node->cond = parse_expression();
        match(TK_RPAREN);
        
        match(TK_LBRACE);
        ASTNode* head = NULL;
        ASTNode* tail = NULL;
        // 解析區塊內的多個陳述句
        while (current_token.type != TK_RBRACE && current_token.type != TK_EOF) {
            ASTNode* stmt = parse_statement();
            if (!head) head = tail = stmt;
            else { tail->next = stmt; tail = stmt; }
        }
        match(TK_RBRACE);
        
        node->body = create_node(AST_BLOCK);
        node->body->next = head; // 將陳述句串接在 block 之下
        return node;
    } else if (current_token.type == TK_ID) {
        // 處理賦值: id = expression
        ASTNode* node = create_node(AST_ASSIGN);
        ASTNode* var_node = create_node(AST_VAR);
        strcpy(var_node->name, current_token.name);
        node->left = var_node;
        
        match(TK_ID);
        match(TK_ASSIGN);
        node->right = parse_expression();
        return node;
    }
    return NULL;
}

// ==========================================
// 5. 程式碼生成器 (Code Generator) -> 走訪 AST
// ==========================================
int label_counter = 0;
int new_label() { return label_counter++; }

void generate_code(ASTNode* node) {
    if (!node) return;

    switch (node->type) {
        case AST_NUM:
            printf("  PUSH %d\n", node->value);
            break;
        case AST_VAR:
            printf("  LOAD %s\n", node->name);
            break;
        case AST_BINOP_PLUS:
            generate_code(node->left);
            generate_code(node->right);
            printf("  ADD\n");
            break;
        case AST_BINOP_LT:
            generate_code(node->left);
            generate_code(node->right);
            printf("  CMP_LT\n");
            break;
        case AST_ASSIGN:
            generate_code(node->right); // 先計算右邊的值
            printf("  STORE %s\n", node->left->name); // 存入左邊的變數
            break;
        case AST_BLOCK:
            {
                ASTNode* curr = node->next;
                while (curr) { generate_code(curr); curr = curr->next; }
            }
            break;
        case AST_WHILE:
            {
                int l_start = new_label();
                int l_end = new_label();
                
                printf("L%d:\n", l_start);
                generate_code(node->cond);      // 生成條件計算的程式碼
                printf("  JUMP_IF_FALSE L%d\n", l_end);
                
                generate_code(node->body);      // 生成迴圈主體的程式碼
                
                printf("  JUMP L%d\n", l_start);
                printf("L%d:\n", l_end);
            }
            break;
    }
}

// ==========================================
// 6. 主程式
// ==========================================
int main() {
    // 測試用的真實邏輯程式碼
    src = "while (i < 10) { i = i + 1 }";
    
    printf("原始碼:\n%s\n", src);
    printf("\n編譯產生的堆疊機指令 (Stack Machine Assembly):\n");
    printf("----------------------------------\n");

    next_token();
    
    // 1. 產生 AST
    ASTNode* root = parse_statement();
    
    // 2. 走訪 AST 並產生程式碼
    generate_code(root);

    printf("----------------------------------\n");
    return 0;
}