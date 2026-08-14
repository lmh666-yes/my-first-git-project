/* 高级函数测试：回调函数 / 变参函数 / 复合函数 */
#include <stdio.h>
#include <stdlib.h>
#include "utils.h"

static int failures = 0;
#define CHECK(cond, msg) do { if (cond) { printf("  [PASS] %s\n", msg); } else { printf("  [FAIL] %s\n", msg); failures++; } } while (0)

/* ---- 回调辅助函数 ---- */
static int twice(int x) { return x * 2; }
static int square(int x) { return x * x; }
static int my_even(int x) { return x % 2 == 0; }
static int add_all(int a, int b) { return a + b; }
static int mul_all(int a, int b) { return a * b; }
static int cmp_asc(int a, int b) { return a - b; }
static int cmp_desc(int a, int b) { return b - a; }
static void collect(int x) { printf("    [list_foreach] %d\n", x); }

static int arr_eq(const int *a, const int *b, int n) {
    for (int i = 0; i < n; i++) if (a[i] != b[i]) return 0;
    return 1;
}

int main(void) {
    int a[6] = {1, 2, 3, 4, 5, 6};

    printf("== 回调函数 ==\n");
    int out[6] = {0};
    CHECK(array_map(a, 6, twice, out) == 0 && arr_eq(out, (int[]){2,4,6,8,10,12}, 6), "array_map 翻倍");
    CHECK(array_map(a, 6, square, out) == 0 && arr_eq(out, (int[]){1,4,9,16,25,36}, 6), "array_map 平方");
    CHECK(array_map(a, 6, twice, a) == 0 && arr_eq(a, (int[]){2,4,6,8,10,12}, 6), "array_map 原地变换");
    int src[6] = {1, 2, 3, 4, 5, 6};
    CHECK(array_filter(src, 6, my_even) == 3 && arr_eq(src, (int[]){2,4,6}, 3), "array_filter 过滤偶数");
    CHECK(array_reduce(src, 3, add_all, 0) == 12, "array_reduce 求和");
    CHECK(array_reduce(src, 3, mul_all, 1) == 48, "array_reduce 求积");
    CHECK(count_if(src, 3, my_even) == 3, "count_if 全为偶数");
    int mix[5] = {1, 3, 4, 6, 7};
    CHECK(count_if(mix, 5, my_even) == 2, "count_if 偶数个数");

    ListNode *h = NULL;
    for (int i = 4; i >= 1; i--) list_insert_head(&h, i);
    printf("    [list_foreach] 遍历 1-2-3-4:\n");
    list_foreach(h, collect);
    list_free(&h);

    int b[6] = {5, 1, 4, 2, 3, 0};
    bubble_sort_cmp(b, 6, cmp_asc);
    CHECK(arr_eq(b, (int[]){0,1,2,3,4,5}, 6), "bubble_sort_cmp 升序");
    bubble_sort_cmp(b, 6, cmp_desc);
    CHECK(arr_eq(b, (int[]){5,4,3,2,1,0}, 6), "bubble_sort_cmp 降序");
    int sorted[6] = {1, 3, 5, 7, 9, 11};
    CHECK(binary_search_cmp(sorted, 6, 7, cmp_asc) == 3, "binary_search_cmp 命中");
    CHECK(binary_search_cmp(sorted, 6, 8, cmp_asc) == -1, "binary_search_cmp 未命中");
    int r[8] = {10, 20, 30, 40, 50, 60, 70, 80};
    apply_to_range(r, 1, 3, twice);
    CHECK(arr_eq(r, (int[]){10,40,60,80,50,60,70,80}, 8), "apply_to_range 区间翻倍");

    printf("== 变参函数 ==\n");
    CHECK(sum_variadic(4, 1, 2, 3, 4) == 10, "sum_variadic 1+2+3+4=10");
    CHECK(sum_variadic(0) == 0, "sum_variadic 空=0");
    CHECK(max_variadic(5, 3, 9, 2, 7, 5) == 9, "max_variadic =9");
    CHECK(min_variadic(5, 3, 9, 2, 7, 5) == 2, "min_variadic =2");
    double av = avg_variadic(4, 1, 2, 3, 4);
    CHECK(av > 2.49 && av < 2.51, "avg_variadic 1,2,3,4=2.5");
    CHECK(mul_variadic(4, 2, 3, 4, 5) == 120, "mul_variadic 2*3*4*5=120");
    char *cs = str_concat_va("Hello", " ", "World", "!", NULL);
    CHECK(cs && strcmp(cs, "Hello World!") == 0, "str_concat_va 拼接");
    free(cs);

    printf("== 复合函数 ==\n");
    int u[8] = {1, 1, 2, 2, 2, 3, 3, 4};
    CHECK(unique_sorted(u, 8) == 4 && arr_eq(u, (int[]){1,2,3,4}, 4), "unique_sorted 有序去重");
    int d[8] = {3, 1, 2, 1, 3, 2, 5, 1};
    int dn = 8;
    CHECK(remove_duplicates_array(d, &dn) == 4 && dn == 4, "remove_duplicates_array 去重后4个");
    int dv[4]; for (int i = 0; i < dn; i++) dv[i] = d[i];
    CHECK(arr_eq(dv, (int[]){1,2,3,5}, 4), "remove_duplicates_array 内容正确");
    double med;
    int m1[5] = {5, 3, 1, 4, 2};
    CHECK(median_of_array(m1, 5, &med) == 0 && med == 3.0, "median_of_array 奇数=3");
    int m2[4] = {4, 1, 3, 2};
    CHECK(median_of_array(m2, 4, &med) == 0 && med > 2.49 && med < 2.51, "median_of_array 偶数=2.5");
    int mn, mx;
    int mm[6] = {3, -1, 7, 0, 5, 2};
    array_minmax(mm, 6, &mn, &mx);
    CHECK(mn == -1 && mx == 7, "array_minmax min=-1 max=7");
    int freq[9];
    int lo, hi;
    CHECK(histogram(mm, 6, freq, &lo, &hi) == 0 && lo == -1 && hi == 7, "histogram 区间[-1,7]");
    int hsum = 0; for (int i = 0; i <= hi - lo; i++) hsum += freq[i];
    CHECK(hsum == 6, "histogram 频次和=6");
    int hc[8] = {2, 3, 2, 4, 3, 2, 5, 4};
    int mode;
    CHECK(mode_of_array(hc, 8, &mode) == 0 && mode == 2, "mode_of_array 众数=2");
    int tie[6] = {1, 1, 2, 2, 3, 4};
    CHECK(mode_of_array(tie, 6, &mode) == 0 && mode == 1, "mode_of_array 并列取小=1");
    int A[4] = {1, 3, 5, 7}, B[4] = {2, 3, 6, 8};
    int merged[8];
    CHECK(merge_sorted_into(merged, A, 4, B, 4) == 8 && arr_eq(merged, (int[]){1,2,3,3,5,6,7,8}, 8), "merge_sorted_into 归并");
    int inter[4];
    CHECK(intersection_sorted(A, 4, B, 4, inter) == 1 && inter[0] == 3, "intersection_sorted 交集={3}");

    printf("\n===== 结果: %s =====\n", failures == 0 ? "全部通过" : "有失败");
    return failures;
}
