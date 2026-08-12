#include "utils.h"
#include <stdarg.h>
#include <ctype.h>

// ============================================================
//                     数组工具函数实现
// ============================================================

void print_int_array(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

void print_double_array(double arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%.2f ", arr[i]);
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
    for (int i = 0; i < size / 2; i++) {
        int temp = arr[i];
        arr[i] = arr[size - 1 - i];
        arr[size - 1 - i] = temp;
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
    for (int i = 0; i < size - 1; i++) {
        int swapped = 0;
        for (int j = 0; j < size - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = 1;
            }
        }
        if (!swapped) break;
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
    int left = 0, right = size - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
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
    a = abs(a); b = abs(b);
    while (b) {
        int t = a % b;
        a = b;
        b = t;
    }
    return a;
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

int max_subarray_sum(int arr[], int size) {
    if (size <= 0) return 0;
    int cur = arr[0], max_sum = arr[0];
    for (int i = 1; i < size; i++) {
        cur = (cur + arr[i] > arr[i]) ? cur + arr[i] : arr[i];
        if (cur > max_sum) max_sum = cur;
    }
    return max_sum;
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