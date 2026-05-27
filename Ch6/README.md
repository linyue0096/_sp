# 行程與檔案相關程式 - System Call 範例

## 環境
- 語言：C
- 編譯：`gcc <source.c> -o <output>`
- 執行於 Linux / WSL（Windows Subsystem for Linux）

## 檔案總覽

| 檔案 | System Call | 功能 |
|------|-------------|------|
| `fork_demo.c` | `fork()` | 建立子行程 |
| `execvp_demo.c` | `fork()` + `execvp()` | 子行程執行外部程式 |
| `open_demo.c` | `open()` | 開啟檔案（寫入 / 讀取） |
| `read_demo.c` | `read()` | 從檔案讀取資料 |
| `write_demo.c` | `write()` | 寫入 stdout、stderr、檔案 |
| `close_demo.c` | `close()` | 關閉檔案描述子 |
| `dup2_demo.c` | `dup2()` | 重新導向 stdout 到檔案 |
| `stdio_fd_demo.c` | `read()` / `write()` | 操作 stdin(0) stdout(1) stderr(2) |

---

## 1. fork_demo.c — fork()

```c
pid_t pid = fork();
```

### 說明
`fork()` 會複製當前行程，產生一個**子行程**（child process）。子行程會從同一行程繼續執行，唯一的區別是 `fork()` 的回傳值：
- **回傳 0** → 目前在子行程中
- **回傳 > 0** → 目前在父行程中，回傳值為子行程的 PID
- **回傳 -1** → 失敗

### 流程
```
父行程 PID=100
    │
    └── fork() ──┬── 子行程 PID=101（fork 回傳 0）
                  │
               父行程繼續（fork 回傳 101）
               呼叫 wait() 等待子行程結束
```

### 預期輸出
```
[Parent] I am the parent process. PID=100, Child PID=101
[Child]  I am the child process. PID=101, Parent PID=100
[Parent] Child process finished.
```

---

## 2. execvp_demo.c — execvp()

```c
int execvp(const char *file, char *const argv[]);
```

### 說明
`execvp()` 會用一個新的程式**完全取代**當前行程的程式碼、資料、堆疊。行程 PID 不變，但執行內容完全換掉。通常搭配 `fork()` 使用：
1. `fork()` 建立子行程
2. 子行程呼叫 `execvp()` 執行另一個程式
3. 父行程用 `wait()` 等待子行程結束

### 流程
```
父行程
    │
    └── fork() ──┬── 子行程
                  │       │
                  │    execvp("ls", ["ls", "-la", NULL])
                  │       │
                  │    行程被 ls 程式取代，執行 ls -la
                  │
               父行程 wait() 直到子行程結束
```

### 預期輸出
```
[Child] Calling execvp to run: ls -la
（ls -la 的輸出內容...）
[Parent] execvp completed in child.
```

---

## 3. open_demo.c — open()

```c
int open(const char *path, int flags, mode_t mode);
```

### 說明
`open()` 用來開啟或建立檔案，回傳一個**檔案描述子**（file descriptor, fd）。fd 是一個非負整數，之後的 `read()` / `write()` / `close()` 都用這個 fd 來操作。

### 參數說明
| 參數 | 意義 |
|------|------|
| `path` | 檔案路徑 |
| `flags` | `O_CREAT`（不存在就建立）、`O_WRONLY`（唯寫）、`O_RDONLY`（唯讀）、`O_TRUNC`（清空） |
| `mode` | 建立檔案時的權限，如 `0644`（rw-r--r--） |

### 程式流程
1. `open(path, O_CREAT | O_WRONLY | O_TRUNC, 0644)` → 建立/清空檔案，取得 fd
2. `write(fd, msg, len)` → 寫入字串
3. `close(fd)` → 關閉
4. `open(path, O_RDONLY)` → 重新以唯讀開啟
5. `read(fd, &ch, 1)` → 逐字元讀取並印出
6. `close(fd)` → 關閉

### 預期輸出
```
open() success: fd=3
open() for read success: fd=3
Hello from open_demo!
```

---

## 4. read_demo.c — read()

```c
ssize_t read(int fd, void *buf, size_t count);
```

### 說明
`read()` 從指定的 fd 讀取最多 `count` 個位元組到 `buf`。回傳值：
- **> 0** → 實際讀取到的位元組數
- **= 0** → 已讀到檔案結尾（EOF）
- **< 0** → 發生錯誤

### 程式流程
1. 建立一個檔案寫入 `ABCDEFGHIJKLMNOPQRSTUVWXYZ\n`
2. 以唯讀開啟，讀取 buffer 大小為 16 bytes
3. 因為 buffer 比檔案小，`read()` 會分多次讀取，每次回傳 16

### 預期輸出
```
read() from file:
ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

`read()` 被呼叫了 **2 次**：第一次讀 16 bytes，第二次讀 11 bytes（剩餘資料）。

---

## 5. write_demo.c — write()

```c
ssize_t write(int fd, const void *buf, size_t count);
```

### 說明
`write()` 將 `buf` 中的 `count` 個位元組寫入到 `fd` 所指向的檔案或裝置。回傳實際寫入的位元組數，負數表示錯誤。

### 示範三種目標
| 目標 | fd | 說明 |
|------|----|------|
| **stdout** | `STDOUT_FILENO` (1) | 寫到螢幕 |
| **stderr** | `STDERR_FILENO` (2) | 寫到錯誤輸出（即使 stdout 被導向仍會顯示） |
| **一般檔案** | `fd = open(...)` | 寫到磁碟檔案 |

### 預期輸出
```
write() to stdout (fd 1)
write() to stderr (fd 2)
wrote to file descriptor 3
```

注意：`stderr` 的輸出順序可能因 buffering 而不同，因為 `write()` 是 unbuffered I/O。

---

## 6. close_demo.c — close()

```c
int close(int fd);
```

### 說明
`close()` 關閉一個檔案描述子，釋放核心資源。關閉後的 fd 可以被後續的 `open()` 重用。

### 重要觀念
- 關閉後再對同一個 fd 進行 `read()` / `write()` 會回傳錯誤（`EBADF: Bad file descriptor`）
- 對已關閉的 fd 再次 `close()` 雖然不安全，但多數實作會忽略第二次呼叫

### 預期輸出
```
fd1=3, fd2=4
closed fd1 (3)
read from closed fd failed (expected): Bad file descriptor
closed fd2 (4)
```

---

## 7. dup2_demo.c — dup2()

```c
int dup2(int oldfd, int newfd);
```

### 說明
`dup2()` 將 `oldfd` 複製到 `newfd`，也就是讓 `newfd` 指向和 `oldfd` 相同的核心檔案表項目。若 `newfd` 原本是開啟的，會先被關閉。

### 搭配 stdout 重新導向
```c
int fd = open("file.txt", O_WRONLY);
dup2(fd, STDOUT_FILENO);   // 從此 printf / write(1, ...) 都寫入檔案
close(fd);
```

### 程式流程
1. `open()` 開啟一個檔案 → fd = 3
2. `dup2(fd, STDOUT_FILENO)` → stdout (1) 現在指向同一個檔案
3. `close(fd)` → 關閉原本的 fd，但因為 stdout 已經複製了指向，檔案仍然是開啟的
4. 之後所有的 `write(1, ...)` 和 `printf()` 都寫入檔案
5. `stderr` 不受影響，仍然輸出到終端機

### 預期輸出（終端機只看到 stderr）
```
（終端機上會顯示 stderr 的內容）
Before dup2: this goes to terminal
stderr (fd 2) still goes to terminal
```

而 `"stdout (fd 1) → file via dup2"` 和 `"dup2 redirected stdout..."` 則寫入檔案 `dup2_demo.txt`。

---

## 8. stdio_fd_demo.c — stdin (0), stdout (1), stderr (2)

```c
read(STDIN_FILENO, buf, size);    // fd = 0，讀取鍵盤輸入
write(STDOUT_FILENO, msg, len);   // fd = 1，輸出到螢幕
write(STDERR_FILENO, msg, len);   // fd = 2，輸出錯誤訊息
```

### 說明
程式啟動時，作業系統會自動開啟三個標準檔案描述子：

| 常數 | 數值 | 名稱 | 用途 |
|------|------|------|------|
| `STDIN_FILENO` | 0 | 標準輸入 | 讀取使用者鍵盤輸入或 pipe 資料 |
| `STDOUT_FILENO` | 1 | 標準輸出 | 輸出一般結果到螢幕 |
| `STDERR_FILENO` | 2 | 標準錯誤 | 輸出錯誤訊息，不受 `>` 導向影響 |

### 為何 stderr 和 stdout 要分開？
```bash
./program > output.txt   # stdout 導向檔案，stderr 仍在終端機
./program 2> error.txt   # stderr 導向檔案，stdout 仍在終端機
./program &> all.txt     # 兩者都導向檔案
```

### 程式流程
1. `write(STDOUT_FILENO, ...)` → 提示使用者輸入
2. `read(STDIN_FILENO, buf, ...)` → 讀取使用者輸入
3. `write(STDOUT_FILENO, ...)` → 顯示輸入內容
4. `write(STDERR_FILENO, ...)` → 顯示錯誤訊息

### 預期輸出（輸入 "Hello"）
```
stdin (fd 0): please type something and press Enter:
stdout (fd 1): you typed → Hello
stderr (fd 2): this is an error message
```

測試時可用 pipe 傳入輸入：
```bash
echo "Hello World" | ./stdio_fd_demo
```

---

## 編譯與執行（一鍵測試）

```bash
cd C:\yy\_sp\Ch6

gcc fork_demo.c -o fork_demo && ./fork_demo
gcc execvp_demo.c -o execvp_demo && ./execvp_demo
gcc open_demo.c -o open_demo && ./open_demo
gcc read_demo.c -o read_demo && ./read_demo
gcc write_demo.c -o write_demo && ./write_demo
gcc close_demo.c -o close_demo && ./close_demo
gcc dup2_demo.c -o dup2_demo && ./dup2_demo
gcc stdio_fd_demo.c -o stdio_fd_demo && echo "test" | ./stdio_fd_demo
```

---

## System Call 對照表

| 名稱 | 標頭檔 | 回傳值 | 原型 |
|------|--------|--------|------|
| fork | `<unistd.h>` | 子行程 PID (parent) / 0 (child) / -1 (error) | `pid_t fork(void)` |
| execvp | `<unistd.h>` | 成功不回傳，失敗回傳 -1 | `int execvp(const char *file, char *const argv[])` |
| open | `<fcntl.h>` | fd 編號 (≥0) / -1 (error) | `int open(const char *path, int flags, mode_t mode)` |
| read | `<unistd.h>` | 實際讀取位元組 / 0 (EOF) / -1 (error) | `ssize_t read(int fd, void *buf, size_t count)` |
| write | `<unistd.h>` | 實際寫入位元組 / -1 (error) | `ssize_t write(int fd, const void *buf, size_t count)` |
| close | `<unistd.h>` | 0 (success) / -1 (error) | `int close(int fd)` |
| dup2 | `<unistd.h>` | 新的 fd / -1 (error) | `int dup2(int oldfd, int newfd)` |

## 重點整理

1. **行程控制**：`fork()` 複製行程，`execvp()` 取代行程內容，兩者常配合實現「執行外部程式」
2. **檔案 I/O**：`open()` → `read()` / `write()` → `close()` 是基本的檔案操作流程
3. **檔案描述子**：0 (stdin)、1 (stdout)、2 (stderr) 是系統預設開啟的，編號 3 以後給一般檔案使用
4. **重新導向**：`dup2()` 可以複製 fd，實現 stdin/stdout 的重新導向
5. **錯誤處理**：所有 system call 回傳 -1 表示錯誤，可用 `perror()` 查看錯誤訊息
