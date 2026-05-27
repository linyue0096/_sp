#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

int main() {
    const char *msg = "stdout (fd 1) → file via dup2\n";

    int fd = open("/tmp/dup2_demo.txt", O_CREAT | O_WRONLY | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open failed");
        return 1;
    }

    printf("Before dup2: this goes to terminal\n");

    dup2(fd, STDOUT_FILENO);
    close(fd);

    printf("%s", msg);
    printf("dup2 redirected stdout (fd 1) to a file\n");

    fflush(stdout);
    close(STDOUT_FILENO);

    // stderr (fd 2) still goes to terminal
    write(STDERR_FILENO, "stderr (fd 2) still goes to terminal\n", 38);

    unlink("/tmp/dup2_demo.txt");
    return 0;
}
