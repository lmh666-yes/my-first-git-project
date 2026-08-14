/* ============================================================
 *  utils_gen.c — 自动生成的函数实现（由 gen_functions.py 生成，请勿手改）
 *  通过 utils.c 末尾的 #include "utils_gen.c" 编译进库
 * ============================================================ */


// ============================================================
//                     数组工具(类型扩展)（自动生成）
// ============================================================

int find_int_array(int arr[], int size, int target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_int_array(int arr[], int size, int target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

long long product_int_array(int arr[], int size) {
    long long p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

int max_abs_int_array(int arr[], int size) {
    int m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        int v = UTILS_ABS(arr[i]);
        if (v > m) m = v;
    }
    return m;
}

int min_abs_int_array(int arr[], int size) {
    int m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        int v = UTILS_ABS(arr[i]);
        if (v < m) m = v;
    }
    return m;
}

int second_max_int_array(int arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    int m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { int t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int second_min_int_array(int arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    int m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { int t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_int_array(int arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_int_array(int arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

void print_long_array(long arr[], int size) {
    for (int i = 0; i < size; i++) printf("%ld ", arr[i]);
    printf("\n");
}

long long sum_long_array(long arr[], int size) {
    long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_long_array(long arr[], int size) {
    if (size == 0) return 0.0;
    long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

long max_long_array(long arr[], int size) {
    long m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

long min_long_array(long arr[], int size) {
    long m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_long_array(long arr[], int size, long value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_long_array(long arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        long t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_long_array(long arr[], int size, long target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_long_array(long arr[], int size, long target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

long long product_long_array(long arr[], int size) {
    long long p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

long* copy_long_array(long arr[], int size) {
    long *r = (long*)malloc(size * sizeof(long));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(long));
    return r;
}

long max_abs_long_array(long arr[], int size) {
    long m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        long v = UTILS_ABS(arr[i]);
        if (v > m) m = v;
    }
    return m;
}

long min_abs_long_array(long arr[], int size) {
    long m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        long v = UTILS_ABS(arr[i]);
        if (v < m) m = v;
    }
    return m;
}

long second_max_long_array(long arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    long m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { long t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

long second_min_long_array(long arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    long m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { long t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_long_array(long arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_long_array(long arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

void print_long_long_array(long long arr[], int size) {
    for (int i = 0; i < size; i++) printf("%lld ", arr[i]);
    printf("\n");
}

long long sum_long_long_array(long long arr[], int size) {
    long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_long_long_array(long long arr[], int size) {
    if (size == 0) return 0.0;
    long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

long long max_long_long_array(long long arr[], int size) {
    long long m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

long long min_long_long_array(long long arr[], int size) {
    long long m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_long_long_array(long long arr[], int size, long long value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_long_long_array(long long arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        long long t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_long_long_array(long long arr[], int size, long long target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_long_long_array(long long arr[], int size, long long target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

long long product_long_long_array(long long arr[], int size) {
    long long p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

long long* copy_long_long_array(long long arr[], int size) {
    long long *r = (long long*)malloc(size * sizeof(long long));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(long long));
    return r;
}

long long max_abs_long_long_array(long long arr[], int size) {
    long long m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        long long v = UTILS_ABS(arr[i]);
        if (v > m) m = v;
    }
    return m;
}

long long min_abs_long_long_array(long long arr[], int size) {
    long long m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        long long v = UTILS_ABS(arr[i]);
        if (v < m) m = v;
    }
    return m;
}

long long second_max_long_long_array(long long arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    long long m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { long long t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

long long second_min_long_long_array(long long arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    long long m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { long long t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_long_long_array(long long arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_long_long_array(long long arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

void print_short_array(short arr[], int size) {
    for (int i = 0; i < size; i++) printf("%d ", arr[i]);
    printf("\n");
}

long long sum_short_array(short arr[], int size) {
    long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_short_array(short arr[], int size) {
    if (size == 0) return 0.0;
    long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

short max_short_array(short arr[], int size) {
    short m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

short min_short_array(short arr[], int size) {
    short m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_short_array(short arr[], int size, short value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_short_array(short arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        short t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_short_array(short arr[], int size, short target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_short_array(short arr[], int size, short target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

long long product_short_array(short arr[], int size) {
    long long p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

short* copy_short_array(short arr[], int size) {
    short *r = (short*)malloc(size * sizeof(short));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(short));
    return r;
}

short max_abs_short_array(short arr[], int size) {
    short m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        short v = UTILS_ABS(arr[i]);
        if (v > m) m = v;
    }
    return m;
}

short min_abs_short_array(short arr[], int size) {
    short m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        short v = UTILS_ABS(arr[i]);
        if (v < m) m = v;
    }
    return m;
}

short second_max_short_array(short arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    short m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { short t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

short second_min_short_array(short arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    short m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { short t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_short_array(short arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_short_array(short arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

void print_uint_array(unsigned int arr[], int size) {
    for (int i = 0; i < size; i++) printf("%u ", arr[i]);
    printf("\n");
}

unsigned long long sum_uint_array(unsigned int arr[], int size) {
    unsigned long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_uint_array(unsigned int arr[], int size) {
    if (size == 0) return 0.0;
    unsigned long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

unsigned int max_uint_array(unsigned int arr[], int size) {
    unsigned int m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

unsigned int min_uint_array(unsigned int arr[], int size) {
    unsigned int m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_uint_array(unsigned int arr[], int size, unsigned int value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_uint_array(unsigned int arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        unsigned int t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_uint_array(unsigned int arr[], int size, unsigned int target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_uint_array(unsigned int arr[], int size, unsigned int target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

unsigned long long product_uint_array(unsigned int arr[], int size) {
    unsigned long long p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

unsigned int* copy_uint_array(unsigned int arr[], int size) {
    unsigned int *r = (unsigned int*)malloc(size * sizeof(unsigned int));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(unsigned int));
    return r;
}

unsigned int second_max_uint_array(unsigned int arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    unsigned int m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { unsigned int t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

unsigned int second_min_uint_array(unsigned int arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    unsigned int m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { unsigned int t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_uint_array(unsigned int arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_uint_array(unsigned int arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

void print_float_array(float arr[], int size) {
    for (int i = 0; i < size; i++) printf("%.2f ", arr[i]);
    printf("\n");
}

double sum_float_array(float arr[], int size) {
    double s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_float_array(float arr[], int size) {
    if (size == 0) return 0.0;
    double s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

float max_float_array(float arr[], int size) {
    float m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

float min_float_array(float arr[], int size) {
    float m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_float_array(float arr[], int size, float value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_float_array(float arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        float t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_float_array(float arr[], int size, float target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_float_array(float arr[], int size, float target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

double product_float_array(float arr[], int size) {
    double p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

float* copy_float_array(float arr[], int size) {
    float *r = (float*)malloc(size * sizeof(float));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(float));
    return r;
}

float max_abs_float_array(float arr[], int size) {
    float m = fabs(arr[0]);
    for (int i = 1; i < size; i++) {
        float v = fabs(arr[i]);
        if (v > m) m = v;
    }
    return m;
}

float min_abs_float_array(float arr[], int size) {
    float m = fabs(arr[0]);
    for (int i = 1; i < size; i++) {
        float v = fabs(arr[i]);
        if (v < m) m = v;
    }
    return m;
}

float second_max_float_array(float arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    float m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { float t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

float second_min_float_array(float arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    float m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { float t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_float_array(float arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_float_array(float arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

double sum_double_array(double arr[], int size) {
    double s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_double_array(double arr[], int size) {
    if (size == 0) return 0.0;
    double s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

double max_double_array(double arr[], int size) {
    double m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

double min_double_array(double arr[], int size) {
    double m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_double_array(double arr[], int size, double value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_double_array(double arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        double t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_double_array(double arr[], int size, double target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_double_array(double arr[], int size, double target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

double product_double_array(double arr[], int size) {
    double p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

double* copy_double_array(double arr[], int size) {
    double *r = (double*)malloc(size * sizeof(double));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(double));
    return r;
}

double max_abs_double_array(double arr[], int size) {
    double m = fabs(arr[0]);
    for (int i = 1; i < size; i++) {
        double v = fabs(arr[i]);
        if (v > m) m = v;
    }
    return m;
}

double min_abs_double_array(double arr[], int size) {
    double m = fabs(arr[0]);
    for (int i = 1; i < size; i++) {
        double v = fabs(arr[i]);
        if (v < m) m = v;
    }
    return m;
}

double second_max_double_array(double arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    double m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { double t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

double second_min_double_array(double arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    double m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { double t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_double_array(double arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_double_array(double arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

void print_char_array(char arr[], int size) {
    for (int i = 0; i < size; i++) printf("%c ", arr[i]);
    printf("\n");
}

int sum_char_array(char arr[], int size) {
    int s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_char_array(char arr[], int size) {
    if (size == 0) return 0.0;
    int s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

char max_char_array(char arr[], int size) {
    char m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

char min_char_array(char arr[], int size) {
    char m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_char_array(char arr[], int size, char value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_char_array(char arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        char t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_char_array(char arr[], int size, char target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_char_array(char arr[], int size, char target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

int product_char_array(char arr[], int size) {
    int p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

char* copy_char_array(char arr[], int size) {
    char *r = (char*)malloc(size * sizeof(char));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(char));
    return r;
}

char max_abs_char_array(char arr[], int size) {
    char m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        char v = UTILS_ABS(arr[i]);
        if (v > m) m = v;
    }
    return m;
}

char min_abs_char_array(char arr[], int size) {
    char m = UTILS_ABS(arr[0]);
    for (int i = 1; i < size; i++) {
        char v = UTILS_ABS(arr[i]);
        if (v < m) m = v;
    }
    return m;
}

char second_max_char_array(char arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    char m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { char t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

char second_min_char_array(char arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    char m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { char t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_char_array(char arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_char_array(char arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

void print_uint8_array(uint8_t arr[], int size) {
    for (int i = 0; i < size; i++) printf("%u ", (unsigned)arr[i]);
    printf("\n");
}

unsigned long long sum_uint8_array(uint8_t arr[], int size) {
    unsigned long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_uint8_array(uint8_t arr[], int size) {
    if (size == 0) return 0.0;
    unsigned long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

uint8_t max_uint8_array(uint8_t arr[], int size) {
    uint8_t m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

uint8_t min_uint8_array(uint8_t arr[], int size) {
    uint8_t m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_uint8_array(uint8_t arr[], int size, uint8_t value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_uint8_array(uint8_t arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        uint8_t t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_uint8_array(uint8_t arr[], int size, uint8_t target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_uint8_array(uint8_t arr[], int size, uint8_t target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

unsigned long long product_uint8_array(uint8_t arr[], int size) {
    unsigned long long p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

uint8_t* copy_uint8_array(uint8_t arr[], int size) {
    uint8_t *r = (uint8_t*)malloc(size * sizeof(uint8_t));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(uint8_t));
    return r;
}

uint8_t second_max_uint8_array(uint8_t arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    uint8_t m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { uint8_t t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

uint8_t second_min_uint8_array(uint8_t arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    uint8_t m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { uint8_t t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_uint8_array(uint8_t arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_uint8_array(uint8_t arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

void print_uint16_array(uint16_t arr[], int size) {
    for (int i = 0; i < size; i++) printf("%u ", (unsigned)arr[i]);
    printf("\n");
}

unsigned long long sum_uint16_array(uint16_t arr[], int size) {
    unsigned long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_uint16_array(uint16_t arr[], int size) {
    if (size == 0) return 0.0;
    unsigned long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

uint16_t max_uint16_array(uint16_t arr[], int size) {
    uint16_t m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

uint16_t min_uint16_array(uint16_t arr[], int size) {
    uint16_t m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_uint16_array(uint16_t arr[], int size, uint16_t value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_uint16_array(uint16_t arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        uint16_t t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_uint16_array(uint16_t arr[], int size, uint16_t target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_uint16_array(uint16_t arr[], int size, uint16_t target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

unsigned long long product_uint16_array(uint16_t arr[], int size) {
    unsigned long long p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

uint16_t* copy_uint16_array(uint16_t arr[], int size) {
    uint16_t *r = (uint16_t*)malloc(size * sizeof(uint16_t));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(uint16_t));
    return r;
}

uint16_t second_max_uint16_array(uint16_t arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    uint16_t m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { uint16_t t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

uint16_t second_min_uint16_array(uint16_t arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    uint16_t m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { uint16_t t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_uint16_array(uint16_t arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_uint16_array(uint16_t arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

void print_uint32_array(uint32_t arr[], int size) {
    for (int i = 0; i < size; i++) printf("%u ", arr[i]);
    printf("\n");
}

unsigned long long sum_uint32_array(uint32_t arr[], int size) {
    unsigned long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s;
}

double avg_uint32_array(uint32_t arr[], int size) {
    if (size == 0) return 0.0;
    unsigned long long s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return (double)s / size;
}

uint32_t max_uint32_array(uint32_t arr[], int size) {
    uint32_t m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] > m) m = arr[i];
    return m;
}

uint32_t min_uint32_array(uint32_t arr[], int size) {
    uint32_t m = arr[0];
    for (int i = 1; i < size; i++) if (arr[i] < m) m = arr[i];
    return m;
}

void fill_uint32_array(uint32_t arr[], int size, uint32_t value) {
    for (int i = 0; i < size; i++) arr[i] = value;
}

void reverse_uint32_array(uint32_t arr[], int size) {
    for (int i = 0; i < size / 2; i++) {
        uint32_t t = arr[i]; arr[i] = arr[size - 1 - i]; arr[size - 1 - i] = t;
    }
}

int find_uint32_array(uint32_t arr[], int size, uint32_t target) {
    for (int i = 0; i < size; i++) if (arr[i] == target) return i;
    return -1;
}

int count_uint32_array(uint32_t arr[], int size, uint32_t target) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) c++;
    return c;
}

unsigned long long product_uint32_array(uint32_t arr[], int size) {
    unsigned long long p = 1;
    for (int i = 0; i < size; i++) p *= arr[i];
    return p;
}

uint32_t* copy_uint32_array(uint32_t arr[], int size) {
    uint32_t *r = (uint32_t*)malloc(size * sizeof(uint32_t));
    if (!r) return NULL;
    memcpy(r, arr, size * sizeof(uint32_t));
    return r;
}

uint32_t second_max_uint32_array(uint32_t arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    uint32_t m1 = arr[0], m2 = arr[1];
    if (m2 > m1) { uint32_t t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] > m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] > m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

uint32_t second_min_uint32_array(uint32_t arr[], int size) {
    if (size < 2) return (size > 0) ? arr[0] : 0;
    uint32_t m1 = arr[0], m2 = arr[1];
    if (m2 < m1) { uint32_t t = m1; m1 = m2; m2 = t; }
    for (int i = 2; i < size; i++) {
        if (arr[i] < m1) { m2 = m1; m1 = arr[i]; }
        else if (arr[i] < m2 && arr[i] != m1) m2 = arr[i];
    }
    return m2;
}

int is_sorted_asc_uint32_array(uint32_t arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) return 0;
    return 1;
}

int is_sorted_desc_uint32_array(uint32_t arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) return 0;
    return 1;
}

// ============================================================
//                     数组统计（自动生成）
// ============================================================

double mean_double_array(double arr[], int size) {
    if (size == 0) return 0.0;
    double s = 0;
    for (int i = 0; i < size; i++) s += arr[i];
    return s / size;
}

double median_double_array(double arr[], int size) {
    if (size == 0) return 0.0;
    double *c = (double*)malloc(size * sizeof(double));
    if (!c) return 0.0;
    memcpy(c, arr, size * sizeof(double));
    for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (c[j] > c[j + 1]) { double t = c[j]; c[j] = c[j + 1]; c[j + 1] = t; }
    double r = (size % 2) ? c[size / 2] : (c[size / 2 - 1] + c[size / 2]) / 2.0;
    free(c);
    return r;
}

int mode_int_array(int arr[], int size) {
    int best = arr[0], bestc = 0;
    for (int i = 0; i < size; i++) { int c = 0; for (int j = 0; j < size; j++) if (arr[j] == arr[i]) c++; if (c > bestc) { bestc = c; best = arr[i]; } }
    return best;
}

double variance_double_array(double arr[], int size) {
    if (size < 1) return 0.0;
    double m = mean_double_array(arr, size), s = 0;
    for (int i = 0; i < size; i++) { double d = arr[i] - m; s += d * d; }
    return s / size;
}

double stddev_double_array(double arr[], int size) {
    return sqrt(variance_double_array(arr, size));
}

double range_double_array(double arr[], int size) {
    if (size < 1) return 0.0;
    double mx = arr[0], mn = arr[0];
    for (int i = 1; i < size; i++) { if (arr[i] > mx) mx = arr[i]; if (arr[i] < mn) mn = arr[i]; }
    return mx - mn;
}

double percentile_double_array(double arr[], int size, double p) {
    if (size < 1) return 0.0;
    double *c = (double*)malloc(size * sizeof(double));
    if (!c) return 0.0;
    memcpy(c, arr, size * sizeof(double));
    for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (c[j] > c[j + 1]) { double t = c[j]; c[j] = c[j + 1]; c[j + 1] = t; }
    int idx = (int)(p * (size - 1));
    double r = c[idx];
    free(c);
    return r;
}

double geometric_mean_double(double arr[], int size) {
    if (size < 1) return 0.0;
    double p = 1.0;
    for (int i = 0; i < size; i++) p *= arr[i];
    return pow(p, 1.0 / size);
}

double harmonic_mean_double(double arr[], int size) {
    if (size < 1) return 0.0;
    double s = 0.0;
    for (int i = 0; i < size; i++) s += 1.0 / arr[i];
    return size / s;
}

// ============================================================
//                     数组查询与谓词（自动生成）
// ============================================================

int has_duplicates_int(int arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

int all_positive_int(int arr[], int size) {
    for (int i = 0; i < size; i++) if (arr[i] <= 0) return 0;
    return 1;
}

int all_negative_int(int arr[], int size) {
    for (int i = 0; i < size; i++) if (arr[i] >= 0) return 0;
    return 1;
}

int all_even_int(int arr[], int size) {
    for (int i = 0; i < size; i++) if (arr[i] % 2) return 0;
    return 1;
}

int all_odd_int(int arr[], int size) {
    for (int i = 0; i < size; i++) if (arr[i] % 2 == 0) return 0;
    return 1;
}

int count_greater_int(int arr[], int size, int value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int count_less_int(int arr[], int size, int value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

int count_between_int(int arr[], int size, int lo, int hi) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] >= lo && arr[i] <= hi) c++;
    return c;
}

int count_even_int(int arr[], int size) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] % 2 == 0) c++;
    return c;
}

int count_odd_int(int arr[], int size) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] % 2) c++;
    return c;
}

int count_positive_int(int arr[], int size) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > 0) c++;
    return c;
}

int count_negative_int(int arr[], int size) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < 0) c++;
    return c;
}

int count_zero_int(int arr[], int size) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] == 0) c++;
    return c;
}

int contains_int(int arr[], int size, int value) {
    for (int i = 0; i < size; i++) if (arr[i] == value) return 1;
    return 0;
}

int arrays_equal_int(int a[], int b[], int size) {
    for (int i = 0; i < size; i++) if (a[i] != b[i]) return 0;
    return 1;
}

int is_subset_int(int a[], int na, int b[], int nb) {
    for (int i = 0; i < na; i++) { int f = 0; for (int j = 0; j < nb; j++) if (a[i] == b[j]) { f = 1; break; } if (!f) return 0; }
    return 1;
}

int most_frequent_int(int arr[], int size) {
    int best = arr[0], bestc = 0;
    for (int i = 0; i < size; i++) { int c = 0; for (int j = 0; j < size; j++) if (arr[j] == arr[i]) c++; if (c > bestc) { bestc = c; best = arr[i]; } }
    return best;
}

// ============================================================
//                     数组变换（自动生成）
// ============================================================

void map_square_int(int arr[], int size) {
    for (int i = 0; i < size; i++) arr[i] = arr[i] * arr[i];
}

void map_negate_int(int arr[], int size) {
    for (int i = 0; i < size; i++) arr[i] = -arr[i];
}

void map_double_int(int arr[], int size) {
    for (int i = 0; i < size; i++) arr[i] *= 2;
}

void map_add_int(int arr[], int size, int offset) {
    for (int i = 0; i < size; i++) arr[i] += offset;
}

void clip_array_int(int arr[], int size, int lo, int hi) {
    for (int i = 0; i < size; i++) { if (arr[i] < lo) arr[i] = lo; if (arr[i] > hi) arr[i] = hi; }
}

void cumulative_sum_int(int arr[], int size) {
    for (int i = 1; i < size; i++) arr[i] += arr[i - 1];
}

void cumulative_product_int(int arr[], int size) {
    for (int i = 1; i < size; i++) arr[i] *= arr[i - 1];
}

void prefix_min_int(int arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] > arr[i - 1]) arr[i] = arr[i - 1];
}

void prefix_max_int(int arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] < arr[i - 1]) arr[i] = arr[i - 1];
}

void differences_int(int arr[], int size) {
    for (int i = size - 1; i > 0; i--) arr[i] = arr[i] - arr[i - 1];
}

int* concat_int_arrays(int a[], int na, int b[], int nb, int *out_size) {
    int *r = (int*)malloc((na + nb) * sizeof(int));
    if (!r) return NULL;
    memcpy(r, a, na * sizeof(int));
    memcpy(r + na, b, nb * sizeof(int));
    *out_size = na + nb;
    return r;
}

// ============================================================
//                     排序算法(补充)（自动生成）
// ============================================================

void shell_sort(int arr[], int size) {
    for (int gap = size / 2; gap > 0; gap /= 2)
        for (int i = gap; i < size; i++) { int t = arr[i], j; for (j = i; j >= gap && arr[j - gap] > t; j -= gap) arr[j] = arr[j - gap]; arr[j] = t; }
}

void cocktail_sort(int arr[], int size) {
    int lo = 0, hi = size - 1, swapped = 1;
    while (swapped) { swapped = 0;
        for (int i = lo; i < hi; i++) if (arr[i] > arr[i + 1]) { int t = arr[i]; arr[i] = arr[i + 1]; arr[i + 1] = t; swapped = 1; }
        hi--;
        for (int i = hi; i > lo; i--) if (arr[i] < arr[i - 1]) { int t = arr[i]; arr[i] = arr[i - 1]; arr[i - 1] = t; swapped = 1; }
        lo++;
    }
}

void gnome_sort(int arr[], int size) {
    int i = 0;
    while (i < size) { if (i == 0 || arr[i - 1] <= arr[i]) i++; else { int t = arr[i]; arr[i] = arr[i - 1]; arr[i - 1] = t; i--; } }
}

void comb_sort(int arr[], int size) {
    int gap = size, swapped = 1;
    while (gap > 1 || swapped) {
        gap = (gap * 10) / 13; if (gap < 1) gap = 1; swapped = 0;
        for (int i = 0; i + gap < size; i++) if (arr[i] > arr[i + gap]) { int t = arr[i]; arr[i] = arr[i + gap]; arr[i + gap] = t; swapped = 1; }
    }
}

void cycle_sort(int arr[], int size) {
    for (int start = 0; start < size - 1; start++) {
        int item = arr[start], pos = start;
        for (int i = start + 1; i < size; i++) if (arr[i] < item) pos++;
        if (pos == start) continue;
        while (item == arr[pos]) pos++;
        int t = arr[pos]; arr[pos] = item; item = t;
        while (pos != start) { pos = start;
            for (int i = start + 1; i < size; i++) if (arr[i] < item) pos++;
            while (item == arr[pos]) pos++;
            t = arr[pos]; arr[pos] = item; item = t;
    }
    }
}

void counting_sort(int arr[], int size, int max_val) {
    int *cnt = (int*)calloc(max_val + 1, sizeof(int));
    if (!cnt) return;
    for (int i = 0; i < size; i++) cnt[arr[i]]++;
    int k = 0;
    for (int v = 0; v <= max_val; v++) for (int j = 0; j < cnt[v]; j++) arr[k++] = v;
    free(cnt);
}

void radix_sort(int arr[], int size) {
    int mx = 0; for (int i = 0; i < size; i++) if (arr[i] > mx) mx = arr[i];
    int *out = (int*)malloc(size * sizeof(int)); if (!out) return;
    for (int exp = 1; mx / exp > 0; exp *= 10) {
        int cnt[10] = {0};
        for (int i = 0; i < size; i++) cnt[(arr[i] / exp) % 10]++;
        for (int i = 1; i < 10; i++) cnt[i] += cnt[i - 1];
        for (int i = size - 1; i >= 0; i--) out[--cnt[(arr[i] / exp) % 10]] = arr[i];
        for (int i = 0; i < size; i++) arr[i] = out[i];
    }
    free(out);
}

void bitonic_sort(int arr[], int size) {
    for (int k = 2; k <= size; k *= 2)
        for (int j = k / 2; j > 0; j /= 2)
            for (int i = 0; i < size; i++) { int l = i ^ j; if (l > i) {
                int asc = ((i & k) == 0);
                if ((asc && arr[i] > arr[l]) || (!asc && arr[i] < arr[l])) { int t = arr[i]; arr[i] = arr[l]; arr[l] = t; }
    } }
}

// ============================================================
//                     查找算法(补充)（自动生成）
// ============================================================

int lower_bound_int(int arr[], int size, int target) {
    int lo = 0, hi = size;
    while (lo < hi) { int mid = lo + (hi - lo) / 2; if (arr[mid] < target) lo = mid + 1; else hi = mid; }
    return lo;
}

int upper_bound_int(int arr[], int size, int target) {
    int lo = 0, hi = size;
    while (lo < hi) { int mid = lo + (hi - lo) / 2; if (arr[mid] <= target) lo = mid + 1; else hi = mid; }
    return lo;
}

int exponential_search(int arr[], int size, int target) {
    if (size == 0) return -1;
    if (arr[0] == target) return 0;
    int i = 1;
    while (i < size && arr[i] <= target) i *= 2;
    int lo = i / 2, hi = (i < size) ? i : size - 1;
    while (lo <= hi) { int mid = lo + (hi - lo) / 2; if (arr[mid] == target) return mid; if (arr[mid] < target) lo = mid + 1; else hi = mid - 1; }
    return -1;
}

int jump_search(int arr[], int size, int target) {
    if (size == 0) return -1;
    int step = (int)sqrt(size), prev = 0;
    while (arr[(step < size ? step : size) - 1] < target) { prev = step; step += (int)sqrt(size); if (prev >= size) return -1; }
    for (int i = prev; i < (step < size ? step : size); i++) if (arr[i] == target) return i;
    return -1;
}

double ternary_search_max(double arr[], int size) {
    int lo = 0, hi = size - 1;
    while (hi - lo > 2) { int m1 = lo + (hi - lo) / 3, m2 = hi - (hi - lo) / 3; if (arr[m1] < arr[m2]) lo = m1; else hi = m2; }
    double best = arr[lo]; for (int i = lo + 1; i <= hi; i++) if (arr[i] > best) best = arr[i]; return best;
}

int binary_search_double(double arr[], int size, double target) {
    int lo = 0, hi = size - 1;
    while (lo <= hi) { int mid = lo + (hi - lo) / 2; if (arr[mid] == target) return mid; if (arr[mid] < target) lo = mid + 1; else hi = mid - 1; }
    return -1;
}

int* find_all_int(int arr[], int size, int target, int *count) {
    *count = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) (*count)++;
    int *r = (int*)malloc(*count * sizeof(int));
    if (!r) { *count = 0; return NULL; }
    int k = 0;
    for (int i = 0; i < size; i++) if (arr[i] == target) r[k++] = i;
    return r;
}

// ============================================================
//                     字符串工具(扩展)（自动生成）
// ============================================================

char* str_upper_copy(const char *str) {
    if (!str) return NULL;
    char *r = (char*)malloc(str_len(str) + 1);
    if (!r) return NULL;
    int i = 0;
    while (str[i]) { r[i] = char_to_upper(str[i]); i++; }
    r[i] = '\0';
    return r;
}

char* str_lower_copy(const char *str) {
    if (!str) return NULL;
    char *r = (char*)malloc(str_len(str) + 1);
    if (!r) return NULL;
    int i = 0;
    while (str[i]) { r[i] = char_to_lower(str[i]); i++; }
    r[i] = '\0';
    return r;
}

char* str_reverse_copy(const char *str) {
    if (!str) return NULL;
    int n = str_len(str);
    char *r = (char*)malloc(n + 1);
    if (!r) return NULL;
    for (int i = 0; i < n; i++) r[i] = str[n - 1 - i];
    r[n] = '\0';
    return r;
}

char* str_trim_copy(const char *str) {
    if (!str) return NULL;
    char *r = (char*)malloc(str_len(str) + 1);
    if (!r) return NULL;
    str_copy(r, str);
    trim(r);
    return r;
}

void str_pad_left(char *buf, int buf_size, char pad, int length) {
    int n = str_len(buf);
    if (n >= length || buf_size <= length) return;
    int shift = length - n;
    for (int i = n; i >= 0; i--) buf[i + shift] = buf[i];
    for (int i = 0; i < shift; i++) buf[i] = pad;
}

void str_pad_right(char *buf, int buf_size, char pad, int length) {
    int n = str_len(buf);
    if (n >= length || buf_size <= length) return;
    for (int i = n; i < length; i++) buf[i] = pad;
    buf[length] = '\0';
}

void str_truncate(char *str, int max_len) {
    if (max_len < 0) return;
    int n = str_len(str);
    if (n > max_len) str[max_len] = '\0';
}

void str_repeat(char *buf, int buf_size, const char *str, int times) {
    int n = str_len(str);
    int k = 0;
    for (int t = 0; t < times && k < buf_size - 1; t++)
        for (int i = 0; i < n && k < buf_size - 1; i++) buf[k++] = str[i];
    buf[k] = '\0';
}

int str_count_substr(const char *str, const char *sub) {
    int c = 0, n = str_len(sub);
    if (n == 0) return 0;
    const char *p = str;
    while ((p = str_find(p, sub)) != NULL) { c++; p += n; }
    return c;
}

int str_is_alpha(const char *str) {
    if (!str || !*str) return 0;
    while (*str) { if (!is_alpha_char(*str)) return 0; str++; }
    return 1;
}

int str_is_digit(const char *str) {
    if (!str || !*str) return 0;
    while (*str) { if (!is_digit_char(*str)) return 0; str++; }
    return 1;
}

int str_is_alnum(const char *str) {
    if (!str || !*str) return 0;
    while (*str) { if (!is_alnum_char(*str)) return 0; str++; }
    return 1;
}

int str_is_lower(const char *str) {
    if (!str || !*str) return 0;
    while (*str) { if (is_upper_char(*str)) return 0; str++; }
    return 1;
}

int str_is_upper(const char *str) {
    if (!str || !*str) return 0;
    while (*str) { if (is_lower_char(*str)) return 0; str++; }
    return 1;
}

void str_swap_case(char *str) {
    while (*str) { if (is_upper_char(*str)) *str = char_to_lower(*str); else if (is_lower_char(*str)) *str = char_to_upper(*str); str++; }
}

void str_title_case(char *str) {
    int cap = 1;
    while (*str) { if (is_alpha_char(*str)) { if (cap) *str = char_to_upper(*str); else *str = char_to_lower(*str); cap = 0; } else if (*str == ' ') cap = 1; str++; }
}

void str_remove_whitespace(char *str) {
    char *w = str;
    while (*str) { if (!is_space_char(*str)) *w++ = *str; str++; }
    *w = '\0';
}

void str_remove_vowels(char *str) {
    char *w = str;
    while (*str) { if (!is_vowel_char(*str)) *w++ = *str; str++; }
    *w = '\0';
}

int str_are_anagrams(const char *a, const char *b) {
    int ca[26] = {0}, cb[26] = {0};
    while (*a) { if (is_alpha_char(*a)) ca[char_to_lower(*a) - 'a']++; a++; }
    while (*b) { if (is_alpha_char(*b)) cb[char_to_lower(*b) - 'a']++; b++; }
    for (int i = 0; i < 26; i++) if (ca[i] != cb[i]) return 0;
    return 1;
}

int str_is_subsequence(const char *s, const char *t) {
    while (*s && *t) { if (*s == *t) s++; t++; }
    return (*s == '\0');
}

char* str_left(const char *str, int n, char *buf, int buf_size) {
    return str_substr(str, 0, n, buf, buf_size);
}

char* str_right(const char *str, int n, char *buf, int buf_size) {
    int len = str_len(str);
    int start = (n >= len) ? 0 : len - n;
    return str_substr(str, start, len - start, buf, buf_size);
}

int str_count_lines(const char *str) {
    int c = 0;
    while (*str) { if (*str == '\n') c++; str++; }
    return c;
}

int str_longest_word_len(const char *str) {
    int best = 0, cur = 0;
    while (*str) { if (is_space_char(*str)) { if (cur > best) best = cur; cur = 0; } else cur++; str++; }
    if (cur > best) best = cur;
    return best;
}

char str_most_common_char(const char *str) {
    int cnt[256] = {0};
    while (*str) cnt[(unsigned char)*str++]++;
    char best = 0; int bc = 0;
    for (int i = 0; i < 256; i++) if (cnt[i] > bc) { bc = cnt[i]; best = (char)i; }
    return best;
}

int str_count_vowels(const char *str) {
    int c = 0;
    while (*str) { if (is_vowel_char(*str)) c++; str++; }
    return c;
}

void str_caesar_shift(char *str, int shift) {
    while (*str) { if (is_alpha_char(*str)) { char base = is_upper_char(*str) ? 'A' : 'a'; *str = (char)(base + (*str - base + shift % 26 + 26) % 26); } str++; }
}

void str_rot13(char *str) {
    while (*str) { if (is_alpha_char(*str)) { char base = is_upper_char(*str) ? 'A' : 'a'; *str = (char)(base + (*str - base + 13) % 26); } str++; }
}

// ============================================================
//                     字符工具（自动生成）
// ============================================================

int is_upper_char(char c) {
    return (c >= 'A' && c <= 'Z');
}

int is_lower_char(char c) {
    return (c >= 'a' && c <= 'z');
}

int is_hex_char(char c) {
    return is_digit_char(c) || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
}

int is_octal_char(char c) {
    return (c >= '0' && c <= '7');
}

int is_printable_char(char c) {
    return (c >= 32 && c < 127);
}

int is_punctuation_char(char c) {
    return is_printable_char(c) && !is_alnum_char(c) && !is_space_char(c);
}

int is_vowel_char(char c) {
    c = char_to_lower(c);
    return (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u');
}

int is_consonant_char(char c) {
    return is_alpha_char(c) && !is_vowel_char(c);
}

char next_char(char c) {
    return (char)(c + 1);
}

char prev_char(char c) {
    return (char)(c - 1);
}

char char_rotate(char c, int n) {
    if (!is_alpha_char(c)) return c;
    char base = is_upper_char(c) ? 'A' : 'a';
    return (char)(base + (c - base + n % 26 + 26) % 26);
}

int digit_char_to_int(char c) {
    return is_digit_char(c) ? (c - '0') : -1;
}

char int_to_digit_char(int v) {
    return (v >= 0 && v <= 9) ? (char)('0' + v) : '?';
}

// ============================================================
//                     数论与数学(扩展)（自动生成）
// ============================================================

int is_even(int n) {
    return (n % 2 == 0);
}

int is_odd(int n) {
    return (n % 2 != 0);
}

int is_square(int n) {
    if (n < 0) return 0;
    int r = (int)sqrt(n);
    return r * r == n;
}

int is_cube(int n) {
    if (n < 0) return 0;
    int r = (int)cbrt(n);
    return r * r * r == n;
}

int digital_root(int n) {
    if (n == 0) return 0;
    int r = n % 9;
    return (r == 0) ? 9 : r;
}

int nth_prime(int n) {
    if (n <= 0) return -1;
    int count = 0, num = 2;
    while (1) { if (is_prime(num)) { count++; if (count == n) return num; } num++; }
}

int next_prime(int n) {
    int p = n + 1;
    while (!is_prime(p)) p++;
    return p;
}

int prev_prime(int n) {
    for (int p = n - 1; p > 1; p--) if (is_prime(p)) return p;
    return -1;
}

int count_primes_upto(int n) {
    int c = 0;
    for (int i = 2; i <= n; i++) if (is_prime(i)) c++;
    return c;
}

long long sum_primes_upto(int n) {
    long long s = 0;
    for (int i = 2; i <= n; i++) if (is_prime(i)) s += i;
    return s;
}

long long binomial_coefficient(int n, int r) {
    if (r < 0 || r > n) return 0;
    if (r > n - r) r = n - r;
    long long res = 1;
    for (int i = 0; i < r; i++) { res = res * (n - i) / (i + 1); }
    return res;
}

long long permutation_count(int n, int r) {
    if (r < 0 || r > n) return 0;
    long long res = 1;
    for (int i = 0; i < r; i++) res *= (n - i);
    return res;
}

double harmonic_number(int n) {
    double s = 0;
    for (int i = 1; i <= n; i++) s += 1.0 / i;
    return s;
}

int is_abundant(int n) {
    if (n <= 1) return 0;
    int s = 0;
    for (int i = 1; i <= n / 2; i++) if (n % i == 0) s += i;
    return s > n;
}

int is_deficient(int n) {
    if (n <= 1) return 1;
    int s = 0;
    for (int i = 1; i <= n / 2; i++) if (n % i == 0) s += i;
    return s < n;
}

int is_amicable(int a, int b) {
    int sa = 0, sb = 0;
    for (int i = 1; i <= a / 2; i++) if (a % i == 0) sa += i;
    for (int i = 1; i <= b / 2; i++) if (b % i == 0) sb += i;
    return sa == b && sb == a && a != b;
}

int is_happy(int n) {
    int seen[1000] = {0};
    while (n != 1 && !seen[n % 1000]) { seen[n % 1000] = 1; int s = 0; while (n) { int d = n % 10; s += d * d; n /= 10; } n = s; }
    return n == 1;
}

int is_harshad(int n) {
    if (n <= 0) return 0;
    int s = sum_digits(n);
    return s != 0 && n % s == 0;
}

int is_kaprekar(int n) {
    if (n <= 0) return 0;
    long long sq = (long long)n * n;
    int d = count_digits(n);
    long long p = 1;
    for (int i = 0; i < d; i++) p *= 10;
    long long hi = sq / p, lo = sq % p;
    return hi + lo == n;
}

int is_automorphic(int n) {
    long long sq = (long long)n * n;
    int d = count_digits(n);
    long long p = 1;
    for (int i = 0; i < d; i++) p *= 10;
    return (sq % p) == n;
}

int is_triangular(int n) {
    int d = 1 + 8 * n;
    int r = (int)sqrt(d);
    return r * r == d;
}

int collatz_steps(int n) {
    int steps = 0;
    while (n != 1) { if (n % 2) n = 3 * n + 1; else n /= 2; steps++; }
    return steps;
}

int aliquot_sum(int n) {
    int s = 0;
    for (int i = 1; i <= n / 2; i++) if (n % i == 0) s += i;
    return s;
}

int count_divisors(int n) {
    int c = 0;
    for (int i = 1; i * i <= n; i++) if (n % i == 0) c += (i * i == n) ? 1 : 2;
    return c;
}

long long sum_divisors(int n) {
    long long s = 0;
    for (int i = 1; i * i <= n; i++) if (n % i == 0) { s += i; if (i != n / i) s += n / i; }
    return s;
}

int euler_phi(int n) {
    int result = n;
    for (int p = 2; p * p <= n; p++) { if (n % p == 0) { while (n % p == 0) n /= p; result -= result / p; } }
    if (n > 1) result -= result / n;
    return result;
}

long long double_factorial(int n) {
    if (n < 0) return -1;
    long long r = 1;
    for (int i = n; i > 0; i -= 2) r *= i;
    return r;
}

long long catalan_number(int n) {
    if (n < 0) return 0;
    long long c = 1;
    for (int i = 0; i < n; i++) c = c * 2 * (2 * i + 1) / (i + 2);
    return c;
}

long long hanoi_moves(int n) {
    if (n < 0) return 0;
    return power(2, n) - 1;
}

int josephus(int n, int k) {
    if (n <= 0 || k <= 0) return -1;
    int r = 0;
    for (int i = 2; i <= n; i++) r = (r + k) % i;
    return r + 1;
}

double radians_to_degrees(double rad) {
    return rad * 180.0 / 3.141592653589793;
}

double degrees_to_radians(double deg) {
    return deg * 3.141592653589793 / 180.0;
}

double sigmoid(double x) {
    return 1.0 / (1.0 + exp(-x));
}

double relu(double x) {
    return (x > 0) ? x : 0.0;
}

double angle_normalize(double deg) {
    double r = fmod(deg, 360.0);
    if (r < 0) r += 360.0;
    return r;
}

long long round_half_up(double x) {
    return (long long)floor(x + 0.5);
}

double percentage(double part, double total) {
    return (total == 0) ? 0.0 : part * 100.0 / total;
}

double median_of_three(double a, double b, double c) {
    if (a > b) { double t = a; a = b; b = t; }
    if (b > c) { double t = b; b = c; c = t; }
    if (a > b) { double t = a; a = b; b = t; }
    return b;
}

double weighted_average(double values[], double weights[], int size) {
    double sv = 0, sw = 0;
    for (int i = 0; i < size; i++) { sv += values[i] * weights[i]; sw += weights[i]; }
    return (sw == 0) ? 0.0 : sv / sw;
}

// ============================================================
//                     进制与转换(扩展)（自动生成）
// ============================================================

char* int_to_base_str(int num, int base, char *buf, int buf_size) {
    if (base < 2 || base > 36 || !buf || buf_size < 2) return buf;
    static const char digits[] = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    int neg = 0;
    if (num < 0) { neg = 1; num = -num; }
    char tmp[40]; int i = 0;
    if (num == 0) tmp[i++] = '0';
    while (num > 0) { tmp[i++] = digits[num % base]; num /= base; }
    int k = 0;
    if (neg && k < buf_size - 1) buf[k++] = '-';
    for (int j = i - 1; j >= 0 && k < buf_size - 1; j--) buf[k++] = tmp[j];
    buf[k] = '\0';
    return buf;
}

long base_str_to_int(const char *str, int base) {
    if (base < 2 || base > 36 || !str) return 0;
    long r = 0;
    while (*str) { int v = hex_char_to_int(*str); if (v < 0 || v >= base) break; r = r * base + v; str++; }
    return r;
}

long str_to_long(const char *str) {
    return strtol(str, NULL, 10);
}

double str_to_double(const char *str) {
    return atof(str);
}

char* double_to_str(double num, char *buf) {
    sprintf(buf, "%.6f", num);
    return buf;
}

char* int_to_roman(int num, char *buf, int buf_size) {
    if (num <= 0 || num >= 4000 || !buf || buf_size < 2) { if (buf && buf_size > 0) buf[0] = '\0'; return buf; }
    static const int vals[] = {1000,900,500,400,100,90,50,40,10,9,5,4,1};
    static const char *syms[] = {"M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"};
    int k = 0;
    for (int i = 0; i < 13 && k < buf_size - 1; i++)
        while (num >= vals[i] && k < buf_size - 1) { buf[k++] = syms[i][0]; if (syms[i][1]) buf[k++] = syms[i][1]; num -= vals[i]; }
    buf[k] = '\0';
    return buf;
}

int roman_to_int(const char *s) {
    int r = 0;
    for (int i = 0; s[i]; i++) {
        int v = (s[i] == 'I') ? 1 : (s[i] == 'V') ? 5 : (s[i] == 'X') ? 10 : (s[i] == 'L') ? 50 : (s[i] == 'C') ? 100 : (s[i] == 'D') ? 500 : (s[i] == 'M') ? 1000 : 0;
        int nv = (s[i+1]) ? ((s[i+1] == 'I') ? 1 : (s[i+1] == 'V') ? 5 : (s[i+1] == 'X') ? 10 : (s[i+1] == 'L') ? 50 : (s[i+1] == 'C') ? 100 : (s[i+1] == 'D') ? 500 : (s[i+1] == 'M') ? 1000 : 0) : 0;
        if (v < nv) r -= v; else r += v;
    }
    return r;
}

char* format_thousands(long long num, char *buf, int buf_size) {
    char tmp[32];
    sprintf(tmp, "%lld", num);
    int neg = 0, i = 0;
    if (tmp[0] == '-') { neg = 1; i = 1; }
    int digits = 0, k = 0;
    for (int j = (int)strlen(tmp) - 1; j >= i; j--) {
        if (digits > 0 && digits % 3 == 0 && k < buf_size - 1) buf[k++] = ',';
        if (k < buf_size - 1) buf[k++] = tmp[j];
        digits++;
    }
    if (neg && k < buf_size - 1) buf[k++] = '-';
    int lo = 0, hi = k - 1;
    while (lo < hi) { char t = buf[lo]; buf[lo] = buf[hi]; buf[hi] = t; lo++; hi--; }
    buf[k] = '\0';
    return buf;
}

char* format_bytes(long long bytes, char *buf, int buf_size) {
    if (!buf || buf_size < 2) return buf;
    const char *units[] = {"B","KB","MB","GB","TB"};
    double v = (double)bytes; int u = 0;
    while (v >= 1024 && u < 4) { v /= 1024; u++; }
    sprintf(buf, "%.2f %s", v, units[u]);
    return buf;
}

// ============================================================
//                     位运算(扩展)（自动生成）
// ============================================================

int get_bit(uint32_t val, int bit) {
    if (bit < 0 || bit > 31) return 0;
    return (val >> bit) & 1u;
}

uint32_t set_bit_value(uint32_t val, int bit, int value) {
    if (bit < 0 || bit > 31) return val;
    if (value) return val | (1u << bit);
    return val & ~(1u << bit);
}

int count_zeros(uint32_t val) {
    return 32 - (int)count_ones(val);
}

int msb_position(uint32_t val) {
    if (val == 0) return -1;
    int pos = 0;
    while (val >>= 1) pos++;
    return pos;
}

uint32_t next_power_of_two(uint32_t n) {
    if (n == 0) return 1;
    if ((n & (n - 1)) == 0) return n;
    uint32_t p = 1;
    while (p < n) p <<= 1;
    return p;
}

uint32_t prev_power_of_two(uint32_t n) {
    if (n == 0) return 0;
    uint32_t p = 1;
    while ((p << 1) <= n) p <<= 1;
    return p;
}

uint32_t reverse_bits(uint32_t val) {
    uint32_t r = 0;
    for (int i = 0; i < 32; i++) { r = (r << 1) | (val & 1u); val >>= 1; }
    return r;
}

uint8_t nibble_high(uint8_t val) {
    return (uint8_t)(val >> 4);
}

uint8_t nibble_low(uint8_t val) {
    return (uint8_t)(val & 0x0F);
}

uint8_t nibble_swap(uint8_t val) {
    return (uint8_t)((val << 4) | (val >> 4));
}

uint32_t bit_field_get(uint32_t val, int start, int len) {
    if (start < 0 || len <= 0 || start + len > 32) return 0;
    return (val >> start) & ((1u << len) - 1);
}

uint32_t bit_field_set(uint32_t val, int start, int len, uint32_t data) {
    if (start < 0 || len <= 0 || start + len > 32) return val;
    uint32_t mask = ((1u << len) - 1) << start;
    return (val & ~mask) | ((data << start) & mask);
}

uint32_t low_bit_mask(int n) {
    if (n <= 0) return 0;
    if (n >= 32) return 0xFFFFFFFFu;
    return (1u << n) - 1;
}

uint32_t high_bit_mask(int n) {
    if (n <= 0) return 0;
    if (n >= 32) return 0xFFFFFFFFu;
    return 0xFFFFFFFFu << (32 - n);
}

void swap_no_temp(int *a, int *b) {
    if (a == b) return;
    *a ^= *b; *b ^= *a; *a ^= *b;
}

int is_mask_contiguous(uint32_t val) {
    if (val == 0) return 0;
    return ((val + (val & -val)) & val) == 0;
}

int sign_int(int n) {
    return (n > 0) - (n < 0);
}

// ============================================================
//                     校验与CRC(扩展)（自动生成）
// ============================================================

uint16_t crc16_ccitt(const uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) { crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021) : (uint16_t)(crc << 1); }
    return crc;
}

uint16_t crc16_xmodem(const uint8_t *data, uint16_t len) {
    uint16_t crc = 0x0000;
    for (uint16_t i = 0; i < len; i++) { crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0; j < 8; j++) crc = (crc & 0x8000) ? (uint16_t)((crc << 1) ^ 0x1021) : (uint16_t)(crc << 1); }
    return crc;
}

uint32_t crc32(const uint8_t *data, uint16_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (uint16_t i = 0; i < len; i++) { crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) crc = (crc & 1) ? (crc >> 1) ^ 0xEDB88320u : crc >> 1; }
    return ~crc;
}

uint16_t fletcher16(const uint8_t *data, uint16_t len) {
    uint16_t sum1 = 0, sum2 = 0;
    for (uint16_t i = 0; i < len; i++) { sum1 = (uint16_t)((sum1 + data[i]) % 255); sum2 = (uint16_t)((sum2 + sum1) % 255); }
    return (uint16_t)((sum2 << 8) | sum1);
}

uint32_t fletcher32(const uint16_t *data, uint16_t len) {
    uint32_t sum1 = 0xFFFF, sum2 = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) { sum1 = (sum1 + data[i]) % 65535; sum2 = (sum2 + sum1) % 65535; }
    return (sum2 << 16) | sum1;
}

uint32_t adler32(const uint8_t *data, uint16_t len) {
    uint32_t a = 1, b = 0;
    for (uint16_t i = 0; i < len; i++) { a = (a + data[i]) % 65521; b = (b + a) % 65521; }
    return (b << 16) | a;
}

uint8_t lrc_checksum(const uint8_t *data, uint16_t len) {
    uint8_t sum = 0;
    for (uint16_t i = 0; i < len; i++) sum += data[i];
    return (uint8_t)(-sum);
}

uint16_t weighted_checksum(const uint8_t *data, uint16_t len) {
    uint16_t sum = 0;
    for (uint16_t i = 0; i < len; i++) sum += (uint16_t)data[i] * (i + 1);
    return sum;
}

uint8_t nmea_checksum(const char *sentence) {
    uint8_t c = 0;
    const char *p = sentence;
    while (*p && *p != '$') p++;
    if (*p == '$') p++;
    while (*p && *p != '*') { c ^= (uint8_t)*p; p++; }
    return c;
}

// ============================================================
//                     哈希函数(扩展)（自动生成）
// ============================================================

uint32_t rshash(const char *str) {
    uint32_t b = 378551, a = 63689, h = 0;
    while (*str) { h = h * a + (unsigned char)*str++; a *= b; }
    return h;
}

uint32_t jshash(const char *str) {
    uint32_t h = 1315423911;
    while (*str) { h ^= ((h << 5) + (unsigned char)*str++ + (h >> 2)); }
    return h;
}

uint32_t pjwhash(const char *str) {
    uint32_t h = 0, high;
    while (*str) { h = (h << 4) + (unsigned char)*str++;
        if ((high = h & 0xF0000000) != 0) h ^= high >> 24;
        h &= ~high; }
    return h;
}

uint32_t elfhash(const char *str) {
    uint32_t h = 0, g;
    while (*str) { h = (h << 4) + (unsigned char)*str++;
        if ((g = h & 0xF0000000) != 0) { h ^= g >> 24; h &= ~g; } }
    return h;
}

uint32_t aphash(const char *str) {
    uint32_t h = 0xAAAAAAAA;
    int i = 0;
    while (*str) {
        h ^= ((i & 1) == 0) ? ((h << 7) ^ (unsigned char)*str * (h >> 3)) : (~((h << 11) + ((unsigned char)*str ^ (h >> 5))));
        i++; str++; }
    return h;
}

uint32_t java_hash(const char *str) {
    uint32_t h = 0;
    while (*str) h = h * 31 + (unsigned char)*str++;
    return h;
}

uint32_t djb2_xor_hash(const char *str) {
    uint32_t h = 5381;
    while (*str) h = ((h << 5) + h) ^ (unsigned char)*str++;
    return h;
}

uint32_t fnv1_hash(const char *str) {
    uint32_t h = 2166136261u;
    while (*str) { h *= 16777619u; h ^= (unsigned char)*str++; }
    return h;
}

uint32_t dekhash(const char *str) {
    uint32_t h = (uint32_t)strlen(str);
    while (*str) { h = ((h << 5) ^ (h >> 27)) ^ (unsigned char)*str++; }
    return h;
}

uint32_t bphash(const char *str) {
    uint32_t h = 0;
    while (*str) h = h * 7 + (unsigned char)*str++;
    return h;
}

uint32_t bkdr_hash_seed(const char *str, uint32_t seed) {
    uint32_t h = 0;
    while (*str) h = h * seed + (unsigned char)*str++;
    return h;
}

// ============================================================
//                     时间与日期（自动生成）
// ============================================================

int is_valid_date(int year, int month, int day) {
    if (month < 1 || month > 12 || day < 1) return 0;
    int dim = days_in_month(year, month);
    return day <= dim;
}

int days_in_month(int year, int month) {
    static const int d[] = {31,28,31,30,31,30,31,31,30,31,30,31};
    if (month < 1 || month > 12) return 0;
    if (month == 2 && is_leap_year(year)) return 29;
    return d[month - 1];
}

int day_of_year(int year, int month, int day) {
    int d = 0;
    for (int m = 1; m < month; m++) d += days_in_month(year, m);
    return d + day;
}

int days_in_year(int year) {
    return is_leap_year(year) ? 366 : 365;
}

int get_year_now(void) {
    time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_year + 1900;
}

int get_month_now(void) {
    time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_mon + 1;
}

int get_day_now(void) {
    time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_mday;
}

int get_hour_now(void) {
    time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_hour;
}

int get_minute_now(void) {
    time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_min;
}

int get_second_now(void) {
    time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_sec;
}

int get_weekday_now(void) {
    time_t t = time(NULL); struct tm *tm = localtime(&t); return tm->tm_wday;
}

char* timestamp_to_date_str(long long ts, char *buf, int buf_size) {
    time_t t = (time_t)ts; struct tm *tm = localtime(&t);
    strftime(buf, (size_t)buf_size, "%Y-%m-%d %H:%M:%S", tm);
    return buf;
}

// ============================================================
//                     随机工具（自动生成）
// ============================================================

void rand_seed_time(void) {
    srand((unsigned)time(NULL));
}

int rand_bool(void) {
    return rand() % 2;
}

double rand_double(void) {
    return (double)rand() / (RAND_MAX + 1.0);
}

double rand_double_range(double min, double max) {
    return min + (max - min) * ((double)rand() / (RAND_MAX + 1.0));
}

int rand_choice_int(int arr[], int size) {
    if (size <= 0) return 0;
    return arr[rand() % size];
}

char* rand_string(char *buf, int buf_size, int len) {
    if (!buf || buf_size <= 0) return buf;
    if (len >= buf_size) len = buf_size - 1;
    for (int i = 0; i < len; i++) buf[i] = (char)(33 + rand() % 94);
    buf[len] = '\0';
    return buf;
}

char* rand_digits_string(char *buf, int buf_size, int len) {
    if (!buf || buf_size <= 0) return buf;
    if (len >= buf_size) len = buf_size - 1;
    for (int i = 0; i < len; i++) buf[i] = (char)('0' + rand() % 10);
    buf[len] = '\0';
    return buf;
}

void rand_shuffle_str(char *str) {
    int n = str_len(str);
    for (int i = n - 1; i > 0; i--) { int j = rand() % (i + 1); char t = str[i]; str[i] = str[j]; str[j] = t; }
}

int* rand_unique_ints(int min, int max, int n) {
    if (min > max || n <= 0) return NULL;
    int range = max - min + 1;
    if (n > range) n = range;
    int *r = (int*)malloc(n * sizeof(int));
    if (!r) return NULL;
    int cnt = 0;
    while (cnt < n) { int v = min + rand() % range; int dup = 0; for (int i = 0; i < cnt; i++) if (r[i] == v) { dup = 1; break; } if (!dup) r[cnt++] = v; }
    return r;
}

// ============================================================
//                     几何工具（自动生成）
// ============================================================

double distance_2d(double x1, double y1, double x2, double y2) {
    double dx = x2 - x1, dy = y2 - y1;
    return sqrt(dx * dx + dy * dy);
}

double distance_3d(double x1, double y1, double z1, double x2, double y2, double z2) {
    double dx = x2 - x1, dy = y2 - y1, dz = z2 - z1;
    return sqrt(dx * dx + dy * dy + dz * dz);
}

double area_triangle_heron(double a, double b, double c) {
    double s = (a + b + c) / 2.0;
    double t = s * (s - a) * (s - b) * (s - c);
    return (t > 0) ? sqrt(t) : 0.0;
}

double perimeter_triangle(double a, double b, double c) {
    return a + b + c;
}

double circle_area(double r) {
    return 3.141592653589793 * r * r;
}

double circle_circumference(double r) {
    return 2.0 * 3.141592653589793 * r;
}

double circle_diameter(double r) {
    return 2.0 * r;
}

double sphere_volume(double r) {
    return 4.0 / 3.0 * 3.141592653589793 * r * r * r;
}

double sphere_surface_area(double r) {
    return 4.0 * 3.141592653589793 * r * r;
}

double rect_area(double w, double h) {
    return w * h;
}

double rect_perimeter(double w, double h) {
    return 2.0 * (w + h);
}

int is_point_in_rect(double px, double py, double x, double y, double w, double h) {
    return (px >= x && px <= x + w && py >= y && py <= y + h);
}

int is_point_in_circle(double px, double py, double cx, double cy, double r) {
    return distance_2d(px, py, cx, cy) <= r;
}

double slope_between(double x1, double y1, double x2, double y2) {
    if (x2 == x1) return 0.0;
    return (y2 - y1) / (x2 - x1);
}

void midpoint_2d(double x1, double y1, double x2, double y2, double *mx, double *my) {
    *mx = (x1 + x2) / 2.0;
    *my = (y1 + y2) / 2.0;
}

double hexagon_area(double side) {
    return (3.0 * sqrt(3.0) / 2.0) * side * side;
}

double cylinder_volume(double r, double h) {
    return 3.141592653589793 * r * r * h;
}

// ============================================================
//                     数值工具（自动生成）
// ============================================================

int clamp_int(int v, int lo, int hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

double clamp_double(double v, double lo, double hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

double lerp_double(double a, double b, double t) {
    return a + (b - a) * t;
}

int lerp_int(int a, int b, int t, int max_t) {
    if (max_t == 0) return a;
    return a + (b - a) * t / max_t;
}

double map_range_double(double v, double s1, double s2, double d1, double d2) {
    if (s2 == s1) return d1;
    return d1 + (v - s1) * (d2 - d1) / (s2 - s1);
}

long long round_to_int(double x) {
    return (long long)floor(x + 0.5);
}

long long ceil_to_multiple(long long v, long long m) {
    if (m <= 0) return v;
    return ((v + m - 1) / m) * m;
}

long long floor_to_multiple(long long v, long long m) {
    if (m <= 0) return v;
    return (v / m) * m;
}

int approx_equal_double(double a, double b, double eps) {
    return (fabs(a - b) <= eps);
}

int max3_int(int a, int b, int c) {
    int m = a;
    if (b > m) m = b;
    if (c > m) m = c;
    return m;
}

int min3_int(int a, int b, int c) {
    int m = a;
    if (b < m) m = b;
    if (c < m) m = c;
    return m;
}

int max4_int(int a, int b, int c, int d) {
    int m = max3_int(a, b, c);
    if (d > m) m = d;
    return m;
}

double fabs_double(double x) {
    return fabs(x);
}

long long floor_int(double x) {
    return (long long)floor(x);
}

long long ceil_int(double x) {
    return (long long)ceil(x);
}

long long sum_natural(int n) {
    return (n <= 0) ? 0 : (long long)n * (n + 1) / 2;
}

long long sum_squares(int n) {
    if (n <= 0) return 0;
    return (long long)n * (n + 1) * (2 * n + 1) / 6;
}

long long sum_cubes(int n) {
    long long s = sum_natural(n);
    return s * s;
}

long long arithmetic_sum(long long a1, long long d, int n) {
    if (n <= 0) return 0;
    return n * (2 * a1 + (n - 1) * d) / 2;
}

// ============================================================
//                     数据结构(扩展)（自动生成）
// ============================================================

DList* dlist_create(void) {
    DList *l = (DList*)malloc(sizeof(DList));
    if (!l) return NULL;
    l->head = l->tail = NULL; l->size = 0;
    return l;
}

int dlist_push_front(DList *l, int data) {
    if (!l) return -1;
    DNode *n = (DNode*)malloc(sizeof(DNode));
    if (!n) return -1;
    n->data = data; n->prev = NULL; n->next = l->head;
    if (l->head) l->head->prev = n; else l->tail = n;
    l->head = n; l->size++;
    return 0;
}

int dlist_push_back(DList *l, int data) {
    if (!l) return -1;
    DNode *n = (DNode*)malloc(sizeof(DNode));
    if (!n) return -1;
    n->data = data; n->next = NULL; n->prev = l->tail;
    if (l->tail) l->tail->next = n; else l->head = n;
    l->tail = n; l->size++;
    return 0;
}

int dlist_remove(DList *l, int data) {
    if (!l) return -1;
    for (DNode *p = l->head; p; p = p->next) {
        if (p->data == data) {
            if (p->prev) p->prev->next = p->next; else l->head = p->next;
            if (p->next) p->next->prev = p->prev; else l->tail = p->prev;
            free(p); l->size--; return 0;
        }
    }
    return -1;
}

DNode* dlist_search(DList *l, int data) {
    if (!l) return NULL;
    for (DNode *p = l->head; p; p = p->next) if (p->data == data) return p;
    return NULL;
}

int dlist_length(DList *l) {
    return (l == NULL) ? 0 : l->size;
}

void dlist_print(DList *l) {
    if (!l) return;
    for (DNode *p = l->head; p; p = p->next) printf("%d <-> ", p->data);
    printf("NULL\n");
}

void dlist_reverse(DList *l) {
    if (!l || l->size < 2) return;
    DNode *p = l->head, *t = l->tail;
    while (p) { DNode *n = p->next; p->next = p->prev; p->prev = n; p = n; }
    l->head = t; l->tail = l->head ? l->head->prev : NULL;
}

void dlist_free(DList *l) {
    if (!l) return;
    DNode *p = l->head;
    while (p) { DNode *n = p->next; free(p); p = n; }
    free(l);
}

Deque* deque_create(int capacity) {
    if (capacity <= 0) return NULL;
    Deque *d = (Deque*)malloc(sizeof(Deque));
    if (!d) return NULL;
    d->data = (int*)malloc(capacity * sizeof(int));
    if (!d->data) { free(d); return NULL; }
    d->front = 0; d->rear = 0; d->size = 0; d->capacity = capacity;
    return d;
}

void deque_destroy(Deque *d) {
    if (!d) return;
    free(d->data);
    free(d);
}

int deque_push_front(Deque *d, int value) {
    if (!d || d->size >= d->capacity) return -1;
    d->front = (d->front - 1 + d->capacity) % d->capacity;
    d->data[d->front] = value; d->size++;
    return 0;
}

int deque_push_back(Deque *d, int value) {
    if (!d || d->size >= d->capacity) return -1;
    d->data[d->rear] = value;
    d->rear = (d->rear + 1) % d->capacity; d->size++;
    return 0;
}

int deque_pop_front(Deque *d, int *out) {
    if (!d || d->size <= 0 || !out) return -1;
    *out = d->data[d->front];
    d->front = (d->front + 1) % d->capacity; d->size--;
    return 0;
}

int deque_pop_back(Deque *d, int *out) {
    if (!d || d->size <= 0 || !out) return -1;
    d->rear = (d->rear - 1 + d->capacity) % d->capacity;
    *out = d->data[d->rear]; d->size--;
    return 0;
}

int deque_peek_front(Deque *d, int *out) {
    if (!d || d->size <= 0 || !out) return -1;
    *out = d->data[d->front];
    return 0;
}

int deque_peek_back(Deque *d, int *out) {
    if (!d || d->size <= 0 || !out) return -1;
    *out = d->data[(d->rear - 1 + d->capacity) % d->capacity];
    return 0;
}

int deque_size(Deque *d) {
    return (d == NULL) ? 0 : d->size;
}

int deque_is_empty(Deque *d) {
    return (d == NULL || d->size == 0);
}

int deque_is_full(Deque *d) {
    return (d != NULL && d->size >= d->capacity);
}

void deque_clear(Deque *d) {
    if (!d) return;
    d->front = 0; d->rear = 0; d->size = 0;
}

MinHeap* mheap_create(int capacity) {
    if (capacity <= 0) return NULL;
    MinHeap *h = (MinHeap*)malloc(sizeof(MinHeap));
    if (!h) return NULL;
    h->data = (int*)malloc(capacity * sizeof(int));
    if (!h->data) { free(h); return NULL; }
    h->size = 0; h->capacity = capacity;
    return h;
}

void mheap_destroy(MinHeap *h) {
    if (!h) return;
    free(h->data);
    free(h);
}

int mheap_push(MinHeap *h, int value) {
    if (!h) return -1;
    if (h->size >= h->capacity) return -1;
    int i = h->size++;
    h->data[i] = value;
    while (i > 0) { int p = (i - 1) / 2; if (h->data[p] <= h->data[i]) break; int t = h->data[p]; h->data[p] = h->data[i]; h->data[i] = t; i = p; }
    return 0;
}

int mheap_pop(MinHeap *h, int *out) {
    if (!h || h->size <= 0 || !out) return -1;
    *out = h->data[0];
    h->data[0] = h->data[--h->size];
    int i = 0;
    while (1) { int l = 2 * i + 1, r = 2 * i + 2, s = i;
        if (l < h->size && h->data[l] < h->data[s]) s = l;
        if (r < h->size && h->data[r] < h->data[s]) s = r;
        if (s == i) break;
        int t = h->data[s]; h->data[s] = h->data[i]; h->data[i] = t; i = s; }
    return 0;
}

int mheap_peek(MinHeap *h, int *out) {
    if (!h || h->size <= 0 || !out) return -1;
    *out = h->data[0];
    return 0;
}

int mheap_size(MinHeap *h) {
    return (h == NULL) ? 0 : h->size;
}

int mheap_is_empty(MinHeap *h) {
    return (h == NULL || h->size == 0);
}

IntSet* iset_create(int capacity) {
    if (capacity <= 0) capacity = 16;
    IntSet *s = (IntSet*)malloc(sizeof(IntSet));
    if (!s) return NULL;
    s->data = (int*)calloc(capacity, sizeof(int));
    s->used = (char*)calloc(capacity, 1);
    s->del = (char*)calloc(capacity, 1);
    if (!s->data || !s->used || !s->del) { free(s->data); free(s->used); free(s->del); free(s); return NULL; }
    s->size = 0; s->capacity = capacity;
    return s;
}

void iset_destroy(IntSet *s) {
    if (!s) return;
    free(s->data); free(s->used); free(s->del); free(s);
}

int iset_add(IntSet *s, int key) {
    if (!s) return -1;
    if (s->size * 2 >= s->capacity) return -1;
    int i = ((key * 2654435761u) & 0x7FFFFFFF) % s->capacity;
    while (s->used[i]) { if (!s->del[i] && s->data[i] == key) return 0; i = (i + 1) % s->capacity; }
    s->used[i] = 1; s->del[i] = 0; s->data[i] = key; s->size++;
    return 0;
}

int iset_contains(IntSet *s, int key) {
    if (!s) return 0;
    int i = ((key * 2654435761u) & 0x7FFFFFFF) % s->capacity;
    while (s->used[i]) { if (!s->del[i] && s->data[i] == key) return 1; i = (i + 1) % s->capacity; }
    return 0;
}

int iset_remove(IntSet *s, int key) {
    if (!s) return -1;
    int i = ((key * 2654435761u) & 0x7FFFFFFF) % s->capacity;
    while (s->used[i]) { if (!s->del[i] && s->data[i] == key) { s->del[i] = 1; s->size--; return 0; } i = (i + 1) % s->capacity; }
    return -1;
}

int iset_size(IntSet *s) {
    return (s == NULL) ? 0 : s->size;
}

void iset_clear(IntSet *s) {
    if (!s) return;
    for (int i = 0; i < s->capacity; i++) { s->used[i] = 0; s->del[i] = 0; }
    s->size = 0;
}

StrMap* smap_create(int capacity) {
    if (capacity <= 0) capacity = 16;
    StrMap *m = (StrMap*)malloc(sizeof(StrMap));
    if (!m) return NULL;
    m->keys = (char**)calloc(capacity, sizeof(char*));
    m->values = (int*)calloc(capacity, sizeof(int));
    m->used = (char*)calloc(capacity, 1);
    if (!m->keys || !m->values || !m->used) { free(m->keys); free(m->values); free(m->used); free(m); return NULL; }
    m->size = 0; m->capacity = capacity;
    return m;
}

void smap_destroy(StrMap *m) {
    if (!m) return;
    for (int i = 0; i < m->capacity; i++) if (m->used[i]) free(m->keys[i]);
    free(m->keys); free(m->values); free(m->used); free(m);
}

int smap_put(StrMap *m, const char *key, int value) {
    if (!m || !key) return -1;
    if (m->size * 2 >= m->capacity) return -1;
    uint32_t h = djb2_hash(key);
    int i = h % m->capacity;
    while (m->used[i]) { if (str_cmp(m->keys[i], key) == 0) { m->values[i] = value; return 0; } i = (i + 1) % m->capacity; }
    m->keys[i] = copy_string(key); if (!m->keys[i]) return -1;
    m->values[i] = value; m->used[i] = 1; m->size++;
    return 0;
}

int smap_get(StrMap *m, const char *key, int *out) {
    if (!m || !key || !out) return -1;
    uint32_t h = djb2_hash(key);
    int i = h % m->capacity;
    while (m->used[i]) { if (str_cmp(m->keys[i], key) == 0) { *out = m->values[i]; return 0; } i = (i + 1) % m->capacity; }
    return -1;
}

int smap_contains(StrMap *m, const char *key) {
    if (!m || !key) return 0;
    uint32_t h = djb2_hash(key);
    int i = h % m->capacity;
    while (m->used[i]) { if (str_cmp(m->keys[i], key) == 0) return 1; i = (i + 1) % m->capacity; }
    return 0;
}

int smap_remove(StrMap *m, const char *key) {
    if (!m || !key) return -1;
    uint32_t h = djb2_hash(key);
    int i = h % m->capacity;
    while (m->used[i]) { if (str_cmp(m->keys[i], key) == 0) { free(m->keys[i]); m->keys[i] = NULL; m->used[i] = 0; m->size--; return 0; } i = (i + 1) % m->capacity; }
    return -1;
}

int smap_size(StrMap *m) {
    return (m == NULL) ? 0 : m->size;
}

Graph* graph_create(int n) {
    if (n <= 0) return NULL;
    Graph *g = (Graph*)malloc(sizeof(Graph));
    if (!g) return NULL;
    g->n = n;
    g->adj = (int**)calloc(n, sizeof(int*));
    if (!g->adj) { free(g); return NULL; }
    for (int i = 0; i < n; i++) { g->adj[i] = (int*)calloc(n, sizeof(int)); if (!g->adj[i]) return NULL; }
    return g;
}

void graph_destroy(Graph *g) {
    if (!g) return;
    for (int i = 0; i < g->n; i++) free(g->adj[i]);
    free(g->adj);
    free(g);
}

void graph_add_edge(Graph *g, int u, int v) {
    if (!g || u < 0 || u >= g->n || v < 0 || v >= g->n) return;
    g->adj[u][v] = 1; g->adj[v][u] = 1;
}

void graph_remove_edge(Graph *g, int u, int v) {
    if (!g || u < 0 || u >= g->n || v < 0 || v >= g->n) return;
    g->adj[u][v] = 0; g->adj[v][u] = 0;
}

int graph_has_edge(Graph *g, int u, int v) {
    if (!g || u < 0 || u >= g->n || v < 0 || v >= g->n) return 0;
    return g->adj[u][v];
}

int graph_degree(Graph *g, int v) {
    if (!g || v < 0 || v >= g->n) return 0;
    int d = 0;
    for (int i = 0; i < g->n; i++) d += g->adj[v][i];
    return d;
}

void graph_print(Graph *g) {
    if (!g) return;
    for (int i = 0; i < g->n; i++) { for (int j = 0; j < g->n; j++) printf("%d ", g->adj[i][j]); printf("\n"); }
}

void graph_bfs(Graph *g, int start) {
    if (!g || start < 0 || start >= g->n) return;
    char *vis = (char*)calloc(g->n, 1);
    int *q = (int*)malloc(g->n * sizeof(int));
    int head = 0, tail = 0;
    vis[start] = 1; q[tail++] = start;
    while (head < tail) { int v = q[head++]; printf("%d ", v);
        for (int i = 0; i < g->n; i++) if (g->adj[v][i] && !vis[i]) { vis[i] = 1; q[tail++] = i; } }
    printf("\n");
    free(vis); free(q);
}

void graph_dfs(Graph *g, int start) {
    if (!g || start < 0 || start >= g->n) return;
    char *vis = (char*)calloc(g->n, 1);
    int st[1024], top = 0;
    vis[start] = 1; st[top++] = start;
    while (top > 0) { int v = st[--top]; printf("%d ", v);
        for (int i = g->n - 1; i >= 0; i--) if (g->adj[v][i] && !vis[i]) { vis[i] = 1; st[top++] = i; } }
    printf("\n");
    free(vis);
}

int* graph_dijkstra(Graph *g, int src) {
    if (!g || src < 0 || src >= g->n) return NULL;
    int *dist = (int*)malloc(g->n * sizeof(int));
    char *done = (char*)calloc(g->n, 1);
    for (int i = 0; i < g->n; i++) dist[i] = 1000000000;
    dist[src] = 0;
    for (int k = 0; k < g->n; k++) {
        int u = -1;
        for (int i = 0; i < g->n; i++) if (!done[i] && (u < 0 || dist[i] < dist[u])) u = i;
        if (u < 0) break;
        done[u] = 1;
        for (int v = 0; v < g->n; v++) if (g->adj[u][v] && dist[u] + 1 < dist[v]) dist[v] = dist[u] + 1;
    }
    free(done);
    return dist;
}

// ============================================================
//                     文件工具(扩展)（自动生成）
// ============================================================

int file_append_line(const char *filename, const char *line) {
    FILE *fp = fopen(filename, "a");
    if (!fp) return -1;
    fprintf(fp, "%s\n", line);
    fclose(fp);
    return 0;
}

int file_is_empty(const char *filename) {
    FILE *fp = fopen(filename, "rb");
    if (!fp) return 1;
    fseek(fp, 0, SEEK_END);
    int e = (ftell(fp) == 0);
    fclose(fp);
    return e;
}

int file_touch(const char *filename) {
    FILE *fp = fopen(filename, "a");
    if (!fp) return -1;
    fclose(fp);
    return 0;
}

int file_delete(const char *filename) {
    return remove(filename);
}

int file_rename(const char *old, const char *new) {
    return rename(old, new);
}

char* file_stem(const char *path, char *buf, int buf_size) {
    if (!path || !buf || buf_size <= 0) return NULL;
    get_base_name(path, buf, buf_size);
    const char *dot = strrchr(buf, '.');
    if (dot) *((char*)dot) = '\0';
    return buf;
}

char* file_read_line(FILE *fp, char *buf, int buf_size) {
    return safe_fgets(buf, (size_t)buf_size, fp);
}

// ============================================================
//                     内存工具(扩展)（自动生成）
// ============================================================

void* safe_memdup(const void *src, size_t size) {
    if (!src) return NULL;
    void *r = malloc(size);
    if (!r) return NULL;
    memcpy(r, src, size);
    return r;
}

void zero_memory(void *ptr, size_t size) {
    if (ptr) memset(ptr, 0, size);
}

void fill_memory(void *ptr, size_t size, unsigned char value) {
    if (ptr) memset(ptr, value, size);
}

int compare_memory(const void *a, const void *b, size_t size) {
    return memcmp(a, b, size);
}

void swap_memory(void *a, void *b, size_t size) {
    if (!a || !b || a == b) return;
    unsigned char *pa = (unsigned char*)a, *pb = (unsigned char*)b;
    for (size_t i = 0; i < size; i++) { unsigned char t = pa[i]; pa[i] = pb[i]; pb[i] = t; }
}

// ============================================================
//                     控制台与调试(扩展)（自动生成）
// ============================================================

void print_int(int v) {
    printf("%d\n", v);
}

void print_long(long v) {
    printf("%ld\n", v);
}

void print_double(double v) {
    printf("%.6f\n", v);
}

void print_hex(unsigned int v) {
    printf("0x%X\n", v);
}

void print_char(char c) {
    printf("%c\n", c);
}

void print_separator(void) {
    printf("----------------------------------------\n");
}

void print_box_title(const char *title) {
    int n = str_len(title);
    printf("=="); for (int i = 0; i < n; i++) printf("="); printf("==\n");
    printf("  %s\n", title);
    printf("=="); for (int i = 0; i < n; i++) printf("="); printf("==\n");
}

void print_str_array(char *arr[], int size) {
    for (int i = 0; i < size; i++) printf("%s\n", arr[i]);
}

void clear_console(void) {
    printf("\033[2J\033[H");
}

void log_info(const char *msg) {
    printf("[INFO] %s\n", msg);
}

void log_warn(const char *msg) {
    printf("[WARN] %s\n", msg);
}

void log_error(const char *msg) {
    printf("[ERROR] %s\n", msg);
}

// ============================================================
//                     矩阵工具（自动生成）
// ============================================================

double** mat_create(int rows, int cols) {
    if (rows <= 0 || cols <= 0) return NULL;
    double **m = (double**)malloc(rows * sizeof(double*));
    if (!m) return NULL;
    for (int i = 0; i < rows; i++) { m[i] = (double*)calloc(cols, sizeof(double)); if (!m[i]) return NULL; }
    return m;
}

void mat_free(double **m, int rows) {
    if (!m) return;
    for (int i = 0; i < rows; i++) free(m[i]);
    free(m);
}

void mat_fill(double **m, int rows, int cols, double v) {
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) m[i][j] = v;
}

void mat_print(double **m, int rows, int cols) {
    for (int i = 0; i < rows; i++) { for (int j = 0; j < cols; j++) printf("%.2f ", m[i][j]); printf("\n"); }
}

void mat_transpose(double **m, int rows, int cols, double **out) {
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[j][i] = m[i][j];
}

void mat_add(double **a, double **b, int rows, int cols, double **out) {
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = a[i][j] + b[i][j];
}

void mat_sub(double **a, double **b, int rows, int cols, double **out) {
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = a[i][j] - b[i][j];
}

void mat_mul(double **a, int ar, int ac, double **b, int bc, double **out) {
    for (int i = 0; i < ar; i++) for (int j = 0; j < bc; j++) { out[i][j] = 0; for (int k = 0; k < ac; k++) out[i][j] += a[i][k] * b[k][j]; }
}

void mat_identity(double **m, int n) {
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) m[i][j] = (i == j) ? 1.0 : 0.0;
}

void mat_scalar_mul(double **m, int rows, int cols, double s, double **out) {
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = m[i][j] * s;
}

double mat_trace(double **m, int n) {
    double t = 0;
    for (int i = 0; i < n; i++) t += m[i][i];
    return t;
}

double mat_det2(double **m) {
    return m[0][0] * m[1][1] - m[0][1] * m[1][0];
}

double mat_det3(double **m) {
    return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1]) - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0]) + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]);
}

double mat_sum(double **m, int rows, int cols) {
    double s = 0;
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) s += m[i][j];
    return s;
}

double mat_max(double **m, int rows, int cols) {
    double v = m[0][0];
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) if (m[i][j] > v) v = m[i][j];
    return v;
}

double mat_min(double **m, int rows, int cols) {
    double v = m[0][0];
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) if (m[i][j] < v) v = m[i][j];
    return v;
}

double mat_row_sum(double **m, int cols, int row) {
    double s = 0;
    for (int j = 0; j < cols; j++) s += m[row][j];
    return s;
}

double mat_col_sum(double **m, int rows, int col) {
    double s = 0;
    for (int i = 0; i < rows; i++) s += m[i][col];
    return s;
}

double** mat_copy(double **m, int rows, int cols) {
    double **r = mat_create(rows, cols);
    if (!r) return NULL;
    for (int i = 0; i < rows; i++) memcpy(r[i], m[i], cols * sizeof(double));
    return r;
}

// ============================================================
//                     向量与杂项（自动生成）
// ============================================================

double dot_product(double a[], double b[], int size) {
    double s = 0;
    for (int i = 0; i < size; i++) s += a[i] * b[i];
    return s;
}

double vector_length_2d(double x, double y) {
    return sqrt(x * x + y * y);
}

double vector_length_3d(double x, double y, double z) {
    return sqrt(x * x + y * y + z * z);
}

void normalize_2d(double x, double y, double *ox, double *oy) {
    double len = sqrt(x * x + y * y);
    if (len == 0) { *ox = 0; *oy = 0; return; }
    *ox = x / len; *oy = y / len;
}

double cross_product_2d(double ax, double ay, double bx, double by) {
    return ax * by - ay * bx;
}

void moving_average(double arr[], int size, int window, double out[]) {
    for (int i = 0; i < size; i++) { double s = 0; int c = 0;
        for (int j = (i - window + 1 < 0) ? 0 : i - window + 1; j <= i; j++) { s += arr[j]; c++; }
        out[i] = s / c; }
}

void int_array_to_double(int src[], double dst[], int size) {
    for (int i = 0; i < size; i++) dst[i] = (double)src[i];
}

void double_array_to_int(double src[], int dst[], int size) {
    for (int i = 0; i < size; i++) dst[i] = (int)src[i];
}

char* base64_encode(const uint8_t *data, int len) {
    static const char tbl[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    int out_len = ((len + 2) / 3) * 4;
    char *out = (char*)malloc(out_len + 1);
    if (!out) return NULL;
    int i = 0, j = 0;
    for (; i + 2 < len; i += 3) {
        unsigned v = ((unsigned)data[i] << 16) | ((unsigned)data[i+1] << 8) | (unsigned)data[i+2];
        out[j++] = tbl[(v >> 18) & 63]; out[j++] = tbl[(v >> 12) & 63]; out[j++] = tbl[(v >> 6) & 63]; out[j++] = tbl[v & 63];
    }
    int rem = len - i;
    if (rem == 1) {
        unsigned v = (unsigned)data[i] << 16;
        out[j++] = tbl[(v >> 18) & 63]; out[j++] = tbl[(v >> 12) & 63]; out[j++] = '='; out[j++] = '=';
    } else if (rem == 2) {
        unsigned v = ((unsigned)data[i] << 16) | ((unsigned)data[i+1] << 8);
        out[j++] = tbl[(v >> 18) & 63]; out[j++] = tbl[(v >> 12) & 63]; out[j++] = tbl[(v >> 6) & 63]; out[j++] = '=';
    }
    out[j] = '\0';
    return out;
}

uint8_t* base64_decode(const char *s, int *out_len) {
    static const int T[] = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,62,-1,-1,-1,63,52,53,54,55,56,57,58,59,60,61,-1,-1,-1,-1,-1,-1,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,-1,-1,-1,-1,-1,-1,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,-1,-1,-1,-1,-1};
    int len = str_len(s);
    uint8_t *out = (uint8_t*)malloc((len / 4) * 3 + 3);
    if (!out) return NULL;
    int j = 0, val = 0, bits = 0;
    for (int i = 0; i < len; i++) {
        if (s[i] == '=') break;
        int d = ((unsigned char)s[i] < 128) ? T[(unsigned char)s[i]] : -1;
        if (d < 0) continue;
        val = (val << 6) | d; bits += 6;
        if (bits >= 8) { bits -= 8; out[j++] = (uint8_t)((val >> bits) & 0xFF); }
    }
    *out_len = j;
    return out;
}

char* url_encode_str(const char *s) {
    static const char hex[] = "0123456789ABCDEF";
    int n = str_len(s);
    char *r = (char*)malloc(n * 3 + 1);
    if (!r) return NULL;
    int j = 0;
    for (int i = 0; i < n; i++) { unsigned char c = (unsigned char)s[i];
        if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') r[j++] = (char)c;
        else { r[j++] = '%'; r[j++] = hex[c >> 4]; r[j++] = hex[c & 15]; } }
    r[j] = '\0';
    return r;
}

// ============================================================
//                     字符串工具(第二批)（自动生成）
// ============================================================

int str_contains_ignore_case(const char *haystack, const char *needle) {
    int n = str_len(needle);
    if (n == 0) return 1;
    const char *p = haystack;
    while (*p) { int ok = 1; for (int i = 0; i < n; i++) if (char_to_lower(p[i]) != char_to_lower(needle[i])) { ok = 0; break; } if (ok) return 1; p++; }
    return 0;
}

int str_compare_case_insensitive(const char *a, const char *b) {
    while (*a && *b) { if (char_to_lower(*a) != char_to_lower(*b)) break; a++; b++; }
    return (unsigned char)char_to_lower(*a) - (unsigned char)char_to_lower(*b);
}

int str_is_palindrome_ignore_case(const char *str) {
    int len = str_len(str);
    for (int i = 0; i < len / 2; i++) if (char_to_lower(str[i]) != char_to_lower(str[len - 1 - i])) return 0;
    return 1;
}

void str_reverse_each_word(char *str) {
    int len = str_len(str), i = 0;
    while (i < len) { while (i < len && str[i] == ' ') i++; int s = i; while (i < len && str[i] != ' ') i++; int a = s, b = i - 1; while (a < b) { char t = str[a]; str[a] = str[b]; str[b] = t; a++; b--; } }
}

void str_shift_left(char *str, int n) {
    int len = str_len(str);
    if (len == 0) return;
    n %= len;
    for (int k = 0; k < n; k++) { char c = str[0]; for (int i = 0; i < len - 1; i++) str[i] = str[i + 1]; str[len - 1] = c; }
}

void str_shift_right(char *str, int n) {
    int len = str_len(str);
    if (len == 0) return;
    n %= len;
    for (int k = 0; k < n; k++) { char c = str[len - 1]; for (int i = len - 1; i > 0; i--) str[i] = str[i - 1]; str[0] = c; }
}

void str_deduplicate_chars(char *str) {
    char *w = str; char prev = '\0';
    while (*str) { if (*str != prev) { *w++ = *str; prev = *str; } str++; }
    *w = '\0';
}

void str_remove_consonants(char *str) {
    char *w = str;
    while (*str) { if (!is_alpha_char(*str) || is_vowel_char(*str)) *w++ = *str; str++; }
    *w = '\0';
}

int str_count_consonants(const char *str) {
    int c = 0;
    while (*str) { if (is_alpha_char(*str) && !is_vowel_char(*str)) c++; str++; }
    return c;
}

void str_append_char(char *buf, int buf_size, char c) {
    int n = str_len(buf);
    if (n + 1 < buf_size) { buf[n] = c; buf[n + 1] = '\0'; }
}

void str_remove_first_char(char *str) {
    if (*str) { char *p = str; while (*p) { *p = *(p + 1); p++; } }
}

void str_remove_last_char(char *str) {
    int n = str_len(str);
    if (n > 0) str[n - 1] = '\0';
}

int str_find_nth(const char *str, const char *sub, int n) {
    int cnt = 0, sl = str_len(sub);
    if (n < 0 || sl == 0) return -1;
    const char *p = str;
    while ((p = str_find(p, sub)) != NULL) { if (cnt == n) return (int)(p - str); cnt++; p += sl; }
    return -1;
}

int str_count_digits(const char *str) {
    int c = 0;
    while (*str) { if (is_digit_char(*str)) c++; str++; }
    return c;
}

int str_count_letters(const char *str) {
    int c = 0;
    while (*str) { if (is_alpha_char(*str)) c++; str++; }
    return c;
}

int str_count_uppercase(const char *str) {
    int c = 0;
    while (*str) { if (is_upper_char(*str)) c++; str++; }
    return c;
}

int str_count_lowercase(const char *str) {
    int c = 0;
    while (*str) { if (is_lower_char(*str)) c++; str++; }
    return c;
}

int str_count_spaces(const char *str) {
    int c = 0;
    while (*str) { if (*str == ' ') c++; str++; }
    return c;
}

void str_normalize_spaces(char *str) {
    char *w = str; int sp = 0;
    while (*str) { if (*str == ' ' || *str == '\t') { if (!sp && w != str) { *w++ = ' '; sp = 1; } } else { *w++ = *str; sp = 0; } str++; }
    if (w != str && w[-1] == ' ') w--;
    *w = '\0';
}

char* str_abbreviate(const char *str, char *buf, int buf_size) {
    int k = 0, in = 0;
    if (buf_size <= 0) return buf;
    while (*str && k < buf_size - 1) { if (is_space_char(*str)) in = 0; else if (!in) { buf[k++] = *str; in = 1; } str++; }
    buf[k] = '\0';
    return buf;
}

char* str_word_at(const char *str, int n, char *buf, int buf_size) {
    int idx = 0, k = 0, in = 0;
    if (buf_size <= 0) return buf;
    buf[0] = '\0';
    while (*str) {
        if (is_space_char(*str)) { in = 0; str++; continue; }
        if (!in) { in = 1; if (idx == n) { while (*str && !is_space_char(*str) && k < buf_size - 1) buf[k++] = *str++; buf[k] = '\0'; return buf; } idx++; }
        str++;
    }
    return buf;
}

char* str_mask_sensitive(const char *str, char *buf, int buf_size) {
    int n = str_len(str);
    if (buf_size <= 0) return buf;
    int keep = (n < 4) ? n : 4, mask = n - keep, k = 0;
    for (int i = 0; i < mask && k < buf_size - 1; i++) buf[k++] = '*';
    for (int i = mask; i < n && k < buf_size - 1; i++) buf[k++] = str[i];
    buf[k] = '\0';
    return buf;
}

int str_is_valid_email(const char *s) {
    const char *at = str_find(s, "@");
    if (!at || at == s) return 0;
    const char *dot = strrchr(s, '.');
    if (!dot || dot < at || dot[1] == '\0') return 0;
    return 1;
}

int str_count_sentences(const char *str) {
    int c = 0;
    while (*str) { if (*str == '.' || *str == '!' || *str == '?') c++; str++; }
    return c;
}

int str_longest_palindrome_substr_len(const char *s) {
    int n = str_len(s);
    if (n < 2) return n;
    int *dp = (int*)calloc((size_t)n * n, sizeof(int));
    if (!dp) return n > 0 ? 1 : 0;
    int best = 1;
    for (int i = 0; i < n; i++) dp[i * n + i] = 1;
    for (int i = 0; i < n - 1; i++) if (s[i] == s[i + 1]) { dp[i * n + i + 1] = 1; best = 2; }
    for (int len = 3; len <= n; len++) for (int i = 0; i + len - 1 < n; i++) {
        int j = i + len - 1;
        if (s[i] == s[j] && dp[(i + 1) * n + j - 1]) { dp[i * n + j] = 1; if (len > best) best = len; } }
    free(dp);
    return best;
}

void str_reverse_vowels(char *str) {
    int len = str_len(str), i = 0, j = len - 1;
    while (i < j) { while (i < j && !is_vowel_char(str[i])) i++; while (i < j && !is_vowel_char(str[j])) j--;
        if (i < j) { char t = str[i]; str[i] = str[j]; str[j] = t; i++; j--; } }
}

void str_remove_digits(char *str) {
    char *w = str;
    while (*str) { if (!is_digit_char(*str)) *w++ = *str; str++; }
    *w = '\0';
}

void str_keep_digits_only(char *str) {
    char *w = str;
    while (*str) { if (is_digit_char(*str)) *w++ = *str; str++; }
    *w = '\0';
}

void str_keep_letters_only(char *str) {
    char *w = str;
    while (*str) { if (is_alpha_char(*str)) *w++ = *str; str++; }
    *w = '\0';
}

void str_fill(char *buf, int buf_size, char c, int len) {
    if (!buf || buf_size <= 0) return;
    int n = (len < buf_size - 1) ? len : buf_size - 1;
    for (int i = 0; i < n; i++) buf[i] = c;
    buf[n] = '\0';
}

void str_swap_chars(char *str, int i, int j) {
    int n = str_len(str);
    if (i < 0 || j < 0 || i >= n || j >= n) return;
    char t = str[i]; str[i] = str[j]; str[j] = t;
}

int str_shortest_word_len(const char *str) {
    int best = 0, cur = 0, started = 0;
    while (*str) { if (is_space_char(*str)) { if (started && (best == 0 || cur < best)) best = cur; cur = 0; started = 0; } else { cur++; started = 1; } str++; }
    if (started && (best == 0 || cur < best)) best = cur;
    return best;
}

double str_avg_word_len(const char *str) {
    int words = 0, chars = 0, in = 0;
    while (*str) { if (is_space_char(*str)) in = 0; else { chars++; if (!in) { words++; in = 1; } } str++; }
    return (words == 0) ? 0.0 : (double)chars / words;
}

int str_is_empty(const char *str) {
    return (str == NULL || *str == '\0');
}

// ============================================================
//                     数论与数学(第二批)（自动生成）
// ============================================================

int gcd3(int a, int b, int c) {
    return gcd(gcd(a, b), c);
}

int gcd4(int a, int b, int c, int d) {
    return gcd(gcd(a, b), gcd(c, d));
}

long long lcm3(int a, int b, int c) {
    return lcm(lcm(a, b), c);
}

int is_relatively_prime(int a, int b) {
    return gcd(a, b) == 1;
}

long long mod_add(long long a, long long b, long long m) {
    return ((a % m) + (b % m)) % m;
}

long long mod_sub(long long a, long long b, long long m) {
    long long r = ((a % m) - (b % m)) % m;
    return (r < 0) ? r + m : r;
}

long long mod_mul(long long a, long long b, long long m) {
    return ((a % m) * (b % m)) % m;
}

int mod_inverse(int a, int m) {
    int x, y;
    int g = extended_gcd(a, m, &x, &y);
    if (g != 1) return -1;
    return ((x % m) + m) % m;
}

long long fast_fibonacci(int n) {
    if (n < 0) return -1;
    if (n == 0) return 0;
    int bit = 0;
    while ((1 << bit) <= n && bit < 31) bit++;
    bit--;
    long long a = 0, b = 1;
    for (int i = bit; i >= 0; i--) { long long c = a * (2 * b - a); long long d = a * a + b * b;
        if ((n >> i) & 1) { a = d; b = c + d; } else { a = c; b = d; } }
    return a;
}

int integer_sqrt(int n) {
    if (n < 0) return -1;
    int r = (int)sqrt((double)n);
    while ((long long)(r + 1) * (r + 1) <= n) r++;
    while ((long long)r * r > n) r--;
    return r;
}

int integer_cbrt(int n) {
    if (n < 0) return -1;
    int r = (int)cbrt((double)n);
    while ((long long)(r + 1) * (r + 1) * (r + 1) <= n) r++;
    return r;
}

int log2_floor(int n) {
    if (n <= 0) return -1;
    int r = 0;
    while (n >>= 1) r++;
    return r;
}

int log10_floor(int n) {
    if (n <= 0) return -1;
    int r = 0;
    while (n >= 10) { n /= 10; r++; }
    return r;
}

long long factorial_mod(int n, long long m) {
    long long r = 1;
    for (int i = 2; i <= n; i++) r = (r * i) % m;
    return r;
}

int is_fibonacci_number(int n) {
    if (n < 0) return 0;
    long long x = 5LL * n * n;
    long long r1 = (long long)sqrt((double)(x + 4)), r2 = (long long)sqrt((double)(x - 4));
    return (r1 * r1 == x + 4) || (r2 * r2 == x - 4);
}

int count_digits_in_base(int n, int base) {
    if (base < 2) return 0;
    if (n == 0) return 1;
    int c = 0;
    while (n) { n /= base; c++; }
    return c;
}

int is_semiprime(int n) {
    if (n < 4) return 0;
    for (int i = 2; i * i <= n; i++) if (n % i == 0) return is_prime(i) && is_prime(n / i);
    return 0;
}

int is_palindromic_prime(int n) {
    return is_prime(n) && is_palindrome_num(n);
}

int is_binary_str(const char *s) {
    if (!s || !*s) return 0;
    while (*s) { if (*s != '0' && *s != '1') return 0; s++; }
    return 1;
}

int is_octal_str(const char *s) {
    if (!s || !*s) return 0;
    while (*s) { if (!is_octal_char(*s)) return 0; s++; }
    return 1;
}

int is_decimal_str(const char *s) {
    if (!s || !*s) return 0;
    while (*s) { if (!is_digit_char(*s)) return 0; s++; }
    return 1;
}

int is_hex_str(const char *s) {
    if (!s || !*s) return 0;
    while (*s) { if (!is_hex_char(*s)) return 0; s++; }
    return 1;
}

int is_number_string(const char *s) {
    if (!s || !*s) return 0;
    if (*s == '+' || *s == '-') s++;
    if (!*s) return 0;
    while (*s) { if (!is_digit_char(*s)) return 0; s++; }
    return 1;
}

int gcd_binary(int a, int b) {
    a = abs(a); b = abs(b);
    if (a == 0) return b;
    if (b == 0) return a;
    int shift = 0;
    while (!((a | b) & 1)) { a >>= 1; b >>= 1; shift++; }
    while (!(a & 1)) a >>= 1;
    while (b) { while (!(b & 1)) b >>= 1; if (a > b) { int t = a; a = b; b = t; } b -= a; }
    return a << shift;
}

int prime_gap(int n) {
    return next_prime(n) - n;
}

int count_trailing_zeros(uint32_t n) {
    if (n == 0) return 32;
    int c = 0;
    while (!(n & 1u)) { n >>= 1; c++; }
    return c;
}

int is_power_of_three(int n) {
    if (n <= 0) return 0;
    while (n % 3 == 0) n /= 3;
    return n == 1;
}

int is_power_of_four(int n) {
    return is_power_of_two(n) && (n % 3 == 1);
}

int digit_frequency(int n, int d) {
    int c = 0;
    if (n < 0) n = -n;
    while (n) { if (n % 10 == d) c++; n /= 10; }
    return c;
}

// ============================================================
//                     数组工具(第二批)（自动生成）
// ============================================================

long long sum_abs_int(int arr[], int size) {
    long long s = 0;
    for (int i = 0; i < size; i++) s += UTILS_ABS(arr[i]);
    return s;
}

long long dot_product_int(int a[], int b[], int size) {
    long long s = 0;
    for (int i = 0; i < size; i++) s += (long long)a[i] * b[i];
    return s;
}

int longest_run_length(int arr[], int size) {
    if (size < 1) return 0;
    int best = 1, cur = 1;
    for (int i = 1; i < size; i++) { if (arr[i] == arr[i - 1]) { cur++; if (cur > best) best = cur; } else cur = 1; }
    return best;
}

int find_local_max_idx(int arr[], int size) {
    if (size <= 0) return -1;
    if (size == 1) return 0;
    if (arr[0] >= arr[1]) return 0;
    if (arr[size - 1] >= arr[size - 2]) return size - 1;
    for (int i = 1; i < size - 1; i++) if (arr[i] >= arr[i - 1] && arr[i] >= arr[i + 1]) return i;
    return -1;
}

int find_local_min_idx(int arr[], int size) {
    if (size <= 0) return -1;
    if (size == 1) return 0;
    if (arr[0] <= arr[1]) return 0;
    if (arr[size - 1] <= arr[size - 2]) return size - 1;
    for (int i = 1; i < size - 1; i++) if (arr[i] <= arr[i - 1] && arr[i] <= arr[i + 1]) return i;
    return -1;
}

int equilibrium_index(int arr[], int size) {
    long long total = 0, left = 0;
    for (int i = 0; i < size; i++) total += arr[i];
    for (int i = 0; i < size; i++) { total -= arr[i]; if (left == total) return i; left += arr[i]; }
    return -1;
}

void reverse_subarray(int arr[], int size, int lo, int hi) {
    if (lo < 0) lo = 0;
    if (hi >= size) hi = size - 1;
    while (lo < hi) { int t = arr[lo]; arr[lo] = arr[hi]; arr[hi] = t; lo++; hi--; }
}

void swap_elements_int(int arr[], int i, int j) {
    int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
}

void fill_sequence_int(int arr[], int size, int start) {
    for (int i = 0; i < size; i++) arr[i] = start + i;
}

void fill_random_double_range(double arr[], int size, double min, double max) {
    for (int i = 0; i < size; i++) arr[i] = min + (max - min) * ((double)rand() / (RAND_MAX + 1.0));
}

int remove_all_value(int arr[], int *size, int value) {
    int j = 0;
    for (int i = 0; i < *size; i++) if (arr[i] != value) arr[j++] = arr[i];
    *size = j;
    return j;
}

int count_distinct_int(int arr[], int size) {
    int c = 0;
    for (int i = 0; i < size; i++) { int dup = 0; for (int j = 0; j < i; j++) if (arr[j] == arr[i]) { dup = 1; break; } if (!dup) c++; }
    return c;
}

int array_min_index(int arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int array_max_index(int arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

void print_array_reverse_int(int arr[], int size) {
    for (int i = size - 1; i >= 0; i--) printf("%d ", arr[i]);
    printf("\n");
}

int check_sorted_strict(int arr[], int size) {
    for (int i = 1; i < size; i++) if (arr[i] <= arr[i - 1]) return 0;
    return 1;
}

int min_gap(int arr[], int size) {
    if (size < 2) return 0;
    int g = arr[1] - arr[0];
    for (int i = 2; i < size; i++) { int d = arr[i] - arr[i - 1]; if (d < g) g = d; }
    return g;
}

int max_gap(int arr[], int size) {
    if (size < 2) return 0;
    int g = arr[1] - arr[0];
    for (int i = 2; i < size; i++) { int d = arr[i] - arr[i - 1]; if (d > g) g = d; }
    return g;
}

// ============================================================
//                     链表工具(扩展)（自动生成）
// ============================================================

int list_get_nth(ListNode *head, int n, int *out) {
    int i = 0;
    while (head) { if (i == n) { *out = head->data; return 0; } i++; head = head->next; }
    return -1;
}

int list_delete_nth(ListNode **head, int n) {
    if (!head) return -1;
    if (n == 0) { ListNode *t = *head; if (!t) return -1; *head = t->next; free(t); return 0; }
    ListNode *p = *head;
    for (int i = 0; p && i < n - 1; i++) p = p->next;
    if (!p || !p->next) return -1;
    ListNode *t = p->next; p->next = t->next; free(t);
    return 0;
}

int list_insert_nth(ListNode **head, int n, int data) {
    if (!head || n < 0) return -1;
    if (n == 0) { list_insert_head(head, data); return 0; }
    ListNode *p = *head;
    for (int i = 0; p && i < n - 1; i++) p = p->next;
    if (!p) return -1;
    ListNode *node = list_create(data);
    if (!node) return -1;
    node->next = p->next; p->next = node;
    return 0;
}

int list_has_cycle(ListNode *head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) { slow = slow->next; fast = fast->next->next; if (slow == fast) return 1; }
    return 0;
}

ListNode* list_middle_node(ListNode *head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) { slow = slow->next; fast = fast->next->next; }
    return slow;
}

ListNode* list_from_array(int arr[], int size) {
    ListNode *head = NULL;
    for (int i = size - 1; i >= 0; i--) list_insert_head(&head, arr[i]);
    return head;
}

int list_max(ListNode *head) {
    if (!head) return 0;
    int m = head->data;
    for (ListNode *p = head->next; p; p = p->next) if (p->data > m) m = p->data;
    return m;
}

int list_min(ListNode *head) {
    if (!head) return 0;
    int m = head->data;
    for (ListNode *p = head->next; p; p = p->next) if (p->data < m) m = p->data;
    return m;
}

long long list_sum(ListNode *head) {
    long long s = 0;
    for (ListNode *p = head; p; p = p->next) s += p->data;
    return s;
}

void list_sort(ListNode *head) {
    if (!head) return;
    int swapped = 1;
    while (swapped) { swapped = 0; for (ListNode *p = head; p->next; p = p->next) if (p->data > p->next->data) { int t = p->data; p->data = p->next->data; p->next->data = t; swapped = 1; } }
}

ListNode* list_merge_sorted(ListNode *a, ListNode *b) {
    ListNode *head = NULL, **tail = &head;
    while (a && b) { if (a->data <= b->data) { *tail = a; a = a->next; } else { *tail = b; b = b->next; } tail = &(*tail)->next; }
    *tail = a ? a : b;
    return head;
}

ListNode* list_append_list(ListNode *a, ListNode *b) {
    if (!a) return b;
    ListNode *p = a;
    while (p->next) p = p->next;
    p->next = b;
    return a;
}

ListNode* list_clone(ListNode *head) {
    ListNode *new_head = NULL, **tail = &new_head;
    while (head) { ListNode *node = list_create(head->data); if (!node) return NULL; *tail = node; tail = &node->next; head = head->next; }
    return new_head;
}

int list_is_sorted(ListNode *head) {
    for (ListNode *p = head; p && p->next; p = p->next) if (p->data > p->next->data) return 0;
    return 1;
}

int list_count_value(ListNode *head, int value) {
    int c = 0;
    for (ListNode *p = head; p; p = p->next) if (p->data == value) c++;
    return c;
}

void list_rotate_right(ListNode **head, int k) {
    if (!head || !*head || k <= 0) return;
    int len = list_length(*head);
    k %= len;
    if (k == 0) return;
    ListNode *p = *head;
    for (int i = 0; i < len - k - 1; i++) p = p->next;
    ListNode *new_head = p->next;
    p->next = NULL;
    ListNode *t = new_head;
    while (t->next) t = t->next;
    t->next = *head;
    *head = new_head;
}

// ============================================================
//                     进制转换(第二批)（自动生成）
// ============================================================

char* int_to_binary_padded(int num, int width, char *buf, int buf_size) {
    if (!buf || buf_size <= 0) return buf;
    if (width >= buf_size) width = buf_size - 1;
    for (int i = width - 1; i >= 0; i--) { if (i < buf_size - 1) buf[i] = (num & 1) ? '1' : '0'; num >>= 1; }
    buf[width] = '\0';
    return buf;
}

int bcd_to_binary(int bcd) {
    int r = 0, m = 1;
    while (bcd) { r += (bcd & 0x0F) * m; m *= 10; bcd >>= 4; }
    return r;
}

int binary_to_bcd(int n) {
    int bcd = 0, shift = 0;
    while (n) { bcd |= (n % 10) << (shift * 4); n /= 10; shift++; }
    return bcd;
}

int float_bits_to_int(float f) {
    int i;
    memcpy(&i, &f, 4);
    return i;
}

float int_bits_to_float(int i) {
    float f;
    memcpy(&f, &i, 4);
    return f;
}

char* double_to_hex_str(double d, char *buf) {
    sprintf(buf, "%a", d);
    return buf;
}

int char_to_ascii_code(char c) {
    return (int)(unsigned char)c;
}

char ascii_code_to_char(int code) {
    return (char)code;
}

void int_to_bytes_be(int val, uint8_t out[4]) {
    out[0] = (uint8_t)((val >> 24) & 0xFF);
    out[1] = (uint8_t)((val >> 16) & 0xFF);
    out[2] = (uint8_t)((val >> 8) & 0xFF);
    out[3] = (uint8_t)(val & 0xFF);
}

int bytes_to_int_be(uint8_t b[4]) {
    return ((int)b[0] << 24) | ((int)b[1] << 16) | ((int)b[2] << 8) | b[3];
}

char* int_to_hex_padded(int num, int width, char *buf, int buf_size) {
    if (!buf || buf_size <= 0) return buf;
    if (width >= buf_size) width = buf_size - 1;
    for (int i = width - 1; i >= 0; i--) { int d = num & 0xF; buf[i] = int_to_hex_char(d); num >>= 4; }
    buf[width] = '\0';
    return buf;
}

// ============================================================
//                     几何工具(第二批)（自动生成）
// ============================================================

double triangle_area_coords(double x1, double y1, double x2, double y2, double x3, double y3) {
    return fabs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0);
}

double polygon_area(double x[], double y[], int n) {
    if (n < 3) return 0.0;
    double s = 0;
    for (int i = 0; i < n; i++) { int j = (i + 1) % n; s += x[i] * y[j] - x[j] * y[i]; }
    return fabs(s) / 2.0;
}

double distance_point_line(double px, double py, double ax, double ay, double bx, double by) {
    double dx = bx - ax, dy = by - ay;
    double len = sqrt(dx * dx + dy * dy);
    if (len == 0) return distance_2d(px, py, ax, ay);
    return fabs(dy * px - dx * py + bx * ay - by * ax) / len;
}

double distance_point_segment(double px, double py, double ax, double ay, double bx, double by) {
    double dx = bx - ax, dy = by - ay;
    double len2 = dx * dx + dy * dy;
    double t = (len2 == 0) ? 0 : ((px - ax) * dx + (py - ay) * dy) / len2;
    if (t < 0) t = 0;
    if (t > 1) t = 1;
    double cx = ax + t * dx, cy = ay + t * dy;
    return distance_2d(px, py, cx, cy);
}

double area_sector(double r, double angle_rad) {
    return 0.5 * r * r * angle_rad;
}

double arc_length(double r, double angle_rad) {
    return r * angle_rad;
}

double sin_deg(double deg) {
    return sin(degrees_to_radians(deg));
}

double cos_deg(double deg) {
    return cos(degrees_to_radians(deg));
}

double tan_deg(double deg) {
    return tan(degrees_to_radians(deg));
}

double angle_between_vectors(double ax, double ay, double bx, double by) {
    double la = sqrt(ax * ax + ay * ay), lb = sqrt(bx * bx + by * by);
    if (la == 0 || lb == 0) return 0.0;
    double c = (ax * bx + ay * by) / (la * lb);
    if (c > 1) c = 1;
    if (c < -1) c = -1;
    return acos(c);
}

int is_point_on_segment(double px, double py, double ax, double ay, double bx, double by) {
    double d = distance_point_segment(px, py, ax, ay, bx, by);
    return (d < 1e-9);
}

// ============================================================
//                     数值工具(第二批)（自动生成）
// ============================================================

int is_positive_double(double x) {
    return x > 0;
}

int is_negative_double(double x) {
    return x < 0;
}

int is_zero_double(double x) {
    return x == 0;
}

double step_function(double x) {
    return (x >= 0) ? 1.0 : 0.0;
}

double round_to_n_decimals(double x, int n) {
    double p = pow(10, n);
    return round(x * p) / p;
}

int abs_diff_int(int a, int b) {
    return UTILS_ABS(a - b);
}

double abs_diff_double(double a, double b) {
    return fabs(a - b);
}

double max_double(double a, double b) {
    return (a > b) ? a : b;
}

double min_double(double a, double b) {
    return (a < b) ? a : b;
}

void reduce_fraction(int num, int den, int *out_num, int *out_den) {
    if (den == 0) return;
    int g = gcd(num, den);
    *out_num = num / g;
    *out_den = den / g;
}

int is_finite_double(double x) {
    return isfinite(x);
}

int is_nan_double(double x) {
    return isnan(x);
}

// ============================================================
//                     编码与杂项(第二批)（自动生成）
// ============================================================

char* url_decode_str(const char *s) {
    if (!s) return NULL;
    int n = str_len(s);
    char *r = (char*)malloc(n + 1);
    if (!r) return NULL;
    int j = 0;
    for (int i = 0; i < n; i++) {
        if (s[i] == '%' && i + 2 < n) { int hi = hex_char_to_int(s[i + 1]), lo = hex_char_to_int(s[i + 2]);
            if (hi >= 0 && lo >= 0) { r[j++] = (char)((hi << 4) | lo); i += 2; continue; } }
        if (s[i] == '+') r[j++] = ' '; else r[j++] = s[i]; }
    r[j] = '\0';
    return r;
}

char* html_escape_str(const char *s) {
    if (!s) return NULL;
    int n = str_len(s);
    char *r = (char*)malloc(n * 6 + 1);
    if (!r) return NULL;
    int j = 0;
    for (int i = 0; i < n; i++) {
        switch (s[i]) { case '&': strcpy(r + j, "&amp;"); j += 5; break; case '<': strcpy(r + j, "&lt;"); j += 4; break; case '>': strcpy(r + j, "&gt;"); j += 4; break; case '"': strcpy(r + j, "&quot;"); j += 6; break; case '\'': strcpy(r + j, "&#39;"); j += 5; break; default: r[j++] = s[i]; } }
    r[j] = '\0';
    return r;
}

char* bytes_to_hex_lower(const uint8_t *data, uint16_t len, char *buf, uint16_t buf_size) {
    if (buf_size < (uint16_t)(len * 2 + 1)) { if (buf && buf_size > 0) buf[0] = '\0'; return buf; }
    for (uint16_t i = 0; i < len; i++) {
        buf[i * 2] = int_to_hex_char((data[i] >> 4) & 0x0F);
        buf[i * 2 + 1] = int_to_hex_char(data[i] & 0x0F); }
    for (uint16_t i = 0; i < len * 2; i++) buf[i] = char_to_lower(buf[i]);
    buf[len * 2] = '\0';
    return buf;
}

char* hex_str_to_upper(const char *hex, char *buf, int buf_size) {
    if (!hex || !buf || buf_size <= 0) return buf;
    int i = 0;
    while (hex[i] && i < buf_size - 1) { buf[i] = char_to_upper(hex[i]); i++; }
    buf[i] = '\0';
    return buf;
}

// ============================================================
//                     图算法(第二批)（自动生成）
// ============================================================

int graph_is_connected(Graph *g) {
    if (!g || g->n <= 1) return 1;
    char *vis = (char*)calloc(g->n, 1);
    int *q = (int*)malloc(g->n * sizeof(int));
    int head = 0, tail = 0;
    vis[0] = 1; q[tail++] = 0;
    while (head < tail) { int v = q[head++]; for (int i = 0; i < g->n; i++) if (g->adj[v][i] && !vis[i]) { vis[i] = 1; q[tail++] = i; } }
    int ok = 1;
    for (int i = 0; i < g->n; i++) if (!vis[i]) { ok = 0; break; }
    free(vis); free(q);
    return ok;
}

int graph_edge_count(Graph *g) {
    if (!g) return 0;
    int c = 0;
    for (int i = 0; i < g->n; i++) for (int j = i + 1; j < g->n; j++) if (g->adj[i][j]) c++;
    return c;
}

void graph_transpose(Graph *g, int **out) {
    if (!g) return;
    for (int i = 0; i < g->n; i++) for (int j = 0; j < g->n; j++) out[j][i] = g->adj[i][j];
}

int graph_path_exists(Graph *g, int u, int v) {
    if (!g || u < 0 || v < 0 || u >= g->n || v >= g->n) return 0;
    if (u == v) return 1;
    char *vis = (char*)calloc(g->n, 1);
    int *q = (int*)malloc(g->n * sizeof(int));
    int head = 0, tail = 0;
    vis[u] = 1; q[tail++] = u;
    while (head < tail) { int x = q[head++]; for (int i = 0; i < g->n; i++) if (g->adj[x][i] && !vis[i]) { if (i == v) { free(vis); free(q); return 1; } vis[i] = 1; q[tail++] = i; } }
    free(vis); free(q);
    return 0;
}

// ============================================================
//                     随机工具(第二批)（自动生成）
// ============================================================

int rand_range_excluding(int min, int max, int excl) {
    int v;
    do { v = rand_range(min, max); } while (v == excl && min < max);
    return v;
}

void rand_fill_int_list(int arr[], int size, int min, int max) {
    for (int i = 0; i < size; i++) arr[i] = rand_range(min, max);
}

void rand_fill_float_array(double arr[], int size, double min, double max) {
    for (int i = 0; i < size; i++) arr[i] = min + (max - min) * ((double)rand() / (RAND_MAX + 1.0));
}

char rand_digit_char(void) {
    return (char)('0' + rand() % 10);
}

char rand_lowercase_char(void) {
    return (char)('a' + rand() % 26);
}

char rand_uppercase_char(void) {
    return (char)('A' + rand() % 26);
}

char rand_letter_char(void) {
    return (rand() % 2) ? rand_uppercase_char() : rand_lowercase_char();
}

// ============================================================
//                     二叉搜索树(第二批)（自动生成）
// ============================================================

int bst_min_value(BSTNode *root) {
    BSTNode *n = bst_find_min(root);
    return n ? n->data : 0;
}

int bst_max_value(BSTNode *root) {
    BSTNode *n = bst_find_max(root);
    return n ? n->data : 0;
}

int bst_count_leaves(BSTNode *root) {
    if (!root) return 0;
    if (!root->left && !root->right) return 1;
    return bst_count_leaves(root->left) + bst_count_leaves(root->right);
}

int bst_count_internal(BSTNode *root) {
    if (!root || (!root->left && !root->right)) return 0;
    return 1 + bst_count_internal(root->left) + bst_count_internal(root->right);
}

int bst_is_valid(BSTNode *root) {
    if (!root) return 1;
    if (root->left && bst_max_value(root->left) >= root->data) return 0;
    if (root->right && bst_min_value(root->right) <= root->data) return 0;
    return bst_is_valid(root->left) && bst_is_valid(root->right);
}

int bst_is_balanced(BSTNode *root) {
    if (!root) return 1;
    int l = bst_height(root->left), r = bst_height(root->right);
    if (abs(l - r) > 1) return 0;
    return bst_is_balanced(root->left) && bst_is_balanced(root->right);
}

BSTNode* bst_mirror(BSTNode *root) {
    if (!root) return NULL;
    BSTNode *t = root->left; root->left = root->right; root->right = t;
    bst_mirror(root->left);
    bst_mirror(root->right);
    return root;
}

int bst_same_tree(BSTNode *a, BSTNode *b) {
    if (!a && !b) return 1;
    if (!a || !b) return 0;
    return (a->data == b->data) && bst_same_tree(a->left, b->left) && bst_same_tree(a->right, b->right);
}

int bst_depth_of_value(BSTNode *root, int value) {
    int d = 0;
    while (root) { if (root->data == value) return d; d++; root = (value < root->data) ? root->left : root->right; }
    return -1;
}

// ============================================================
//                     矩阵工具(第二批)（自动生成）
// ============================================================

double** mat_zeros(int rows, int cols) {
    return mat_create(rows, cols);
}

double** mat_ones(int rows, int cols) {
    double **m = mat_create(rows, cols);
    if (!m) return NULL;
    mat_fill(m, rows, cols, 1.0);
    return m;
}

double** mat_identity_alloc(int n) {
    double **m = mat_create(n, n);
    if (!m) return NULL;
    mat_identity(m, n);
    return m;
}

double** mat_transpose_alloc(double **m, int rows, int cols) {
    double **out = mat_create(cols, rows);
    if (!out) return NULL;
    mat_transpose(m, rows, cols, out);
    return out;
}

int mat_is_symmetric(double **m, int n) {
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (m[i][j] != m[j][i]) return 0;
    return 1;
}

void mat_add_scalar(double **m, int rows, int cols, double s, double **out) {
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = m[i][j] + s;
}

void mat_negate(double **m, int rows, int cols, double **out) {
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) out[i][j] = -m[i][j];
}

double mat_avg(double **m, int rows, int cols) {
    if (rows <= 0 || cols <= 0) return 0.0;
    return mat_sum(m, rows, cols) / (rows * cols);
}

void mat_rand_fill(double **m, int rows, int cols, double min, double max) {
    for (int i = 0; i < rows; i++) for (int j = 0; j < cols; j++) m[i][j] = min + (max - min) * ((double)rand() / (RAND_MAX + 1.0));
}

// ============================================================
//                     数组统计(第二批)（自动生成）
// ============================================================

double mode_double_array(double arr[], int size) {
    double best = arr[0]; int bestc = 0;
    for (int i = 0; i < size; i++) { int c = 0; for (int j = 0; j < size; j++) if (arr[j] == arr[i]) c++; if (c > bestc) { bestc = c; best = arr[i]; } }
    return best;
}

double median_int_array(int arr[], int size) {
    if (size == 0) return 0.0;
    int *c = (int*)malloc(size * sizeof(int));
    if (!c) return 0.0;
    memcpy(c, arr, size * sizeof(int));
    for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (c[j] > c[j + 1]) { int t = c[j]; c[j] = c[j + 1]; c[j + 1] = t; }
    double r = (size % 2) ? c[size / 2] : (c[size / 2 - 1] + c[size / 2]) / 2.0;
    free(c);
    return r;
}

double variance_int_array(int arr[], int size) {
    if (size < 1) return 0.0;
    double m = avg_int_array(arr, size), s = 0;
    for (int i = 0; i < size; i++) { double d = arr[i] - m; s += d * d; }
    return s / size;
}

double stddev_int_array(int arr[], int size) {
    return sqrt(variance_int_array(arr, size));
}

int range_int_array(int arr[], int size) {
    if (size < 1) return 0;
    return max_int_array(arr, size) - min_int_array(arr, size);
}

// ============================================================
//                     数组工具(类型变体)（自动生成）
// ============================================================

int int_array_min_index(int arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int int_array_max_index(int arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int int_array_count_greater(int arr[], int size, int value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int int_array_count_less(int arr[], int size, int value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void int_array_scale(int arr[], int size, int scalar) {
    for (int i = 0; i < size; i++) arr[i] = (int)(arr[i] * scalar);
}

void int_array_add_scalar(int arr[], int size, int offset) {
    for (int i = 0; i < size; i++) arr[i] = (int)(arr[i] + offset);
}

int int_array_has_duplicates(int arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void int_array_rotate_left(int arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    int *tmp = (int*)malloc(k * sizeof(int));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

long long int_array_sum_abs(int arr[], int size) {
    long long s = 0;
    for (int i = 0; i < size; i++) { int v = arr[i]; s += ( UTILS_ABS(v) ); }
    return s;
}

int long_array_min_index(long arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int long_array_max_index(long arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int long_array_count_greater(long arr[], int size, long value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int long_array_count_less(long arr[], int size, long value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void long_array_scale(long arr[], int size, long scalar) {
    for (int i = 0; i < size; i++) arr[i] = (long)(arr[i] * scalar);
}

void long_array_add_scalar(long arr[], int size, long offset) {
    for (int i = 0; i < size; i++) arr[i] = (long)(arr[i] + offset);
}

int long_array_has_duplicates(long arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void long_array_rotate_left(long arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    long *tmp = (long*)malloc(k * sizeof(long));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

long long long_array_sum_abs(long arr[], int size) {
    long long s = 0;
    for (int i = 0; i < size; i++) { long v = arr[i]; s += ( UTILS_ABS(v) ); }
    return s;
}

int long_long_array_min_index(long long arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int long_long_array_max_index(long long arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int long_long_array_count_greater(long long arr[], int size, long long value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int long_long_array_count_less(long long arr[], int size, long long value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void long_long_array_scale(long long arr[], int size, long long scalar) {
    for (int i = 0; i < size; i++) arr[i] = (long long)(arr[i] * scalar);
}

void long_long_array_add_scalar(long long arr[], int size, long long offset) {
    for (int i = 0; i < size; i++) arr[i] = (long long)(arr[i] + offset);
}

int long_long_array_has_duplicates(long long arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void long_long_array_rotate_left(long long arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    long long *tmp = (long long*)malloc(k * sizeof(long long));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

long long long_long_array_sum_abs(long long arr[], int size) {
    long long s = 0;
    for (int i = 0; i < size; i++) { long long v = arr[i]; s += ( UTILS_ABS(v) ); }
    return s;
}

int short_array_min_index(short arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int short_array_max_index(short arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int short_array_count_greater(short arr[], int size, short value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int short_array_count_less(short arr[], int size, short value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void short_array_scale(short arr[], int size, short scalar) {
    for (int i = 0; i < size; i++) arr[i] = (short)(arr[i] * scalar);
}

void short_array_add_scalar(short arr[], int size, short offset) {
    for (int i = 0; i < size; i++) arr[i] = (short)(arr[i] + offset);
}

int short_array_has_duplicates(short arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void short_array_rotate_left(short arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    short *tmp = (short*)malloc(k * sizeof(short));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

long long short_array_sum_abs(short arr[], int size) {
    long long s = 0;
    for (int i = 0; i < size; i++) { short v = arr[i]; s += ( UTILS_ABS(v) ); }
    return s;
}

int uint_array_min_index(unsigned int arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int uint_array_max_index(unsigned int arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int uint_array_count_greater(unsigned int arr[], int size, unsigned int value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int uint_array_count_less(unsigned int arr[], int size, unsigned int value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void uint_array_scale(unsigned int arr[], int size, unsigned int scalar) {
    for (int i = 0; i < size; i++) arr[i] = (unsigned int)(arr[i] * scalar);
}

void uint_array_add_scalar(unsigned int arr[], int size, unsigned int offset) {
    for (int i = 0; i < size; i++) arr[i] = (unsigned int)(arr[i] + offset);
}

int uint_array_has_duplicates(unsigned int arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void uint_array_rotate_left(unsigned int arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    unsigned int *tmp = (unsigned int*)malloc(k * sizeof(unsigned int));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

int float_array_min_index(float arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int float_array_max_index(float arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int float_array_count_greater(float arr[], int size, float value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int float_array_count_less(float arr[], int size, float value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void float_array_scale(float arr[], int size, float scalar) {
    for (int i = 0; i < size; i++) arr[i] = (float)(arr[i] * scalar);
}

void float_array_add_scalar(float arr[], int size, float offset) {
    for (int i = 0; i < size; i++) arr[i] = (float)(arr[i] + offset);
}

int float_array_has_duplicates(float arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void float_array_rotate_left(float arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    float *tmp = (float*)malloc(k * sizeof(float));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

double float_array_sum_abs(float arr[], int size) {
    double s = 0;
    for (int i = 0; i < size; i++) { float v = arr[i]; s += ( fabs(v) ); }
    return s;
}

int double_array_min_index(double arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int double_array_max_index(double arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int double_array_count_greater(double arr[], int size, double value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int double_array_count_less(double arr[], int size, double value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void double_array_scale(double arr[], int size, double scalar) {
    for (int i = 0; i < size; i++) arr[i] = (double)(arr[i] * scalar);
}

void double_array_add_scalar(double arr[], int size, double offset) {
    for (int i = 0; i < size; i++) arr[i] = (double)(arr[i] + offset);
}

int double_array_has_duplicates(double arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void double_array_rotate_left(double arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    double *tmp = (double*)malloc(k * sizeof(double));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

double double_array_sum_abs(double arr[], int size) {
    double s = 0;
    for (int i = 0; i < size; i++) { double v = arr[i]; s += ( fabs(v) ); }
    return s;
}

int char_array_min_index(char arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int char_array_max_index(char arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int char_array_count_greater(char arr[], int size, char value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int char_array_count_less(char arr[], int size, char value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void char_array_scale(char arr[], int size, char scalar) {
    for (int i = 0; i < size; i++) arr[i] = (char)(arr[i] * scalar);
}

void char_array_add_scalar(char arr[], int size, char offset) {
    for (int i = 0; i < size; i++) arr[i] = (char)(arr[i] + offset);
}

int char_array_has_duplicates(char arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void char_array_rotate_left(char arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    char *tmp = (char*)malloc(k * sizeof(char));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

int char_array_sum_abs(char arr[], int size) {
    int s = 0;
    for (int i = 0; i < size; i++) { char v = arr[i]; s += ( UTILS_ABS(v) ); }
    return s;
}

int uint8_array_min_index(uint8_t arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int uint8_array_max_index(uint8_t arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int uint8_array_count_greater(uint8_t arr[], int size, uint8_t value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int uint8_array_count_less(uint8_t arr[], int size, uint8_t value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void uint8_array_scale(uint8_t arr[], int size, uint8_t scalar) {
    for (int i = 0; i < size; i++) arr[i] = (uint8_t)(arr[i] * scalar);
}

void uint8_array_add_scalar(uint8_t arr[], int size, uint8_t offset) {
    for (int i = 0; i < size; i++) arr[i] = (uint8_t)(arr[i] + offset);
}

int uint8_array_has_duplicates(uint8_t arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void uint8_array_rotate_left(uint8_t arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    uint8_t *tmp = (uint8_t*)malloc(k * sizeof(uint8_t));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

int uint16_array_min_index(uint16_t arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int uint16_array_max_index(uint16_t arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int uint16_array_count_greater(uint16_t arr[], int size, uint16_t value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int uint16_array_count_less(uint16_t arr[], int size, uint16_t value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void uint16_array_scale(uint16_t arr[], int size, uint16_t scalar) {
    for (int i = 0; i < size; i++) arr[i] = (uint16_t)(arr[i] * scalar);
}

void uint16_array_add_scalar(uint16_t arr[], int size, uint16_t offset) {
    for (int i = 0; i < size; i++) arr[i] = (uint16_t)(arr[i] + offset);
}

int uint16_array_has_duplicates(uint16_t arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void uint16_array_rotate_left(uint16_t arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    uint16_t *tmp = (uint16_t*)malloc(k * sizeof(uint16_t));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

int uint32_array_min_index(uint32_t arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}

int uint32_array_max_index(uint32_t arr[], int size) {
    if (size <= 0) return -1;
    int idx = 0;
    for (int i = 1; i < size; i++) if (arr[i] > arr[idx]) idx = i;
    return idx;
}

int uint32_array_count_greater(uint32_t arr[], int size, uint32_t value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] > value) c++;
    return c;
}

int uint32_array_count_less(uint32_t arr[], int size, uint32_t value) {
    int c = 0;
    for (int i = 0; i < size; i++) if (arr[i] < value) c++;
    return c;
}

void uint32_array_scale(uint32_t arr[], int size, uint32_t scalar) {
    for (int i = 0; i < size; i++) arr[i] = (uint32_t)(arr[i] * scalar);
}

void uint32_array_add_scalar(uint32_t arr[], int size, uint32_t offset) {
    for (int i = 0; i < size; i++) arr[i] = (uint32_t)(arr[i] + offset);
}

int uint32_array_has_duplicates(uint32_t arr[], int size) {
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] == arr[j]) return 1;
    return 0;
}

void uint32_array_rotate_left(uint32_t arr[], int size, int k) {
    if (size <= 1 || k <= 0) return;
    k %= size;
    if (k == 0) return;
    uint32_t *tmp = (uint32_t*)malloc(k * sizeof(uint32_t));
    if (!tmp) return;
    for (int i = 0; i < k; i++) tmp[i] = arr[i];
    for (int i = 0; i < size - k; i++) arr[i] = arr[i + k];
    for (int i = 0; i < k; i++) arr[size - k + i] = tmp[i];
    free(tmp);
}

// ============================================================
//                     数组工具(第三批)（自动生成）
// ============================================================

int count_runs_int(int arr[], int size) {
    if (size < 1) return 0;
    int runs = 1;
    for (int i = 1; i < size; i++) if (arr[i] != arr[i - 1]) runs++;
    return runs;
}

int is_permutation_int(int arr[], int size) {
    for (int v = 1; v <= size; v++) { int f = 0; for (int i = 0; i < size; i++) if (arr[i] == v) { f = 1; break; } if (!f) return 0; }
    return 1;
}

long long max_pair_product(int arr[], int size) {
    if (size < 2) return 0;
    long long best = (long long)arr[0] * arr[1];
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) { long long p = (long long)arr[i] * arr[j]; if (p > best) best = p; }
    return best;
}

int find_missing_number(int arr[], int n) {
    long long total = (long long)n * (n + 1) / 2, s = 0;
    for (int i = 0; i < n; i++) s += arr[i];
    return (int)(total - s);
}

int find_duplicate_number(int arr[], int n) {
    long long sum = 0, sum_sq = 0;
    long long expect = (long long)n * (n + 1) / 2;
    long long expect_sq = (long long)n * (n + 1) * (2 * n + 1) / 6;
    for (int i = 0; i < n + 1; i++) { sum += arr[i]; sum_sq += (long long)arr[i] * arr[i]; }
    long long diff_sum = sum - expect;
    long long diff_sq = sum_sq - expect_sq;
    return (int)((diff_sq / diff_sum + diff_sum) / 2);
}

void move_zeros_to_end(int arr[], int size) {
    int j = 0;
    for (int i = 0; i < size; i++) if (arr[i] != 0) arr[j++] = arr[i];
    while (j < size) arr[j++] = 0;
}

void move_negatives_to_front(int arr[], int size) {
    int j = 0;
    for (int i = 0; i < size; i++) if (arr[i] < 0) { int t = arr[i]; arr[i] = arr[j]; arr[j] = t; j++; }
}

void separate_even_odd(int arr[], int size) {
    int j = 0;
    for (int i = 0; i < size; i++) if (arr[i] % 2 == 0) { int t = arr[i]; arr[i] = arr[j]; arr[j] = t; j++; }
}

long long sum_range_int(int arr[], int lo, int hi) {
    long long s = 0;
    for (int i = lo; i <= hi; i++) s += arr[i];
    return s;
}

int count_occurrences_sorted(int arr[], int size, int target) {
    int l = lower_bound_int(arr, size, target);
    if (l >= size || arr[l] != target) return 0;
    int u = upper_bound_int(arr, size, target);
    return u - l;
}

void reverse_in_groups(int arr[], int size, int k) {
    if (k <= 1) return;
    for (int i = 0; i < size; i += k) { int lo = i, hi = (i + k - 1 < size) ? i + k - 1 : size - 1; while (lo < hi) { int t = arr[lo]; arr[lo] = arr[hi]; arr[hi] = t; lo++; hi--; } }
}

int is_mountain_array(int arr[], int size) {
    if (size < 3) return 0;
    int i = 0;
    while (i + 1 < size && arr[i] < arr[i + 1]) i++;
    if (i == 0 || i == size - 1) return 0;
    while (i + 1 < size && arr[i] > arr[i + 1]) i++;
    return i == size - 1;
}

int majority_element(int arr[], int size) {
    int cand = arr[0], count = 1;
    for (int i = 1; i < size; i++) { if (arr[i] == cand) count++; else if (--count == 0) { cand = arr[i]; count = 1; } }
    return cand;
}

int pairs_with_sum(int arr[], int size, int target) {
    int c = 0;
    for (int i = 0; i < size; i++) for (int j = i + 1; j < size; j++) if (arr[i] + arr[j] == target) c++;
    return c;
}

int next_greater_element(int arr[], int size, int out[]) {
    for (int i = 0; i < size; i++) { out[i] = -1; for (int j = i + 1; j < size; j++) if (arr[j] > arr[i]) { out[i] = arr[j]; break; } }
    return 0;
}

int find_peak_index(int arr[], int size) {
    if (size < 3) return -1;
    for (int i = 1; i < size - 1; i++) if (arr[i] > arr[i - 1] && arr[i] > arr[i + 1]) return i;
    return -1;
}

// ============================================================
//                     字符串工具(第三批)（自动生成）
// ============================================================

char* str_rot13_copy(const char *s) {
    if (!s) return NULL;
    char *r = (char*)malloc(str_len(s) + 1);
    if (!r) return NULL;
    int i = 0;
    while (s[i]) { char c = s[i]; if (is_alpha_char(c)) { char b = is_upper_char(c) ? 'A' : 'a'; r[i] = (char)(b + (c - b + 13) % 26); } else r[i] = c; i++; }
    r[i] = '\0';
    return r;
}

char* str_caesar_copy(const char *s, int shift) {
    if (!s) return NULL;
    char *r = (char*)malloc(str_len(s) + 1);
    if (!r) return NULL;
    int i = 0;
    while (s[i]) { char c = s[i]; if (is_alpha_char(c)) { char b = is_upper_char(c) ? 'A' : 'a'; r[i] = (char)(b + (c - b + shift % 26 + 26) % 26); } else r[i] = c; i++; }
    r[i] = '\0';
    return r;
}

char* str_replace_all(const char *s, const char *old, const char *new) {
    if (!s || !old || !*old) return NULL;
    int count = str_count_substr(s, old);
    int old_len = str_len(old), new_len = str_len(new), slen = str_len(s);
    char *r = (char*)malloc(slen + count * (new_len - old_len) + 1);
    if (!r) return NULL;
    const char *p = s;
    char *w = r;
    while (*p) { if (strncmp(p, old, (size_t)old_len) == 0) { memcpy(w, new, (size_t)new_len); w += new_len; p += old_len; } else *w++ = *p++; }
    *w = '\0';
    return r;
}

char* str_extract_digits(const char *s) {
    if (!s) return NULL;
    char *r = (char*)malloc(str_len(s) + 1);
    if (!r) return NULL;
    int j = 0;
    while (*s) { if (is_digit_char(*s)) r[j++] = *s; s++; }
    r[j] = '\0';
    return r;
}

void str_remove_char_at(char *str, int pos) {
    int n = str_len(str);
    if (pos < 0 || pos >= n) return;
    for (int i = pos; i < n; i++) str[i] = str[i + 1];
}

void str_insert_char_at(char *str, int buf_size, int pos, char c) {
    int n = str_len(str);
    if (pos < 0 || pos > n || n + 1 >= buf_size) return;
    for (int i = n; i >= pos; i--) str[i + 1] = str[i];
    str[pos] = c;
}

int str_is_all_same_char(const char *str) {
    if (!str || !*str) return 0;
    char c = str[0];
    while (*str) { if (*str != c) return 0; str++; }
    return 1;
}

int str_has_duplicate_chars(const char *str) {
    for (int i = 0; str[i]; i++) for (int j = i + 1; str[j]; j++) if (str[i] == str[j]) return 1;
    return 0;
}

int str_longest_common_prefix(const char *a, const char *b) {
    int i = 0;
    while (a[i] && b[i] && a[i] == b[i]) i++;
    return i;
}

int str_count_unique_chars(const char *str) {
    int cnt[256] = {0}, c = 0;
    while (*str) { if (!cnt[(unsigned char)*str]) c++; cnt[(unsigned char)*str] = 1; str++; }
    return c;
}

int str_last_word_len(const char *str) {
    int n = str_len(str), len = 0;
    int i = n - 1;
    while (i >= 0 && is_space_char(str[i])) i--;
    while (i >= 0 && !is_space_char(str[i])) { len++; i--; }
    return len;
}

int str_first_word_len(const char *str) {
    int len = 0;
    while (*str && is_space_char(*str)) str++;
    while (*str && !is_space_char(*str)) { len++; str++; }
    return len;
}

int str_contains_any_char(const char *str, const char *chars) {
    while (*str) { if (str_find(chars, (char[]){*str, '\0'})) return 1; str++; }
    return 0;
}

int str_is_balanced_parens(const char *str) {
    int depth = 0;
    while (*str) { if (*str == '(') depth++; else if (*str == ')') { if (--depth < 0) return 0; } str++; }
    return depth == 0;
}

int str_is_valid_brackets(const char *s) {
    int n = str_len(s);
    char *st = (char*)malloc(n + 1);
    if (!st) return 0;
    int top = 0;
    while (*s) { char c = *s++;
        if (c == '(' || c == '[' || c == '{') st[top++] = c;
        else { if (top == 0) { free(st); return 0; } char o = st[--top];
            if (!((o == '(' && c == ')') || (o == '[' && c == ']') || (o == '{' && c == '}'))) { free(st); return 0; } } }
    int ok = (top == 0);
    free(st);
    return ok;
}

double str_similarity(const char *a, const char *b) {
    int na = str_len(a), nb = str_len(b);
    if (na + nb == 0) return 100.0;
    int same = 0;
    int n = (na < nb) ? na : nb;
    for (int i = 0; i < n; i++) if (a[i] == b[i]) same++;
    return 100.0 * same / ((na + nb + 1) / 2);
}

// ============================================================
//                     数论与数学(第三批)（自动生成）
// ============================================================

int gcd_of_array(int arr[], int size) {
    if (size < 1) return 0;
    int g = arr[0];
    for (int i = 1; i < size; i++) g = gcd(g, arr[i]);
    return g;
}

long long lcm_of_array(int arr[], int size) {
    if (size < 1) return 0;
    long long l = arr[0];
    for (int i = 1; i < size; i++) l = lcm((int)l, arr[i]);
    return l;
}

int sum_of_squares_digits(int n) {
    int s = 0;
    if (n < 0) n = -n;
    while (n) { int d = n % 10; s += d * d; n /= 10; }
    return s;
}

int is_pandigital(int n) {
    if (n <= 0) return 0;
    int seen[10] = {0}, len = 0;
    while (n) { int d = n % 10; if (d == 0 || seen[d]) return 0; seen[d] = 1; len++; n /= 10; }
    for (int i = 1; i <= len; i++) if (!seen[i]) return 0;
    return 1;
}

int is_repdigit(int n) {
    if (n < 0) n = -n;
    int d = n % 10;
    while (n) { if (n % 10 != d) return 0; n /= 10; }
    return 1;
}

int digit_product(int n) {
    int p = 1;
    if (n < 0) n = -n;
    if (n == 0) return 0;
    while (n) { p *= n % 10; n /= 10; }
    return p;
}

long long nth_triangular(int n) {
    return (n <= 0) ? 0 : (long long)n * (n + 1) / 2;
}

long long fib_sum_first(int n) {
    long long a = 0, b = 1, s = 0;
    for (int i = 0; i < n; i++) { s += a; long long t = a + b; a = b; b = t; }
    return s;
}

int is_ugly_number(int n) {
    if (n <= 0) return 0;
    while (n % 2 == 0) n /= 2;
    while (n % 3 == 0) n /= 3;
    while (n % 5 == 0) n /= 5;
    return n == 1;
}

int is_square_free(int n) {
    if (n < 1) return 0;
    for (int i = 2; i * i <= n; i++) if (n % (i * i) == 0) return 0;
    return 1;
}

int radical(int n) {
    int r = 1;
    for (int i = 2; i * i <= n; i++) if (n % i == 0) { r *= i; while (n % i == 0) n /= i; }
    if (n > 1) r *= n;
    return r;
}

int is_emirp(int n) {
    if (!is_prime(n)) return 0;
    int r = reverse_int(n);
    return (r != n) && is_prime(r);
}

int count_coprimes(int n) {
    int c = 0;
    for (int i = 1; i <= n; i++) if (gcd(i, n) == 1) c++;
    return c;
}

uint32_t int_to_gray(uint32_t n) {
    return n ^ (n >> 1);
}

uint32_t gray_to_int(uint32_t g) {
    uint32_t n = 0;
    while (g) { n ^= g; g >>= 1; }
    return n;
}

// ============================================================
//                     数值工具(第三批)（自动生成）
// ============================================================

long clamp_long(long v, long lo, long hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

float clamp_float(float v, float lo, float hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

double lerp_clamped(double a, double b, double t) {
    if (t < 0) t = 0;
    if (t > 1) t = 1;
    return a + (b - a) * t;
}

double smoothstep(double x) {
    if (x <= 0) return 0.0;
    if (x >= 1) return 1.0;
    return x * x * (3 - 2 * x);
}

double normalize_01(double x, double min, double max) {
    if (max == min) return 0.0;
    return (x - min) / (max - min);
}

long long int_divide_ceil(long long a, long long b) {
    if (b == 0) return 0;
    return (a + b - 1) / b;
}

long long int_divide_floor(long long a, long long b) {
    if (b == 0) return 0;
    return a / b;
}

int is_between_int(int v, int lo, int hi) {
    return (v >= lo && v <= hi);
}

int is_between_double(double v, double lo, double hi) {
    return (v >= lo && v <= hi);
}

double percent_delta(double a, double b) {
    if (a == 0) return 0.0;
    return (b - a) * 100.0 / a;
}

double average_of_three(double a, double b, double c) {
    return (a + b + c) / 3.0;
}

double product_of_three(double a, double b, double c) {
    return a * b * c;
}

int sign_double(double x) {
    return (x > 0) - (x < 0);
}

double percent_of(double part, double total) {
    return (total == 0) ? 0.0 : part / total * 100.0;
}

double distance_1d(double a, double b) {
    return fabs(a - b);
}

// ============================================================
//                     位运算(第三批)（自动生成）
// ============================================================

uint32_t clear_high_bits(uint32_t val, int n) {
    if (n <= 0) return 0;
    if (n >= 32) return val;
    return val & ((1u << n) - 1);
}

uint32_t toggle_bits(uint32_t val, uint32_t mask) {
    return val ^ mask;
}

uint32_t set_bits_mask(uint32_t val, uint32_t mask) {
    return val | mask;
}

uint32_t clear_bits_mask(uint32_t val, uint32_t mask) {
    return val & ~mask;
}

uint8_t bit_reverse_byte(uint8_t b) {
    uint8_t r = 0;
    for (int i = 0; i < 8; i++) { r = (uint8_t)((r << 1) | (b & 1)); b >>= 1; }
    return r;
}

uint16_t int_to_gray16(uint16_t n) {
    return (uint16_t)(n ^ (n >> 1));
}

int is_single_bit(uint32_t val) {
    return (val != 0) && ((val & (val - 1)) == 0);
}

uint32_t lowest_one(uint32_t val) {
    return val & (uint32_t)(-(int32_t)val);
}

// ============================================================
//                     进制转换(第三批)（自动生成）
// ============================================================

char* byte_to_bin_str(uint8_t b, char *buf, int buf_size) {
    if (!buf || buf_size < 9) return buf;
    for (int i = 7; i >= 0; i--) buf[7 - i] = (b & (1u << i)) ? '1' : '0';
    buf[8] = '\0';
    return buf;
}

char* word_to_bin_str(uint16_t w, char *buf, int buf_size) {
    if (!buf || buf_size < 17) return buf;
    for (int i = 15; i >= 0; i--) buf[15 - i] = (w & (1u << i)) ? '1' : '0';
    buf[16] = '\0';
    return buf;
}

long long float_to_int_round(float f) {
    return (long long)(f >= 0 ? f + 0.5f : f - 0.5f);
}

long long float_to_int_truncate(float f) {
    return (long long)f;
}

char* long_to_str(long v, char *buf) {
    sprintf(buf, "%ld", v);
    return buf;
}

long char_array_to_long(const char *s, int len) {
    long r = 0;
    for (int i = 0; i < len && s[i]; i++) { if (!is_digit_char(s[i])) break; r = r * 10 + (s[i] - '0'); }
    return r;
}

char* dec_str_to_hex_str(const char *dec, char *buf, int buf_size) {
    (void)buf_size;
    long v = str_to_long(dec);
    return int_to_hex_str((int)v, buf);
}

// ============================================================
//                     控制台与调试(第三批)（自动生成）
// ============================================================

void print_progress_bar(int percent, int width) {
    if (percent < 0) percent = 0;
    if (percent > 100) percent = 100;
    int fill = width * percent / 100;
    printf("[");
    for (int i = 0; i < width; i++) putchar(i < fill ? '#' : ' ');
    printf("] %d%%\n", percent);
}

void print_ok(const char *msg) {
    printf("\033[32m[OK] %s\033[0m\n", msg);
}

void print_fail(const char *msg) {
    printf("\033[31m[FAIL] %s\033[0m\n", msg);
}

void print_warn(const char *msg) {
    printf("\033[33m[WARN] %s\033[0m\n", msg);
}

void log_timestamp(const char *msg) {
    char ts[20];
    get_time_str(ts);
    printf("[%s] %s\n", ts, msg);
}

void print_padded_int(int v, int width) {
    printf("%*d\n", width, v);
}

void print_bool(int b) {
    printf("%s\n", b ? "true" : "false");
}

void print_center(const char *title, int width) {
    int n = str_len(title), pad = (width - n) / 2;
    if (pad < 0) pad = 0;
    for (int i = 0; i < pad; i++) putchar(' ');
    printf("%s\n", title);
}

// ============================================================
//                     数列与序列（自动生成）
// ============================================================

void fibonacci_array(long long out[], int n) {
    if (n < 1) return;
    out[0] = 0;
    if (n > 1) out[1] = 1;
    for (int i = 2; i < n; i++) out[i] = out[i - 1] + out[i - 2];
}

void square_array(long long out[], int n) {
    for (int i = 0; i < n; i++) out[i] = (long long)(i + 1) * (i + 1);
}

void triangular_array(long long out[], int n) {
    for (int i = 0; i < n; i++) out[i] = (long long)(i + 1) * (i + 2) / 2;
}

int collatz_sequence(int n, int out[], int max_len) {
    int c = 0;
    while (n != 1 && c < max_len) { out[c++] = n; n = (n % 2) ? 3 * n + 1 : n / 2; }
    if (c < max_len) out[c++] = 1;
    return c;
}

int pascal_row(int n, int out[], int *len) {
    if (n < 0) { *len = 0; return 0; }
    *len = n + 1;
    long long v = 1;
    for (int k = 0; k <= n; k++) { out[k] = (int)v; v = v * (n - k) / (k + 1); }
    return 0;
}

int is_arithmetic_sequence(int arr[], int size) {
    if (size < 3) return 1;
    int d = arr[1] - arr[0];
    for (int i = 2; i < size; i++) if (arr[i] - arr[i - 1] != d) return 0;
    return 1;
}

int is_geometric_sequence(double arr[], int size) {
    if (size < 3) return 1;
    if (arr[0] == 0) return 0;
    double r = arr[1] / arr[0];
    for (int i = 2; i < size; i++) if (fabs(arr[i] / arr[i - 1] - r) > 1e-9) return 0;
    return 1;
}

long long subfactorial(int n) {
    if (n < 0) return 0;
    if (n == 0) return 1;
    if (n == 1) return 0;
    long long a = 1, b = 0, c;
    for (int i = 2; i <= n; i++) { c = (long long)(i - 1) * (a + b); a = b; b = c; }
    return b;
}

long long lucas_number(int n) {
    if (n < 0) return -1;
    if (n == 0) return 2;
    if (n == 1) return 1;
    long long a = 2, b = 1, c;
    for (int i = 2; i <= n; i++) { c = a + b; a = b; b = c; }
    return b;
}

// ============================================================
//                     文件工具(第三批)（自动生成）
// ============================================================

int file_clear(const char *filename) {
    FILE *fp = fopen(filename, "w");
    if (!fp) return -1;
    fclose(fp);
    return 0;
}

uint8_t* file_read_all_bytes(const char *filename, size_t *out_len) {
    FILE *fp = fopen(filename, "rb");
    if (!fp) return NULL;
    fseek(fp, 0, SEEK_END);
    long sz = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    uint8_t *buf = (uint8_t*)malloc((size_t)sz);
    if (!buf) { fclose(fp); return NULL; }
    fread(buf, 1, (size_t)sz, fp);
    fclose(fp);
    *out_len = (size_t)sz;
    return buf;
}

int file_write_bytes(const char *filename, const uint8_t *data, size_t len) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) return -1;
    fwrite(data, 1, len, fp);
    fclose(fp);
    return 0;
}

int file_count_words(const char *filename) {
    char *s = read_file(filename);
    if (!s) return -1;
    int c = count_words(s);
    free(s);
    return c;
}

int file_has_line(const char *filename, const char *line) {
    FILE *fp = fopen(filename, "r");
    if (!fp) return 0;
    char buf[1024];
    while (safe_fgets(buf, sizeof(buf), fp)) { if (str_cmp(buf, line) == 0) { fclose(fp); return 1; } }
    fclose(fp);
    return 0;
}

// ============================================================
//                     排序算法(第三批)（自动生成）
// ============================================================

void sort_asc(int arr[], int size) {
    bubble_sort(arr, size);
}

void sort_desc(int arr[], int size) {
    bubble_sort(arr, size);
    reverse_int_array(arr, size);
}

void sort_double_asc(double arr[], int size) {
    for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[j] > arr[j + 1]) { double t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t; }
}

void sort_float_asc(float arr[], int size) {
    for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[j] > arr[j + 1]) { float t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t; }
}

void sort_long_asc(long arr[], int size) {
    for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[j] > arr[j + 1]) { long t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t; }
}

void sort_char_asc(char arr[], int size) {
    for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[j] > arr[j + 1]) { char t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t; }
}

int sort_unique(int arr[], int *size) {
    bubble_sort(arr, *size);
    return remove_duplicates_int(arr, size);
}

int* sort_indices(int arr[], int size) {
    int *idx = (int*)malloc(size * sizeof(int));
    if (!idx) return NULL;
    for (int i = 0; i < size; i++) idx[i] = i;
    for (int i = 0; i < size - 1; i++) for (int j = 0; j < size - 1 - i; j++) if (arr[idx[j]] > arr[idx[j + 1]]) { int t = idx[j]; idx[j] = idx[j + 1]; idx[j + 1] = t; }
    return idx;
}

// ============================================================
//                     核心算法(补齐)（自动生成）
// ============================================================

int interpolation_search(int arr[], int size, int target) {
    int lo = 0, hi = size - 1;
    while (lo <= hi && target >= arr[lo] && target <= arr[hi]) {
        if (arr[hi] == arr[lo]) return (arr[lo] == target) ? lo : -1;
        int pos = lo + (int)(((long long)(target - arr[lo]) * (hi - lo)) / (arr[hi] - arr[lo]));
        if (arr[pos] == target) return pos;
        if (arr[pos] < target) lo = pos + 1; else hi = pos - 1; }
    return -1;
}

int sentinel_search(int arr[], int size, int target) {
    if (size <= 0) return -1;
    int last = arr[size - 1];
    arr[size - 1] = target;
    int i = 0;
    while (arr[i] != target) i++;
    arr[size - 1] = last;
    if (i < size - 1) return i;
    return (last == target) ? size - 1 : -1;
}

int fibonacci_search(int arr[], int size, int target) {
    int f2 = 0, f1 = 1, f = f2 + f1;
    while (f < size) { f2 = f1; f1 = f; f = f2 + f1; }
    int offset = -1;
    while (f > 1) {
        int i = (offset + f2 < size - 1) ? offset + f2 : size - 1;
        if (arr[i] < target) { f = f1; f1 = f2; f2 = f - f1; offset = i; }
        else if (arr[i] > target) { f = f2; f1 = f1 - f2; f2 = f - f1; }
        else return i; }
    if (f1 && offset + 1 < size && arr[offset + 1] == target) return offset + 1;
    return -1;
}

int kmp_search(const char *text, const char *pattern) {
    if (!text || !pattern) return -1;
    int m = str_len(pattern);
    if (m == 0) return 0;
    int n = str_len(text);
    int *next = (int*)malloc(m * sizeof(int));
    if (!next) return -1;
    next[0] = 0;
    int j = 0;
    for (int i = 1; i < m; i++) { while (j > 0 && pattern[i] != pattern[j]) j = next[j - 1]; if (pattern[i] == pattern[j]) j++; next[i] = j; }
    j = 0;
    int found = -1;
    for (int i = 0; i < n; i++) { while (j > 0 && text[i] != pattern[j]) j = next[j - 1]; if (text[i] == pattern[j]) j++; if (j == m) { found = i - m + 1; break; } }
    free(next);
    return found;
}

int str_longest_common_substr(const char *s1, const char *s2) {
    int n1 = str_len(s1), n2 = str_len(s2), best = 0;
    for (int i = 0; i < n1; i++) for (int j = 0; j < n2; j++) {
        int l = 0;
        while (i + l < n1 && j + l < n2 && s1[i + l] == s2[j + l]) l++;
        if (l > best) best = l; }
    return best;
}

int str_edit_distance(const char *s1, const char *s2) {
    int n1 = str_len(s1), n2 = str_len(s2);
    if (n1 == 0) return n2;
    if (n2 == 0) return n1;
    int *dp = (int*)malloc((n2 + 1) * sizeof(int));
    if (!dp) return -1;
    for (int j = 0; j <= n2; j++) dp[j] = j;
    for (int i = 1; i <= n1; i++) { int prev = dp[0]; dp[0] = i;
        for (int j = 1; j <= n2; j++) { int t = dp[j];
            if (s1[i - 1] == s2[j - 1]) dp[j] = prev;
            else { int d = dp[j - 1] + 1, ins = dp[j] + 1, rep = prev + 1; dp[j] = UTILS_MIN(d, UTILS_MIN(ins, rep)); }
            prev = t; } }
    int r = dp[n2];
    free(dp);
    return r;
}

void str_reverse_words(char *str) {
    int len = str_len(str);
    for (int i = 0; i < len / 2; i++) { char t = str[i]; str[i] = str[len - 1 - i]; str[len - 1 - i] = t; }
    int i = 0;
    while (i < len) { while (i < len && str[i] == ' ') i++; int s = i; while (i < len && str[i] != ' ') i++; int a = s, b = i - 1; while (a < b) { char t = str[a]; str[a] = str[b]; str[b] = t; a++; b--; } }
}

long long* build_prefix_sum(int arr[], int size) {
    long long *pre = (long long*)malloc((size + 1) * sizeof(long long));
    if (!pre) return NULL;
    pre[0] = 0;
    for (int i = 0; i < size; i++) pre[i + 1] = pre[i] + arr[i];
    return pre;
}

long long range_sum_query(long long pre[], int l, int r) {
    if (!pre || l > r) return 0;
    return pre[r + 1] - pre[l];
}

void build_diff_array(int arr[], int size, int diff[]) {
    diff[0] = arr[0];
    for (int i = 1; i < size; i++) diff[i] = arr[i] - arr[i - 1];
    diff[size] = 0;
}

void apply_diff_array(int diff[], int size, int out[]) {
    out[0] = diff[0];
    for (int i = 1; i < size; i++) out[i] = out[i - 1] + diff[i];
}

int* sieve_primes(int n, int *count) {
    *count = 0;
    if (n < 2) return NULL;
    char *mark = (char*)calloc(n + 1, 1);
    if (!mark) return NULL;
    for (int i = 2; i <= n; i++) mark[i] = 1;
    for (int i = 2; i * i <= n; i++) if (mark[i]) for (int j = i * i; j <= n; j += i) mark[j] = 0;
    int cnt = 0;
    for (int i = 2; i <= n; i++) if (mark[i]) cnt++;
    int *p = (int*)malloc(cnt * sizeof(int));
    if (!p) { free(mark); return NULL; }
    int k = 0;
    for (int i = 2; i <= n; i++) if (mark[i]) p[k++] = i;
    free(mark);
    *count = cnt;
    return p;
}

int prime_factors(int n, int factors[], int *count) {
    *count = 0;
    if (n <= 1) return 0;
    for (int i = 2; (long long)i * i <= n; i++) while (n % i == 0) { factors[*count] = i; (*count)++; n /= i; }
    if (n > 1) { factors[*count] = n; (*count)++; }
    return *count;
}

long long mod_pow(long long base, long long exp, long long mod) {
    long long r = 1 % mod;
    base %= mod;
    while (exp > 0) { if (exp & 1) r = (r * base) % mod; base = (base * base) % mod; exp >>= 1; }
    return r;
}

int extended_gcd(int a, int b, int *x, int *y) {
    if (b == 0) { *x = 1; *y = 0; return a; }
    int x1, y1;
    int g = extended_gcd(b, a % b, &x1, &y1);
    *x = y1;
    *y = x1 - (a / b) * y1;
    return g;
}

int next_permutation(int arr[], int size) {
    if (size <= 1) return 0;
    int i = size - 2;
    while (i >= 0 && arr[i] >= arr[i + 1]) i--;
    if (i < 0) return 0;
    int j = size - 1;
    while (arr[j] <= arr[i]) j--;
    int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    int l = i + 1, r = size - 1;
    while (l < r) { t = arr[l]; arr[l] = arr[r]; arr[r] = t; l++; r--; }
    return 1;
}

int is_leap_year(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

int is_power_of_two(int n) {
    return (n > 0) && ((n & (n - 1)) == 0);
}

int lowest_set_bit(uint32_t n) {
    if (n == 0) return -1;
    int p = 0;
    while (!(n & 1u)) { n >>= 1; p++; }
    return p;
}

int find_single_number(int arr[], int size) {
    int r = 0;
    for (int i = 0; i < size; i++) r ^= arr[i];
    return r;
}

int hamming_distance(uint32_t a, uint32_t b) {
    uint32_t x = a ^ b;
    int c = 0;
    while (x) { c += (int)(x & 1u); x >>= 1; }
    return c;
}

int knapsack01(int weights[], int values[], int n, int capacity) {
    int *dp = (int*)calloc(capacity + 1, sizeof(int));
    if (!dp) return 0;
    for (int i = 0; i < n; i++) for (int c = capacity; c >= weights[i]; c--) {
        int take = dp[c - weights[i]] + values[i];
        if (take > dp[c]) dp[c] = take; }
    int r = dp[capacity];
    free(dp);
    return r;
}

int lis_length(int arr[], int size) {
    if (size <= 0) return 0;
    int *dp = (int*)malloc(size * sizeof(int));
    if (!dp) return 0;
    int best = 1;
    for (int i = 0; i < size; i++) { dp[i] = 1; for (int j = 0; j < i; j++) if (arr[j] < arr[i] && dp[j] + 1 > dp[i]) dp[i] = dp[j] + 1; if (dp[i] > best) best = dp[i]; }
    free(dp);
    return best;
}

uint32_t djb2_hash(const char *str) {
    uint32_t h = 5381;
    while (*str) h = ((h << 5) + h) + (uint32_t)(unsigned char)*str++;
    return h;
}

uint32_t fnv1a_hash(const char *str) {
    uint32_t h = 2166136261u;
    while (*str) { h ^= (uint32_t)(unsigned char)*str++; h *= 16777619u; }
    return h;
}

uint32_t sdbm_hash(const char *str) {
    uint32_t h = 0;
    while (*str) h = (uint32_t)(unsigned char)*str++ + (h << 6) + (h << 16) - h;
    return h;
}

uint32_t bkdr_hash(const char *str) {
    uint32_t h = 0;
    while (*str) h = h * 131 + (uint32_t)(unsigned char)*str++;
    return h;
}

RingBuffer* rb_create(uint16_t capacity) {
    if (capacity == 0) return NULL;
    RingBuffer *rb = (RingBuffer*)malloc(sizeof(RingBuffer));
    if (!rb) return NULL;
    rb->buffer = (uint8_t*)malloc(capacity);
    if (!rb->buffer) { free(rb); return NULL; }
    rb->head = 0; rb->tail = 0; rb->capacity = capacity; rb->count = 0;
    return rb;
}

void rb_destroy(RingBuffer *rb) {
    if (!rb) return;
    free(rb->buffer);
    free(rb);
}

int rb_write(RingBuffer *rb, uint8_t byte) {
    if (!rb || rb->count >= rb->capacity) return -1;
    rb->buffer[rb->head] = byte;
    rb->head = (uint16_t)((rb->head + 1) % rb->capacity);
    rb->count++;
    return 0;
}

int rb_read(RingBuffer *rb, uint8_t *out) {
    if (!rb || rb->count == 0 || !out) return -1;
    *out = rb->buffer[rb->tail];
    rb->tail = (uint16_t)((rb->tail + 1) % rb->capacity);
    rb->count--;
    return 0;
}

int rb_peek(RingBuffer *rb, uint8_t *out) {
    if (!rb || rb->count == 0 || !out) return -1;
    *out = rb->buffer[rb->tail];
    return 0;
}

uint16_t rb_available(RingBuffer *rb) {
    return (rb == NULL) ? 0 : rb->count;
}

uint16_t rb_free(RingBuffer *rb) {
    return (rb == NULL) ? 0 : (uint16_t)(rb->capacity - rb->count);
}

int rb_is_empty(RingBuffer *rb) {
    return (rb == NULL || rb->count == 0);
}

int rb_is_full(RingBuffer *rb) {
    return (rb != NULL && rb->count >= rb->capacity);
}

void rb_clear(RingBuffer *rb) {
    if (!rb) return;
    rb->head = 0; rb->tail = 0; rb->count = 0;
}

Vector* vec_create(int init_capacity) {
    if (init_capacity <= 0) init_capacity = 4;
    Vector *v = (Vector*)malloc(sizeof(Vector));
    if (!v) return NULL;
    v->data = (int*)malloc(init_capacity * sizeof(int));
    if (!v->data) { free(v); return NULL; }
    v->size = 0; v->capacity = init_capacity;
    return v;
}

void vec_destroy(Vector *v) {
    if (!v) return;
    free(v->data);
    free(v);
}

int vec_push_back(Vector *v, int value) {
    if (!v) return -1;
    if (v->size >= v->capacity) {
        int nc = v->capacity * 2;
        int *nd = (int*)realloc(v->data, nc * sizeof(int));
        if (!nd) return -1;
        v->data = nd; v->capacity = nc; }
    v->data[v->size++] = value;
    return 0;
}

int vec_pop_back(Vector *v, int *out) {
    if (!v || v->size <= 0 || !out) return -1;
    *out = v->data[--v->size];
    return 0;
}

int vec_get(Vector *v, int index, int *out) {
    if (!v || index < 0 || index >= v->size || !out) return -1;
    *out = v->data[index];
    return 0;
}

int vec_set(Vector *v, int index, int value) {
    if (!v || index < 0 || index >= v->size) return -1;
    v->data[index] = value;
    return 0;
}

int vec_size(Vector *v) {
    return (v == NULL) ? 0 : v->size;
}

int vec_capacity(Vector *v) {
    return (v == NULL) ? 0 : v->capacity;
}

int vec_is_empty(Vector *v) {
    return (v == NULL || v->size == 0);
}

void vec_clear(Vector *v) {
    if (v) v->size = 0;
}

int vec_insert(Vector *v, int index, int value) {
    if (!v || index < 0 || index > v->size) return -1;
    if (v->size >= v->capacity) { int nc = v->capacity * 2; int *nd = (int*)realloc(v->data, nc * sizeof(int)); if (!nd) return -1; v->data = nd; v->capacity = nc; }
    for (int i = v->size; i > index; i--) v->data[i] = v->data[i - 1];
    v->data[index] = value; v->size++;
    return 0;
}

int vec_remove(Vector *v, int index, int *out) {
    if (!v || index < 0 || index >= v->size) return -1;
    if (out) *out = v->data[index];
    for (int i = index; i < v->size - 1; i++) v->data[i] = v->data[i + 1];
    v->size--;
    return 0;
}

PriorityQueue* pq_create(int capacity) {
    if (capacity <= 0) capacity = 16;
    PriorityQueue *pq = (PriorityQueue*)malloc(sizeof(PriorityQueue));
    if (!pq) return NULL;
    pq->data = (int*)malloc(capacity * sizeof(int));
    if (!pq->data) { free(pq); return NULL; }
    pq->size = 0; pq->capacity = capacity;
    return pq;
}

void pq_destroy(PriorityQueue *pq) {
    if (!pq) return;
    free(pq->data);
    free(pq);
}

int pq_push(PriorityQueue *pq, int value) {
    if (!pq) return -1;
    if (pq->size >= pq->capacity) { int nc = pq->capacity * 2; int *nd = (int*)realloc(pq->data, nc * sizeof(int)); if (!nd) return -1; pq->data = nd; pq->capacity = nc; }
    int i = pq->size++;
    pq->data[i] = value;
    while (i > 0) { int p = (i - 1) / 2; if (pq->data[p] >= pq->data[i]) break; int t = pq->data[p]; pq->data[p] = pq->data[i]; pq->data[i] = t; i = p; }
    return 0;
}

int pq_pop(PriorityQueue *pq, int *out) {
    if (!pq || pq->size <= 0 || !out) return -1;
    *out = pq->data[0];
    pq->data[0] = pq->data[--pq->size];
    int i = 0;
    while (1) { int l = 2 * i + 1, r = 2 * i + 2, s = i;
        if (l < pq->size && pq->data[l] > pq->data[s]) s = l;
        if (r < pq->size && pq->data[r] > pq->data[s]) s = r;
        if (s == i) break;
        int t = pq->data[s]; pq->data[s] = pq->data[i]; pq->data[i] = t; i = s; }
    return 0;
}

int pq_peek(PriorityQueue *pq, int *out) {
    if (!pq || pq->size <= 0 || !out) return -1;
    *out = pq->data[0];
    return 0;
}

int pq_is_empty(PriorityQueue *pq) {
    return (pq == NULL || pq->size == 0);
}

int pq_size(PriorityQueue *pq) {
    return (pq == NULL) ? 0 : pq->size;
}

BSTNode* bst_insert(BSTNode *root, int data) {
    if (root == NULL) { BSTNode *n = (BSTNode*)malloc(sizeof(BSTNode)); if (!n) return NULL; n->data = data; n->left = n->right = NULL; return n; }
    if (data < root->data) root->left = bst_insert(root->left, data);
    else if (data > root->data) root->right = bst_insert(root->right, data);
    return root;
}

BSTNode* bst_search(BSTNode *root, int data) {
    while (root) { if (data == root->data) return root; root = (data < root->data) ? root->left : root->right; }
    return NULL;
}

BSTNode* bst_find_min(BSTNode *root) {
    if (!root) return NULL;
    while (root->left) root = root->left;
    return root;
}

BSTNode* bst_find_max(BSTNode *root) {
    if (!root) return NULL;
    while (root->right) root = root->right;
    return root;
}

BSTNode* bst_delete(BSTNode *root, int data) {
    if (!root) return NULL;
    if (data < root->data) root->left = bst_delete(root->left, data);
    else if (data > root->data) root->right = bst_delete(root->right, data);
    else { if (!root->left) { BSTNode *r = root->right; free(root); return r; }
        if (!root->right) { BSTNode *l = root->left; free(root); return l; }
        BSTNode *mn = bst_find_min(root->right);
        root->data = mn->data;
        root->right = bst_delete(root->right, mn->data); }
    return root;
}

int bst_height(BSTNode *root) {
    if (!root) return 0;
    int l = bst_height(root->left), r = bst_height(root->right);
    return (l > r ? l : r) + 1;
}

int bst_node_count(BSTNode *root) {
    if (!root) return 0;
    return 1 + bst_node_count(root->left) + bst_node_count(root->right);
}

void bst_inorder(BSTNode *root) {
    if (!root) return;
    bst_inorder(root->left);
    printf("%d ", root->data);
    bst_inorder(root->right);
}

void bst_preorder(BSTNode *root) {
    if (!root) return;
    printf("%d ", root->data);
    bst_preorder(root->left);
    bst_preorder(root->right);
}

void bst_postorder(BSTNode *root) {
    if (!root) return;
    bst_postorder(root->left);
    bst_postorder(root->right);
    printf("%d ", root->data);
}

void bst_levelorder(BSTNode *root) {
    if (!root) return;
    BSTNode **q = (BSTNode**)malloc(128 * sizeof(BSTNode*));
    if (!q) return;
    int head = 0, tail = 0;
    q[tail++] = root;
    while (head < tail) { BSTNode *n = q[head++]; printf("%d ", n->data); if (n->left) q[tail++] = n->left; if (n->right) q[tail++] = n->right; }
    free(q);
}

void bst_free(BSTNode *root) {
    if (!root) return;
    bst_free(root->left);
    bst_free(root->right);
    free(root);
}

long long get_timestamp_ms(void) {
    #if defined(_WIN32)
    FILETIME ft;
    GetSystemTimeAsFileTime(&ft);
    const long long DIFF = 116444736000000000LL;
    long long t = ((long long)ft.dwHighDateTime << 32) | ft.dwLowDateTime;
    return (t - DIFF) / 10000;
    #elif defined(__unix__) || defined(__linux__) || defined(__APPLE__)
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (long long)tv.tv_sec * 1000 + tv.tv_usec / 1000;
    #else
    return (long long)time(NULL) * 1000;
    #endif
}

long long get_timestamp_us(void) {
    #if defined(_WIN32)
    FILETIME ft;
    GetSystemTimeAsFileTime(&ft);
    const long long DIFF = 116444736000000000LL;
    long long t = ((long long)ft.dwHighDateTime << 32) | ft.dwLowDateTime;
    return (t - DIFF) / 10;
    #elif defined(__unix__) || defined(__linux__) || defined(__APPLE__)
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (long long)tv.tv_sec * 1000000 + tv.tv_usec;
    #else
    return (long long)time(NULL) * 1000000;
    #endif
}

void log_to_file(const char *filename, const char *format, ...) {
    if (!filename || !format) return;
    FILE *fp = fopen(filename, "a");
    if (!fp) return;
    char ts[20];
    get_time_str(ts);
    fprintf(fp, "[%s] ", ts);
    va_list args;
    va_start(args, format);
    vfprintf(fp, format, args);
    va_end(args);
    fprintf(fp, "\n");
    fclose(fp);
}

/* ============================================================
 *  手动扩展区（与 utils_gen.h 手动扩展区对应，人工维护）
 * ============================================================ */

/* ---------- 并查集 ---------- */

UnionFind* uf_create(int size) {
    if (size <= 0) return NULL;
    UnionFind *uf = (UnionFind*)malloc(sizeof(UnionFind));
    if (!uf) return NULL;
    uf->parent = (int*)malloc((size_t)size * sizeof(int));
    uf->rank = (int*)malloc((size_t)size * sizeof(int));
    if (!uf->parent || !uf->rank) {
        free(uf->parent);
        free(uf->rank);
        free(uf);
        return NULL;
    }
    /* 初始时每个元素自成集合，秩为 0 */
    for (int i = 0; i < size; i++) {
        uf->parent[i] = i;
        uf->rank[i] = 0;
    }
    uf->size = size;
    return uf;
}

int uf_find(UnionFind *uf, int x) {
    if (!uf || x < 0 || x >= uf->size) return -1;
    /* 路径压缩：把沿途节点直接指向根 */
    if (uf->parent[x] != x) uf->parent[x] = uf_find(uf, uf->parent[x]);
    return uf->parent[x];
}

int uf_union(UnionFind *uf, int a, int b) {
    if (!uf) return -1;
    int ra = uf_find(uf, a);
    int rb = uf_find(uf, b);
    if (ra < 0 || rb < 0) return -1;
    if (ra == rb) return 1;   /* 已在同一集合 */
    /* 按秩合并：秩小的根接到秩大的根上 */
    if (uf->rank[ra] < uf->rank[rb]) {
        uf->parent[ra] = rb;
    } else if (uf->rank[ra] > uf->rank[rb]) {
        uf->parent[rb] = ra;
    } else {
        uf->parent[rb] = ra;
        uf->rank[ra]++;
    }
    return 0;
}

int uf_connected(UnionFind *uf, int a, int b) {
    int ra = uf_find(uf, a);
    int rb = uf_find(uf, b);
    return (ra >= 0 && ra == rb) ? 1 : 0;
}

void uf_destroy(UnionFind *uf) {
    if (!uf) return;
    free(uf->parent);
    free(uf->rank);
    free(uf);
}

/* ---------- 图：有向加边 ---------- */

void graph_add_edge_dir(Graph *g, int u, int v) {
    if (!g || u < 0 || u >= g->n || v < 0 || v >= g->n) return;
    g->adj[u][v] = 1;   /* 只设置 u -> v 方向 */
}

/* ---------- 图：拓扑排序（Kahn 算法） ---------- */

int topological_sort(const Graph *g, int *out) {
    if (!g || !out || g->n <= 0) return -1;
    int n = g->n;
    int *indeg = (int*)calloc((size_t)n, sizeof(int));
    if (!indeg) return -1;
    /* 计算每个节点的入度 */
    for (int u = 0; u < n; u++)
        for (int v = 0; v < n; v++)
            if (g->adj[u][v]) indeg[v]++;
    /* 用数组模拟队列，存放下标 */
    int *queue = (int*)malloc((size_t)n * sizeof(int));
    if (!queue) { free(indeg); return -1; }
    int head = 0, tail = 0;
    for (int v = 0; v < n; v++) if (indeg[v] == 0) queue[tail++] = v;
    int cnt = 0;
    while (head < tail) {
        int u = queue[head++];
        out[cnt++] = u;
        for (int v = 0; v < n; v++) {
            if (g->adj[u][v] && --indeg[v] == 0) queue[tail++] = v;
        }
    }
    free(indeg);
    free(queue);
    /* 输出节点数不足说明存在环 */
    return (cnt == n) ? cnt : -1;
}

/* ---------- 图：Prim 最小生成树权值和 ---------- */

int prim_mst(const Graph *g) {
    if (!g || g->n <= 0) return -1;
    int n = g->n;
    int *lowcost = (int*)malloc((size_t)n * sizeof(int));
    int *inmst = (int*)calloc((size_t)n, sizeof(int));
    if (!lowcost || !inmst) { free(lowcost); free(inmst); return -1; }
    /* 从 0 号节点出发，记录到各节点当前最小边权 */
    for (int i = 0; i < n; i++) lowcost[i] = g->adj[0][i] ? g->adj[0][i] : 0x7FFFFFFF;
    inmst[0] = 1;
    int total = 0;
    for (int it = 1; it < n; it++) {
        int minc = 0x7FFFFFFF, u = -1;
        for (int v = 0; v < n; v++) {
            if (!inmst[v] && lowcost[v] < minc) { minc = lowcost[v]; u = v; }
        }
        if (u < 0) { free(lowcost); free(inmst); return -1; }   /* 图不连通 */
        inmst[u] = 1;
        total += minc;
        /* 用新加入的节点更新其他节点的最小边权 */
        for (int v = 0; v < n; v++) {
            if (!inmst[v] && g->adj[u][v] && g->adj[u][v] < lowcost[v])
                lowcost[v] = g->adj[u][v];
        }
    }
    free(lowcost);
    free(inmst);
    return total;
}

/* ---------- 二分边界（数组需升序） ---------- */

int lower_bound(int arr[], int size, int target) {
    int lo = 0, hi = size;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] < target) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

int upper_bound(int arr[], int size, int target) {
    int lo = 0, hi = size;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] <= target) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

/* ---------- 逆序对（归并排序） ---------- */

static long long inv_merge_count(int arr[], int tmp[], int lo, int hi) {
    if (lo >= hi) return 0;
    int mid = lo + (hi - lo) / 2;
    long long cnt = inv_merge_count(arr, tmp, lo, mid) + inv_merge_count(arr, tmp, mid + 1, hi);
    int i = lo, j = mid + 1, k = lo;
    while (i <= mid && j <= hi) {
        if (arr[i] <= arr[j]) tmp[k++] = arr[i++];
        else { tmp[k++] = arr[j++]; cnt += (mid - i + 1); }   /* 左边剩余都大于 arr[j] */
    }
    while (i <= mid) tmp[k++] = arr[i++];
    while (j <= hi) tmp[k++] = arr[j++];
    for (i = lo; i <= hi; i++) arr[i] = tmp[i];
    return cnt;
}

long long count_inversions(int arr[], int size) {
    if (size <= 1) return 0;
    int *tmp = (int*)malloc((size_t)size * sizeof(int));
    if (!tmp) return 0;
    long long cnt = inv_merge_count(arr, tmp, 0, size - 1);
    free(tmp);
    return cnt;
}

/* ---------- 滑动窗口最大值（单调双端队列） ---------- */

int sliding_window_max(int arr[], int size, int k, int *out) {
    if (!arr || !out || k <= 0 || k > size) return 0;
    int *dq = (int*)malloc((size_t)size * sizeof(int));   /* 存下标 */
    if (!dq) return 0;
    int head = 0, tail = 0;   /* 队区间 [head, tail) */
    int cnt = 0;
    for (int i = 0; i < size; i++) {
        /* 队首元素滑出窗口 */
        if (head < tail && dq[head] <= i - k) head++;
        /* 移除队尾所有 <= 当前元素的（它们不可能成为最大值） */
        while (head < tail && arr[dq[tail - 1]] <= arr[i]) tail--;
        dq[tail++] = i;
        /* 窗口已满，队首即当前窗口最大值 */
        if (i >= k - 1) out[cnt++] = arr[dq[head]];
    }
    free(dq);
    return cnt;
}

/* ---------- 两数之和（朴素双重循环） ---------- */

int two_sum(int arr[], int size, int target, int *idx1, int *idx2) {
    if (!arr || !idx1 || !idx2 || size < 2) return 0;
    for (int i = 0; i < size - 1; i++) {
        for (int j = i + 1; j < size; j++) {
            if (arr[i] + arr[j] == target) {
                *idx1 = i;
                *idx2 = j;
                return 1;
            }
        }
    }
    return 0;
}

/* ---------- 字母异位词 ---------- */

int is_anagram(const char *a, const char *b) {
    if (!a || !b) return 0;
    int cnt[256] = {0};
    for (const char *p = a; *p; p++) cnt[(unsigned char)*p]++;
    for (const char *p = b; *p; p++) cnt[(unsigned char)*p]--;
    for (int i = 0; i < 256; i++) if (cnt[i] != 0) return 0;
    return 1;
}

/* ---------- 最长公共子序列长度（动态规划） ---------- */

int str_lcs(const char *a, const char *b) {
    if (!a || !b) return 0;
    int la = str_len(a), lb = str_len(b);
    if (la == 0 || lb == 0) return 0;
    int **dp = (int**)malloc((size_t)(la + 1) * sizeof(int*));
    if (!dp) return 0;
    int alloc_ok = 1;
    for (int i = 0; i <= la; i++) {
        dp[i] = (int*)calloc((size_t)(lb + 1), sizeof(int));
        if (!dp[i]) { alloc_ok = 0; break; }
    }
    if (!alloc_ok) {
        for (int i = 0; i <= la; i++) if (dp[i]) free(dp[i]);
        free(dp);
        return 0;
    }
    for (int i = 1; i <= la; i++) {
        for (int j = 1; j <= lb; j++) {
            if (a[i-1] == b[j-1]) dp[i][j] = dp[i-1][j-1] + 1;
            else dp[i][j] = (dp[i-1][j] > dp[i][j-1]) ? dp[i-1][j] : dp[i][j-1];
        }
    }
    int ans = dp[la][lb];
    for (int i = 0; i <= la; i++) free(dp[i]);
    free(dp);
    return ans;
}

/* ---------- 数论补充 ---------- */

int is_perfect_square(int n) {
    if (n < 0) return 0;
    int r = (int)(sqrt((double)n) + 0.5);   /* 四舍五入避免浮点误差 */
    return r * r == n;
}

int is_ugly(int n) {
    if (n <= 0) return 0;
    while (n % 2 == 0) n /= 2;
    while (n % 3 == 0) n /= 3;
    while (n % 5 == 0) n /= 5;
    return n == 1;
}

int count_primes(int n) {
    if (n < 2) return 0;
    char *iscomp = (char*)calloc((size_t)(n + 1), 1);
    if (!iscomp) return 0;
    int cnt = 0;
    for (int i = 2; i <= n; i++) {
        if (!iscomp[i]) {
            cnt++;
            if ((long long)i * i <= n)
                for (long long j = (long long)i * i; j <= n; j += i)
                    iscomp[(int)j] = 1;
        }
    }
    free(iscomp);
    return cnt;
}

/* ---------- 链表进阶（快慢指针等） ---------- */

ListNode* list_get_middle(ListNode *head) {
    if (!head) return NULL;
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;
}

ListNode* list_find_kth_from_end(ListNode *head, int k) {
    if (!head || k <= 0) return NULL;
    ListNode *fast = head, *slow = head;
    /* fast 先走 k 步 */
    for (int i = 0; i < k; i++) {
        if (!fast) return NULL;   /* 链表长度不足 k */
        fast = fast->next;
    }
    /* 再一起走，fast 到末尾时 slow 即倒数第 k 个 */
    while (fast) {
        slow = slow->next;
        fast = fast->next;
    }
    return slow;
}

int list_remove_duplicates(ListNode **head) {
    if (!head || !*head) return 0;
    int removed = 0;
    ListNode *cur = *head;
    while (cur && cur->next) {
        if (cur->data == cur->next->data) {   /* 相邻重复，删掉后一个 */
            ListNode *tmp = cur->next;
            cur->next = tmp->next;
            free(tmp);
            removed++;
        } else {
            cur = cur->next;
        }
    }
    return removed;
}

int list_is_palindrome(ListNode *head) {
    if (!head || !head->next) return 1;
    /* 快慢指针找中间 */
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
    }
    /* 反转后半部分 */
    ListNode *prev = NULL, *cur = slow;
    while (cur) {
        ListNode *nxt = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nxt;
    }
    /* 前半与反转后的后半逐项比较 */
    ListNode *a = head, *b = prev;
    while (b) {
        if (a->data != b->data) return 0;
        a = a->next;
        b = b->next;
    }
    return 1;
}

int list_insert_at(ListNode **head, int pos, int data) {
    if (!head || pos < 0) return -1;
    if (pos == 0) { list_insert_head(head, data); return 0; }
    ListNode *p = *head;
    for (int i = 0; i < pos - 1 && p; i++) p = p->next;
    if (!p) return -1;                         /* 位置越界 */
    ListNode *node = list_create(data);
    if (!node) return -1;
    node->next = p->next;
    p->next = node;
    return 0;
}

int list_delete_at(ListNode **head, int pos) {
    if (!head || !*head || pos < 0) return -1;
    if (pos == 0) {
        ListNode *tmp = *head;
        *head = (*head)->next;
        free(tmp);
        return 0;
    }
    ListNode *p = *head;
    for (int i = 0; i < pos - 1 && p->next; i++) p = p->next;
    if (!p->next) return -1;
    ListNode *tmp = p->next;
    p->next = tmp->next;
    free(tmp);
    return 0;
}

/* ---------- 循环链表（尾节点指向头节点） ---------- */

ListNode* clist_create(int data) {
    ListNode *node = list_create(data);
    if (node) node->next = node;   /* 单节点自成环 */
    return node;
}

int clist_insert_head(ListNode **head, int data) {
    if (!head) return -1;
    ListNode *node = list_create(data);
    if (!node) return -1;
    if (!*head) { node->next = node; *head = node; return 0; }
    ListNode *tail = *head;
    while (tail->next != *head) tail = tail->next;   /* 找尾节点 */
    node->next = *head;
    tail->next = node;
    *head = node;
    return 0;
}

int clist_append(ListNode **head, int data) {
    if (!head) return -1;
    ListNode *node = list_create(data);
    if (!node) return -1;
    if (!*head) { node->next = node; *head = node; return 0; }
    ListNode *tail = *head;
    while (tail->next != *head) tail = tail->next;
    tail->next = node;
    node->next = *head;   /* 尾指向头，保持循环 */
    return 0;
}

int clist_remove_value(ListNode **head, int data) {
    if (!head || !*head) return -1;
    ListNode *cur = *head;
    ListNode *prev = NULL;
    do {
        if (cur->data == data) {
            if (cur == *head) {
                if (cur->next == *head) {   /* 只剩一个节点 */
                    free(cur);
                    *head = NULL;
                    return 0;
                }
                /* 删除头节点：先找尾，尾指向新头 */
                ListNode *tail = *head;
                while (tail->next != *head) tail = tail->next;
                *head = cur->next;
                tail->next = *head;
                free(cur);
                return 0;
            }
            prev->next = cur->next;
            free(cur);
            return 0;
        }
        prev = cur;
        cur = cur->next;
    } while (cur != *head);
    return -1;   /* 未找到 */
}

int clist_length(ListNode *head) {
    if (!head) return 0;
    int len = 1;
    ListNode *p = head->next;
    while (p != head) { len++; p = p->next; }
    return len;
}

void clist_print(ListNode *head) {
    if (!head) { printf("(empty)\n"); return; }
    ListNode *p = head;
    do {
        printf("%d -> ", p->data);
        p = p->next;
    } while (p != head);
    printf("(back to head)\n");
}

void clist_free(ListNode **head) {
    if (!head || !*head) return;
    /* 先断开环，避免释放时死循环 */
    ListNode *tail = *head;
    while (tail->next != *head) tail = tail->next;
    tail->next = NULL;
    ListNode *cur = *head;
    while (cur) {
        ListNode *nxt = cur->next;
        free(cur);
        cur = nxt;
    }
    *head = NULL;
}

// ============================================================
//                     回调函数（手动扩展）
// ============================================================

/**
 * 把一元函数 f 依次应用到数组每个元素，结果写入 out（可与 arr 相同实现原地变换）
 * @param arr 输入数组
 * @param n 数组长度
 * @param f 回调函数（接收 int，返回 int）
 * @param out 输出缓冲区（长度至少 n）
 * @return 0 成功；-1 参数无效
 */
int array_map(const int *arr, int n, int (*f)(int), int *out) {
    if (!arr || !out || !f || n <= 0) return -1;
    for (int i = 0; i < n; i++) out[i] = f(arr[i]);
    return 0;
}

/**
 * 原地过滤：保留满足谓词 pred 的元素（保持原顺序），返回新长度
 * @param arr 数组（会被改写）
 * @param n 原长度
 * @param pred 谓词回调（返回非 0 表示保留）
 * @return 过滤后的长度；-1 参数无效
 */
int array_filter(int *arr, int n, int (*pred)(int)) {
    if (!arr || !pred || n < 0) return -1;
    int w = 0;
    for (int i = 0; i < n; i++)
        if (pred(arr[i])) arr[w++] = arr[i];
    return w;
}

/**
 * 归约：acc = init，然后依次 acc = f(acc, arr[i])，返回最终 acc
 * @param arr 数组
 * @param n 长度
 * @param f 二元回调（两个 int，返回 int）
 * @param init 初始值（如求和传 0、求积传 1）
 * @return 归约结果
 */
int array_reduce(const int *arr, int n, int (*f)(int, int), int init) {
    if (!arr || !f || n <= 0) return init;
    int acc = init;
    for (int i = 0; i < n; i++) acc = f(acc, arr[i]);
    return acc;
}

/**
 * 统计数组中满足谓词 pred 的元素个数
 * @param arr 数组
 * @param n 长度
 * @param pred 谓词回调
 * @return 满足条件的个数
 */
int count_if(const int *arr, int n, int (*pred)(int)) {
    if (!arr || !pred || n < 0) return 0;
    int c = 0;
    for (int i = 0; i < n; i++) if (pred(arr[i])) c++;
    return c;
}

/**
 * 遍历链表，对每个节点的数据调用回调 fn
 * @param head 链表头
 * @param fn 回调（接收 int 数据）
 */
void list_foreach(ListNode *head, void (*fn)(int)) {
    if (!fn) return;
    for (ListNode *p = head; p; p = p->next) fn(p->data);
}

/**
 * 带比较器的冒泡排序：升序/降序由 cmp 决定（cmp(a,b)<0 表示 a 排在 b 前）
 * @param arr 数组（原地排序）
 * @param n 长度
 * @param cmp 比较器回调：返回负/零/正
 */
void bubble_sort_cmp(int *arr, int n, int (*cmp)(int, int)) {
    if (!arr || !cmp || n <= 1) return;
    for (int i = 0; i < n - 1; i++)
        for (int j = 0; j < n - 1 - i; j++)
            if (cmp(arr[j], arr[j + 1]) > 0) {
                int t = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = t;
            }
}

/**
 * 带比较器的二分查找（要求数组已按 cmp 有序）
 * @param arr 有序数组
 * @param n 长度
 * @param target 目标值
 * @param cmp 比较器回调（决定序关系）
 * @return 目标索引；未找到返回 -1
 */
int binary_search_cmp(const int *arr, int n, int target, int (*cmp)(int, int)) {
    if (!arr || !cmp || n <= 0) return -1;
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        int c = cmp(arr[mid], target);
        if (c == 0) return mid;
        if (c < 0) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}

/**
 * 对数组闭区间 [lo, hi] 的每个元素应用回调 f（原地变换）
 * @param arr 数组
 * @param lo 起始下标
 * @param hi 结束下标（含）
 * @param f 回调函数
 */
void apply_to_range(int *arr, int lo, int hi, int (*f)(int)) {
    if (!arr || !f || lo > hi) return;
    for (int i = lo; i <= hi; i++) arr[i] = f(arr[i]);
}

// ============================================================
//                     变参函数（手动扩展）
// ============================================================

/**
 * 变参求和：sum_variadic(3, 1, 2, 3) == 6
 * @param count 参数个数（不含 count 本身）
 * @param ... 若干 int
 * @return 所有参数之和
 */
long long sum_variadic(int count, ...) {
    va_list ap;
    va_start(ap, count);
    long long s = 0;
    for (int i = 0; i < count; i++) s += va_arg(ap, int);
    va_end(ap);
    return s;
}

/**
 * 变参求最大值：max_variadic(4, 3, 9, 2, 7) == 9
 * @param count 参数个数
 * @param ... 若干 int
 * @return 最大值
 */
int max_variadic(int count, ...) {
    va_list ap;
    va_start(ap, count);
    int m = va_arg(ap, int);
    for (int i = 1; i < count; i++) {
        int v = va_arg(ap, int);
        if (v > m) m = v;
    }
    va_end(ap);
    return m;
}

/**
 * 变参求最小值
 * @param count 参数个数
 * @param ... 若干 int
 * @return 最小值
 */
int min_variadic(int count, ...) {
    va_list ap;
    va_start(ap, count);
    int m = va_arg(ap, int);
    for (int i = 1; i < count; i++) {
        int v = va_arg(ap, int);
        if (v < m) m = v;
    }
    va_end(ap);
    return m;
}

/**
 * 变参求平均值
 * @param count 参数个数
 * @param ... 若干 int
 * @return 平均值（double），count<=0 返回 0
 */
double avg_variadic(int count, ...) {
    va_list ap;
    va_start(ap, count);
    long long s = 0;
    for (int i = 0; i < count; i++) s += va_arg(ap, int);
    va_end(ap);
    return count > 0 ? (double)s / count : 0.0;
}

/**
 * 变参求乘积
 * @param count 参数个数
 * @param ... 若干 int
 * @return 乘积（long long）
 */
long long mul_variadic(int count, ...) {
    va_list ap;
    va_start(ap, count);
    long long p = 1;
    for (int i = 0; i < count; i++) p *= va_arg(ap, int);
    va_end(ap);
    return p;
}

/**
 * 拼接多个字符串到新分配的内存，最后一个参数传 NULL 结束
 * 示例：str_concat_va("Hello", " ", "World", NULL) -> "Hello World"
 * @param first 第一个字符串（必填）
 * @param ... 后续字符串，以 NULL 结尾
 * @return 新字符串（需 free 释放）；失败返回 NULL
 */
char* str_concat_va(const char *first, ...) {
    if (!first) return NULL;
    va_list ap;
    /* 第一遍：统计总长度（内部调用 strlen） */
    va_start(ap, first);
    size_t len = strlen(first);
    const char *s = va_arg(ap, const char*);
    while (s) { len += strlen(s); s = va_arg(ap, const char*); }
    va_end(ap);
    char *out = (char*)malloc(len + 1);
    if (!out) return NULL;
    /* 第二遍：依次拷贝（内部调用 strcpy/strcat） */
    strcpy(out, first);
    va_start(ap, first);
    s = va_arg(ap, const char*);
    while (s) { strcat(out, s); s = va_arg(ap, const char*); }
    va_end(ap);
    return out;
}

// ============================================================
//                     复合函数（手动扩展）
// ============================================================

/**
 * 有序数组去重（要求已升序，相邻重复只保留一个），返回去重后长度
 * @param arr 有序数组（会被改写）
 * @param n 原长度
 * @return 去重后长度
 */
int unique_sorted(int *arr, int n) {
    if (!arr || n <= 0) return 0;
    int w = 1;
    for (int i = 1; i < n; i++)
        if (arr[i] != arr[w - 1]) arr[w++] = arr[i];
    return w;
}

/**
 * 任意顺序数组去重：内部先排序再去重（复合调用 quick_sort + unique_sorted）
 * @param arr 数组（会被改写）
 * @param n 输入原长度，输出去重后长度
 * @return 去重后长度
 */
int remove_duplicates_array(int *arr, int *n) {
    if (!arr || !n || *n <= 0) return 0;
    quick_sort(arr, *n);            /* 复合：先排序 */
    int m = unique_sorted(arr, *n); /* 复合：再相邻去重 */
    *n = m;
    return m;
}

/**
 * 求数组的中位数：内部复制数组并排序（复合调用 quick_sort）
 * @param arr 数组
 * @param n 长度
 * @param out 输出中位数（偶数个取中间两数平均）
 * @return 0 成功；-1 参数无效或内存不足
 */
int median_of_array(const int *arr, int n, double *out) {
    if (!arr || !out || n <= 0) return -1;
    int *tmp = (int*)malloc((size_t)n * sizeof(int));
    if (!tmp) return -1;
    memcpy(tmp, arr, (size_t)n * sizeof(int));
    quick_sort(tmp, n);             /* 复合：复制后排序 */
    if (n % 2 == 1) *out = tmp[n / 2];
    else *out = (tmp[n / 2 - 1] + tmp[n / 2]) / 2.0;
    free(tmp);
    return 0;
}

/**
 * 单趟扫描同时求数组的最小值和最大值
 * @param arr 数组
 * @param n 长度
 * @param min 输出最小值
 * @param max 输出最大值
 */
void array_minmax(const int *arr, int n, int *min, int *max) {
    if (!arr || !min || !max || n <= 0) return;
    *min = *max = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] < *min) *min = arr[i];
        if (arr[i] > *max) *max = arr[i];
    }
}

/**
 * 统计数组每个值的出现次数（频次表）
 * 内部先调用 array_minmax 确定取值区间，再逐项计数（复合）
 * @param arr 数组
 * @param n 长度
 * @param freq 输出频次表（长度需 >= max-min+1，会被清零）
 * @param lo 输出取值最小值
 * @param hi 输出取值最大值
 * @return 0 成功；-1 参数无效
 */
int histogram(const int *arr, int n, int *freq, int *lo, int *hi) {
    if (!arr || !freq || !lo || !hi || n <= 0) return -1;
    int mn, mx;
    array_minmax(arr, n, &mn, &mx);   /* 复合：先求取值区间 */
    int span = mx - mn + 1;
    memset(freq, 0, (size_t)span * sizeof(int));
    for (int i = 0; i < n; i++) freq[arr[i] - mn]++;
    *lo = mn; *hi = mx;
    return 0;
}

/**
 * 求众数（出现次数最多的值，并列时返回较小的）
 * 内部复合调用 array_minmax 与 histogram 完成统计
 * @param arr 数组
 * @param n 长度
 * @param mode 输出众数
 * @return 0 成功；-1 参数无效或内存不足
 */
int mode_of_array(const int *arr, int n, int *mode) {
    if (!arr || !mode || n <= 0) return -1;
    int mn, mx;
    array_minmax(arr, n, &mn, &mx);   /* 复合：确定取值区间 */
    int span = mx - mn + 1;
    int *freq = (int*)calloc((size_t)span, sizeof(int));
    if (!freq) return -1;
    int lo, hi;
    if (histogram(arr, n, freq, &lo, &hi) != 0) { free(freq); return -1; }
    int best = lo, bestc = freq[0];
    for (int i = 1; i <= hi - lo; i++)
        if (freq[i] > bestc) { bestc = freq[i]; best = lo + i; }
    free(freq);
    *mode = best;
    return 0;
}

/**
 * 将两个升序数组合并到 out（稳定归并）
 * @param out 输出缓冲区（长度 >= na+nb）
 * @param a 第一个升序数组
 * @param na 其长度
 * @param b 第二个升序数组
 * @param nb 其长度
 * @return 合并后长度；-1 参数无效
 */
int merge_sorted_into(int *out, const int *a, int na, const int *b, int nb) {
    if (!out || (na > 0 && !a) || (nb > 0 && !b) || na < 0 || nb < 0) return -1;
    int i = 0, j = 0, k = 0;
    while (i < na && j < nb)
        out[k++] = (a[i] <= b[j]) ? a[i++] : b[j++];
    while (i < na) out[k++] = a[i++];
    while (j < nb) out[k++] = b[j++];
    return k;
}

/**
 * 求两个升序数组的交集写入 out（结果升序且无重复，归并式扫描）
 * @param a 第一个升序数组
 * @param na 其长度
 * @param b 第二个升序数组
 * @param nb 其长度
 * @param out 输出缓冲区（长度 >= min(na,nb)）
 * @return 交集长度；-1 参数无效
 */
int intersection_sorted(const int *a, int na, const int *b, int nb, int *out) {
    if (!out || (na > 0 && !a) || (nb > 0 && !b) || na < 0 || nb < 0) return -1;
    int i = 0, j = 0, k = 0;
    while (i < na && j < nb) {
        if (a[i] < b[j]) i++;
        else if (a[i] > b[j]) j++;
        else {
            if (k == 0 || out[k - 1] != a[i]) out[k++] = a[i];
            i++; j++;
        }
    }
    return k;
}


