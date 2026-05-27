#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>

int main() {
    const char *path = "/tmp/close_demo.txt";

    // open twice to show two fd numbers
    int fd1 = open(path, O_CREAT | O_RDONLY, 0644);
    int fd2 = open(path, O_RDONLY);

    printf("fd1=%d, fd2=%d\n", fd1, fd2);

    close(fd1);
    printf("closed fd1 (%d)\n", fd1);

    // reading from a closed fd returns error
    char buf[8];
    if (read(fd1, buf, sizeof(buf)) < 0)
        perror("read from closed fd failed (expected)");

    close(fd2);
    printf("closed fd2 (%d)\n", fd2);

    // close again on same fd is undefined but usually harmless
    close(fd2);

    unlink(path);
    return 0;
}
