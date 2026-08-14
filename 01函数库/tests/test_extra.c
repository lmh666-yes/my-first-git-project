/* 临时测试: 验证手动扩展区新增函数的正确性 */
#include <stdio.h>
#include "utils.h"

static int failures = 0;
#define CHECK(cond, msg) do { if (cond) { printf("  [PASS] %s\n", msg); } else { printf("  [FAIL] %s\n", msg); failures++; } } while (0)

int main(void) {
    printf("== 并查集 ==\n");
    UnionFind *uf = uf_create(6);
    CHECK(uf != NULL, "uf_create 创建成功");
    CHECK(uf_find(uf, 3) == 3, "uf_find 初始根为自身");
    CHECK(uf_union(uf, 0, 1) == 0, "uf_union(0,1)");
    CHECK(uf_union(uf, 1, 2) == 0, "uf_union(1,2)");
    CHECK(uf_connected(uf, 0, 2) == 1, "0 与 2 连通");
    CHECK(uf_connected(uf, 0, 3) == 0, "0 与 3 不连通");
    CHECK(uf_union(uf, 0, 2) == 1, "重复合并返回 1");
    uf_destroy(uf);
    printf("== lower/upper_bound ==\n");
    int a1[] = {1, 3, 3, 5, 7};
    CHECK(lower_bound(a1, 5, 3) == 1, "lower_bound(3)==1");
    CHECK(upper_bound(a1, 5, 3) == 3, "upper_bound(3)==3");
    CHECK(lower_bound(a1, 5, 6) == 4, "lower_bound(6)==4");
    CHECK(upper_bound(a1, 5, 7) == 5, "upper_bound(7)==5");
    printf("== 逆序对 ==\n");
    int a2[] = {3, 1, 2};
    CHECK(count_inversions(a2, 3) == 2, "count_inversions({3,1,2})==2");
    int a3[] = {1, 3, 2, 4, 5};
    CHECK(count_inversions(a3, 5) == 1, "count_inversions({1,3,2,4,5})==1");
    printf("== 滑动窗口最大值 ==\n");
    int a4[] = {1, 3, -1, -3, 5, 3, 6, 7};
    int out[8];
    int nw = sliding_window_max(a4, 8, 3, out);
    CHECK(nw == 6, "窗口个数==6");
    CHECK(out[0]==3 && out[1]==3 && out[2]==5 && out[3]==5 && out[4]==6 && out[5]==7, "滑动窗口最大值序列正确");
    printf("== 两数之和 ==\n");
    int a5[] = {2, 7, 11, 15};
    int i1, i2;
    CHECK(two_sum(a5, 4, 9, &i1, &i2) == 1 && a5[i1] + a5[i2] == 9, "two_sum 找到 2+7=9");
    CHECK(two_sum(a5, 4, 100, &i1, &i2) == 0, "two_sum 未找到返回 0");
    printf("== 字母异位词 ==\n");
    CHECK(is_anagram("listen", "silent") == 1, "listen/silent 是异位词");
    CHECK(is_anagram("abc", "abd") == 0, "abc/abd 不是");
    printf("== 最长公共子序列 ==\n");
    CHECK(str_lcs("abcde", "ace") == 3, "LCS(abcde,ace)==3");
    CHECK(str_lcs("abc", "def") == 0, "LCS(abc,def)==0");
    printf("== 数论 ==\n");
    CHECK(is_perfect_square(16) == 1 && is_perfect_square(15) == 0, "16 是完全平方,15 不是");
    CHECK(is_ugly(6) == 1 && is_ugly(14) == 0, "6 是丑数,14 不是");
    CHECK(count_primes(10) == 4, "[2,10] 素数个数==4");
    CHECK(count_primes(2) == 1, "[2,2] 素数个数==1");
    printf("== 拓扑排序 ==\n");
    Graph *g = graph_create(5);
    graph_add_edge_dir(g, 0, 1);
    graph_add_edge_dir(g, 0, 2);
    graph_add_edge_dir(g, 1, 3);
    graph_add_edge_dir(g, 2, 3);
    graph_add_edge_dir(g, 3, 4);
    int order[5];
    int nc = topological_sort(g, order);
    CHECK(nc == 5, "拓扑排序节点数==5");
    if (nc == 5) {
        /* 验证每条边 u->v 在 order 中 u 在 v 前 */
        int pos[5];
        for (int i = 0; i < 5; i++) pos[order[i]] = i;
        int ok = 1;
        ok = ok && pos[0] < pos[1] && pos[0] < pos[2] && pos[1] < pos[3] && pos[2] < pos[3] && pos[3] < pos[4];
        CHECK(ok, "拓扑序满足所有边的先后关系");
    }
    /* 环检测（有向边 4 -> 0） */
    graph_add_edge_dir(g, 4, 0);
    CHECK(topological_sort(g, order) == -1, "含环时返回 -1");
    graph_destroy(g);
    printf("== Prim 最小生成树 ==\n");
    Graph *g2 = graph_create(4);
    graph_add_edge(g2, 0, 1); graph_add_edge(g2, 1, 0);
    graph_add_edge(g2, 0, 2); graph_add_edge(g2, 2, 0);
    graph_add_edge(g2, 1, 2); graph_add_edge(g2, 2, 1);
    graph_add_edge(g2, 1, 3); graph_add_edge(g2, 3, 1);
    graph_add_edge(g2, 2, 3); graph_add_edge(g2, 3, 2);
    graph_add_edge(g2, 0, 3); graph_add_edge(g2, 3, 0);
    int mst = prim_mst(g2);
    CHECK(mst == 3, "4 节点全连通图最小生成树权值和==3(每条边权1)");
    graph_destroy(g2);
    printf("== 宏 ==\n");
    CHECK(UTILS_CLAMP(15, 0, 10) == 10 && UTILS_CLAMP(-5, 0, 10) == 0 && UTILS_CLAMP(5, 0, 10) == 5, "UTILS_CLAMP 正确");
    int x = 3, y = 8;
    UTILS_SWAP(x, y, int);
    CHECK(x == 8 && y == 3, "UTILS_SWAP 正确");
    CHECK(UTILS_IS_EVEN(4) == 1 && UTILS_IS_ODD(3) == 1, "IS_EVEN/IS_ODD 正确");
    CHECK(UTILS_IS_POW2(16) == 1 && UTILS_IS_POW2(12) == 0, "IS_POW2 正确");
    CHECK(UTILS_SIGN(-7) == -1 && UTILS_SIGN(0) == 0 && UTILS_SIGN(9) == 1, "SIGN 正确");
    CHECK(UTILS_MAX3(1, 5, 3) == 5 && UTILS_MIN3(1, 5, 3) == 1, "MAX3/MIN3 正确");
    CHECK(UTILS_DIV_CEIL(10, 3) == 4, "DIV_CEIL 正确");
    CHECK(UTILS_ALIGN_UP(13, 4) == 16 && UTILS_ALIGN_DOWN(13, 4) == 12, "ALIGN 正确");
    unsigned int b = 0;
    UTILS_SET_BIT(b, 3);
    CHECK(b == 8 && UTILS_GET_BIT(b, 3) == 1, "SET/GET_BIT 正确");
    UTILS_CLEAR_BIT(b, 3);
    CHECK(b == 0, "CLEAR_BIT 正确");
    UTILS_TOGGLE_BIT(b, 2);
    CHECK(b == 4, "TOGGLE_BIT 正确");
    CHECK(UTILS_SQUARE(6) == 36, "SQUARE 正确");

    printf("\n===== 结果: %s =====\n", failures == 0 ? "全部通过" : "有失败");
    return failures;
}
