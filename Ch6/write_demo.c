#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

int main() {
    const char *msg1 = "write() to stdout (fd 1)\n";
    const char *msg2 = "write() to stderr (fd 2)\n";

    write(STDOUT_FILENO, msg1, strlen(msg1));
    write(STDERR_FILENO, msg2, strlen(msg2));

    const char *path = "/tmp/write_demo.txt";
    int fd = open(path, O_CREAT | O_WRONLY | O_TRUNC, 0644);

    if (fd < 0) {
        perror("open failed");
        return 1;
    }

    const char *msg3 = "write() to a file (fd 3)\n";
    write(fd, msg3, strlen(msg3));
    printf("wrote to file descriptor %d\n", fd);

    close(fd);
    unlink(path);
    return 0;
}
