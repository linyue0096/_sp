#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

int main() {
    const char *path = "/tmp/open_demo.txt";
    const char *msg = "Hello from open_demo!\n";

    // open for write (create if not exist, truncate if exist)
    int fd = open(path, O_CREAT | O_WRONLY | O_TRUNC, 0644);

    if (fd < 0) {
        perror("open for write failed");
        return 1;
    }

    printf("open() success: fd=%d\n", fd);
    write(fd, msg, strlen(msg));
    close(fd);

    // open for read
    fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("open for read failed");
        return 1;
    }

    printf("open() for read success: fd=%d\n", fd);

    char ch;
    while (read(fd, &ch, 1) > 0) putchar(ch);

    close(fd);
    unlink(path);
    return 0;
}
