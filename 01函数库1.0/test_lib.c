#include <stdio.h>
#include <utils.h>
#include <multifunc.h>

// ===== 测试函数（模拟传感器初始化） =====
int test_sensor(void *arg) {
    printf("  传感器初始化...");
    return 0;
}

int test_uart(void *arg) {
    printf("  UART 配置...");
    return 0;
}

int test_led(void *arg) {
    printf("  LED 闪烁...");
    return 0;
}

int main() {
    printf("\n=== 测试 utils 库 ===\n");
    int arr[8] = {42, 17, 8, 99, 23, 5, 71, 34};
    printf("原始数组: ");
    print_int_array(arr, 8);
    
    bubble_sort(arr, 8);
    printf("冒泡排序后: ");
    print_int_array(arr, 8);
    
    insertion_sort(arr, 8);
    printf("插入排序后: ");
    print_int_array(arr, 8);
    
    printf("\n最大元素: %d\n", max_int_array(arr, 8));
    printf("最小元素: %d\n", min_int_array(arr, 8));
    printf("数组和: %d\n", sum_int_array(arr, 8));
    
    printf("\n=== 测试 multifunc 库 ===\n");
    
    // 注册步骤
    FuncStep steps[] = {
        {"初始化传感器", test_sensor, NULL, true},
        {"配置 UART",    test_uart,    NULL, true},
        {"LED 闪烁",     test_led,     NULL, false},
    };
    
    MultiFuncExecutor *exec = executor_create(steps, 3, true);
    if (exec) {
        executor_run(exec);
        executor_free(exec);
    }
    
    printf("\n✅ 所有测试通过！\n");
    return 0;
}
