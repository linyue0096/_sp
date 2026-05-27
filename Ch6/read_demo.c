#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>

int main() {
    const char *path = "/tmp/read_demo.txt";

    int fd = open(path, O_CREAT | O_WRONLY | O_TRUNC, 0644);
    write(fd, "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n", 27);
    close(fd);

    fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("open failed");
        return 1;
    }

    char buf[16];
    ssize_t n;

    printf("read() from file:\n");
    while ((n = read(fd, buf, sizeof(buf))) > 0) {
        write(STDOUT_FILENO, buf, n);
    }

    close(fd);
    unlink(path);
    return 0;
}
