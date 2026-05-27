#include <stdio.h>
#include <pthread.h>

int balance = 0;

void *add(void *arg) {
    for (int i = 0; i < 100000; i++)
        balance++;
    return NULL;
}

void *sub(void *arg) {
    for (int i = 0; i < 100000; i++)
        balance--;
    return NULL;
}

int main() {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, add, NULL);
    pthread_create(&t2, NULL, sub, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("Final balance (no mutex): %d\n", balance);
    return 0;
}
