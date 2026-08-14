#ifndef UTILS_H
#define UTILS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================
 *              UTILS 函数库 · 分区快速索引
 * ============================================================
 * 本库按功能分区组织，查找函数时用 Ctrl+F 搜下面分区名即可快速定位：
 *
 *   【数组工具】       print_int_array / bubble_sort / binary_search ...
 *   【字符串工具】     str_len / trim / str_split / str_starts_with ...
 *   【数学工具】       factorial / gcd / lcm / is_prime ...
 *   【文件工具】       read_file / write_file / copy_file ...
 *   【内存管理】       safe_malloc / safe_free / copy_string ...
 *   【位操作(单片机)】 bit_set / byte_get_high / swap_bytes16 ...
 *   【进制转换】       int_to_binary_str / hex_str_to_int ...
 *   【数字工具】       is_armstrong / reverse_int / count_digits ...
 *   【排序算法】       quick_sort / merge_sort / heap_sort ...
 *   【数据结构】       ListNode(链表) / Stack(栈) / Queue(队列) ...
 *   【校验与CRC】      checksum8 / crc16_modbus / xor_checksum ...
 *   【延时(单片机)】   soft_delay_ms / soft_delay_us ...
 *   【系统工具(Linux)】file_exists / run_cmd / path_join / hex_dump ...
 *   【调试工具】       debug_log / get_time_str / wait_for_key ...
 *
 * 说明：
 * 1. 本库为纯 C 实现，C++ 工程可直接 #include "utils.h"（已做 extern "C" 保护）。
 * 2. 所有函数命名已避开 STM32 HAL / 标准外设库等固件库常用名，可放心混用。
 * 3. 返回 malloc 分配内存的函数，使用后请调用 safe_free() 释放。
 * ============================================================ */

// ============================================================
//                     数组工具函数
// ============================================================

/**
 * 打印整型数组所有元素，以空格分隔，末尾换行
 * @param arr 数组
 * @param size 数组大小
 */
void print_int_array(int arr[], int size);

/**
 * 打印双精度浮点型数组所有元素，以空格分隔，末尾换行
 * @param arr 数组
 * @param size 数组大小
 */
void print_double_array(double arr[], int size);

/**
 * 用指定值填充整型数组
 * @param arr 数组
 * @param size 数组大小
 * @param value 填充值
 */
void fill_int_array(int arr[], int size, int value);

/**
 * 用随机数填充整型数组（范围 0~99）
 * @param arr 数组
 * @param size 数组大小
 * @note 调用前需先 srand(time(NULL))
 */
void fill_random_int(int arr[], int size);

/**
 * 用随机数填充整型数组（指定范围）
 * @param arr 数组
 * @param size 数组大小
 * @param min 最小值
 * @param max 最大值
 * @note 调用前需先 srand(time(NULL))
 */
void fill_random_range(int arr[], int size, int min, int max);

/**
 * 反转整型数组（原地）
 * @param arr 数组
 * @param size 数组大小
 */
void reverse_int_array(int arr[], int size);

/**
 * 查找整型数组中第一个等于 target 的元素下标
 * @param arr 数组
 * @param size 数组大小
 * @param target 目标值
 * @return 下标，若未找到返回 -1
 */
int find_int(int arr[], int size, int target);

/**
 * 查找整型数组中最后一个等于 target 的元素下标
 * @param arr 数组
 * @param size 数组大小
 * @param target 目标值
 * @return 下标，若未找到返回 -1
 */
int find_last_int(int arr[], int size, int target);

/**
 * 计算整型数组元素之和
 * @param arr 数组
 * @param size 数组大小
 * @return 总和
 */
int sum_int_array(int arr[], int size);

/**
 * 计算整型数组元素平均值
 * @param arr 数组
 * @param size 数组大小
 * @return 平均值（浮点数）
 */
double avg_int_array(int arr[], int size);

/**
 * 查找整型数组最大值
 * @param arr 数组
 * @param size 数组大小
 * @return 最大值
 */
int max_int_array(int arr[], int size);

/**
 * 查找整型数组最小值
 * @param arr 数组
 * @param size 数组大小
 * @return 最小值
 */
int min_int_array(int arr[], int size);

/**
 * 冒泡排序（升序）
 * @param arr 数组
 * @param size 数组大小
 */
void bubble_sort(int arr[], int size);

/**
 * 插入排序（升序）
 * @param arr 数组
 * @param size 数组大小
 */
void insertion_sort(int arr[], int size);

/**
 * 选择排序（升序）
 * @param arr 数组
 * @param size 数组大小
 */
void selection_sort(int arr[], int size);

// ===== 最大子数组之和（Kadane 算法） =====
// 求整型数组中连续子数组的最大和，返回最大和
int max_subarray_sum(int arr[], int size);

/**
 * 二分查找（要求数组已升序）
 * @param arr 数组
 * @param size 数组大小
 * @param target 目标值
 * @return 下标，若未找到返回 -1
 */
int binary_search(int arr[], int size, int target);

/**
 * 合并两个已升序的数组，返回新数组（需手动 free）
 * @param arr1 数组1
 * @param size1 数组1大小
 * @param arr2 数组2
 * @param size2 数组2大小
 * @param out_size 输出合并后的数组大小
 * @return 合并后的数组指针
 */
int* merge_sorted_arrays(int arr1[], int size1, int arr2[], int size2, int *out_size);

/**
 * 删除整型数组中指定下标元素（原地，顺序前移）
 * @param arr 数组
 * @param size 数组大小（传入指针，会被修改）
 * @param index 要删除的下标
 * @return 0 成功，-1 失败
 */
int remove_at_index(int arr[], int *size, int index);

/**
 * 在整型数组指定位置插入元素（原地，后移）
 * @param arr 数组
 * @param size 数组大小（传入指针，会被修改）
 * @param index 插入位置
 * @param value 要插入的值
 * @param max_capacity 数组最大容量
 * @return 0 成功，-1 失败
 */
int insert_at_index(int arr[], int *size, int index, int value, int max_capacity);

// ============================================================
//                     字符串工具函数
// ============================================================

/**
 * 获取字符串长度（不包含 '\0'）
 * @param str 字符串
 * @return 长度
 */
int str_len(const char *str);

/**
 * 复制字符串（目标缓冲区需足够大）
 * @param dest 目标
 * @param src 源
 * @return dest
 */
char* str_copy(char *dest, const char *src);

/**
 * 拼接字符串（目标缓冲区需足够大）
 * @param dest 目标
 * @param src 源
 * @return dest
 */
char* str_cat(char *dest, const char *src);

/**
 * 比较两个字符串
 * @param s1 字符串1
 * @param s2 字符串2
 * @return 0 相等，<0 s1<s2，>0 s1>s2
 */
int str_cmp(const char *s1, const char *s2);

/**
 * 查找子串第一次出现的位置
 * @param haystack 主串
 * @param needle 子串
 * @return 指向子串首字符的指针，未找到返回 NULL
 */
char* str_find(const char *haystack, const char *needle);

/**
 * 统计某个字符在字符串中出现的次数
 * @param str 字符串
 * @param ch 字符
 * @return 出现次数
 */
int count_char(const char *str, char ch);

/**
 * 删除字符串中所有指定字符（原地）
 * @param str 字符串
 */
void remove_char(char *str, char ch);

/**
 * 判断字符串是否是回文
 * @param str 字符串
 * @return 1 是回文，0 不是
 */
int is_palindrome_str(const char *str);

/**
 * 将字符串中的所有大写字母转为小写
 * @param str 字符串（原地修改）
 */
void to_lower(char *str);

/**
 * 将字符串中的所有小写字母转为大写
 * @param str 字符串（原地修改）
 */
void to_upper(char *str);

/**
 * 反转字符串（原地）
 * @param str 字符串
 */
void reverse_str(char *str);

/**
 * 将字符串转换为整数（支持前导空格和正负号）
 * @param str 字符串
 * @return 转换后的整数
 */
int str_to_int(const char *str);

/**
 * 将整数转换为字符串
 * @param num 整数
 * @param buf 输出缓冲区（需足够大）
 * @return buf
 */
char* int_to_str(int num, char *buf);

/**
 * 去除字符串首尾空格（原地）
 * @param str 字符串
 */
void trim(char *str);

/**
 * 统计字符串中单词个数（单词由空格分隔）
 * @param str 字符串
 * @return 单词个数
 */
int count_words(const char *str);

// ============================================================
//                     数学工具函数
// ============================================================

/**
 * 计算阶乘 n!
 * @param n 非负整数
 * @return 阶乘结果（long long）
 */
long long factorial(int n);

/**
 * 判断一个整数是否为素数
 * @param n 整数
 * @return 1 素数，0 非素数
 */
int is_prime(int n);

/**
 * 计算最大公约数（辗转相除法）
 * @param a 整数
 * @param b 整数
 * @return 最大公约数
 */
int gcd(int a, int b);

/**
 * 计算最小公倍数
 * @param a 整数
 * @param b 整数
 * @return 最小公倍数
 */
int lcm(int a, int b);

/**
 * 计算 a 的 b 次方（快速幂）
 * @param base 底数
 * @param exp 指数（非负）
 * @return 幂结果
 */
long long power(int base, int exp);

/**
 * 判断一个整数是否是完数（真因子之和等于自身）
 * @param n 正整数
 * @return 1 是完数，0 不是
 */
int is_perfect(int n);

/**
 * 斐波那契数列第 n 项（迭代）
 * @param n 项数（从 0 开始）
 * @return 第 n 项的值
 */
long long fibonacci(int n);

/**
 * 计算数组的最大子数组和（Kadane 算法）
 * @param arr 数组
 * @param size 数组大小
 * @return 最大子数组和
 */
int max_subarray_sum(int arr[], int size);

/**
 * 生成 [min, max] 范围内的随机整数
 * @param min 最小值
 * @param max 最大值
 * @return 随机整数
 */
int rand_range(int min, int max);

/**
 * 洗牌算法（打乱数组）
 * @param arr 数组
 * @param size 数组大小
 */
void shuffle_array(int arr[], int size);

// ============================================================
//                     文件工具函数
// ============================================================

/**
 * 读取整个文本文件到字符串（需手动 free）
 * @param filename 文件名
 * @return 文件内容字符串，失败返回 NULL
 */
char* read_file(const char *filename);

/**
 * 将字符串写入文件
 * @param filename 文件名
 * @param content 内容
 * @return 0 成功，-1 失败
 */
int write_file(const char *filename, const char *content);

/**
 * 将字符串追加到文件末尾
 * @param filename 文件名
 * @param content 内容
 * @return 0 成功，-1 失败
 */
int append_file(const char *filename, const char *content);

/**
 * 复制文件
 * @param src 源文件
 * @param dest 目标文件
 * @return 0 成功，-1 失败
 */
int copy_file(const char *src, const char *dest);

/**
 * 统计文件行数
 * @param filename 文件名
 * @return 行数，失败返回 -1
 */
int count_file_lines(const char *filename);

// ============================================================
//                     内存管理工具
// ============================================================

/**
 * 安全分配内存（失败时输出错误并退出）
 * @param size 要分配的字节数
 * @return 分配的内存指针
 */
void* safe_malloc(size_t size);

/**
 * 安全分配并清零内存
 * @param count 元素个数
 * @param size 每个元素大小
 * @return 分配的内存指针
 */
void* safe_calloc(size_t count, size_t size);

/**
 * 安全重新分配内存
 * @param ptr 原指针
 * @param size 新大小
 * @return 重新分配的内存指针
 */
void* safe_realloc(void *ptr, size_t size);

/**
 * 安全释放内存并将指针置为 NULL
 * @param ptr 指针的指针
 */
void safe_free(void **ptr);

/**
 * 复制整型数组（返回新数组，需手动 free）
 * @param src 源数组
 * @param size 数组大小
 * @return 新数组指针
 */
int* copy_int_array(int src[], int size);

/**
 * 复制字符串（返回新字符串，需手动 free）
 * @param src 源字符串
 * @return 新字符串指针
 */
char* copy_string(const char *src);

// ============================================================
//                     实用工具函数
// ============================================================

/**
 * 打印带时间戳的调试信息
 * @param format 格式字符串
 * @param ... 可变参数
 */
void debug_log(const char *format, ...);

/**
 * 获取当前时间字符串（格式：YYYY-MM-DD HH:MM:SS）
 * @param buf 输出缓冲区（至少 20 字节）
 * @return buf
 */
char* get_time_str(char *buf);

/**
 * 暂停程序，提示按任意键继续
 */
void wait_for_key(void);

/**
 * 清空输入缓冲区（stdin）
 */
void clear_input_buffer(void);

/**
 * 安全读取整行（避免缓冲区溢出）
 * @param buf 缓冲区
 * @param size 缓冲区大小
 * @param stream 输入流
 * @return 成功返回 buf，失败返回 NULL
 */
char* safe_fgets(char *buf, size_t size, FILE *stream);

// ============================================================
//                     位操作工具（单片机）
// ============================================================
// 用于寄存器/端口位操作，命名已避开 HAL、标准外设库等固件库。

/**
 * 置位：将寄存器第 bit 位置 1
 * @param reg 寄存器地址（如 &GPIOA->ODR）
 * @param bit 位号（0~7）
 */
void bit_set(volatile uint8_t *reg, uint8_t bit);

/** 清零：将寄存器第 bit 位清 0 */
void bit_clear(volatile uint8_t *reg, uint8_t bit);

/** 翻转：将寄存器第 bit 位取反 */
void bit_toggle(volatile uint8_t *reg, uint8_t bit);

/** 查询：返回 1 表示该位为 1，0 表示该位为 0 */
uint8_t bit_is_set(volatile uint8_t *reg, uint8_t bit);

/** 查询：返回 1 表示该位为 0，0 表示该位为 1 */
uint8_t bit_is_clear(volatile uint8_t *reg, uint8_t bit);

/** 取 16 位数据的高字节 */
uint8_t byte_get_high(uint16_t val);

/** 取 16 位数据的低字节 */
uint8_t byte_get_low(uint16_t val);

/** 由高字节 + 低字节组合成 16 位数据 */
uint16_t byte_combine(uint8_t hi, uint8_t lo);

/** 统计 32 位数据中 1 的个数（汉明重量） */
uint8_t count_ones(uint32_t val);

/** 32 位循环左移 n 位 */
uint32_t rotate_left(uint32_t val, uint8_t n);

/** 32 位循环右移 n 位 */
uint32_t rotate_right(uint32_t val, uint8_t n);

/** 16 位高低字节交换（大小端转换） */
uint16_t swap_bytes16(uint16_t val);

/** 32 位字节序反转（大小端转换） */
uint32_t swap_bytes32(uint32_t val);

/** 判断当前平台是否小端字节序（1 小端，0 大端） */
int is_little_endian(void);

// ============================================================
//                     字符与进制转换工具
// ============================================================

/** 判断字符是否为数字 '0'~'9' */
int is_digit_char(char c);

/** 判断字符是否为字母 a~z / A~Z */
int is_alpha_char(char c);

/** 判断字符是否为数字或字母 */
int is_alnum_char(char c);

/** 判断字符是否为空白符（空格/制表/换行等） */
int is_space_char(char c);

/** 单个字符转小写 */
char char_to_lower(char c);

/** 单个字符转大写 */
char char_to_upper(char c);

/** 十六进制字符转数值（'0'-'9','a'-'f','A'-'F'），非法返回 -1 */
int hex_char_to_int(char c);

/** 数值(0~15)转十六进制字符，非法返回 '?' */
char int_to_hex_char(int v);

/**
 * 十进制整数转二进制字符串
 * @param num 整数
 * @param buf 输出缓冲区
 * @param buf_size 缓冲区大小
 * @return buf
 */
char* int_to_binary_str(int num, char *buf, int buf_size);

/** 十进制整数转八进制字符串 */
char* int_to_octal_str(int num, char *buf);

/** 十进制整数转十六进制字符串（大写） */
char* int_to_hex_str(int num, char *buf);

/** 二进制字符串转十进制整数 */
long bin_str_to_int(const char *str);

/** 八进制字符串转十进制整数 */
long oct_str_to_int(const char *str);

/** 十六进制字符串转十进制整数 */
long hex_str_to_int(const char *str);

// ============================================================
//                     数字工具（基础算法）
// ============================================================

/** 统计十进制整数的位数（0 返回 1） */
int count_digits(int n);

/** 反转十进制整数（123 -> 321，-123 -> -321） */
int reverse_int(int n);

/** 求十进制整数各位数字之和 */
int sum_digits(int n);

/** 判断是否为水仙花数（阿姆斯特朗数） */
int is_armstrong(int n);

/** 判断是否为回文数（121、1221 等） */
int is_palindrome_num(int n);

// ============================================================
//                     排序算法补充
// ============================================================

/** 快速排序（升序，原地） */
void quick_sort(int arr[], int size);

/** 归并排序（升序，原地，内部临时申请内存） */
void merge_sort(int arr[], int size);

/** 堆排序（升序，原地） */
void heap_sort(int arr[], int size);

// ============================================================
//                     数组工具补充
// ============================================================

/** 数组整体左旋 k 位（原地） */
void rotate_array_left(int arr[], int size, int k);

/** 数组整体右旋 k 位（原地） */
void rotate_array_right(int arr[], int size, int k);

/**
 * 原地去重（保持首次出现顺序），返回去重后的新长度
 * @param arr 数组
 * @param size 数组大小（指针，会被修改为新长度）
 * @return 去重后的长度
 */
int remove_duplicates_int(int arr[], int *size);

// ============================================================
//                     字符串工具补充
// ============================================================

/**
 * 提取子串
 * @param str 原字符串
 * @param start 起始下标
 * @param len 要提取的长度
 * @param buf 输出缓冲区
 * @param buf_size 缓冲区大小
 * @return buf
 */
char* str_substr(const char *str, int start, int len, char *buf, int buf_size);

/** 将字符串中所有 old_ch 替换为 new_ch，返回替换次数 */
int str_replace_char(char *str, char old_ch, char new_ch);

/** 判断字符串是否以 prefix 开头 */
int str_starts_with(const char *str, const char *prefix);

/** 判断字符串是否以 suffix 结尾 */
int str_ends_with(const char *str, const char *suffix);

/**
 * 按分隔符分割字符串（返回动态分配的字符串数组）
 * @param str 原字符串（不会被修改）
 * @param delim 分隔符
 * @param count 输出分割段数
 * @return 字符串数组（NULL 结尾），用后调用 str_free_split 释放
 */
char** str_split(const char *str, char delim, int *count);

/** 释放 str_split 返回的字符串数组 */
void str_free_split(char **tokens, int count);

// ============================================================
//                     单向链表（数据结构）
// ============================================================

/** 链表节点 */
typedef struct ListNode {
    int data;
    struct ListNode *next;
} ListNode;

/** 创建值为 data 的新节点（需 free 释放） */
ListNode* list_create(int data);

/** 头插法：在链表头部插入节点 */
void list_insert_head(ListNode **head, int data);

/** 尾插法：在链表尾部插入节点 */
void list_insert_tail(ListNode **head, int data);

/** 有序插入：按升序将节点插入有序链表 */
void list_insert_sorted(ListNode **head, int data);

/** 删除链表中所有等于 data 的节点 */
void list_delete_value(ListNode **head, int data);

/** 查找第一个等于 data 的节点，返回节点指针（找不到返回 NULL） */
ListNode* list_find(ListNode *head, int data);

/** 获取链表长度 */
int list_length(ListNode *head);

/** 反转链表（原地） */
void list_reverse(ListNode **head);

/** 打印链表：1 -> 2 -> 3 -> NULL */
void list_print(ListNode *head);

/** 释放整个链表并置 head 为 NULL */
void list_free(ListNode **head);

// ============================================================
//                     栈（数据结构）
// ============================================================

/** 栈结构体（基于数组实现） */
typedef struct {
    int *data;
    int top;
    int capacity;
} Stack;

/** 创建容量为 capacity 的栈 */
Stack* stack_create(int capacity);

/** 销毁栈（释放内存） */
void stack_destroy(Stack *s);

/** 入栈，0 成功，-1 失败（栈满） */
int stack_push(Stack *s, int value);

/** 出栈，0 成功，-1 失败（栈空） */
int stack_pop(Stack *s, int *out);

/** 查看栈顶元素（不出栈），0 成功，-1 失败 */
int stack_peek(Stack *s, int *out);

/** 判断栈是否为空 */
int stack_is_empty(Stack *s);

/** 判断栈是否已满 */
int stack_is_full(Stack *s);

/** 获取栈中元素个数 */
int stack_size(Stack *s);

// ============================================================
//                     队列（数据结构）
// ============================================================

/** 循环队列结构体 */
typedef struct {
    int *data;
    int front;
    int rear;
    int size;
    int capacity;
} Queue;

/** 创建容量为 capacity 的循环队列 */
Queue* queue_create(int capacity);

/** 销毁队列（释放内存） */
void queue_destroy(Queue *q);

/** 入队，0 成功，-1 失败（队满） */
int queue_enqueue(Queue *q, int value);

/** 出队，0 成功，-1 失败（队空） */
int queue_dequeue(Queue *q, int *out);

/** 查看队首元素（不出队），0 成功，-1 失败 */
int queue_peek(Queue *q, int *out);

/** 判断队列是否为空 */
int queue_is_empty(Queue *q);

/** 判断队列是否已满 */
int queue_is_full(Queue *q);

/** 获取队列中元素个数 */
int queue_size(Queue *q);

// ============================================================
//                     校验与CRC工具（单片机通信）
// ============================================================

/** 异或校验和（数据逐字节异或） */
uint8_t xor_checksum(const uint8_t *data, uint16_t len);

/** 8 位累加校验和（取累加和低 8 位） */
uint8_t checksum8(const uint8_t *data, uint16_t len);

/** 16 位累加校验和（取累加和低 16 位） */
uint16_t checksum16(const uint8_t *data, uint16_t len);

/** CRC-8 校验（多项式 0x07，初始值 0x00） */
uint8_t crc8(const uint8_t *data, uint16_t len);

/** CRC-16 Modbus 校验（多项式 0xA001，初始值 0xFFFF） */
uint16_t crc16_modbus(const uint8_t *data, uint16_t len);

/** 奇偶校验：返回 1 表示 1 的个数为奇数，0 为偶数 */
uint8_t parity_check(uint32_t val);

/**
 * 字节数组转十六进制字符串
 * @param data 数据
 * @param len 长度
 * @param buf 输出缓冲区（需 >= len*2+1）
 * @param buf_size 缓冲区大小
 * @return buf
 */
char* bytes_to_hex_str(const uint8_t *data, uint16_t len, char *buf, uint16_t buf_size);

/**
 * 十六进制字符串转字节数组
 * @param hex 十六进制字符串（长度需为偶数）
 * @param out 输出缓冲区
 * @param max_len 缓冲区最大长度
 * @return 转换成功的字节数，格式错误返回 -1
 */
int hex_str_to_bytes(const char *hex, uint8_t *out, uint16_t max_len);

// ============================================================
//                     延时工具（单片机）
// ============================================================
// 软件空循环延时，精度与主频相关，仅用于学习演示；
// 正式工程建议使用硬件定时器（如 HAL_Delay / SysTick）。

/** 软件延时约 ms 毫秒（需按主频微调循环次数） */
void soft_delay_ms(uint32_t ms);

/** 软件延时约 us 微秒（需按主频微调循环次数） */
void soft_delay_us(uint32_t us);

// ============================================================
//                     系统工具（Linux / PC 开发）
// ============================================================
// 此分区面向 Linux 嵌入式 / PC 开发环境（Windows 与 Linux 均支持）。
// 若在裸机单片机工程中使用，请确认工具链提供 sys/stat.h、unistd.h。

/** 判断文件是否存在 */
int file_exists(const char *path);

/** 判断目录是否存在 */
int dir_exists(const char *path);

/** 获取文件大小（字节），失败返回 -1 */
long get_file_size(const char *path);

/** 创建目录，0 成功，-1 失败 */
int create_dir(const char *path);

/** 删除空目录，0 成功，-1 失败 */
int remove_dir(const char *path);

/**
 * 拼接目录与文件名（自动使用平台分隔符）
 * @param dir 目录
 * @param file 文件名
 * @param buf 输出缓冲区
 * @param buf_size 缓冲区大小
 * @return buf
 */
char* path_join(const char *dir, const char *file, char *buf, int buf_size);

/** 获取文件扩展名（不含点，如 "c"），无扩展名返回空串 */
const char* get_file_ext(const char *path);

/** 获取文件名（不含目录路径部分） */
char* get_base_name(const char *path, char *buf, int buf_size);

/** 执行系统命令（返回命令返回值） */
int run_cmd(const char *cmd);

/**
 * 执行命令并捕获其标准输出（返回动态字符串，需 safe_free）
 * @param cmd 命令
 * @return 输出字符串，失败返回 NULL
 */
char* run_cmd_capture(const char *cmd);

/**
 * 十六进制打印内存内容（调试利器）
 * @param ptr 内存指针
 * @param len 长度
 */
void hex_dump(const void *ptr, size_t len);



// 自动生成的函数声明（由 gen_functions.py 生成）
#include "utils_gen.h"
#ifdef __cplusplus
}
#endif

#endif // UTILS_H