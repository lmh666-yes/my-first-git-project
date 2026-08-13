/* ============================================================
 *  verify_install.c — 库安装验证程序
 *  仅用于 install_my_lib.bat 部署后验证：
 *  在任意临时目录用 -lmylib 链接并运行，能成功就说明
 *  头文件和静态库都已正确安装到 MinGW。
 *  输出刻意用英文，避免旧版 cmd(GBK) 控制台中文乱码。
 * ============================================================ */
#include <stdio.h>
#include <utils.h>
#include <multifunc.h>

static int demo_func(void *arg) {
    (void)arg;
    printf("  [OK] multifunc step executed\n");
    return 0;
}

int main(void) {
    int a[3] = {3, 1, 2};
    bubble_sort(a, 3);
    printf("  [OK] utils bubble_sort: %d %d %d\n", a[0], a[1], a[2]);

    FuncStep steps[] = {{"demo", demo_func, 0, true}};
    MultiFuncExecutor *e = executor_create(steps, 1, true);
    if (!e) {
        printf("  [FAIL] executor_create returned NULL\n");
        return 1;
    }
    if (executor_run(e) != 0) {
        printf("  [FAIL] executor_run failed\n");
        executor_free(e);
        return 1;
    }
    executor_free(e);

    printf("\nInstall verification PASSED. Library usable from anywhere.\n");
    return 0;
}
