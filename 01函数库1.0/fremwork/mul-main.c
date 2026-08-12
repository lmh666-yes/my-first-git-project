#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "multifunc.h"

// ===== 模拟的功能函数 =====

int init_sensor(void *arg) {
    printf("  初始化传感器...");
    return 0; // 成功
}

int config_uart(void *arg) {
    printf("  配置 UART ...");
    return 0; // 成功
}

int read_temp(void *arg) {
    printf("  读取温度传感器...");
    // 随机模拟成功/失败
    return (rand() % 3 == 0) ? -1 : 0;
}

int save_data(void *arg) {
    printf("  保存数据到Flash...");
    return 0;
}

int led_blink(void *arg) {
    printf("  LED 闪烁...");
    return 0;
}

// ===== 错误回调 =====
void on_step_error(int code) {
    printf("\n⚠️ 出现错误，执行终止。错误码: %d\n", code);
}

int main() {
    srand(time(NULL));

    // 1. 定义初始步骤
    FuncStep steps[] = {
        {"初始化传感器", init_sensor, NULL, true},
        {"配置 UART",    config_uart,  NULL, true},
        {"读取温度",     read_temp,    NULL, false},  // 非必须步骤
        {"保存数据",     save_data,    NULL, true},
        {"LED 闪烁",     led_blink,    NULL, true},
    };

    // 2. 创建执行器（遇到必须步骤失败则停止）
    MultiFuncExecutor *exec = executor_create(steps, 5, true);
    executor_set_error_callback(exec, on_step_error);

    // 3. 也可以动态添加步骤
    executor_add_step(exec, "额外校验", read_temp, NULL, false);

    // 4. 执行所有步骤
    int result = executor_run(exec);

    // 5. 打印结果
    printf("\n最终结果: %s\n", result == 0 ? "所有必须步骤成功" : "执行中断");

    // 6. 释放资源
    executor_free(exec);

    return 0;
}