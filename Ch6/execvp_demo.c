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
        char *args[] = {"ls", "-la", NULL};
        printf("[Child] Calling execvp to run: ls -la\n");
        execvp("ls", args);
        perror("execvp failed");
        return 1;
    } else {
        wait(NULL);
        printf("[Parent] execvp completed in child.\n");
    }

    return 0;
}
