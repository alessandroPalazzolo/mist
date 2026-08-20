#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    char buffer[16];
    char input[100];

    fgets(input, sizeof(input), stdin);

    if (strlen(input) > 15) {
        strcpy(buffer, input);
    }

    printf("You entered: %s\n", buffer);
    return 0;
}
