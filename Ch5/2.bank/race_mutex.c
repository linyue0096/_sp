#include <stdio.h>
#include <pthread.h>

int balance = 0;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

void *add(void *arg) {
    for (int i = 0; i < 100000; i++) {
        pthread_mutex_lock(&lock);
        balance++;
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

void *sub(void *arg) {
    for (int i = 0; i < 100000; i++) {
        pthread_mutex_lock(&lock);
        balance--;
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, add, NULL);
    pthread_create(&t2, NULL, sub, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("Final balance (with mutex): %d\n", balance);
    return 0;
}
