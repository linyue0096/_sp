#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_SIZE 5
#define TOTAL_ITEMS 20

int buffer[BUFFER_SIZE];
int count = 0, in = 0, out = 0;

pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t not_full = PTHREAD_COND_INITIALIZER;
pthread_cond_t not_empty = PTHREAD_COND_INITIALIZER;

void *producer(void *arg) {
    for (int i = 1; i <= TOTAL_ITEMS; i++) {
        pthread_mutex_lock(&lock);

        while (count == BUFFER_SIZE)
            pthread_cond_wait(&not_full, &lock);

        buffer[in] = i;
        printf("Produced: %d at slot %d\n", i, in);
        in = (in + 1) % BUFFER_SIZE;
        count++;

        pthread_cond_signal(&not_empty);
        pthread_mutex_unlock(&lock);

        usleep(50000);
    }
    return NULL;
}

void *consumer(void *arg) {
    for (int i = 0; i < TOTAL_ITEMS; i++) {
        pthread_mutex_lock(&lock);

        while (count == 0)
            pthread_cond_wait(&not_empty, &lock);

        int val = buffer[out];
        printf("Consumed: %d from slot %d\n", val, out);
        out = (out + 1) % BUFFER_SIZE;
        count--;

        pthread_cond_signal(&not_full);
        pthread_mutex_unlock(&lock);

        usleep(100000);
    }
    return NULL;
}

int main() {
    pthread_t prod, cons;
    pthread_create(&prod, NULL, producer, NULL);
    pthread_create(&cons, NULL, consumer, NULL);
    pthread_join(prod, NULL);
    pthread_join(cons, NULL);
    return 0;
}
