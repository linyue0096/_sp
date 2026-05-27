# Ch5 — 多執行緒程式設計 (POSIX Threads)

## 目錄結構

```
C:\yy\_sp\Ch5\
│
├── 1.text                    Thread、Race Condition、Mutex、Deadlock 生活類比說明
│
├── 1\
│   ├── demo.c                四階段因果鏈展示（Thread→Race→Mutex→Deadlock）
│   └── demo.exe
│
├── 2.bank\race.c             無鎖版本銀行存提款（展示 Race Condition）
│   ├── race_mutex.c          有鎖版本（Mutex 解決 Race Condition）
│   ├── race.exe
│   └── race_mutex.exe
│
├── 3.coustom\pc.c            生產者消費者（Producer-Consumer）附 Condition Variable
│   └── pc.exe
│
├── 4.philosopher\philosopher.c  哲學家晚餐（Deadlock 預防策略）
│   └── philosopher.exe
│
└── readme.md
```

---

## 四個核心概念的因果關係

```
Thread → Race Condition → Mutex → Deadlock
```

### 1. Thread（執行緒）
多個執行緒共用同一塊記憶體，可同時執行任務。

- **程式對應**：`race.c` 中 `pthread_create` 建立兩個 thread 同時讀寫 `balance`
- **生活類比**：廚房裡多位廚師共用同一冰箱、瓦斯爐

### 2. Race Condition（競爭條件）
多個 thread 同時讀寫共用變數。`balance++` 在 CPU 底層拆成三步驟（讀取 → 計算 → 寫回），交錯執行導致結果不確定。

- **程式對應**：執行 `race.exe`，每次 `balance` 結果都不同
- **生活類比**：兩人同時更新同一本記帳本

### 3. Mutex（互斥鎖）
`pthread_mutex_lock/unlock` 保護臨界區段，確保一次僅一個 thread 操作共用變數。

- **程式對應**：`race_mutex.exe`，`balance` 永遠是正確的 0
- **生活類比**：廁所門鎖 — 進去鎖門，出來開鎖

### 4. Deadlock（死結）
鎖的拿取順序不當形成循環等待。

- **程式對應**：`demo.exe` — 兩位哲學家各拿一根筷子互等
- **生活類比**：狹窄走廊兩人互不相讓

---

## 三大經典同步題目

### 題目一：銀行存提款 — Race Condition + Mutex

**程式**：`2.bank/race.c`、`2.bank/race_mutex.c`

模擬銀行帳戶，兩個 Thread 分別執行 100,000 次存款（+1）與提款（-1）。

```
無鎖版本 (race.c)：      每次結果不同（如 -83711、58340…），因為 ++/-- 非原子操作
有鎖版本 (race_mutex.c)： 用 pthread_mutex_lock/unlock 保護，最終餘額永遠是 0
```

### 題目二：生產者消費者 — Condition Variable

**程式**：`3.coustom/pc.c`

- 環形 Buffer（容量 5 格）
- **Producer**：放入資料，滿了等 `not_full`
- **Consumer**：取出資料，空了等 `not_empty`
- 使用 `pthread_cond_t` 讓 thread 在條件不滿足時睡眠、滿足時喚醒

```
Producer: 放入 1~20
Consumer: 取出 1~20
Buffer 滿 → Producer 等待 not_full
Buffer 空 → Consumer 等待 not_empty
```

### 題目三：哲學家晚餐 — Deadlock 預防

**程式**：`4.philosopher/philosopher.c`

- 5 位哲學家（Thread）圍桌
- 5 根筷子（Mutex），每人需兩根才能吃飯
- 全部先拿左筷 → Deadlock

**預防策略（破壞循環等待）**：

```
偶數哲學家（0,2,4）：先左筷 → 再右筷
奇數哲學家（1,3）：  先右筷 → 再左筷
```

拿筷順序不同，不會形成循環等待，Deadlock 解除。

---

## 編譯方式

```bash
gcc 2.bank/race.c -o 2.bank/race -pthread
gcc 2.bank/race_mutex.c -o 2.bank/race_mutex -pthread
gcc 1/demo.c -o 1/demo -pthread
gcc 3.coustom/pc.c -o 3.coustom/pc -pthread
gcc 4.philosopher/philosopher.c -o 4.philosopher/philosopher -pthread
```

---

## 程式碼實作細節

### 1. `race.c` — Race Condition 展示

兩個 thread 對共用變數 `balance` 分別執行 10 萬次 `++` 和 `--`。
`balance++` 在 CPU 層級是「讀取→加 1→寫回」三步驟，非原子操作。
當兩個 thread 交錯執行時，發生**遺失更新 (lost update)**：

```
Thread A 讀到 balance=100 → (被中斷)
Thread B 讀到 balance=100 → +1 → 寫回 101 → (被中斷)
Thread A 做 +1 (仍用舊值 100) → 寫回 101
```

兩次操作但 balance 只增加 1，結果不正確。

**關鍵函式**：`pthread_create()` 建立執行緒，`pthread_join()` 等待結束。

---

### 2. `race_mutex.c` — Mutex 解決方案

用 `pthread_mutex_lock` / `unlock` 把 `balance++` / `balance--` 包成**臨界區段 (critical section)**。同一時間只有一個 thread 能持有鎖，確保「讀取→計算→寫回」不被中斷。

靜態初始化鎖：
```c
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
```

進入前 `lock`，退出後 `unlock`。

---

### 3. `demo.c` — 四階段因果鏈展示

單一程式用四個階段完整展示概念鏈：

| 階段 | 主題 | 實作方式 |
|---|---|---|
| 一 + 二 | Thread → Race Condition | `demo_race_condition()` — 無鎖，跑 5 次秀每次不同結果 |
| 三 | Mutex 解決 Race | `demo_mutex()` — 有鎖，跑 3 次秀每次結果都是 0 |
| 四 | Deadlock | `demo_deadlock()` — 兩哲學家各拿一根筷子後 `usleep`，接著互等對方另一根，形成循環等待，程式卡死 |

Deadlock 成因：Philosopher A 拿 chopstick_A → 等 chopstick_B；Philosopher B 拿 chopstick_B → 等 chopstick_A。

```c
// 兩人各拿一根筷子後 sleep，醒來互等對方那根 → Deadlock
void *philosopher_a(void *arg) {
    pthread_mutex_lock(&chopstick_a);  // 拿到左筷
    usleep(10000);                     // 讓 B 有時間拿右筷
    pthread_mutex_lock(&chopstick_b);  // 等 B 放右筷 → 永遠等不到
    ...
}
void *philosopher_b(void *arg) {
    pthread_mutex_lock(&chopstick_b);  // 拿到右筷
    usleep(10000);
    pthread_mutex_lock(&chopstick_a);  // 等 A 放左筷 → 永遠等不到
    ...
}
```

---

### 4. `pc.c` — 生產者消費者 (Producer-Consumer)

使用 **Mutex + Condition Variable**，解決「Buffer 滿/空時如何等待與喚醒」：

- **環形 Buffer**：`buffer[5]`，`in` 寫入位置，`out` 讀出位置，`count` 記錄數量
- **Producer**：`count == BUFFER_SIZE` 時 `pthread_cond_wait(&not_full, &lock)` 睡眠；放入後 `pthread_cond_signal(&not_empty)` 喚醒 Consumer
- **Consumer**：`count == 0` 時 `pthread_cond_wait(&not_empty, &lock)` 睡眠；取出後 `pthread_cond_signal(&not_full)` 喚醒 Producer

**為何用 `while` 而非 `if`**：`pthread_cond_wait` 可能發生**虛假喚醒 (spurious wakeup)**，回圈重新檢查條件才安全。

```c
// Producer 核心邏輯
pthread_mutex_lock(&lock);
while (count == BUFFER_SIZE)
    pthread_cond_wait(&not_full, &lock);  // 滿了 → 睡眠
buffer[in] = i;                           // 放入資料
in = (in + 1) % BUFFER_SIZE;
count++;
pthread_cond_signal(&not_empty);          // 通知 Consumer
pthread_mutex_unlock(&lock);
```

```c
// Consumer 核心邏輯
pthread_mutex_lock(&lock);
while (count == 0)
    pthread_cond_wait(&not_empty, &lock); // 空了 → 睡眠
int val = buffer[out];                    // 取出資料
out = (out + 1) % BUFFER_SIZE;
count--;
pthread_cond_signal(&not_full);           // 通知 Producer
pthread_mutex_unlock(&lock);
```

---

### 5. `philosopher.c` — 哲學家晚餐 (Dining Philosophers)

解決 Deadlock 的**不對稱資源取得策略**，破壞「循環等待」條件：

```c
if (id % 2 == 0) {           // 偶數：先左後右
    pthread_mutex_lock(&chopsticks[left]);
    pthread_mutex_lock(&chopsticks[right]);
} else {                     // 奇數：先右後左
    pthread_mutex_lock(&chopsticks[right]);
    pthread_mutex_lock(&chopsticks[left]);
}
```

確保不會形成 5 人全拿一根筷子等另一根的循環。同時記錄每位哲學家吃飯次數，結束時印出統計。

---

### 總結對照表

| 程式 | 核心機制 | 關鍵 API | 展示概念 |
|---|---|---|---|
| `race.c` | 無鎖 | `pthread_create` / `join` | Race Condition |
| `race_mutex.c` | Mutex | `pthread_mutex_lock` / `unlock` | 互斥鎖解決 Race |
| `demo.c` | 全部 | 上述全部 + `usleep` | Thread→Race→Mutex→Deadlock |
| `pc.c` | Mutex + CondVar | `pthread_cond_wait` / `signal` | 生產者消費者 |
| `philosopher.c` | 不對稱鎖順序 | `pthread_mutex_init` / `lock` / `unlock` | Deadlock 預防 |
