#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

/* ================================================================
 * 這支程式用四個階段展示 Thread → Race Condition → Mutex → Deadlock
 * 的因果關係鏈。
 * ================================================================ */

/* ---- 共用資源 ---- */
int balance = 0;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

/********** 階段一 + 二：Thread → Race Condition **********/

void *add_race(void *arg) {
    for (int i = 0; i < 100000; i++)
        balance++;  /* 三步驟：讀取→加一→寫回，非原子操作 */
    return NULL;
}

void *sub_race(void *arg) {
    for (int i = 0; i < 100000; i++)
        balance--;  /* 三步驟：讀取→減一→寫回，非原子操作 */
    return NULL;
}

void demo_race_condition() {
    balance = 0;
    pthread_t t1, t2;
    pthread_create(&t1, NULL, add_race, NULL);
    pthread_create(&t2, NULL, sub_race, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("  balance = %d  (期望 0，但每次結果不同)\n", balance);
}

/********** 階段三：引入 Mutex 解決 Race Condition **********/

void *add_mutex(void *arg) {
    for (int i = 0; i < 100000; i++) {
        pthread_mutex_lock(&lock);
        balance++;          /* 鎖保護：讀取→加一→寫回，一氣呵成 */
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

void *sub_mutex(void *arg) {
    for (int i = 0; i < 100000; i++) {
        pthread_mutex_lock(&lock);
        balance--;          /* 鎖保護：讀取→減一→寫回，一氣呵成 */
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

void demo_mutex() {
    balance = 0;
    pthread_t t1, t2;
    pthread_create(&t1, NULL, add_mutex, NULL);
    pthread_create(&t2, NULL, sub_mutex, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("  balance = %d  (每次都是正確的 0)\n", balance);
}

/********** 階段四：鎖設計不良 → Deadlock **********/

pthread_mutex_t chopstick_a = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t chopstick_b = PTHREAD_MUTEX_INITIALIZER;

void *philosopher_a(void *arg) {
    printf("  Philosopher A: 拿起左筷...\n");
    pthread_mutex_lock(&chopstick_a);
    usleep(10000);
    printf("  Philosopher A: 等待右筷...\n");
    pthread_mutex_lock(&chopstick_b);   /* 等 B 放下右筷，但 B 也在等 A */
    printf("  Philosopher A: 吃到飯了！\n");
    pthread_mutex_unlock(&chopstick_b);
    pthread_mutex_unlock(&chopstick_a);
    return NULL;
}

void *philosopher_b(void *arg) {
    printf("  Philosopher B: 拿起右筷...\n");
    pthread_mutex_lock(&chopstick_b);
    usleep(10000);
    printf("  Philosopher B: 等待左筷...\n");
    pthread_mutex_lock(&chopstick_a);   /* 等 A 放下左筷，但 A 也在等 B */
    printf("  Philosopher B: 吃到飯了！\n");
    pthread_mutex_unlock(&chopstick_a);
    pthread_mutex_unlock(&chopstick_b);
    return NULL;
}

void demo_deadlock() {
    pthread_t a, b;
    printf("\n  [建立兩個哲學家，各拿一根筷子後互等]\n");
    pthread_create(&a, NULL, philosopher_a, NULL);
    pthread_create(&b, NULL, philosopher_b, NULL);
    pthread_join(a, NULL);
    pthread_join(b, NULL);
    printf("  (這行永遠不會被执行，因為 Deadlock 卡死了)\n");
}

/********** Main **********/

int main() {
    printf("========================================\n");
    printf("  Thread → Race Condition → Mutex → Deadlock\n");
    printf("========================================\n\n");

    setbuf(stdout, NULL);

    /* 階段一 + 二：Thread + Race Condition */
    printf("【階段一 + 二】多個 Thread 導致 Race Condition\n");
    printf("  兩個 Thread 同時對 balance 做 100000 次 +1/-1\n");
    printf("  (沒有 Mutex 保護)\n");
    for (int i = 0; i < 5; i++) {
        printf("  第 %d 次：", i + 1);
        demo_race_condition();
    }
    printf("  → 餘額亂跳，因為 ++/-- 不是原子操作\n\n");

    /* 階段三：Mutex 解決 Race Condition */
    printf("【階段三】引入 Mutex 保護臨界區段\n");
    printf("  用鎖包住 balance 的讀取→計算→寫回\n");
    for (int i = 0; i < 3; i++) {
        printf("  第 %d 次：", i + 1);
        demo_mutex();
    }
    printf("  → 結果永遠正確，Race Condition 解決\n\n");

    /* 階段四：Deadlock */
    printf("【階段四】鎖設計不良 → Deadlock\n");
    printf("  兩位哲學家各拿一根筷子，互相等待對方放下\n");
    printf("  程式將在此卡死，不會印出接下來的訊息\n");
    demo_deadlock();

    /* 這行永遠不會被執行 */
    printf("\n  程式正常結束。\n");
    return 0;
}
