/* 链表进阶 + 循环链表 测试 */
#include <stdio.h>
#include "utils.h"

static int failures = 0;
#define CHECK(cond, msg) do { if (cond) { printf("  [PASS] %s\n", msg); } else { printf("  [FAIL] %s\n", msg); failures++; } } while (0)

/* 构造 1->2->3->4->5 */
static ListNode* build12345(void) {
    ListNode *h = NULL;
    int a[] = {5, 4, 3, 2, 1};
    for (int i = 0; i < 5; i++) list_insert_head(&h, a[i]);
    return h;
}

int main(void) {
    printf("== list_get_middle ==\n");
    ListNode *h = build12345();
    CHECK(list_get_middle(h)->data == 3, "1-2-3-4-5 中间是 3");
    list_free(&h);
    ListNode *h2 = NULL;
    for (int i = 4; i >= 1; i--) list_insert_head(&h2, i);   /* 1-2-3-4 */
    CHECK(list_get_middle(h2)->data == 3, "1-2-3-4 中间是 3(靠后)");
    list_free(&h2);

    printf("== list_find_kth_from_end ==\n");
    h = build12345();
    CHECK(list_find_kth_from_end(h, 2)->data == 4, "倒数第2个是 4");
    CHECK(list_find_kth_from_end(h, 5)->data == 1, "倒数第5个是 1");
    CHECK(list_find_kth_from_end(h, 6) == NULL, "倒数第6个为 NULL");
    list_free(&h);

    printf("== list_remove_duplicates ==\n");
    ListNode *d = NULL;
    int arr[] = {1, 1, 2, 3, 3, 3};
    for (int i = 5; i >= 0; i--) list_insert_head(&d, arr[i]);
    int rm = list_remove_duplicates(&d);
    CHECK(rm == 3, "删除 3 个重复节点");
    CHECK(list_length(d) == 3, "去重后长度 3");
    CHECK(d->data == 1 && d->next->data == 2 && d->next->next->data == 3, "去重后 1-2-3");
    list_free(&d);

    printf("== list_is_palindrome ==\n");
    ListNode *p = NULL;
    int pa[] = {1, 2, 2, 1};
    for (int i = 3; i >= 0; i--) list_insert_head(&p, pa[i]);
    CHECK(list_is_palindrome(p) == 1, "1-2-2-1 是回文");
    list_free(&p);
    p = NULL;
    int pb[] = {1, 2, 3};
    for (int i = 2; i >= 0; i--) list_insert_head(&p, pb[i]);
    CHECK(list_is_palindrome(p) == 0, "1-2-3 不是回文");
    list_free(&p);
    p = NULL;
    list_insert_head(&p, 7);
    CHECK(list_is_palindrome(p) == 1, "单节点是回文");
    list_free(&p);

    printf("== list_insert_at / list_delete_at ==\n");
    ListNode *t = NULL;
    CHECK(list_insert_at(&t, 0, 1) == 0, "在空链表 pos0 插入");
    CHECK(list_insert_at(&t, 1, 3) == 0, "pos1 插入 3");
    CHECK(list_insert_at(&t, 1, 2) == 0, "pos1 插入 2 → 1-2-3");
    CHECK(t->data == 1 && t->next->data == 2 && t->next->next->data == 3, "链表为 1-2-3");
    CHECK(list_insert_at(&t, 99, 9) == -1, "越界插入返回 -1");
    CHECK(list_delete_at(&t, 1) == 0, "删除 pos1 → 1-3");
    CHECK(t->data == 1 && t->next->data == 3, "删除后 1-3");
    CHECK(list_delete_at(&t, 0) == 0 && t->data == 3, "删除 pos0 → 3");
    CHECK(list_delete_at(&t, 5) == -1, "越界删除返回 -1");
    list_free(&t);

    printf("== 循环链表 ==\n");
    ListNode *c = NULL;
    c = clist_create(10);
    CHECK(c != NULL && c->next == c, "clist_create 单节点指向自身");
    CHECK(clist_length(c) == 1, "循环长度 1");
    CHECK(clist_append(&c, 20) == 0, "尾追加 20");
    CHECK(clist_insert_head(&c, 5) == 0, "头插 5");
    CHECK(clist_length(c) == 3, "循环长度 3");
    CHECK(c->data == 5, "循环头是 5");
    /* 5->10->20->(back to 5) */
    CHECK(c->next->data == 10 && c->next->next->data == 20 && c->next->next->next == c, "循环链 5-10-20 结构正确");
    CHECK(clist_remove_value(&c, 10) == 0, "删除 10");
    CHECK(clist_length(c) == 2, "删除后长度 2");
    CHECK(clist_remove_value(&c, 99) == -1, "删除不存在的返回 -1");
    CHECK(clist_remove_value(&c, 5) == 0 && c->data == 20, "删除头节点 5, 新头 20");
    clist_free(&c);
    CHECK(c == NULL, "clist_free 置 NULL");

    printf("\n===== 结果: %s =====\n", failures == 0 ? "全部通过" : "有失败");
    return failures;
}
