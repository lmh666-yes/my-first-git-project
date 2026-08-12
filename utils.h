#ifndef UTILS_H
#define UTILS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

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

#endif // UTILS_H