#include "utils.h"
#include <stdarg.h>
#include <ctype.h>

// Windows / Linux 系统工具所需的头文件（仅在对应平台编译时引入）
#ifdef _WIN32
#include <windows.h>
#include <direct.h>
#else
#include <sys/stat.h>
#include <unistd.h>
#endif

// ============================================================
//                     数组工具函数实现
// ============================================================

void print_int_array(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

void print_double_array(double array[], int length) {
    for (int index = 0; index < length; index++) {
        printf("%.2f ", array[index]);
    }
    printf("\n");
}

void fill_int_array(int arr[], int size, int value) {
    for (int i = 0; i < size; i++) {
        arr[i] = value;
    }
}

void fill_random_int(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        arr[i] = rand() % 100;
    }
}

void fill_random_range(int arr[], int size, int min, int max) {
    for (int i = 0; i < size; i++) {
        arr[i] = rand() % (max - min + 1) + min;
    }
}

void reverse_int_array(int arr[], int size) {
    /* 首尾对称交换，只需遍历前半部分 */
    for (int i = 0; i < size / 2; i++) {
        int temp = arr[i];              /* 暂存左端元素 */
        arr[i] = arr[size - 1 - i];     /* 左端换成右端元素 */
        arr[size - 1 - i] = temp;       /* 右端换成左端元素 */
    }
}

int find_int(int arr[], int size, int target) {
    for (int i = 0; i < size; i++) {
        if (arr[i] == target) return i;
    }
    return -1;
}

int find_last_int(int arr[], int size, int target) {
    for (int i = size - 1; i >= 0; i--) {
        if (arr[i] == target) return i;
    }
    return -1;
}

int sum_int_array(int arr[], int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}

double avg_int_array(int arr[], int size) {
    if (size == 0) return 0.0;
    return (double)sum_int_array(arr, size) / size;
}

int max_subarray_sum(int arr[], int size) {
    if (size <= 0) return 0;
    int cur = arr[0], max_sum = arr[0];
    for (int i = 1; i < size; i++) {
        cur = (cur + arr[i] > arr[i]) ? cur + arr[i] : arr[i];
        if (cur > max_sum) max_sum = cur;
    }
    return max_sum;
}

int max_int_array(int arr[], int size) {
    int max = arr[0];
    for (int i = 1; i < size; i++) {
        if (arr[i] > max) max = arr[i];
    }
    return max;
}

int min_int_array(int arr[], int size) {
    int min = arr[0];
    for (int i = 1; i < size; i++) {
        if (arr[i] < min) min = arr[i];
    }
    return min;
}

void bubble_sort(int arr[], int size) {
    /* 外层循环：最多需要 size-1 轮 */
    for (int i = 0; i < size - 1; i++) {
        int swapped = 0;   /* 标记本轮是否发生过交换 */
        /* 内层循环：把当前未排序部分的最大元素“冒泡”到末尾 */
        for (int j = 0; j < size - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {        /* 前一个比后一个大则交换 */
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = 1;
            }
        }
        if (!swapped) break;   /* 一轮没有交换说明已经有序，提前结束 */
    }
}

void insertion_sort(int arr[], int size) {
    for (int i = 1; i < size; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}

void selection_sort(int arr[], int size) {
    for (int i = 0; i < size - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < size; j++) {
            if (arr[j] < arr[min_idx]) min_idx = j;
        }
        if (min_idx != i) {
            int temp = arr[i];
            arr[i] = arr[min_idx];
            arr[min_idx] = temp;
        }
    }
}

int binary_search(int arr[], int size, int target) {
    int left = 0, right = size - 1;        /* 当前查找区间 [left, right] */
    while (left <= right) {                /* 区间非空则继续查找 */
        int mid = left + (right - left) / 2;   /* 取中间下标（避免溢出） */
        if (arr[mid] == target) return mid;    /* 命中，返回下标 */
        if (arr[mid] < target) left = mid + 1; /* 目标在右半区，收缩左边界 */
        else right = mid - 1;                  /* 目标在左半区，收缩右边界 */
    }
    return -1;                               /* 未找到返回 -1 */
}

int* merge_sorted_arrays(int arr1[], int size1, int arr2[], int size2, int *out_size) {
    int *result = (int*)malloc((size1 + size2) * sizeof(int));
    if (!result) return NULL;
    int i = 0, j = 0, k = 0;
    while (i < size1 && j < size2) {
        if (arr1[i] <= arr2[j]) result[k++] = arr1[i++];
        else result[k++] = arr2[j++];
    }
    while (i < size1) result[k++] = arr1[i++];
    while (j < size2) result[k++] = arr2[j++];
    *out_size = k;
    return result;
}

int remove_at_index(int arr[], int *size, int index) {
    if (index < 0 || index >= *size) return -1;
    for (int i = index; i < *size - 1; i++) {
        arr[i] = arr[i + 1];
    }
    (*size)--;
    return 0;
}

int insert_at_index(int arr[], int *size, int index, int value, int max_capacity) {
    if (index < 0 || index > *size || *size >= max_capacity) return -1;
    for (int i = *size; i > index; i--) {
        arr[i] = arr[i - 1];
    }
    arr[index] = value;
    (*size)++;
    return 0;
}

// ============================================================
//                     字符串工具函数实现
// ============================================================

int str_len(const char *str) {
    int len = 0;
    while (str[len]) len++;
    return len;
}

char* str_copy(char *dest, const char *src) {
    char *d = dest;
    while ((*d++ = *src++));
    return dest;
}

char* str_cat(char *dest, const char *src) {
    char *d = dest;
    while (*d) d++;
    while ((*d++ = *src++));
    return dest;
}

int str_cmp(const char *s1, const char *s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(unsigned char*)s1 - *(unsigned char*)s2;
}

char* str_find(const char *haystack, const char *needle) {
    if (!*needle) return (char*)haystack;
    int len = str_len(needle);
    while (*haystack) {
        if (strncmp(haystack, needle, len) == 0) {
            return (char*)haystack;
        }
        haystack++;
    }
    return NULL;
}

int count_char(const char *str, char ch) {
    int count = 0;
    while (*str) {
        if (*str == ch) count++;
        str++;
    }
    return count;
}

void remove_char(char *str, char ch) {
    char *write = str;
    while (*str) {
        if (*str != ch) {
            *write++ = *str;
        }
        str++;
    }
    *write = '\0';
}

int is_palindrome_str(const char *str) {
    int len = str_len(str);
    for (int i = 0; i < len / 2; i++) {
        if (str[i] != str[len - 1 - i]) return 0;
    }
    return 1;
}

void to_lower(char *str) {
    while (*str) {
        if (*str >= 'A' && *str <= 'Z') *str += 32;
        str++;
    }
}

void to_upper(char *str) {
    while (*str) {
        if (*str >= 'a' && *str <= 'z') *str -= 32;
        str++;
    }
}

void reverse_str(char *str) {
    int len = str_len(str);
    for (int i = 0; i < len / 2; i++) {
        char temp = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = temp;
    }
}

int str_to_int(const char *str) {
    int sign = 1, result = 0;
    while (*str == ' ' || *str == '\t') str++;
    if (*str == '-') { sign = -1; str++; }
    else if (*str == '+') str++;
    while (*str >= '0' && *str <= '9') {
        result = result * 10 + (*str - '0');
        str++;
    }
    return sign * result;
}

char* int_to_str(int num, char *buf) {
    sprintf(buf, "%d", num);
    return buf;
}

void trim(char *str) {
    char *end;
    while (*str == ' ') str++;
    if (*str == '\0') return;
    end = str + str_len(str) - 1;
    while (end > str && *end == ' ') end--;
    *(end + 1) = '\0';
}

int count_words(const char *str) {
    int count = 0, in_word = 0;
    while (*str) {
        if (*str == ' ' || *str == '\t' || *str == '\n') {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            count++;
        }
        str++;
    }
    return count;
}

// ============================================================
//                     数学工具函数实现
// ============================================================

long long factorial(int n) {
    if (n < 0) return -1;
    long long result = 1;
    for (int i = 1; i <= n; i++) result *= i;
    return result;
}

int is_prime(int n) {
    if (n <= 1) return 0;
    if (n == 2) return 1;
    if (n % 2 == 0) return 0;
    for (int i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return 0;
    }
    return 1;
}

int gcd(int a, int b) {
    a = abs(a); b = abs(b);   /* 先取绝对值，负数也能正确计算 */
    while (b) {               /* 辗转相除：直到余数为 0 */
        int t = a % b;        /* 求余数 */
        a = b;                /* 原来的除数成为新的被除数 */
        b = t;                /* 余数成为新的除数 */
    }
    return a;                 /* 余数为 0 时 a 即最大公约数 */
}

int lcm(int a, int b) {
    if (a == 0 || b == 0) return 0;
    return a / gcd(a, b) * b;
}

long long power(int base, int exp) {
    if (exp < 0) return 0;
    long long result = 1, b = base;
    int e = exp;
    while (e) {
        if (e & 1) result *= b;
        b *= b;
        e >>= 1;
    }
    return result;
}

int is_perfect(int n) {
    if (n <= 1) return 0;
    int sum = 0;
    for (int i = 1; i <= n / 2; i++) {
        if (n % i == 0) sum += i;
    }
    return sum == n;
}

long long fibonacci(int n) {
    if (n <= 1) return n;
    long long a = 0, b = 1, c;
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}

int rand_range(int min, int max) {
    if (min > max) {
        int t = min; min = max; max = t;
    }
    return rand() % (max - min + 1) + min;
}

void shuffle_array(int arr[], int size) {
    for (int i = size - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}

// ============================================================
//                     文件工具函数实现
// ============================================================

char* read_file(const char *filename) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return NULL;
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    char *buf = (char*)malloc(size + 1);
    if (!buf) {
        fclose(fp);
        return NULL;
    }
    fread(buf, 1, size, fp);
    buf[size] = '\0';
    fclose(fp);
    return buf;
}

int write_file(const char *filename, const char *content) {
    FILE *fp = fopen(filename, "w");
    if (!fp) return -1;
    fprintf(fp, "%s", content);
    fclose(fp);
    return 0;
}

int append_file(const char *filename, const char *content) {
    FILE *fp = fopen(filename, "a");
    if (!fp) return -1;
    fprintf(fp, "%s", content);
    fclose(fp);
    return 0;
}

int copy_file(const char *src, const char *dest) {
    FILE *fs = fopen(src, "rb");
    if (!fs) return -1;
    FILE *fd = fopen(dest, "wb");
    if (!fd) {
        fclose(fs);
        return -1;
    }
    char buffer[4096];
    size_t n;
    while ((n = fread(buffer, 1, sizeof(buffer), fs)) > 0) {
        fwrite(buffer, 1, n, fd);
    }
    fclose(fs);
    fclose(fd);
    return 0;
}

int count_file_lines(const char *filename) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return -1;
    int lines = 0;
    char ch;
    while ((ch = fgetc(fp)) != EOF) {
        if (ch == '\n') lines++;
    }
    fclose(fp);
    return lines;
}

// ============================================================
//                     内存管理工具函数实现
// ============================================================

void* safe_malloc(size_t size) {
    void *ptr = malloc(size);
    if (!ptr) {
        perror("safe_malloc failed");
        exit(EXIT_FAILURE);
    }
    return ptr;
}

void* safe_calloc(size_t count, size_t size) {
    void *ptr = calloc(count, size);
    if (!ptr) {
        perror("safe_calloc failed");
        exit(EXIT_FAILURE);
    }
    return ptr;
}

void* safe_realloc(void *ptr, size_t size) {
    void *new_ptr = realloc(ptr, size);
    if (!new_ptr && size != 0) {
        perror("safe_realloc failed");
        exit(EXIT_FAILURE);
    }
    return new_ptr;
}

void safe_free(void **ptr) {
    if (ptr && *ptr) {
        free(*ptr);
        *ptr = NULL;
    }
}

int* copy_int_array(int src[], int size) {
    int *dst = (int*)malloc(size * sizeof(int));
    if (!dst) return NULL;
    memcpy(dst, src, size * sizeof(int));
    return dst;
}

char* copy_string(const char *src) {
    if (!src) return NULL;
    char *dst = (char*)malloc(str_len(src) + 1);
    if (!dst) return NULL;
    str_copy(dst, src);
    return dst;
}

// ============================================================
//                     实用工具函数实现
// ============================================================

void debug_log(const char *format, ...) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    char time_buf[20];
    strftime(time_buf, sizeof(time_buf), "%Y-%m-%d %H:%M:%S", tm_info);
    printf("[%s] ", time_buf);
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
    printf("\n");
}

char* get_time_str(char *buf) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    strftime(buf, 20, "%Y-%m-%d %H:%M:%S", tm_info);
    return buf;
}

void wait_for_key(void) {
    printf("按任意键继续...");
    getchar();
}

void clear_input_buffer(void) {
    int ch;
    while ((ch = getchar()) != '\n' && ch != EOF);
}

char* safe_fgets(char *buf, size_t size, FILE *stream) {
    if (!fgets(buf, size, stream)) return NULL;
    size_t len = str_len(buf);
    if (len > 0 && buf[len - 1] == '\n') {
        buf[len - 1] = '\0';
    }
    return buf;
}

// ============================================================
//                     位操作工具函数实现
// ============================================================

void bit_set(volatile uint8_t *reg, uint8_t bit) {
    *reg |= (uint8_t)(1u << bit);
}

void bit_clear(volatile uint8_t *reg, uint8_t bit) {
    *reg &= (uint8_t)~(1u << bit);
}

void bit_toggle(volatile uint8_t *reg, uint8_t bit) {
    *reg ^= (uint8_t)(1u << bit);
}

uint8_t bit_is_set(volatile uint8_t *reg, uint8_t bit) {
    return (*reg & (uint8_t)(1u << bit)) ? 1 : 0;
}

uint8_t bit_is_clear(volatile uint8_t *reg, uint8_t bit) {
    return (*reg & (uint8_t)(1u << bit)) ? 0 : 1;
}

uint8_t byte_get_high(uint16_t val) {
    return (uint8_t)(val >> 8);
}

uint8_t byte_get_low(uint16_t val) {
    return (uint8_t)(val & 0xFF);
}

uint16_t byte_combine(uint8_t hi, uint8_t lo) {
    return (uint16_t)(((uint16_t)hi << 8) | lo);
}

uint8_t count_ones(uint32_t val) {
    uint8_t count = 0;
    while (val) {
        count += (uint8_t)(val & 1u);
        val >>= 1;
    }
    return count;
}

uint32_t rotate_left(uint32_t val, uint8_t n) {
    n %= 32;
    if (n == 0) return val;
    return (val << n) | (val >> (32 - n));
}

uint32_t rotate_right(uint32_t val, uint8_t n) {
    n %= 32;
    if (n == 0) return val;
    return (val >> n) | (val << (32 - n));
}

uint16_t swap_bytes16(uint16_t val) {
    return (uint16_t)((val << 8) | (val >> 8));
}

uint32_t swap_bytes32(uint32_t val) {
    return ((val << 24) & 0xFF000000u) |
           ((val << 8)  & 0x00FF0000u) |
           ((val >> 8)  & 0x0000FF00u) |
           ((val >> 24) & 0x000000FFu);
}

int is_little_endian(void) {
    uint16_t x = 1;
    return *((uint8_t*)&x) == 1;
}

// ============================================================
//                     字符与进制转换函数实现
// ============================================================

int is_digit_char(char c) {
    return (c >= '0' && c <= '9');
}

int is_alpha_char(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

int is_alnum_char(char c) {
    return is_digit_char(c) || is_alpha_char(c);
}

int is_space_char(char c) {
    return c == ' ' || c == '\t' || c == '\n' || c == '\r' || c == '\v' || c == '\f';
}

char char_to_lower(char c) {
    return (c >= 'A' && c <= 'Z') ? (char)(c + 32) : c;
}

char char_to_upper(char c) {
    return (c >= 'a' && c <= 'z') ? (char)(c - 32) : c;
}

int hex_char_to_int(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

char int_to_hex_char(int v) {
    static const char table[] = "0123456789ABCDEF";
    if (v < 0 || v > 15) return '?';
    return table[v];
}

char* int_to_binary_str(int num, char *buf, int buf_size) {
    if (buf_size <= 0) return buf;
    buf[0] = '\0';
    if (buf_size < 2) return buf;
    int bits = (int)(sizeof(int) * 8);
    int idx = 0, started = 0;
    for (int i = bits - 1; i >= 0; i--) {
        if ((num >> i) & 1) started = 1;
        if (started) {
            if (idx >= buf_size - 1) break;
            buf[idx++] = ((num >> i) & 1) ? '1' : '0';
        }
    }
    if (idx == 0) buf[idx++] = '0';
    buf[idx] = '\0';
    return buf;
}

char* int_to_octal_str(int num, char *buf) {
    sprintf(buf, "%o", num);
    return buf;
}

char* int_to_hex_str(int num, char *buf) {
    sprintf(buf, "%X", num);
    return buf;
}

long bin_str_to_int(const char *str) {
    long result = 0;
    while (*str) {
        if (*str != '0' && *str != '1') break;
        result = result * 2 + (*str - '0');
        str++;
    }
    return result;
}

long oct_str_to_int(const char *str) {
    long result = 0;
    while (*str) {
        if (*str < '0' || *str > '7') break;
        result = result * 8 + (*str - '0');
        str++;
    }
    return result;
}

long hex_str_to_int(const char *str) {
    long result = 0;
    while (*str) {
        int v = hex_char_to_int(*str);
        if (v < 0) break;
        result = result * 16 + v;
        str++;
    }
    return result;
}

// ============================================================
//                     数字工具函数实现
// ============================================================

int count_digits(int n) {
    if (n == 0) return 1;
    if (n < 0) n = -n;
    int count = 0;
    while (n) {
        count++;
        n /= 10;
    }
    return count;
}

int reverse_int(int n) {
    int rev = 0;
    int neg = (n < 0);
    if (neg) n = -n;
    while (n) {
        rev = rev * 10 + n % 10;
        n /= 10;
    }
    return neg ? -rev : rev;
}

int sum_digits(int n) {
    if (n < 0) n = -n;
    int sum = 0;
    while (n) {
        sum += n % 10;
        n /= 10;
    }
    return sum;
}

int is_armstrong(int n) {
    if (n < 0) return 0;
    int digits = count_digits(n);
    int tmp = n;
    long long sum = 0;
    while (tmp) {
        int d = tmp % 10;
        long long p = 1;
        for (int i = 0; i < digits; i++) p *= d;
        sum += p;
        tmp /= 10;
    }
    return sum == n;
}

int is_palindrome_num(int n) {
    if (n < 0) return 0;
    return n == reverse_int(n);
}

// ============================================================
//                     排序算法函数实现
// ============================================================

/* 分区：以最后一个元素为基准，小的放左边、大的放右边，返回基准最终下标 */
static int qs_partition(int arr[], int low, int high) {
    int pivot = arr[high];       /* 基准值取区间最后一个元素 */
    int i = low - 1;             /* i 指向“已排好的小值区”末尾 */
    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {    /* 比基准小则交换到左边区域 */
            i++;
            int temp = arr[i]; arr[i] = arr[j]; arr[j] = temp;
        }
    }
    /* 把基准放到正确位置（i+1 处） */
    int temp = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = temp;
    return i + 1;                /* 返回基准最终下标 */
}

static void qs_recursive(int arr[], int low, int high) {
    if (low < high) {
        int pi = qs_partition(arr, low, high);  /* 分区，得到基准位置 */
        qs_recursive(arr, low, pi - 1);         /* 递归排序左半部分 */
        qs_recursive(arr, pi + 1, high);        /* 递归排序右半部分 */
    }
}

void quick_sort(int arr[], int size) {
    if (size <= 1) return;
    qs_recursive(arr, 0, size - 1);
}

static void ms_merge(int arr[], int temp[], int left, int mid, int right) {
    int i = left, j = mid + 1, k = left;
    while (i <= mid && j <= right) {
        if (arr[i] <= arr[j]) temp[k++] = arr[i++];
        else temp[k++] = arr[j++];
    }
    while (i <= mid) temp[k++] = arr[i++];
    while (j <= right) temp[k++] = arr[j++];
    for (i = left; i <= right; i++) arr[i] = temp[i];
}

static void ms_recursive(int arr[], int temp[], int left, int right) {
    if (left >= right) return;
    int mid = left + (right - left) / 2;
    ms_recursive(arr, temp, left, mid);
    ms_recursive(arr, temp, mid + 1, right);
    ms_merge(arr, temp, left, mid, right);
}

void merge_sort(int arr[], int size) {
    if (size <= 1) return;
    int *temp = (int*)malloc(size * sizeof(int));
    if (!temp) return;
    ms_recursive(arr, temp, 0, size - 1);
    free(temp);
}

static void heapify(int arr[], int size, int root) {
    int largest = root;
    int left = 2 * root + 1;
    int right = 2 * root + 2;
    if (left < size && arr[left] > arr[largest]) largest = left;
    if (right < size && arr[right] > arr[largest]) largest = right;
    if (largest != root) {
        int temp = arr[root]; arr[root] = arr[largest]; arr[largest] = temp;
        heapify(arr, size, largest);
    }
}

void heap_sort(int arr[], int size) {
    for (int i = size / 2 - 1; i >= 0; i--) heapify(arr, size, i);
    for (int i = size - 1; i > 0; i--) {
        int temp = arr[0]; arr[0] = arr[i]; arr[i] = temp;
        heapify(arr, i, 0);
    }
}

// ============================================================
//                     数组工具补充实现
// ============================================================

void rotate_array_left(int arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    int *temp = (int*)malloc(k * sizeof(int));
    if (!temp) return;
    for (int i = 0; i < k; i++) temp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = temp[i];
    free(temp);
}

void rotate_array_right(int arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    rotate_array_left(arr, size, size - k);
}

int remove_duplicates_int(int arr[], int *size) {
    if (!size || *size <= 1) return (*size) ? *size : 0;
    int j = 0;
    for (int i = 0; i < *size; i++) {
        int dup = 0;
        for (int k = 0; k < j; k++) {
            if (arr[k] == arr[i]) { dup = 1; break; }
        }
        if (!dup) arr[j++] = arr[i];
    }
    *size = j;
    return j;
}

// ============================================================
//                     字符串工具补充实现
// ============================================================

char* str_substr(const char *str, int start, int len, char *buf, int buf_size) {
    if (!buf || buf_size <= 0) return buf;
    buf[0] = '\0';
    if (!str) return buf;
    int slen = str_len(str);
    if (start < 0) start = 0;
    if (start >= slen || len <= 0) return buf;
    if (start + len > slen) len = slen - start;
    if (len >= buf_size) len = buf_size - 1;
    for (int i = 0; i < len; i++) buf[i] = str[start + i];
    buf[len] = '\0';
    return buf;
}

int str_replace_char(char *str, char old_ch, char new_ch) {
    int count = 0;
    while (*str) {
        if (*str == old_ch) {
            *str = new_ch;
            count++;
        }
        str++;
    }
    return count;
}

int str_starts_with(const char *str, const char *prefix) {
    if (!str || !prefix) return 0;
    return strncmp(str, prefix, str_len(prefix)) == 0;
}

int str_ends_with(const char *str, const char *suffix) {
    if (!str || !suffix) return 0;
    int slen = str_len(str);
    int suffix_len = str_len(suffix);
    if (suffix_len > slen) return 0;
    return strcmp(str + slen - suffix_len, suffix) == 0;
}

char** str_split(const char *str, char delim, int *count) {
    *count = 0;
    if (!str) return NULL;
    int n = 1;
    const char *p = str;
    while (*p) {
        if (*p == delim) n++;
        p++;
    }
    char **tokens = (char**)malloc((n + 1) * sizeof(char*));
    if (!tokens) return NULL;
    int idx = 0;
    const char *start = str;
    const char *cur = str;
    while (1) {
        if (*cur == delim || *cur == '\0') {
            int len = (int)(cur - start);
            char *token = (char*)malloc(len + 1);
            if (!token) break;
            for (int i = 0; i < len; i++) token[i] = start[i];
            token[len] = '\0';
            tokens[idx++] = token;
            start = cur + 1;
            if (*cur == '\0') break;
        }
        cur++;
    }
    tokens[idx] = NULL;
    *count = idx;
    return tokens;
}

void str_free_split(char **tokens, int count) {
    if (!tokens) return;
    for (int i = 0; i < count; i++) free(tokens[i]);
    free(tokens);
}

// ============================================================
//                     单向链表函数实现
// ============================================================

ListNode* list_create(int data) {
    ListNode *node = (ListNode*)malloc(sizeof(ListNode));
    if (!node) return NULL;
    node->data = data;
    node->next = NULL;
    return node;
}

void list_insert_head(ListNode **head, int data) {
    if (!head) return;
    ListNode *node = list_create(data);
    if (!node) return;
    node->next = *head;
    *head = node;
}

void list_insert_tail(ListNode **head, int data) {
    if (!head) return;
    ListNode *node = list_create(data);
    if (!node) return;
    if (*head == NULL) {
        *head = node;
        return;
    }
    ListNode *p = *head;
    while (p->next) p = p->next;
    p->next = node;
}

void list_insert_sorted(ListNode **head, int data) {
    if (!head) return;
    ListNode *node = list_create(data);   /* 新建节点 */
    if (!node) return;
    /* 链表为空，或新值比头节点还小 → 插入到头部 */
    if (*head == NULL || (*head)->data >= data) {
        node->next = *head;
        *head = node;
        return;
    }
    /* 从头部向后找插入位置：第一个值 >= data 的节点之前 */
    ListNode *p = *head;
    while (p->next && p->next->data < data) p = p->next;
    node->next = p->next;   /* 新节点先指向后一个节点 */
    p->next = node;         /* 前一个节点再指向新节点 */
}

void list_delete_value(ListNode **head, int data) {
    if (!head) return;
    while (*head && (*head)->data == data) {
        ListNode *tmp = *head;
        *head = (*head)->next;
        free(tmp);
    }
    ListNode *p = *head;
    while (p && p->next) {
        if (p->next->data == data) {
            ListNode *tmp = p->next;
            p->next = tmp->next;
            free(tmp);
        } else {
            p = p->next;
        }
    }
}

ListNode* list_find(ListNode *head, int data) {
    while (head) {
        if (head->data == data) return head;
        head = head->next;
    }
    return NULL;
}

int list_length(ListNode *head) {
    int len = 0;
    while (head) {
        len++;
        head = head->next;
    }
    return len;
}

void list_reverse(ListNode **head) {
    if (!head) return;
    ListNode *prev = NULL, *cur = *head, *next = NULL;
    while (cur) {
        next = cur->next;
        cur->next = prev;
        prev = cur;
        cur = next;
    }
    *head = prev;
}

void list_print(ListNode *head) {
    while (head) {
        printf("%d -> ", head->data);
        head = head->next;
    }
    printf("NULL\n");
}

void list_free(ListNode **head) {
    if (!head) return;
    ListNode *cur = *head;
    while (cur) {
        ListNode *next = cur->next;
        free(cur);
        cur = next;
    }
    *head = NULL;
}

// ============================================================
//                     栈函数实现
// ============================================================

Stack* stack_create(int capacity) {
    if (capacity <= 0) return NULL;
    Stack *s = (Stack*)malloc(sizeof(Stack));
    if (!s) return NULL;
    s->data = (int*)malloc(capacity * sizeof(int));
    if (!s->data) {
        free(s);
        return NULL;
    }
    s->top = -1;
    s->capacity = capacity;
    return s;
}

void stack_destroy(Stack *s) {
    if (!s) return;
    free(s->data);
    free(s);
}

int stack_push(Stack *s, int value) {
    if (!s || s->top >= s->capacity - 1) return -1;
    s->data[++s->top] = value;
    return 0;
}

int stack_pop(Stack *s, int *out) {
    if (!s || s->top < 0 || !out) return -1;
    *out = s->data[s->top--];
    return 0;
}

int stack_peek(Stack *s, int *out) {
    if (!s || s->top < 0 || !out) return -1;
    *out = s->data[s->top];
    return 0;
}

int stack_is_empty(Stack *s) {
    return (s == NULL || s->top < 0);
}

int stack_is_full(Stack *s) {
    return (s != NULL && s->top >= s->capacity - 1);
}

int stack_size(Stack *s) {
    return (s == NULL) ? 0 : s->top + 1;
}

// ============================================================
//                     队列函数实现
// ============================================================

Queue* queue_create(int capacity) {
    if (capacity <= 0) return NULL;
    Queue *q = (Queue*)malloc(sizeof(Queue));
    if (!q) return NULL;
    q->data = (int*)malloc(capacity * sizeof(int));
    if (!q->data) {
        free(q);
        return NULL;
    }
    q->front = 0;
    q->rear = 0;
    q->size = 0;
    q->capacity = capacity;
    return q;
}

void queue_destroy(Queue *q) {
    if (!q) return;
    free(q->data);
    free(q);
}

int queue_enqueue(Queue *q, int value) {
    if (!q || q->size >= q->capacity) return -1;  /* 队列已满则失败 */
    q->data[q->rear] = value;                     /* 元素写入队尾位置 */
    q->rear = (q->rear + 1) % q->capacity;        /* 队尾后移（环形回绕） */
    q->size++;                                    /* 元素个数 +1 */
    return 0;
}

int queue_dequeue(Queue *q, int *out) {
    if (!q || q->size <= 0 || !out) return -1;
    *out = q->data[q->front];
    q->front = (q->front + 1) % q->capacity;
    q->size--;
    return 0;
}

int queue_peek(Queue *q, int *out) {
    if (!q || q->size <= 0 || !out) return -1;
    *out = q->data[q->front];
    return 0;
}

int queue_is_empty(Queue *q) {
    return (q == NULL || q->size == 0);
}

int queue_is_full(Queue *q) {
    return (q != NULL && q->size >= q->capacity);
}

int queue_size(Queue *q) {
    return (q == NULL) ? 0 : q->size;
}

// ============================================================
//                     校验与CRC函数实现
// ============================================================

uint8_t xor_checksum(const uint8_t *data, uint16_t len) {
    uint8_t sum = 0;
    for (uint16_t i = 0; i < len; i++) sum ^= data[i];
    return sum;
}

uint8_t checksum8(const uint8_t *data, uint16_t len) {
    uint16_t sum = 0;
    for (uint16_t i = 0; i < len; i++) sum += data[i];
    return (uint8_t)(sum & 0xFF);
}

uint16_t checksum16(const uint8_t *data, uint16_t len) {
    uint32_t sum = 0;
    for (uint16_t i = 0; i < len; i++) sum += data[i];
    return (uint16_t)(sum & 0xFFFF);
}

uint8_t crc8(const uint8_t *data, uint16_t len) {
    uint8_t crc = 0x00;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80) crc = (uint8_t)((crc << 1) ^ 0x07);
            else crc = (uint8_t)(crc << 1);
        }
    }
    return crc;
}

uint16_t crc16_modbus(const uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) crc = (uint16_t)((crc >> 1) ^ 0xA001);
            else crc = (uint16_t)(crc >> 1);
        }
    }
    return crc;
}

uint8_t parity_check(uint32_t val) {
    return (uint8_t)(count_ones(val) & 1u);
}

char* bytes_to_hex_str(const uint8_t *data, uint16_t len, char *buf, uint16_t buf_size) {
    if (buf_size < (uint16_t)(len * 2 + 1)) {
        if (buf && buf_size > 0) buf[0] = '\0';
        return buf;
    }
    for (uint16_t i = 0; i < len; i++) {
        buf[i * 2] = int_to_hex_char((data[i] >> 4) & 0x0F);
        buf[i * 2 + 1] = int_to_hex_char(data[i] & 0x0F);
    }
    buf[len * 2] = '\0';
    return buf;
}

int hex_str_to_bytes(const char *hex, uint8_t *out, uint16_t max_len) {
    if (!hex || !out) return -1;
    int len = str_len(hex);
    if (len % 2 != 0) return -1;
    int count = 0;
    for (int i = 0; i < len; i += 2) {
        if (count >= max_len) break;
        int hi = hex_char_to_int(hex[i]);
        int lo = hex_char_to_int(hex[i + 1]);
        if (hi < 0 || lo < 0) return -1;
        out[count++] = (uint8_t)((hi << 4) | lo);
    }
    return count;
}

// ============================================================
//                     延时函数实现
// ============================================================

void soft_delay_ms(uint32_t ms) {
    for (uint32_t i = 0; i < ms; i++) {
        // 空循环约 1ms，实际时长与主频/编译器优化相关，需自行校准
        volatile uint32_t loops = 1000;
        while (loops--) { }
    }
}

void soft_delay_us(uint32_t us) {
    for (uint32_t i = 0; i < us; i++) {
        // 空循环约 1us，实际时长与主频/编译器优化相关，需自行校准
        volatile uint32_t loops = 2;
        while (loops--) { }
    }
}

// ============================================================
//                     系统工具函数实现
// ============================================================

int file_exists(const char *path) {
    FILE *fp = fopen(path, "r");
    if (fp) {
        fclose(fp);
        return 1;
    }
    return 0;
}

int dir_exists(const char *path) {
#ifdef _WIN32
    DWORD attr = GetFileAttributesA(path);
    return (attr != INVALID_FILE_ATTRIBUTES && (attr & FILE_ATTRIBUTE_DIRECTORY));
#else
    struct stat st;
    if (stat(path, &st) != 0) return 0;
    return S_ISDIR(st.st_mode);
#endif
}

long get_file_size(const char *path) {
    FILE *fp = fopen(path, "rb");
    if (!fp) return -1;
    fseek(fp, 0, SEEK_END);
    long size = ftell(fp);
    fclose(fp);
    return size;
}

int create_dir(const char *path) {
#ifdef _WIN32
    return (_mkdir(path) == 0) ? 0 : -1;
#else
    return (mkdir(path, 0755) == 0) ? 0 : -1;
#endif
}

int remove_dir(const char *path) {
#ifdef _WIN32
    return (_rmdir(path) == 0) ? 0 : -1;
#else
    return (rmdir(path) == 0) ? 0 : -1;
#endif
}

char* path_join(const char *dir, const char *file, char *buf, int buf_size) {
    if (!dir || !file || !buf || buf_size <= 0) return NULL;
#ifdef _WIN32
    snprintf(buf, buf_size, "%s\\%s", dir, file);
#else
    snprintf(buf, buf_size, "%s/%s", dir, file);
#endif
    return buf;
}

const char* get_file_ext(const char *path) {
    if (!path) return "";
    const char *dot = strrchr(path, '.');
    const char *slash = strrchr(path, '/');
#ifdef _WIN32
    const char *bslash = strrchr(path, '\\');
    if (bslash && (!slash || bslash > slash)) slash = bslash;
#endif
    if (!dot || (slash && dot < slash)) return "";
    return dot + 1;
}

char* get_base_name(const char *path, char *buf, int buf_size) {
    if (!path || !buf || buf_size <= 0) return NULL;
    const char *slash = strrchr(path, '/');
#ifdef _WIN32
    const char *bslash = strrchr(path, '\\');
    if (bslash && (!slash || bslash > slash)) slash = bslash;
#endif
    const char *name = slash ? slash + 1 : path;
    snprintf(buf, buf_size, "%s", name);
    return buf;
}

int run_cmd(const char *cmd) {
    if (!cmd) return -1;
    return system(cmd);
}

char* run_cmd_capture(const char *cmd) {
    if (!cmd) return NULL;
#ifdef _WIN32
    FILE *fp = _popen(cmd, "r");
#else
    FILE *fp = popen(cmd, "r");
#endif
    if (!fp) return NULL;
    char *buf = NULL;
    size_t len = 0;
    char chunk[256];
    size_t n;
    while ((n = fread(chunk, 1, sizeof(chunk) - 1, fp)) > 0) {
        chunk[n] = '\0';
        size_t new_len = len + n + 1;
        char *tmp = (char*)realloc(buf, new_len);
        if (!tmp) {
            free(buf);
            buf = NULL;
            break;
        }
        buf = tmp;
        memcpy(buf + len, chunk, n);
        len += n;
        buf[len] = '\0';
    }
#ifdef _WIN32
    _pclose(fp);
#else
    pclose(fp);
#endif
    return buf;
}

void hex_dump(const void *ptr, size_t len) {
    const uint8_t *p = (const uint8_t*)ptr;
    for (size_t i = 0; i < len; i += 16) {
        printf("%08lX  ", (unsigned long)i);
        for (size_t j = 0; j < 16; j++) {
            if (i + j < len) printf("%02X ", p[i + j]);
            else printf("   ");
            if (j == 7) printf(" ");
        }
        printf(" |");
        for (size_t j = 0; j < 16 && i + j < len; j++) {
            char c = (char)p[i + j];
            putchar((c >= 32 && c < 127) ? c : '.');
        }
        printf("|\n");
    }
}

// 自动生成的函数实现（由 gen_functions.py 生成）
#include "utils_gen.c"
