#include "utils.h"
#include <stdint.h>

int main() {
    // ========== 数组示例 ==========
    int arr[10];
    fill_random_range(arr, 10, 0, 100);
    printf("随机数组: ");
    print_int_array(arr, 10);
    bubble_sort(arr, 10);
    printf("排序后: ");
    print_int_array(arr, 10);

    // ========== 字符串示例 ==========
    char s[100] = "  Hello, World!  ";
    trim(s);
    to_lower(s);
    printf("处理后: %s\n", s);

    // ========== 数学示例 ==========
    printf("5! = %lld\n", factorial(5));
    printf("gcd(24, 36) = %d\n", gcd(24, 36));

    // ========== 位操作示例 ==========
    volatile uint8_t reg = 0x00;
    bit_set(&reg, 3);
    bit_set(&reg, 0);
    printf("reg = 0x%02X, bit3 = %d\n", reg, bit_is_set(&reg, 3));
    bit_toggle(&reg, 3);
    printf("翻转后 reg = 0x%02X, 1的个数 = %d\n", reg, count_ones(reg));

    // ========== 进制转换示例 ==========
    char bin[40], hex[20], oct[20];
    int_to_binary_str(42, bin, sizeof(bin));
    printf("42 -> 二进制 %s, 十六进制 %s, 八进制 %s\n",
           bin, int_to_hex_str(42, hex), int_to_octal_str(42, oct));
    printf("十六进制 FF 转十进制 = %ld\n", hex_str_to_int("FF"));

    // ========== 数字工具示例 ==========
    printf("153 是水仙花数? %d, 12345 位数 = %d, 反转 12345 = %d\n",
           is_armstrong(153), count_digits(12345), reverse_int(12345));

    // ========== 排序算法示例 ==========
    int b[] = {5, 3, 8, 1, 9, 2};
    quick_sort(b, 6);
    printf("快速排序: ");
    print_int_array(b, 6);

    // ========== 数据结构示例：链表 ==========
    ListNode *head = NULL;
    list_insert_tail(&head, 3);
    list_insert_head(&head, 1);
    list_insert_tail(&head, 2);
    printf("链表: ");
    list_print(head);
    printf("链表长度: %d\n", list_length(head));
    list_free(&head);

    // ========== 数据结构示例：栈 ==========
    Stack *stk = stack_create(5);
    stack_push(stk, 10);
    stack_push(stk, 20);
    int v;
    stack_pop(stk, &v);
    printf("栈顶出栈: %d\n", v);
    stack_destroy(stk);

    // ========== 数据结构示例：队列 ==========
    Queue *q = queue_create(5);
    queue_enqueue(q, 1);
    queue_enqueue(q, 2);
    queue_dequeue(q, &v);
    printf("队首出队: %d\n", v);
    queue_destroy(q);

    // ========== 校验与CRC示例 ==========
    uint8_t data[] = {0x01, 0x03, 0x00, 0x00, 0x00, 0x0A};
    printf("CRC16(Modbus): 0x%04X, 校验和8: 0x%02X, XOR: 0x%02X\n",
           crc16_modbus(data, 6), checksum8(data, 6), xor_checksum(data, 6));

    // ========== 系统工具示例 ==========
    printf("file_exists(utils.c) = %d\n", file_exists("utils.c"));
    printf("文件扩展名 = %s\n", get_file_ext("utils.c"));
    char joined[128];
    path_join("src", "main.c", joined, sizeof(joined));
    printf("路径拼接 = %s\n", joined);

    // ========== 调试工具示例 ==========
    hex_dump(data, sizeof(data));

    return 0;
}