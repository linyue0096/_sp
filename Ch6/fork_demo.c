#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork();

    if (pid < 0) {
        perror("fork failed");
        return 1;
    }

    if (pid == 0) {
        printf("[Child]  I am the child process. PID=%d, Parent PID=%d\n",
               getpid(), getppid());
    } else {
        printf("[Parent] I am the parent process. PID=%d, Child PID=%d\n",
               getpid(), pid);
        wait(NULL);
        printf("[Parent] Child process finished.\n");
    }

    return 0;
}
