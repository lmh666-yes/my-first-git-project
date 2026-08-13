/* ============================================================
 *  utils_gen.h — 自动生成的函数声明（由 gen_functions.py 生成，请勿手改）
 * ============================================================ */

#ifndef UTILS_GEN_H
#define UTILS_GEN_H

/* ===== 常用宏兜底（若 utils.h 已定义则跳过，避免重复定义） ===== */
#ifndef UTILS_MIN
#define UTILS_MIN(a, b) ((a) < (b) ? (a) : (b))
#endif
#ifndef UTILS_MAX
#define UTILS_MAX(a, b) ((a) > (b) ? (a) : (b))
#endif
#ifndef UTILS_ABS
#define UTILS_ABS(x) ((x) < 0 ? -(x) : (x))
#endif
#ifndef UTILS_ARRAY_SIZE
#define UTILS_ARRAY_SIZE(arr) ((int)(sizeof(arr) / sizeof((arr)[0])))
#endif
#ifndef UTILS_BIT
#define UTILS_BIT(n) (1u << (n))
#endif

/* ===== 数据结构兜底（若 utils.h 已定义相同类型请删除对应行） ===== */
typedef struct { int *data; int size, capacity; } Vector;
typedef struct { int *data; int size, capacity; } PriorityQueue;
typedef struct { uint8_t *buffer; uint16_t head, tail, capacity, count; } RingBuffer;
typedef struct BSTNode { int data; struct BSTNode *left, *right; } BSTNode;

/** 自动生成的数据结构 */
typedef struct DNode { int data; struct DNode *prev, *next; } DNode;

/** 自动生成的数据结构 */
typedef struct { DNode *head, *tail; int size; } DList;

/** 自动生成的数据结构 */
typedef struct { int *data; int front, rear, size, capacity; } Deque;

/** 自动生成的数据结构 */
typedef struct { int *data; int size, capacity; } MinHeap;

/** 自动生成的数据结构 */
typedef struct { int *data; char *used, *del; int size, capacity; } IntSet;

/** 自动生成的数据结构 */
typedef struct { char **keys; int *values; char *used; int size, capacity; } StrMap;

/** 自动生成的数据结构 */
typedef struct { int **adj; int n; } Graph;


// ============================================================
//                     数组工具(类型扩展)（自动生成）
// ============================================================

/** 查找元素下标 */
int find_int_array(int arr[], int size, int target);

/** 统计元素出现次数 */
int count_int_array(int arr[], int size, int target);

/** 数组元素乘积 */
long long product_int_array(int arr[], int size);

/** 最大绝对值 */
int max_abs_int_array(int arr[], int size);

/** 最小绝对值 */
int min_abs_int_array(int arr[], int size);

/** 第二大元素 */
int second_max_int_array(int arr[], int size);

/** 第二小元素 */
int second_min_int_array(int arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_int_array(int arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_int_array(int arr[], int size);

/** 打印数组元素 */
void print_long_array(long arr[], int size);

/** 数组元素求和 */
long long sum_long_array(long arr[], int size);

/** 数组平均值 */
double avg_long_array(long arr[], int size);

/** 数组最大值 */
long max_long_array(long arr[], int size);

/** 数组最小值 */
long min_long_array(long arr[], int size);

/** 用指定值填充数组 */
void fill_long_array(long arr[], int size, long value);

/** 反转数组 */
void reverse_long_array(long arr[], int size);

/** 查找元素下标 */
int find_long_array(long arr[], int size, long target);

/** 统计元素出现次数 */
int count_long_array(long arr[], int size, long target);

/** 数组元素乘积 */
long long product_long_array(long arr[], int size);

/** 复制数组(需free) */
long* copy_long_array(long arr[], int size);

/** 最大绝对值 */
long max_abs_long_array(long arr[], int size);

/** 最小绝对值 */
long min_abs_long_array(long arr[], int size);

/** 第二大元素 */
long second_max_long_array(long arr[], int size);

/** 第二小元素 */
long second_min_long_array(long arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_long_array(long arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_long_array(long arr[], int size);

/** 打印数组元素 */
void print_long_long_array(long long arr[], int size);

/** 数组元素求和 */
long long sum_long_long_array(long long arr[], int size);

/** 数组平均值 */
double avg_long_long_array(long long arr[], int size);

/** 数组最大值 */
long long max_long_long_array(long long arr[], int size);

/** 数组最小值 */
long long min_long_long_array(long long arr[], int size);

/** 用指定值填充数组 */
void fill_long_long_array(long long arr[], int size, long long value);

/** 反转数组 */
void reverse_long_long_array(long long arr[], int size);

/** 查找元素下标 */
int find_long_long_array(long long arr[], int size, long long target);

/** 统计元素出现次数 */
int count_long_long_array(long long arr[], int size, long long target);

/** 数组元素乘积 */
long long product_long_long_array(long long arr[], int size);

/** 复制数组(需free) */
long long* copy_long_long_array(long long arr[], int size);

/** 最大绝对值 */
long long max_abs_long_long_array(long long arr[], int size);

/** 最小绝对值 */
long long min_abs_long_long_array(long long arr[], int size);

/** 第二大元素 */
long long second_max_long_long_array(long long arr[], int size);

/** 第二小元素 */
long long second_min_long_long_array(long long arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_long_long_array(long long arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_long_long_array(long long arr[], int size);

/** 打印数组元素 */
void print_short_array(short arr[], int size);

/** 数组元素求和 */
long long sum_short_array(short arr[], int size);

/** 数组平均值 */
double avg_short_array(short arr[], int size);

/** 数组最大值 */
short max_short_array(short arr[], int size);

/** 数组最小值 */
short min_short_array(short arr[], int size);

/** 用指定值填充数组 */
void fill_short_array(short arr[], int size, short value);

/** 反转数组 */
void reverse_short_array(short arr[], int size);

/** 查找元素下标 */
int find_short_array(short arr[], int size, short target);

/** 统计元素出现次数 */
int count_short_array(short arr[], int size, short target);

/** 数组元素乘积 */
long long product_short_array(short arr[], int size);

/** 复制数组(需free) */
short* copy_short_array(short arr[], int size);

/** 最大绝对值 */
short max_abs_short_array(short arr[], int size);

/** 最小绝对值 */
short min_abs_short_array(short arr[], int size);

/** 第二大元素 */
short second_max_short_array(short arr[], int size);

/** 第二小元素 */
short second_min_short_array(short arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_short_array(short arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_short_array(short arr[], int size);

/** 打印数组元素 */
void print_uint_array(unsigned int arr[], int size);

/** 数组元素求和 */
unsigned long long sum_uint_array(unsigned int arr[], int size);

/** 数组平均值 */
double avg_uint_array(unsigned int arr[], int size);

/** 数组最大值 */
unsigned int max_uint_array(unsigned int arr[], int size);

/** 数组最小值 */
unsigned int min_uint_array(unsigned int arr[], int size);

/** 用指定值填充数组 */
void fill_uint_array(unsigned int arr[], int size, unsigned int value);

/** 反转数组 */
void reverse_uint_array(unsigned int arr[], int size);

/** 查找元素下标 */
int find_uint_array(unsigned int arr[], int size, unsigned int target);

/** 统计元素出现次数 */
int count_uint_array(unsigned int arr[], int size, unsigned int target);

/** 数组元素乘积 */
unsigned long long product_uint_array(unsigned int arr[], int size);

/** 复制数组(需free) */
unsigned int* copy_uint_array(unsigned int arr[], int size);

/** 第二大元素 */
unsigned int second_max_uint_array(unsigned int arr[], int size);

/** 第二小元素 */
unsigned int second_min_uint_array(unsigned int arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_uint_array(unsigned int arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_uint_array(unsigned int arr[], int size);

/** 打印数组元素 */
void print_float_array(float arr[], int size);

/** 数组元素求和 */
double sum_float_array(float arr[], int size);

/** 数组平均值 */
double avg_float_array(float arr[], int size);

/** 数组最大值 */
float max_float_array(float arr[], int size);

/** 数组最小值 */
float min_float_array(float arr[], int size);

/** 用指定值填充数组 */
void fill_float_array(float arr[], int size, float value);

/** 反转数组 */
void reverse_float_array(float arr[], int size);

/** 查找元素下标 */
int find_float_array(float arr[], int size, float target);

/** 统计元素出现次数 */
int count_float_array(float arr[], int size, float target);

/** 数组元素乘积 */
double product_float_array(float arr[], int size);

/** 复制数组(需free) */
float* copy_float_array(float arr[], int size);

/** 最大绝对值 */
float max_abs_float_array(float arr[], int size);

/** 最小绝对值 */
float min_abs_float_array(float arr[], int size);

/** 第二大元素 */
float second_max_float_array(float arr[], int size);

/** 第二小元素 */
float second_min_float_array(float arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_float_array(float arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_float_array(float arr[], int size);

/** 数组元素求和 */
double sum_double_array(double arr[], int size);

/** 数组平均值 */
double avg_double_array(double arr[], int size);

/** 数组最大值 */
double max_double_array(double arr[], int size);

/** 数组最小值 */
double min_double_array(double arr[], int size);

/** 用指定值填充数组 */
void fill_double_array(double arr[], int size, double value);

/** 反转数组 */
void reverse_double_array(double arr[], int size);

/** 查找元素下标 */
int find_double_array(double arr[], int size, double target);

/** 统计元素出现次数 */
int count_double_array(double arr[], int size, double target);

/** 数组元素乘积 */
double product_double_array(double arr[], int size);

/** 复制数组(需free) */
double* copy_double_array(double arr[], int size);

/** 最大绝对值 */
double max_abs_double_array(double arr[], int size);

/** 最小绝对值 */
double min_abs_double_array(double arr[], int size);

/** 第二大元素 */
double second_max_double_array(double arr[], int size);

/** 第二小元素 */
double second_min_double_array(double arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_double_array(double arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_double_array(double arr[], int size);

/** 打印数组元素 */
void print_char_array(char arr[], int size);

/** 数组元素求和 */
int sum_char_array(char arr[], int size);

/** 数组平均值 */
double avg_char_array(char arr[], int size);

/** 数组最大值 */
char max_char_array(char arr[], int size);

/** 数组最小值 */
char min_char_array(char arr[], int size);

/** 用指定值填充数组 */
void fill_char_array(char arr[], int size, char value);

/** 反转数组 */
void reverse_char_array(char arr[], int size);

/** 查找元素下标 */
int find_char_array(char arr[], int size, char target);

/** 统计元素出现次数 */
int count_char_array(char arr[], int size, char target);

/** 数组元素乘积 */
int product_char_array(char arr[], int size);

/** 复制数组(需free) */
char* copy_char_array(char arr[], int size);

/** 最大绝对值 */
char max_abs_char_array(char arr[], int size);

/** 最小绝对值 */
char min_abs_char_array(char arr[], int size);

/** 第二大元素 */
char second_max_char_array(char arr[], int size);

/** 第二小元素 */
char second_min_char_array(char arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_char_array(char arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_char_array(char arr[], int size);

/** 打印数组元素 */
void print_uint8_array(uint8_t arr[], int size);

/** 数组元素求和 */
unsigned long long sum_uint8_array(uint8_t arr[], int size);

/** 数组平均值 */
double avg_uint8_array(uint8_t arr[], int size);

/** 数组最大值 */
uint8_t max_uint8_array(uint8_t arr[], int size);

/** 数组最小值 */
uint8_t min_uint8_array(uint8_t arr[], int size);

/** 用指定值填充数组 */
void fill_uint8_array(uint8_t arr[], int size, uint8_t value);

/** 反转数组 */
void reverse_uint8_array(uint8_t arr[], int size);

/** 查找元素下标 */
int find_uint8_array(uint8_t arr[], int size, uint8_t target);

/** 统计元素出现次数 */
int count_uint8_array(uint8_t arr[], int size, uint8_t target);

/** 数组元素乘积 */
unsigned long long product_uint8_array(uint8_t arr[], int size);

/** 复制数组(需free) */
uint8_t* copy_uint8_array(uint8_t arr[], int size);

/** 第二大元素 */
uint8_t second_max_uint8_array(uint8_t arr[], int size);

/** 第二小元素 */
uint8_t second_min_uint8_array(uint8_t arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_uint8_array(uint8_t arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_uint8_array(uint8_t arr[], int size);

/** 打印数组元素 */
void print_uint16_array(uint16_t arr[], int size);

/** 数组元素求和 */
unsigned long long sum_uint16_array(uint16_t arr[], int size);

/** 数组平均值 */
double avg_uint16_array(uint16_t arr[], int size);

/** 数组最大值 */
uint16_t max_uint16_array(uint16_t arr[], int size);

/** 数组最小值 */
uint16_t min_uint16_array(uint16_t arr[], int size);

/** 用指定值填充数组 */
void fill_uint16_array(uint16_t arr[], int size, uint16_t value);

/** 反转数组 */
void reverse_uint16_array(uint16_t arr[], int size);

/** 查找元素下标 */
int find_uint16_array(uint16_t arr[], int size, uint16_t target);

/** 统计元素出现次数 */
int count_uint16_array(uint16_t arr[], int size, uint16_t target);

/** 数组元素乘积 */
unsigned long long product_uint16_array(uint16_t arr[], int size);

/** 复制数组(需free) */
uint16_t* copy_uint16_array(uint16_t arr[], int size);

/** 第二大元素 */
uint16_t second_max_uint16_array(uint16_t arr[], int size);

/** 第二小元素 */
uint16_t second_min_uint16_array(uint16_t arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_uint16_array(uint16_t arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_uint16_array(uint16_t arr[], int size);

/** 打印数组元素 */
void print_uint32_array(uint32_t arr[], int size);

/** 数组元素求和 */
unsigned long long sum_uint32_array(uint32_t arr[], int size);

/** 数组平均值 */
double avg_uint32_array(uint32_t arr[], int size);

/** 数组最大值 */
uint32_t max_uint32_array(uint32_t arr[], int size);

/** 数组最小值 */
uint32_t min_uint32_array(uint32_t arr[], int size);

/** 用指定值填充数组 */
void fill_uint32_array(uint32_t arr[], int size, uint32_t value);

/** 反转数组 */
void reverse_uint32_array(uint32_t arr[], int size);

/** 查找元素下标 */
int find_uint32_array(uint32_t arr[], int size, uint32_t target);

/** 统计元素出现次数 */
int count_uint32_array(uint32_t arr[], int size, uint32_t target);

/** 数组元素乘积 */
unsigned long long product_uint32_array(uint32_t arr[], int size);

/** 复制数组(需free) */
uint32_t* copy_uint32_array(uint32_t arr[], int size);

/** 第二大元素 */
uint32_t second_max_uint32_array(uint32_t arr[], int size);

/** 第二小元素 */
uint32_t second_min_uint32_array(uint32_t arr[], int size);

/** 判断数组是否升序 */
int is_sorted_asc_uint32_array(uint32_t arr[], int size);

/** 判断数组是否降序 */
int is_sorted_desc_uint32_array(uint32_t arr[], int size);


// ============================================================
//                     数组统计（自动生成）
// ============================================================

/** 平均值(double数组) */
double mean_double_array(double arr[], int size);

/** 中位数(double数组) */
double median_double_array(double arr[], int size);

/** 众数(int数组，返回出现最多的值) */
int mode_int_array(int arr[], int size);

/** 方差(double数组) */
double variance_double_array(double arr[], int size);

/** 标准差(double数组) */
double stddev_double_array(double arr[], int size);

/** 极差(最大值-最小值) */
double range_double_array(double arr[], int size);

/** 分位数(p为0~1) */
double percentile_double_array(double arr[], int size, double p);

/** 几何平均数 */
double geometric_mean_double(double arr[], int size);

/** 调和平均数 */
double harmonic_mean_double(double arr[], int size);


// ============================================================
//                     数组查询与谓词（自动生成）
// ============================================================

/** 数组是否有重复 */
int has_duplicates_int(int arr[], int size);

/** 数组是否全部为正 */
int all_positive_int(int arr[], int size);

/** 数组是否全部为负 */
int all_negative_int(int arr[], int size);

/** 数组是否全部为偶数 */
int all_even_int(int arr[], int size);

/** 数组是否全部为奇数 */
int all_odd_int(int arr[], int size);

/** 统计大于 value 的元素个数 */
int count_greater_int(int arr[], int size, int value);

/** 统计小于 value 的元素个数 */
int count_less_int(int arr[], int size, int value);

/** 统计区间 [lo,hi] 内元素个数 */
int count_between_int(int arr[], int size, int lo, int hi);

/** 统计偶数个数 */
int count_even_int(int arr[], int size);

/** 统计奇数个数 */
int count_odd_int(int arr[], int size);

/** 统计正数个数 */
int count_positive_int(int arr[], int size);

/** 统计负数个数 */
int count_negative_int(int arr[], int size);

/** 统计零元素个数 */
int count_zero_int(int arr[], int size);

/** 数组是否包含 value */
int contains_int(int arr[], int size, int value);

/** 两个数组是否相等 */
int arrays_equal_int(int a[], int b[], int size);

/** a 是否为 b 的子集 */
int is_subset_int(int a[], int na, int b[], int nb);

/** 出现次数最多的元素 */
int most_frequent_int(int arr[], int size);


// ============================================================
//                     数组变换（自动生成）
// ============================================================

/** 每个元素平方(原地) */
void map_square_int(int arr[], int size);

/** 每个元素取反(原地) */
void map_negate_int(int arr[], int size);

/** 每个元素翻倍(原地) */
void map_double_int(int arr[], int size);

/** 每个元素加 offset */
void map_add_int(int arr[], int size, int offset);

/** 数组裁剪到 [lo,hi] */
void clip_array_int(int arr[], int size, int lo, int hi);

/** 前缀和(原地覆盖) */
void cumulative_sum_int(int arr[], int size);

/** 前缀积(原地覆盖) */
void cumulative_product_int(int arr[], int size);

/** 前缀最小值(原地覆盖) */
void prefix_min_int(int arr[], int size);

/** 前缀最大值(原地覆盖) */
void prefix_max_int(int arr[], int size);

/** 相邻元素差分(原地) */
void differences_int(int arr[], int size);

/** 拼接两个数组(需free) */
int* concat_int_arrays(int a[], int na, int b[], int nb, int *out_size);


// ============================================================
//                     排序算法(补充)（自动生成）
// ============================================================

/** 希尔排序 */
void shell_sort(int arr[], int size);

/** 鸡尾酒排序 */
void cocktail_sort(int arr[], int size);

/** 侏儒排序 */
void gnome_sort(int arr[], int size);

/** 梳排序 */
void comb_sort(int arr[], int size);

/** 圈排序 */
void cycle_sort(int arr[], int size);

/** 计数排序(值域0~max_val) */
void counting_sort(int arr[], int size, int max_val);

/** 基数排序 */
void radix_sort(int arr[], int size);

/** 双调排序 */
void bitonic_sort(int arr[], int size);


// ============================================================
//                     查找算法(补充)（自动生成）
// ============================================================

/** 下界：第一个 >= target 的下标 */
int lower_bound_int(int arr[], int size, int target);

/** 上界：第一个 > target 的下标 */
int upper_bound_int(int arr[], int size, int target);

/** 指数查找(升序) */
int exponential_search(int arr[], int size, int target);

/** 跳跃查找(升序，步长 sqrt) */
int jump_search(int arr[], int size, int target);

/** 三分查找(单峰数组最大值) */
double ternary_search_max(double arr[], int size);

/** 浮点二分查找(升序) */
int binary_search_double(double arr[], int size, double target);

/** 线性查找全部匹配下标(需free) */
int* find_all_int(int arr[], int size, int target, int *count);


// ============================================================
//                     字符串工具(扩展)（自动生成）
// ============================================================

/** 返回大写副本(需free) */
char* str_upper_copy(const char *str);

/** 返回小写副本(需free) */
char* str_lower_copy(const char *str);

/** 返回反转副本(需free) */
char* str_reverse_copy(const char *str);

/** 返回去空格副本(需free) */
char* str_trim_copy(const char *str);

/** 左侧补齐到 length 位 */
void str_pad_left(char *buf, int buf_size, char pad, int length);

/** 右侧补齐到 length 位 */
void str_pad_right(char *buf, int buf_size, char pad, int length);

/** 截断到 max_len */
void str_truncate(char *str, int max_len);

/** 重复字符串 times 次写入 buf */
void str_repeat(char *buf, int buf_size, const char *str, int times);

/** 统计子串出现次数 */
int str_count_substr(const char *str, const char *sub);

/** 判断是否全为字母 */
int str_is_alpha(const char *str);

/** 判断是否全为数字 */
int str_is_digit(const char *str);

/** 判断是否全为字母数字 */
int str_is_alnum(const char *str);

/** 判断是否全为小写 */
int str_is_lower(const char *str);

/** 判断是否全为大写 */
int str_is_upper(const char *str);

/** 大小写互换(原地) */
void str_swap_case(char *str);

/** 单词首字母大写(原地) */
void str_title_case(char *str);

/** 删除所有空白字符(原地) */
void str_remove_whitespace(char *str);

/** 删除所有元音(原地) */
void str_remove_vowels(char *str);

/** 是否互为字母异位词 */
int str_are_anagrams(const char *a, const char *b);

/** 是否为子序列 */
int str_is_subsequence(const char *s, const char *t);

/** 取前 n 个字符 */
char* str_left(const char *str, int n, char *buf, int buf_size);

/** 取后 n 个字符 */
char* str_right(const char *str, int n, char *buf, int buf_size);

/** 统计行数 */
int str_count_lines(const char *str);

/** 最长单词长度 */
int str_longest_word_len(const char *str);

/** 出现最多的字符 */
char str_most_common_char(const char *str);

/** 统计元音个数 */
int str_count_vowels(const char *str);

/** 凯撒加密(原地) */
void str_caesar_shift(char *str, int shift);

/** ROT13 加密(原地) */
void str_rot13(char *str);


// ============================================================
//                     字符工具（自动生成）
// ============================================================

/** 是否大写字母 */
int is_upper_char(char c);

/** 是否小写字母 */
int is_lower_char(char c);

/** 是否十六进制字符 */
int is_hex_char(char c);

/** 是否八进制字符 */
int is_octal_char(char c);

/** 是否可打印字符 */
int is_printable_char(char c);

/** 是否标点字符 */
int is_punctuation_char(char c);

/** 是否元音 */
int is_vowel_char(char c);

/** 是否辅音 */
int is_consonant_char(char c);

/** 下一个字符 */
char next_char(char c);

/** 上一个字符 */
char prev_char(char c);

/** 字符循环右移 n */
char char_rotate(char c, int n);

/** 数字字符转数值 */
int digit_char_to_int(char c);

/** 数值转数字字符(0~9) */
char int_to_digit_char(int v);


// ============================================================
//                     数论与数学(扩展)（自动生成）
// ============================================================

/** 是否偶数 */
int is_even(int n);

/** 是否奇数 */
int is_odd(int n);

/** 是否完全平方数 */
int is_square(int n);

/** 是否完全立方数 */
int is_cube(int n);

/** 数字根(数位反复求和) */
int digital_root(int n);

/** 第 n 个素数 */
int nth_prime(int n);

/** 下一个素数(大于 n) */
int next_prime(int n);

/** 上一个素数(小于 n) */
int prev_prime(int n);

/** n 以内素数个数 */
int count_primes_upto(int n);

/** n 以内素数之和 */
long long sum_primes_upto(int n);

/** 组合数 C(n,r) */
long long binomial_coefficient(int n, int r);

/** 排列数 P(n,r) */
long long permutation_count(int n, int r);

/** 第 n 个调和数 */
double harmonic_number(int n);

/** 是否盈数(真因子和>自身) */
int is_abundant(int n);

/** 是否亏数 */
int is_deficient(int n);

/** 是否亲和数对(a,b) */
int is_amicable(int a, int b);

/** 是否快乐数 */
int is_happy(int n);

/** 是否哈沙德数(可被数位和整除) */
int is_harshad(int n);

/** 是否卡普雷卡数 */
int is_kaprekar(int n);

/** 是否自守数 */
int is_automorphic(int n);

/** 是否三角形数 */
int is_triangular(int n);

/** 科拉兹猜想步数 */
int collatz_steps(int n);

/** 真因子之和(别名) */
int aliquot_sum(int n);

/** 因子个数 */
int count_divisors(int n);

/** 因子之和 */
long long sum_divisors(int n);

/** 欧拉函数 φ(n) */
int euler_phi(int n);

/** 双阶乘 n!! */
long long double_factorial(int n);

/** 第 n 个卡塔兰数 */
long long catalan_number(int n);

/** n 个圆盘汉诺塔最少步数 */
long long hanoi_moves(int n);

/** 约瑟夫环幸存者 */
int josephus(int n, int k);

/** 弧度转角度 */
double radians_to_degrees(double rad);

/** 角度转弧度 */
double degrees_to_radians(double deg);

/** Sigmoid 函数 */
double sigmoid(double x);

/** ReLU 函数 */
double relu(double x);

/** 角度归一化到 [0,360) */
double angle_normalize(double deg);

/** 四舍五入(到整数) */
long long round_half_up(double x);

/** 百分比 */
double percentage(double part, double total);

/** 三个数的中位数 */
double median_of_three(double a, double b, double c);

/** 加权平均 */
double weighted_average(double values[], double weights[], int size);


// ============================================================
//                     进制与转换(扩展)（自动生成）
// ============================================================

/** 十进制转任意进制(2~36) */
char* int_to_base_str(int num, int base, char *buf, int buf_size);

/** 任意进制字符串转十进制 */
long base_str_to_int(const char *str, int base);

/** 字符串转 long */
long str_to_long(const char *str);

/** 字符串转 double */
double str_to_double(const char *str);

/** double 转字符串 */
char* double_to_str(double num, char *buf);

/** 十进制转罗马数字 */
char* int_to_roman(int num, char *buf, int buf_size);

/** 罗马数字转十进制 */
int roman_to_int(const char *s);

/** 千位分隔符格式化 */
char* format_thousands(long long num, char *buf, int buf_size);

/** 字节大小格式化(KB/MB/GB) */
char* format_bytes(long long bytes, char *buf, int buf_size);


// ============================================================
//                     位运算(扩展)（自动生成）
// ============================================================

/** 读取第 bit 位(0/1) */
int get_bit(uint32_t val, int bit);

/** 把第 bit 位设为 value(0/1) */
uint32_t set_bit_value(uint32_t val, int bit, int value);

/** 统计 0 的个数 */
int count_zeros(uint32_t val);

/** 最高位 1 的位置(0~31) */
int msb_position(uint32_t val);

/** 下一个 2 的幂 */
uint32_t next_power_of_two(uint32_t n);

/** 上一个 2 的幂 */
uint32_t prev_power_of_two(uint32_t n);

/** 反转二进制位 */
uint32_t reverse_bits(uint32_t val);

/** 取高 4 位 */
uint8_t nibble_high(uint8_t val);

/** 取低 4 位 */
uint8_t nibble_low(uint8_t val);

/** 交换高低 4 位 */
uint8_t nibble_swap(uint8_t val);

/** 取位域(从 start 起 len 位) */
uint32_t bit_field_get(uint32_t val, int start, int len);

/** 把位域写入(从 start 起 len 位) */
uint32_t bit_field_set(uint32_t val, int start, int len, uint32_t data);

/** 生成低 n 位全 1 掩码 */
uint32_t low_bit_mask(int n);

/** 生成高 n 位全 1 掩码 */
uint32_t high_bit_mask(int n);

/** 无临时变量交换 */
void swap_no_temp(int *a, int *b);

/** 判断二进制是否为连续 1 */
int is_mask_contiguous(uint32_t val);

/** 整数符号(1/-1/0) */
int sign_int(int n);


// ============================================================
//                     校验与CRC(扩展)（自动生成）
// ============================================================

/** CRC-16/CCITT */
uint16_t crc16_ccitt(const uint8_t *data, uint16_t len);

/** CRC-16/XMODEM */
uint16_t crc16_xmodem(const uint8_t *data, uint16_t len);

/** CRC-32 */
uint32_t crc32(const uint8_t *data, uint16_t len);

/** Fletcher-16 校验 */
uint16_t fletcher16(const uint8_t *data, uint16_t len);

/** Fletcher-32 校验 */
uint32_t fletcher32(const uint16_t *data, uint16_t len);

/** Adler-32 校验 */
uint32_t adler32(const uint8_t *data, uint16_t len);

/** LRC 纵向冗余校验 */
uint8_t lrc_checksum(const uint8_t *data, uint16_t len);

/** 加权校验和 */
uint16_t weighted_checksum(const uint8_t *data, uint16_t len);

/** NMEA 校验($ 与 * 之间异或) */
uint8_t nmea_checksum(const char *sentence);


// ============================================================
//                     哈希函数(扩展)（自动生成）
// ============================================================

/** RS 哈希 */
uint32_t rshash(const char *str);

/** JS 哈希 */
uint32_t jshash(const char *str);

/** PJW 哈希 */
uint32_t pjwhash(const char *str);

/** ELF 哈希 */
uint32_t elfhash(const char *str);

/** AP 哈希 */
uint32_t aphash(const char *str);

/** Java 字符串哈希 */
uint32_t java_hash(const char *str);

/** DJB2-XOR 哈希 */
uint32_t djb2_xor_hash(const char *str);

/** FNV-1 哈希 */
uint32_t fnv1_hash(const char *str);

/** DEK 哈希 */
uint32_t dekhash(const char *str);

/** BP 哈希 */
uint32_t bphash(const char *str);

/** BKDR 哈希(可指定种子) */
uint32_t bkdr_hash_seed(const char *str, uint32_t seed);


// ============================================================
//                     时间与日期（自动生成）
// ============================================================

/** 判断日期是否有效 */
int is_valid_date(int year, int month, int day);

/** 某月天数 */
int days_in_month(int year, int month);

/** 一年中的第几天 */
int day_of_year(int year, int month, int day);

/** 一年有多少天 */
int days_in_year(int year);

/** 当前年 */
int get_year_now(void);

/** 当前月(1~12) */
int get_month_now(void);

/** 当前日(1~31) */
int get_day_now(void);

/** 当前小时(0~23) */
int get_hour_now(void);

/** 当前分钟(0~59) */
int get_minute_now(void);

/** 当前秒(0~59) */
int get_second_now(void);

/** 当前星期几(0=周日) */
int get_weekday_now(void);

/** 时间戳转日期字符串 */
char* timestamp_to_date_str(long long ts, char *buf, int buf_size);


// ============================================================
//                     随机工具（自动生成）
// ============================================================

/** 用当前时间设置随机种子 */
void rand_seed_time(void);

/** 随机布尔值 */
int rand_bool(void);

/** 随机浮点数 [0,1) */
double rand_double(void);

/** 随机浮点数 [min,max) */
double rand_double_range(double min, double max);

/** 随机选择数组元素 */
int rand_choice_int(int arr[], int size);

/** 生成随机字符串(可打印字符) */
char* rand_string(char *buf, int buf_size, int len);

/** 生成随机数字字符串 */
char* rand_digits_string(char *buf, int buf_size, int len);

/** 打乱字符串(原地) */
void rand_shuffle_str(char *str);

/** 在 [min,max] 生成 n 个不重复随机数 */
int* rand_unique_ints(int min, int max, int n);


// ============================================================
//                     几何工具（自动生成）
// ============================================================

/** 二维两点距离 */
double distance_2d(double x1, double y1, double x2, double y2);

/** 三维两点距离 */
double distance_3d(double x1, double y1, double z1, double x2, double y2, double z2);

/** 海伦公式三角形面积 */
double area_triangle_heron(double a, double b, double c);

/** 三角形周长 */
double perimeter_triangle(double a, double b, double c);

/** 圆面积 */
double circle_area(double r);

/** 圆周长 */
double circle_circumference(double r);

/** 圆直径 */
double circle_diameter(double r);

/** 球体积 */
double sphere_volume(double r);

/** 球表面积 */
double sphere_surface_area(double r);

/** 矩形面积 */
double rect_area(double w, double h);

/** 矩形周长 */
double rect_perimeter(double w, double h);

/** 点是否在矩形内 */
int is_point_in_rect(double px, double py, double x, double y, double w, double h);

/** 点是否在圆内 */
int is_point_in_circle(double px, double py, double cx, double cy, double r);

/** 两点斜率 */
double slope_between(double x1, double y1, double x2, double y2);

/** 二维中点 */
void midpoint_2d(double x1, double y1, double x2, double y2, double *mx, double *my);

/** 正六边形面积 */
double hexagon_area(double side);

/** 圆柱体积 */
double cylinder_volume(double r, double h);


// ============================================================
//                     数值工具（自动生成）
// ============================================================

/** 整数裁剪到 [lo,hi] */
int clamp_int(int v, int lo, int hi);

/** 浮点裁剪到 [lo,hi] */
double clamp_double(double v, double lo, double hi);

/** 线性插值 */
double lerp_double(double a, double b, double t);

/** 整数线性插值 */
int lerp_int(int a, int b, int t, int max_t);

/** 数值映射(从 [s1,s2] 到 [d1,d2]) */
double map_range_double(double v, double s1, double s2, double d1, double d2);

/** 取整到最近整数 */
long long round_to_int(double x);

/** 向上取整到 m 的倍数 */
long long ceil_to_multiple(long long v, long long m);

/** 向下取整到 m 的倍数 */
long long floor_to_multiple(long long v, long long m);

/** 是否近似相等(误差 eps) */
int approx_equal_double(double a, double b, double eps);

/** 三数最大值 */
int max3_int(int a, int b, int c);

/** 三数最小值 */
int min3_int(int a, int b, int c);

/** 四数最大值 */
int max4_int(int a, int b, int c, int d);

/** 浮点绝对值 */
double fabs_double(double x);

/** 高斯取整(向下取整) */
long long floor_int(double x);

/** 向上取整 */
long long ceil_int(double x);

/** 自然数 1..n 之和 */
long long sum_natural(int n);

/** 平方和 1^2+..+n^2 */
long long sum_squares(int n);

/** 立方和 1^3+..+n^3 */
long long sum_cubes(int n);

/** 等差数列前 n 项和 */
long long arithmetic_sum(long long a1, long long d, int n);


// ============================================================
//                     数据结构(扩展)（自动生成）
// ============================================================

/** 创建空双向链表 */
DList* dlist_create(void);

/** 头部插入 */
int dlist_push_front(DList *l, int data);

/** 尾部插入 */
int dlist_push_back(DList *l, int data);

/** 删除第一个等于 data 的节点 */
int dlist_remove(DList *l, int data);

/** 查找节点 */
DNode* dlist_search(DList *l, int data);

/** 链表长度 */
int dlist_length(DList *l);

/** 正序打印 */
void dlist_print(DList *l);

/** 反转链表 */
void dlist_reverse(DList *l);

/** 释放链表 */
void dlist_free(DList *l);

/** 创建双端队列 */
Deque* deque_create(int capacity);

/** 销毁双端队列 */
void deque_destroy(Deque *d);

/** 头部入队 */
int deque_push_front(Deque *d, int value);

/** 尾部入队 */
int deque_push_back(Deque *d, int value);

/** 头部出队 */
int deque_pop_front(Deque *d, int *out);

/** 尾部出队 */
int deque_pop_back(Deque *d, int *out);

/** 查看头部 */
int deque_peek_front(Deque *d, int *out);

/** 查看尾部 */
int deque_peek_back(Deque *d, int *out);

/** 元素个数 */
int deque_size(Deque *d);

/** 是否为空 */
int deque_is_empty(Deque *d);

/** 是否已满 */
int deque_is_full(Deque *d);

/** 清空 */
void deque_clear(Deque *d);

/** 创建最小堆 */
MinHeap* mheap_create(int capacity);

/** 销毁最小堆 */
void mheap_destroy(MinHeap *h);

/** 入堆 */
int mheap_push(MinHeap *h, int value);

/** 弹出最小值 */
int mheap_pop(MinHeap *h, int *out);

/** 查看最小值 */
int mheap_peek(MinHeap *h, int *out);

/** 堆大小 */
int mheap_size(MinHeap *h);

/** 堆是否为空 */
int mheap_is_empty(MinHeap *h);

/** 创建整数集合 */
IntSet* iset_create(int capacity);

/** 销毁整数集合 */
void iset_destroy(IntSet *s);

/** 添加元素 */
int iset_add(IntSet *s, int key);

/** 是否包含元素 */
int iset_contains(IntSet *s, int key);

/** 删除元素 */
int iset_remove(IntSet *s, int key);

/** 元素个数 */
int iset_size(IntSet *s);

/** 清空集合 */
void iset_clear(IntSet *s);

/** 创建字符串哈希表 */
StrMap* smap_create(int capacity);

/** 销毁哈希表 */
void smap_destroy(StrMap *m);

/** 写入键值对 */
int smap_put(StrMap *m, const char *key, int value);

/** 读取键对应的值 */
int smap_get(StrMap *m, const char *key, int *out);

/** 是否包含键 */
int smap_contains(StrMap *m, const char *key);

/** 删除键 */
int smap_remove(StrMap *m, const char *key);

/** 键值对数量 */
int smap_size(StrMap *m);

/** 创建 n 个节点的图 */
Graph* graph_create(int n);

/** 销毁图 */
void graph_destroy(Graph *g);

/** 添加无向边 */
void graph_add_edge(Graph *g, int u, int v);

/** 删除无向边 */
void graph_remove_edge(Graph *g, int u, int v);

/** 是否有边 */
int graph_has_edge(Graph *g, int u, int v);

/** 节点度数 */
int graph_degree(Graph *g, int v);

/** 打印邻接矩阵 */
void graph_print(Graph *g);

/** 广度优先遍历(打印) */
void graph_bfs(Graph *g, int start);

/** 深度优先遍历(打印) */
void graph_dfs(Graph *g, int start);

/** Dijkstra 单源最短路(需free) */
int* graph_dijkstra(Graph *g, int src);


// ============================================================
//                     文件工具(扩展)（自动生成）
// ============================================================

/** 追加一行 */
int file_append_line(const char *filename, const char *line);

/** 文件是否为空 */
int file_is_empty(const char *filename);

/** 创建空文件 */
int file_touch(const char *filename);

/** 删除文件 */
int file_delete(const char *filename);

/** 重命名文件 */
int file_rename(const char *old, const char *new);

/** 取文件主名(不含扩展名) */
char* file_stem(const char *path, char *buf, int buf_size);

/** 读取一行到缓冲区 */
char* file_read_line(FILE *fp, char *buf, int buf_size);


// ============================================================
//                     内存工具(扩展)（自动生成）
// ============================================================

/** 复制内存块(需free) */
void* safe_memdup(const void *src, size_t size);

/** 内存清零 */
void zero_memory(void *ptr, size_t size);

/** 内存填充 */
void fill_memory(void *ptr, size_t size, unsigned char value);

/** 内存比较 */
int compare_memory(const void *a, const void *b, size_t size);

/** 交换内存块 */
void swap_memory(void *a, void *b, size_t size);


// ============================================================
//                     控制台与调试(扩展)（自动生成）
// ============================================================

/** 打印整数 */
void print_int(int v);

/** 打印长整数 */
void print_long(long v);

/** 打印浮点数 */
void print_double(double v);

/** 打印十六进制 */
void print_hex(unsigned int v);

/** 打印单个字符 */
void print_char(char c);

/** 打印分隔线 */
void print_separator(void);

/** 打印带边框标题 */
void print_box_title(const char *title);

/** 打印字符串数组 */
void print_str_array(char *arr[], int size);

/** 清空控制台 */
void clear_console(void);

/** 打印信息日志 */
void log_info(const char *msg);

/** 打印警告日志 */
void log_warn(const char *msg);

/** 打印错误日志 */
void log_error(const char *msg);


// ============================================================
//                     矩阵工具（自动生成）
// ============================================================

/** 创建 rows x cols 双精度矩阵 */
double** mat_create(int rows, int cols);

/** 释放矩阵 */
void mat_free(double **m, int rows);

/** 用值填充矩阵 */
void mat_fill(double **m, int rows, int cols, double v);

/** 打印矩阵 */
void mat_print(double **m, int rows, int cols);

/** 矩阵转置(写入 out) */
void mat_transpose(double **m, int rows, int cols, double **out);

/** 矩阵加法(out = a + b) */
void mat_add(double **a, double **b, int rows, int cols, double **out);

/** 矩阵减法(out = a - b) */
void mat_sub(double **a, double **b, int rows, int cols, double **out);

/** 矩阵乘法(out = a * b) */
void mat_mul(double **a, int ar, int ac, double **b, int bc, double **out);

/** 单位矩阵 */
void mat_identity(double **m, int n);

/** 数乘矩阵 */
void mat_scalar_mul(double **m, int rows, int cols, double s, double **out);

/** 方阵迹(对角线之和) */
double mat_trace(double **m, int n);

/** 2x2 行列式 */
double mat_det2(double **m);

/** 3x3 行列式 */
double mat_det3(double **m);

/** 矩阵元素和 */
double mat_sum(double **m, int rows, int cols);

/** 矩阵最大值 */
double mat_max(double **m, int rows, int cols);

/** 矩阵最小值 */
double mat_min(double **m, int rows, int cols);

/** 行元素和 */
double mat_row_sum(double **m, int cols, int row);

/** 列元素和 */
double mat_col_sum(double **m, int rows, int col);

/** 复制矩阵 */
double** mat_copy(double **m, int rows, int cols);


// ============================================================
//                     向量与杂项（自动生成）
// ============================================================

/** 向量点积 */
double dot_product(double a[], double b[], int size);

/** 二维向量长度 */
double vector_length_2d(double x, double y);

/** 三维向量长度 */
double vector_length_3d(double x, double y, double z);

/** 二维向量归一化(写入 out) */
void normalize_2d(double x, double y, double *ox, double *oy);

/** 二维叉积(带符号面积) */
double cross_product_2d(double ax, double ay, double bx, double by);

/** 移动平均(写入 out) */
void moving_average(double arr[], int size, int window, double out[]);

/** 整数数组转 double 数组 */
void int_array_to_double(int src[], double dst[], int size);

/** double 数组转 int 数组 */
void double_array_to_int(double src[], int dst[], int size);

/** Base64 编码(需free) */
char* base64_encode(const uint8_t *data, int len);

/** Base64 解码(需free) */
uint8_t* base64_decode(const char *s, int *out_len);

/** URL 编码(需free) */
char* url_encode_str(const char *s);


// ============================================================
//                     字符串工具(第二批)（自动生成）
// ============================================================

/** 忽略大小写判断是否包含子串 */
int str_contains_ignore_case(const char *haystack, const char *needle);

/** 忽略大小写比较字符串 */
int str_compare_case_insensitive(const char *a, const char *b);

/** 忽略大小写判断回文 */
int str_is_palindrome_ignore_case(const char *str);

/** 反转每个单词内部的字母 */
void str_reverse_each_word(char *str);

/** 字符串左循环移动 n 位 */
void str_shift_left(char *str, int n);

/** 字符串右循环移动 n 位 */
void str_shift_right(char *str, int n);

/** 去除相邻重复字符 */
void str_deduplicate_chars(char *str);

/** 删除所有辅音字母 */
void str_remove_consonants(char *str);

/** 统计辅音字母个数 */
int str_count_consonants(const char *str);

/** 尾部追加一个字符 */
void str_append_char(char *buf, int buf_size, char c);

/** 删除第一个字符 */
void str_remove_first_char(char *str);

/** 删除最后一个字符 */
void str_remove_last_char(char *str);

/** 查找第 n 次出现的子串下标(0起) */
int str_find_nth(const char *str, const char *sub, int n);

/** 统计数字字符个数 */
int str_count_digits(const char *str);

/** 统计字母个数 */
int str_count_letters(const char *str);

/** 统计大写字母个数 */
int str_count_uppercase(const char *str);

/** 统计小写字母个数 */
int str_count_lowercase(const char *str);

/** 统计空格个数 */
int str_count_spaces(const char *str);

/** 把连续多个空格合并为一个 */
void str_normalize_spaces(char *str);

/** 取每个单词首字母缩写 */
char* str_abbreviate(const char *str, char *buf, int buf_size);

/** 提取第 n 个单词(0起) */
char* str_word_at(const char *str, int n, char *buf, int buf_size);

/** 敏感信息打码(保留后4位) */
char* str_mask_sensitive(const char *str, char *buf, int buf_size);

/** 简单邮箱格式校验 */
int str_is_valid_email(const char *s);

/** 统计句子数(. ! ?) */
int str_count_sentences(const char *str);

/** 最长回文子串长度(动态规划) */
int str_longest_palindrome_substr_len(const char *s);

/** 反转元音字母顺序 */
void str_reverse_vowels(char *str);

/** 删除所有数字 */
void str_remove_digits(char *str);

/** 只保留数字 */
void str_keep_digits_only(char *str);

/** 只保留字母 */
void str_keep_letters_only(char *str);

/** 用字符填满缓冲区 */
void str_fill(char *buf, int buf_size, char c, int len);

/** 交换两个位置的字符 */
void str_swap_chars(char *str, int i, int j);

/** 最短单词长度 */
int str_shortest_word_len(const char *str);

/** 平均单词长度 */
double str_avg_word_len(const char *str);

/** 字符串是否为空 */
int str_is_empty(const char *str);


// ============================================================
//                     数论与数学(第二批)（自动生成）
// ============================================================

/** 三数最大公约数 */
int gcd3(int a, int b, int c);

/** 四数最大公约数 */
int gcd4(int a, int b, int c, int d);

/** 三数最小公倍数 */
long long lcm3(int a, int b, int c);

/** 是否互质 */
int is_relatively_prime(int a, int b);

/** 模加法 (a+b)%m */
long long mod_add(long long a, long long b, long long m);

/** 模减法 (a-b)%m */
long long mod_sub(long long a, long long b, long long m);

/** 模乘法 (a*b)%m */
long long mod_mul(long long a, long long b, long long m);

/** 模逆元(需互质，否则-1) */
int mod_inverse(int a, int m);

/** 快速加倍法求斐波那契 */
long long fast_fibonacci(int n);

/** 整数平方根 */
int integer_sqrt(int n);

/** 整数立方根 */
int integer_cbrt(int n);

/** log2 向下取整 */
int log2_floor(int n);

/** log10 向下取整 */
int log10_floor(int n);

/** 阶乘取模 n! % m */
long long factorial_mod(int n, long long m);

/** 是否为斐波那契数 */
int is_fibonacci_number(int n);

/** n 在 base 进制下的位数 */
int count_digits_in_base(int n, int base);

/** 是否为半素数(两素数之积) */
int is_semiprime(int n);

/** 是否为回文素数 */
int is_palindromic_prime(int n);

/** 字符串是否只含0/1 */
int is_binary_str(const char *s);

/** 字符串是否只含八进制字符 */
int is_octal_str(const char *s);

/** 字符串是否为十进制数 */
int is_decimal_str(const char *s);

/** 字符串是否为十六进制数 */
int is_hex_str(const char *s);

/** 字符串是否为数字(可带符号) */
int is_number_string(const char *s);

/** Stein 二进制最大公约数 */
int gcd_binary(int a, int b);

/** 到下一个素数的间隔 */
int prime_gap(int n);

/** 二进制末尾 0 的个数 */
int count_trailing_zeros(uint32_t n);

/** 是否为 3 的幂 */
int is_power_of_three(int n);

/** 是否为 4 的幂 */
int is_power_of_four(int n);

/** 数字 d 在 n 中出现次数 */
int digit_frequency(int n, int d);


// ============================================================
//                     数组工具(第二批)（自动生成）
// ============================================================

/** 绝对值之和 */
long long sum_abs_int(int arr[], int size);

/** 两个数组点积 */
long long dot_product_int(int a[], int b[], int size);

/** 最长连续相同段长度 */
int longest_run_length(int arr[], int size);

/** 局部极大值下标 */
int find_local_max_idx(int arr[], int size);

/** 局部极小值下标 */
int find_local_min_idx(int arr[], int size);

/** 平衡点下标(左右和相等) */
int equilibrium_index(int arr[], int size);

/** 反转子数组 [lo,hi] */
void reverse_subarray(int arr[], int size, int lo, int hi);

/** 交换两个元素 */
void swap_elements_int(int arr[], int i, int j);

/** 填充递增序列 start..start+n-1 */
void fill_sequence_int(int arr[], int size, int start);

/** 填充随机浮点数范围 */
void fill_random_double_range(double arr[], int size, double min, double max);

/** 删除所有等于 value 的元素 */
int remove_all_value(int arr[], int *size, int value);

/** 不同元素个数 */
int count_distinct_int(int arr[], int size);

/** 最小值下标 */
int array_min_index(int arr[], int size);

/** 最大值下标 */
int array_max_index(int arr[], int size);

/** 倒序打印数组 */
void print_array_reverse_int(int arr[], int size);

/** 是否严格递增 */
int check_sorted_strict(int arr[], int size);

/** 相邻最小差值(需已排序) */
int min_gap(int arr[], int size);

/** 相邻最大差值(需已排序) */
int max_gap(int arr[], int size);


// ============================================================
//                     链表工具(扩展)（自动生成）
// ============================================================

/** 取第 n 个节点的值 */
int list_get_nth(ListNode *head, int n, int *out);

/** 删除第 n 个节点 */
int list_delete_nth(ListNode **head, int n);

/** 在第 n 个位置插入 */
int list_insert_nth(ListNode **head, int n, int data);

/** 检测链表是否有环(快慢指针) */
int list_has_cycle(ListNode *head);

/** 链表中间节点 */
ListNode* list_middle_node(ListNode *head);

/** 由数组构建链表 */
ListNode* list_from_array(int arr[], int size);

/** 链表最大值 */
int list_max(ListNode *head);

/** 链表最小值 */
int list_min(ListNode *head);

/** 链表元素之和 */
long long list_sum(ListNode *head);

/** 链表排序(冒泡) */
void list_sort(ListNode *head);

/** 合并两个升序链表 */
ListNode* list_merge_sorted(ListNode *a, ListNode *b);

/** 把 b 接到 a 末尾(破坏性) */
ListNode* list_append_list(ListNode *a, ListNode *b);

/** 深拷贝链表 */
ListNode* list_clone(ListNode *head);

/** 链表是否升序 */
int list_is_sorted(ListNode *head);

/** 统计值等于 value 的节点数 */
int list_count_value(ListNode *head, int value);

/** 链表右旋 k 次 */
void list_rotate_right(ListNode **head, int k);


// ============================================================
//                     进制转换(第二批)（自动生成）
// ============================================================

/** 定宽二进制字符串(补0) */
char* int_to_binary_padded(int num, int width, char *buf, int buf_size);

/** BCD 码转二进制 */
int bcd_to_binary(int bcd);

/** 二进制转 BCD 码 */
int binary_to_bcd(int n);

/** 浮点位模式转整数 */
int float_bits_to_int(float f);

/** 整数位模式转浮点 */
float int_bits_to_float(int i);

/** 浮点转十六进制字符串 */
char* double_to_hex_str(double d, char *buf);

/** 字符转 ASCII 码 */
int char_to_ascii_code(char c);

/** ASCII 码转字符 */
char ascii_code_to_char(int code);

/** 整数转大端字节 */
void int_to_bytes_be(int val, uint8_t out[4]);

/** 大端字节转整数 */
int bytes_to_int_be(uint8_t b[4]);

/** 定宽十六进制字符串(补0) */
char* int_to_hex_padded(int num, int width, char *buf, int buf_size);


// ============================================================
//                     几何工具(第二批)（自动生成）
// ============================================================

/** 三点坐标三角形面积 */
double triangle_area_coords(double x1, double y1, double x2, double y2, double x3, double y3);

/** 多边形面积(鞋带公式) */
double polygon_area(double x[], double y[], int n);

/** 点到直线距离 */
double distance_point_line(double px, double py, double ax, double ay, double bx, double by);

/** 点到线段距离 */
double distance_point_segment(double px, double py, double ax, double ay, double bx, double by);

/** 扇形面积 */
double area_sector(double r, double angle_rad);

/** 弧长 */
double arc_length(double r, double angle_rad);

/** 正弦(角度制) */
double sin_deg(double deg);

/** 余弦(角度制) */
double cos_deg(double deg);

/** 正切(角度制) */
double tan_deg(double deg);

/** 两向量夹角(弧度) */
double angle_between_vectors(double ax, double ay, double bx, double by);

/** 点是否在线段上 */
int is_point_on_segment(double px, double py, double ax, double ay, double bx, double by);


// ============================================================
//                     数值工具(第二批)（自动生成）
// ============================================================

/** 是否为正数 */
int is_positive_double(double x);

/** 是否为负数 */
int is_negative_double(double x);

/** 是否为零 */
int is_zero_double(double x);

/** 阶跃函数 */
double step_function(double x);

/** 保留 n 位小数 */
double round_to_n_decimals(double x, int n);

/** 整数绝对差 */
int abs_diff_int(int a, int b);

/** 浮点绝对差 */
double abs_diff_double(double a, double b);

/** 两数最大值 */
double max_double(double a, double b);

/** 两数最小值 */
double min_double(double a, double b);

/** 分数约分 */
void reduce_fraction(int num, int den, int *out_num, int *out_den);

/** 是否为有限浮点数 */
int is_finite_double(double x);

/** 是否为 NaN */
int is_nan_double(double x);


// ============================================================
//                     编码与杂项(第二批)（自动生成）
// ============================================================

/** URL 解码(需free) */
char* url_decode_str(const char *s);

/** HTML 转义(需free) */
char* html_escape_str(const char *s);

/** 小写十六进制字符串 */
char* bytes_to_hex_lower(const uint8_t *data, uint16_t len, char *buf, uint16_t buf_size);

/** 十六进制字符串转大写 */
char* hex_str_to_upper(const char *hex, char *buf, int buf_size);


// ============================================================
//                     图算法(第二批)（自动生成）
// ============================================================

/** 图是否连通 */
int graph_is_connected(Graph *g);

/** 无向边数量 */
int graph_edge_count(Graph *g);

/** 图的转置(out 需已分配 n x n) */
void graph_transpose(Graph *g, int **out);

/** u 到 v 是否有路径(BFS) */
int graph_path_exists(Graph *g, int u, int v);


// ============================================================
//                     随机工具(第二批)（自动生成）
// ============================================================

/** 排除某个值的区间随机数 */
int rand_range_excluding(int min, int max, int excl);

/** 填充随机整数列表 */
void rand_fill_int_list(int arr[], int size, int min, int max);

/** 填充随机浮点数组 */
void rand_fill_float_array(double arr[], int size, double min, double max);

/** 随机数字字符 */
char rand_digit_char(void);

/** 随机小写字母 */
char rand_lowercase_char(void);

/** 随机大写字母 */
char rand_uppercase_char(void);

/** 随机字母(大小写) */
char rand_letter_char(void);


// ============================================================
//                     二叉搜索树(第二批)（自动生成）
// ============================================================

/** 最小值 */
int bst_min_value(BSTNode *root);

/** 最大值 */
int bst_max_value(BSTNode *root);

/** 叶子节点数 */
int bst_count_leaves(BSTNode *root);

/** 内部节点数 */
int bst_count_internal(BSTNode *root);

/** 是否为合法 BST */
int bst_is_valid(BSTNode *root);

/** 是否平衡(左右子树高差<=1) */
int bst_is_balanced(BSTNode *root);

/** 镜像翻转(返回新根) */
BSTNode* bst_mirror(BSTNode *root);

/** 两棵树是否相同 */
int bst_same_tree(BSTNode *a, BSTNode *b);

/** 值为 value 的节点深度(根为0) */
int bst_depth_of_value(BSTNode *root, int value);


// ============================================================
//                     矩阵工具(第二批)（自动生成）
// ============================================================

/** 创建全零矩阵 */
double** mat_zeros(int rows, int cols);

/** 创建全一矩阵 */
double** mat_ones(int rows, int cols);

/** 创建单位矩阵 */
double** mat_identity_alloc(int n);

/** 转置并返回新矩阵 */
double** mat_transpose_alloc(double **m, int rows, int cols);

/** 是否对称矩阵 */
int mat_is_symmetric(double **m, int n);

/** 矩阵加标量 */
void mat_add_scalar(double **m, int rows, int cols, double s, double **out);

/** 矩阵取负 */
void mat_negate(double **m, int rows, int cols, double **out);

/** 矩阵元素平均值 */
double mat_avg(double **m, int rows, int cols);

/** 随机填充矩阵 */
void mat_rand_fill(double **m, int rows, int cols, double min, double max);


// ============================================================
//                     数组统计(第二批)（自动生成）
// ============================================================

/** 众数(double数组) */
double mode_double_array(double arr[], int size);

/** 中位数(int数组) */
double median_int_array(int arr[], int size);

/** 方差(int数组) */
double variance_int_array(int arr[], int size);

/** 标准差(int数组) */
double stddev_int_array(int arr[], int size);

/** 极差(int数组) */
int range_int_array(int arr[], int size);


// ============================================================
//                     数组工具(类型变体)（自动生成）
// ============================================================

/** 最小值下标 */
int int_array_min_index(int arr[], int size);

/** 最大值下标 */
int int_array_max_index(int arr[], int size);

/** 统计大于 value 的元素个数 */
int int_array_count_greater(int arr[], int size, int value);

/** 统计小于 value 的元素个数 */
int int_array_count_less(int arr[], int size, int value);

/** 每个元素乘以 scalar */
void int_array_scale(int arr[], int size, int scalar);

/** 每个元素加 offset */
void int_array_add_scalar(int arr[], int size, int offset);

/** 数组是否有重复 */
int int_array_has_duplicates(int arr[], int size);

/** 数组左旋 k 位 */
void int_array_rotate_left(int arr[], int size, int k);

/** 绝对值之和 */
long long int_array_sum_abs(int arr[], int size);

/** 最小值下标 */
int long_array_min_index(long arr[], int size);

/** 最大值下标 */
int long_array_max_index(long arr[], int size);

/** 统计大于 value 的元素个数 */
int long_array_count_greater(long arr[], int size, long value);

/** 统计小于 value 的元素个数 */
int long_array_count_less(long arr[], int size, long value);

/** 每个元素乘以 scalar */
void long_array_scale(long arr[], int size, long scalar);

/** 每个元素加 offset */
void long_array_add_scalar(long arr[], int size, long offset);

/** 数组是否有重复 */
int long_array_has_duplicates(long arr[], int size);

/** 数组左旋 k 位 */
void long_array_rotate_left(long arr[], int size, int k);

/** 绝对值之和 */
long long long_array_sum_abs(long arr[], int size);

/** 最小值下标 */
int long_long_array_min_index(long long arr[], int size);

/** 最大值下标 */
int long_long_array_max_index(long long arr[], int size);

/** 统计大于 value 的元素个数 */
int long_long_array_count_greater(long long arr[], int size, long long value);

/** 统计小于 value 的元素个数 */
int long_long_array_count_less(long long arr[], int size, long long value);

/** 每个元素乘以 scalar */
void long_long_array_scale(long long arr[], int size, long long scalar);

/** 每个元素加 offset */
void long_long_array_add_scalar(long long arr[], int size, long long offset);

/** 数组是否有重复 */
int long_long_array_has_duplicates(long long arr[], int size);

/** 数组左旋 k 位 */
void long_long_array_rotate_left(long long arr[], int size, int k);

/** 绝对值之和 */
long long long_long_array_sum_abs(long long arr[], int size);

/** 最小值下标 */
int short_array_min_index(short arr[], int size);

/** 最大值下标 */
int short_array_max_index(short arr[], int size);

/** 统计大于 value 的元素个数 */
int short_array_count_greater(short arr[], int size, short value);

/** 统计小于 value 的元素个数 */
int short_array_count_less(short arr[], int size, short value);

/** 每个元素乘以 scalar */
void short_array_scale(short arr[], int size, short scalar);

/** 每个元素加 offset */
void short_array_add_scalar(short arr[], int size, short offset);

/** 数组是否有重复 */
int short_array_has_duplicates(short arr[], int size);

/** 数组左旋 k 位 */
void short_array_rotate_left(short arr[], int size, int k);

/** 绝对值之和 */
long long short_array_sum_abs(short arr[], int size);

/** 最小值下标 */
int uint_array_min_index(unsigned int arr[], int size);

/** 最大值下标 */
int uint_array_max_index(unsigned int arr[], int size);

/** 统计大于 value 的元素个数 */
int uint_array_count_greater(unsigned int arr[], int size, unsigned int value);

/** 统计小于 value 的元素个数 */
int uint_array_count_less(unsigned int arr[], int size, unsigned int value);

/** 每个元素乘以 scalar */
void uint_array_scale(unsigned int arr[], int size, unsigned int scalar);

/** 每个元素加 offset */
void uint_array_add_scalar(unsigned int arr[], int size, unsigned int offset);

/** 数组是否有重复 */
int uint_array_has_duplicates(unsigned int arr[], int size);

/** 数组左旋 k 位 */
void uint_array_rotate_left(unsigned int arr[], int size, int k);

/** 最小值下标 */
int float_array_min_index(float arr[], int size);

/** 最大值下标 */
int float_array_max_index(float arr[], int size);

/** 统计大于 value 的元素个数 */
int float_array_count_greater(float arr[], int size, float value);

/** 统计小于 value 的元素个数 */
int float_array_count_less(float arr[], int size, float value);

/** 每个元素乘以 scalar */
void float_array_scale(float arr[], int size, float scalar);

/** 每个元素加 offset */
void float_array_add_scalar(float arr[], int size, float offset);

/** 数组是否有重复 */
int float_array_has_duplicates(float arr[], int size);

/** 数组左旋 k 位 */
void float_array_rotate_left(float arr[], int size, int k);

/** 绝对值之和 */
double float_array_sum_abs(float arr[], int size);

/** 最小值下标 */
int double_array_min_index(double arr[], int size);

/** 最大值下标 */
int double_array_max_index(double arr[], int size);

/** 统计大于 value 的元素个数 */
int double_array_count_greater(double arr[], int size, double value);

/** 统计小于 value 的元素个数 */
int double_array_count_less(double arr[], int size, double value);

/** 每个元素乘以 scalar */
void double_array_scale(double arr[], int size, double scalar);

/** 每个元素加 offset */
void double_array_add_scalar(double arr[], int size, double offset);

/** 数组是否有重复 */
int double_array_has_duplicates(double arr[], int size);

/** 数组左旋 k 位 */
void double_array_rotate_left(double arr[], int size, int k);

/** 绝对值之和 */
double double_array_sum_abs(double arr[], int size);

/** 最小值下标 */
int char_array_min_index(char arr[], int size);

/** 最大值下标 */
int char_array_max_index(char arr[], int size);

/** 统计大于 value 的元素个数 */
int char_array_count_greater(char arr[], int size, char value);

/** 统计小于 value 的元素个数 */
int char_array_count_less(char arr[], int size, char value);

/** 每个元素乘以 scalar */
void char_array_scale(char arr[], int size, char scalar);

/** 每个元素加 offset */
void char_array_add_scalar(char arr[], int size, char offset);

/** 数组是否有重复 */
int char_array_has_duplicates(char arr[], int size);

/** 数组左旋 k 位 */
void char_array_rotate_left(char arr[], int size, int k);

/** 绝对值之和 */
int char_array_sum_abs(char arr[], int size);

/** 最小值下标 */
int uint8_array_min_index(uint8_t arr[], int size);

/** 最大值下标 */
int uint8_array_max_index(uint8_t arr[], int size);

/** 统计大于 value 的元素个数 */
int uint8_array_count_greater(uint8_t arr[], int size, uint8_t value);

/** 统计小于 value 的元素个数 */
int uint8_array_count_less(uint8_t arr[], int size, uint8_t value);

/** 每个元素乘以 scalar */
void uint8_array_scale(uint8_t arr[], int size, uint8_t scalar);

/** 每个元素加 offset */
void uint8_array_add_scalar(uint8_t arr[], int size, uint8_t offset);

/** 数组是否有重复 */
int uint8_array_has_duplicates(uint8_t arr[], int size);

/** 数组左旋 k 位 */
void uint8_array_rotate_left(uint8_t arr[], int size, int k);

/** 最小值下标 */
int uint16_array_min_index(uint16_t arr[], int size);

/** 最大值下标 */
int uint16_array_max_index(uint16_t arr[], int size);

/** 统计大于 value 的元素个数 */
int uint16_array_count_greater(uint16_t arr[], int size, uint16_t value);

/** 统计小于 value 的元素个数 */
int uint16_array_count_less(uint16_t arr[], int size, uint16_t value);

/** 每个元素乘以 scalar */
void uint16_array_scale(uint16_t arr[], int size, uint16_t scalar);

/** 每个元素加 offset */
void uint16_array_add_scalar(uint16_t arr[], int size, uint16_t offset);

/** 数组是否有重复 */
int uint16_array_has_duplicates(uint16_t arr[], int size);

/** 数组左旋 k 位 */
void uint16_array_rotate_left(uint16_t arr[], int size, int k);

/** 最小值下标 */
int uint32_array_min_index(uint32_t arr[], int size);

/** 最大值下标 */
int uint32_array_max_index(uint32_t arr[], int size);

/** 统计大于 value 的元素个数 */
int uint32_array_count_greater(uint32_t arr[], int size, uint32_t value);

/** 统计小于 value 的元素个数 */
int uint32_array_count_less(uint32_t arr[], int size, uint32_t value);

/** 每个元素乘以 scalar */
void uint32_array_scale(uint32_t arr[], int size, uint32_t scalar);

/** 每个元素加 offset */
void uint32_array_add_scalar(uint32_t arr[], int size, uint32_t offset);

/** 数组是否有重复 */
int uint32_array_has_duplicates(uint32_t arr[], int size);

/** 数组左旋 k 位 */
void uint32_array_rotate_left(uint32_t arr[], int size, int k);


// ============================================================
//                     数组工具(第三批)（自动生成）
// ============================================================

/** 连续相同段的数量 */
int count_runs_int(int arr[], int size);

/** 是否为 1..n 的排列 */
int is_permutation_int(int arr[], int size);

/** 任意两数最大乘积 */
long long max_pair_product(int arr[], int size);

/** 找缺失数字(0..n 缺一个) */
int find_missing_number(int arr[], int n);

/** 找重复数字(1..n 有一个重复) */
int find_duplicate_number(int arr[], int n);

/** 把 0 移到末尾 */
void move_zeros_to_end(int arr[], int size);

/** 把负数移到前面 */
void move_negatives_to_front(int arr[], int size);

/** 奇偶分离(偶数在前) */
void separate_even_odd(int arr[], int size);

/** 区间和(直接计算) */
long long sum_range_int(int arr[], int lo, int hi);

/** 排序数组中 target 出现次数 */
int count_occurrences_sorted(int arr[], int size, int target);

/** 按 k 分组反转 */
void reverse_in_groups(int arr[], int size, int k);

/** 是否为山脉数组 */
int is_mountain_array(int arr[], int size);

/** 多数元素(Boyer-Moore) */
int majority_element(int arr[], int size);

/** 和为 target 的数对数量 */
int pairs_with_sum(int arr[], int size, int target);

/** 单调递增栈(写入结果数组) */
int next_greater_element(int arr[], int size, int out[]);

/** 山峰下标(严格单峰) */
int find_peak_index(int arr[], int size);


// ============================================================
//                     字符串工具(第三批)（自动生成）
// ============================================================

/** ROT13 副本(需free) */
char* str_rot13_copy(const char *s);

/** 凯撒加密副本(需free) */
char* str_caesar_copy(const char *s, int shift);

/** 替换所有子串(需free) */
char* str_replace_all(const char *s, const char *old, const char *new);

/** 提取数字(需free) */
char* str_extract_digits(const char *s);

/** 删除指定位置字符 */
void str_remove_char_at(char *str, int pos);

/** 在指定位置插入字符 */
void str_insert_char_at(char *str, int buf_size, int pos, char c);

/** 是否所有字符相同 */
int str_is_all_same_char(const char *str);

/** 是否有重复字符 */
int str_has_duplicate_chars(const char *str);

/** 两字符串最长公共前缀长度 */
int str_longest_common_prefix(const char *a, const char *b);

/** 不同字符个数 */
int str_count_unique_chars(const char *str);

/** 最后一个单词长度 */
int str_last_word_len(const char *str);

/** 第一个单词长度 */
int str_first_word_len(const char *str);

/** 是否包含任意给定字符 */
int str_contains_any_char(const char *str, const char *chars);

/** 括号是否匹配 */
int str_is_balanced_parens(const char *str);

/** 括号组是否合法({[]}) */
int str_is_valid_brackets(const char *s);

/** 字符串相似度(简单字符重合率0~100) */
double str_similarity(const char *a, const char *b);


// ============================================================
//                     数论与数学(第三批)（自动生成）
// ============================================================

/** 数组的最大公约数 */
int gcd_of_array(int arr[], int size);

/** 数组的最小公倍数 */
long long lcm_of_array(int arr[], int size);

/** 各位数字平方和 */
int sum_of_squares_digits(int n);

/** 是否全数字数(1..len各一次) */
int is_pandigital(int n);

/** 是否重位数(各位相同) */
int is_repdigit(int n);

/** 各位数字之积 */
int digit_product(int n);

/** 第 n 个三角形数 */
long long nth_triangular(int n);

/** 前 n 个斐波那契和 */
long long fib_sum_first(int n);

/** 是否丑数(因子只有2,3,5) */
int is_ugly_number(int n);

/** 是否无平方因子数 */
int is_square_free(int n);

/** 无平方因子积(radical) */
int radical(int n);

/** 是否反素数(逆转仍是素数) */
int is_emirp(int n);

/** 1..n 中与 n 互质的个数 */
int count_coprimes(int n);

/** 十进制转格雷码 */
uint32_t int_to_gray(uint32_t n);

/** 格雷码转十进制 */
uint32_t gray_to_int(uint32_t g);


// ============================================================
//                     数值工具(第三批)（自动生成）
// ============================================================

/** 长整数裁剪 */
long clamp_long(long v, long lo, long hi);

/** 单精度裁剪 */
float clamp_float(float v, float lo, float hi);

/** 限制线性插值 */
double lerp_clamped(double a, double b, double t);

/** Smoothstep 平滑插值 */
double smoothstep(double x);

/** 归一化到 [0,1] */
double normalize_01(double x, double min, double max);

/** 整数向上整除 */
long long int_divide_ceil(long long a, long long b);

/** 整数向下整除 */
long long int_divide_floor(long long a, long long b);

/** 是否在区间内(含端点) */
int is_between_int(int v, int lo, int hi);

/** 是否在区间内(浮点) */
int is_between_double(double v, double lo, double hi);

/** 百分比变化 */
double percent_delta(double a, double b);

/** 三个数平均值 */
double average_of_three(double a, double b, double c);

/** 三个数乘积 */
double product_of_three(double a, double b, double c);

/** 浮点符号(1/-1/0) */
int sign_double(double x);

/** 百分比保留 */
double percent_of(double part, double total);

/** 两点在数轴上的距离 */
double distance_1d(double a, double b);


// ============================================================
//                     位运算(第三批)（自动生成）
// ============================================================

/** 保留低 n 位 */
uint32_t clear_high_bits(uint32_t val, int n);

/** 按掩码翻转位 */
uint32_t toggle_bits(uint32_t val, uint32_t mask);

/** 按掩码置位 */
uint32_t set_bits_mask(uint32_t val, uint32_t mask);

/** 按掩码清位 */
uint32_t clear_bits_mask(uint32_t val, uint32_t mask);

/** 反转单个字节 */
uint8_t bit_reverse_byte(uint8_t b);

/** 16 位格雷码转换 */
uint16_t int_to_gray16(uint16_t n);

/** 判断是否只有一个 1 */
int is_single_bit(uint32_t val);

/** 最低位 1 的值 */
uint32_t lowest_one(uint32_t val);


// ============================================================
//                     进制转换(第三批)（自动生成）
// ============================================================

/** 字节转 8 位二进制字符串 */
char* byte_to_bin_str(uint8_t b, char *buf, int buf_size);

/** 16 位转二进制字符串 */
char* word_to_bin_str(uint16_t w, char *buf, int buf_size);

/** 浮点转整数(四舍五入) */
long long float_to_int_round(float f);

/** 浮点转整数(截断) */
long long float_to_int_truncate(float f);

/** 整数转 long 字符串 */
char* long_to_str(long v, char *buf);

/** 字符数组转长整数(限长) */
long char_array_to_long(const char *s, int len);

/** 十进制字符串直接转十六进制字符串 */
char* dec_str_to_hex_str(const char *dec, char *buf, int buf_size);


// ============================================================
//                     控制台与调试(第三批)（自动生成）
// ============================================================

/** 打印进度条 */
void print_progress_bar(int percent, int width);

/** 打印带颜色的成功信息 */
void print_ok(const char *msg);

/** 打印带颜色的失败信息 */
void print_fail(const char *msg);

/** 打印带颜色的警告信息 */
void print_warn(const char *msg);

/** 带时间戳打印普通日志 */
void log_timestamp(const char *msg);

/** 定宽打印整数 */
void print_padded_int(int v, int width);

/** 打印布尔值 */
void print_bool(int b);

/** 居中打印标题 */
void print_center(const char *title, int width);


// ============================================================
//                     数列与序列（自动生成）
// ============================================================

/** 填充前 n 个斐波那契数 */
void fibonacci_array(long long out[], int n);

/** 填充前 n 个平方数 */
void square_array(long long out[], int n);

/** 填充前 n 个三角形数 */
void triangular_array(long long out[], int n);

/** 填充科拉茨序列 */
int collatz_sequence(int n, int out[], int max_len);

/** 杨辉三角第 n 行 */
int pascal_row(int n, int out[], int *len);

/** 是否等差数列 */
int is_arithmetic_sequence(int arr[], int size);

/** 是否等比数列 */
int is_geometric_sequence(double arr[], int size);

/** 错排数(子阶乘) */
long long subfactorial(int n);

/** 第 n 个卢卡斯数 */
long long lucas_number(int n);


// ============================================================
//                     文件工具(第三批)（自动生成）
// ============================================================

/** 清空文件内容 */
int file_clear(const char *filename);

/** 读取整个文件为字节(需free) */
uint8_t* file_read_all_bytes(const char *filename, size_t *out_len);

/** 写入字节到文件 */
int file_write_bytes(const char *filename, const uint8_t *data, size_t len);

/** 统计文件中的单词数 */
int file_count_words(const char *filename);

/** 文件是否包含指定行 */
int file_has_line(const char *filename, const char *line);


// ============================================================
//                     排序算法(第三批)（自动生成）
// ============================================================

/** 升序排序(包装冒泡) */
void sort_asc(int arr[], int size);

/** 降序排序 */
void sort_desc(int arr[], int size);

/** double 数组升序(冒泡) */
void sort_double_asc(double arr[], int size);

/** float 数组升序(冒泡) */
void sort_float_asc(float arr[], int size);

/** long 数组升序(冒泡) */
void sort_long_asc(long arr[], int size);

/** char 数组升序(冒泡) */
void sort_char_asc(char arr[], int size);

/** 排序并去重(返回新长度) */
int sort_unique(int arr[], int *size);

/** 排序索引(返回索引数组需free) */
int* sort_indices(int arr[], int size);


// ============================================================
//                     核心算法(补齐)（自动生成）
// ============================================================

/** 插值查找(升序) */
int interpolation_search(int arr[], int size, int target);

/** 哨兵查找 */
int sentinel_search(int arr[], int size, int target);

/** 斐波那契查找(升序) */
int fibonacci_search(int arr[], int size, int target);

/** KMP 字符串匹配 */
int kmp_search(const char *text, const char *pattern);

/** 最长公共子串长度 */
int str_longest_common_substr(const char *s1, const char *s2);

/** 编辑距离(莱文斯坦) */
int str_edit_distance(const char *s1, const char *s2);

/** 反转句子单词顺序 */
void str_reverse_words(char *str);

/** 构建前缀和数组(需free) */
long long* build_prefix_sum(int arr[], int size);

/** 前缀和区间查询 */
long long range_sum_query(long long pre[], int l, int r);

/** 构建差分数组 */
void build_diff_array(int arr[], int size, int diff[]);

/** 差分数组还原 */
void apply_diff_array(int diff[], int size, int out[]);

/** 埃氏筛求素数(需free) */
int* sieve_primes(int n, int *count);

/** 质因数分解 */
int prime_factors(int n, int factors[], int *count);

/** 快速幂取模 */
long long mod_pow(long long base, long long exp, long long mod);

/** 扩展欧几里得 */
int extended_gcd(int a, int b, int *x, int *y);

/** 下一个字典序排列 */
int next_permutation(int arr[], int size);

/** 闰年判断 */
int is_leap_year(int year);

/** 判断 2 的幂 */
int is_power_of_two(int n);

/** 最低位 1 的位置 */
int lowest_set_bit(uint32_t n);

/** 异或找唯一出现一次的数 */
int find_single_number(int arr[], int size);

/** 汉明距离 */
int hamming_distance(uint32_t a, uint32_t b);

/** 0-1 背包最大价值 */
int knapsack01(int weights[], int values[], int n, int capacity);

/** 最长递增子序列长度 */
int lis_length(int arr[], int size);

/** DJB2 哈希 */
uint32_t djb2_hash(const char *str);

/** FNV-1a 哈希 */
uint32_t fnv1a_hash(const char *str);

/** SDBM 哈希 */
uint32_t sdbm_hash(const char *str);

/** BKDR 哈希 */
uint32_t bkdr_hash(const char *str);

/** 创建环形缓冲区 */
RingBuffer* rb_create(uint16_t capacity);

/** 销毁环形缓冲区 */
void rb_destroy(RingBuffer *rb);

/** 写入一个字节 */
int rb_write(RingBuffer *rb, uint8_t byte);

/** 读取一个字节 */
int rb_read(RingBuffer *rb, uint8_t *out);

/** 查看队首字节 */
int rb_peek(RingBuffer *rb, uint8_t *out);

/** 可读字节数 */
uint16_t rb_available(RingBuffer *rb);

/** 剩余空间 */
uint16_t rb_free(RingBuffer *rb);

/** 是否为空 */
int rb_is_empty(RingBuffer *rb);

/** 是否为满 */
int rb_is_full(RingBuffer *rb);

/** 清空缓冲区 */
void rb_clear(RingBuffer *rb);

/** 创建动态数组 */
Vector* vec_create(int init_capacity);

/** 销毁动态数组 */
void vec_destroy(Vector *v);

/** 尾部追加 */
int vec_push_back(Vector *v, int value);

/** 尾部弹出 */
int vec_pop_back(Vector *v, int *out);

/** 按下标取值 */
int vec_get(Vector *v, int index, int *out);

/** 按下标赋值 */
int vec_set(Vector *v, int index, int value);

/** 元素个数 */
int vec_size(Vector *v);

/** 当前容量 */
int vec_capacity(Vector *v);

/** 是否为空 */
int vec_is_empty(Vector *v);

/** 清空(不释放) */
void vec_clear(Vector *v);

/** 按下标插入 */
int vec_insert(Vector *v, int index, int value);

/** 按下标删除 */
int vec_remove(Vector *v, int index, int *out);

/** 创建最大堆队列 */
PriorityQueue* pq_create(int capacity);

/** 销毁队列 */
void pq_destroy(PriorityQueue *pq);

/** 入队 */
int pq_push(PriorityQueue *pq, int value);

/** 弹出最大值 */
int pq_pop(PriorityQueue *pq, int *out);

/** 查看最大值 */
int pq_peek(PriorityQueue *pq, int *out);

/** 是否为空 */
int pq_is_empty(PriorityQueue *pq);

/** 元素个数 */
int pq_size(PriorityQueue *pq);

/** BST 插入节点 */
BSTNode* bst_insert(BSTNode *root, int data);

/** BST 查找节点 */
BSTNode* bst_search(BSTNode *root, int data);

/** BST 最小节点 */
BSTNode* bst_find_min(BSTNode *root);

/** BST 最大节点 */
BSTNode* bst_find_max(BSTNode *root);

/** BST 删除节点 */
BSTNode* bst_delete(BSTNode *root, int data);

/** BST 树高 */
int bst_height(BSTNode *root);

/** BST 节点数 */
int bst_node_count(BSTNode *root);

/** BST 中序遍历 */
void bst_inorder(BSTNode *root);

/** BST 前序遍历 */
void bst_preorder(BSTNode *root);

/** BST 后序遍历 */
void bst_postorder(BSTNode *root);

/** BST 层序遍历 */
void bst_levelorder(BSTNode *root);

/** BST 释放整棵树 */
void bst_free(BSTNode *root);

/** 毫秒级时间戳 */
long long get_timestamp_ms(void);

/** 微秒级时间戳 */
long long get_timestamp_us(void);

/** 带时间戳写入日志文件 */
void log_to_file(const char *filename, const char *format, ...);

#endif /* UTILS_GEN_H */
