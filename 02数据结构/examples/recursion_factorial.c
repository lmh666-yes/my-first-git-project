/* 递归阶乘示例：点击 main 里调用 fact(4) 的每一行，右侧显示完整调用栈 */
#include <stdio.h>

int fact(int n) {
    if (n <= 1) return 1;
    return n * fact(n - 1);
}

int main() {
    int r = fact(4);
    return 0;
}
