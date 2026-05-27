#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

#define N 5

pthread_mutex_t chopsticks[N];
int eating_count[N];

void think(int id) {
    printf("Philosopher %d is thinking...\n", id);
    usleep(100000);
}

void eat(int id) {
    printf("Philosopher %d is eating! 🍝\n", id);
    eating_count[id]++;
    usleep(100000);
}

void *philosopher(void *arg) {
    int id = *(int *)arg;
    int left = id;
    int right = (id + 1) % N;

    for (int i = 0; i < 5; i++) {
        think(id);

        if (id % 2 == 0) {
            pthread_mutex_lock(&chopsticks[left]);
            pthread_mutex_lock(&chopsticks[right]);
        } else {
            pthread_mutex_lock(&chopsticks[right]);
            pthread_mutex_lock(&chopsticks[left]);
        }

        eat(id);

        pthread_mutex_unlock(&chopsticks[left]);
        pthread_mutex_unlock(&chopsticks[right]);
    }
    return NULL;
}

int main() {
    pthread_t philosophers[N];
    int ids[N];

    for (int i = 0; i < N; i++) {
        pthread_mutex_init(&chopsticks[i], NULL);
        eating_count[i] = 0;
    }

    for (int i = 0; i < N; i++) {
        ids[i] = i;
        pthread_create(&philosophers[i], NULL, philosopher, &ids[i]);
    }

    for (int i = 0; i < N; i++)
        pthread_join(philosophers[i], NULL);

    printf("\n=== Eating summary ===\n");
    for (int i = 0; i < N; i++)
        printf("Philosopher %d ate %d times\n", i, eating_count[i]);

    return 0;
}
