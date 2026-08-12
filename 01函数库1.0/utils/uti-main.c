#include "utils.h"

int main() {
    // 数组示例
    int arr[10];
    fill_random_range(arr, 10, 0, 100);
    printf("随机数组: ");
    print_int_array(arr, 10);
    bubble_sort(arr, 10);
    printf("排序后: ");
    print_int_array(arr, 10);

    // 字符串示例
    char s[100] = "  Hello, World!  ";
    trim(s);
    to_lower(s);
    printf("处理后: %s\n", s);

    // 数学示例
    printf("5! = %lld\n", factorial(5));
    printf("gcd(24, 36) = %d\n", gcd(24, 36));

    return 0;
}