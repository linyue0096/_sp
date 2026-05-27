#include <unistd.h>
#include <string.h>

int main() {
    const char *prompt  = "stdin (fd 0): please type something and press Enter:\n";
    const char *out_msg = "stdout (fd 1): you typed → ";
    const char *err_msg = "stderr (fd 2): this is an error message\n";

    write(STDOUT_FILENO, prompt, strlen(prompt));

    char buf[128];
    ssize_t n = read(STDIN_FILENO, buf, sizeof(buf));

    if (n > 0) {
        write(STDOUT_FILENO, out_msg, strlen(out_msg));
        write(STDOUT_FILENO, buf, n);
    }

    write(STDERR_FILENO, err_msg, strlen(err_msg));

    return 0;
}
