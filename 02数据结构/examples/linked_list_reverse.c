/* 链表反转示例：点击 while 循环里的每一行，观察 prev/cur/nxt 三个指针如何移动 */
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int val;
    struct Node *next;
} Node;

int main() {
    Node *head = NULL;
    Node *a = malloc(sizeof(Node)); a->val = 1; a->next = NULL;
    Node *b = malloc(sizeof(Node)); b->val = 2; b->next = NULL;
    Node *c = malloc(sizeof(Node)); c->val = 3; c->next = NULL;
    head = a;
    a->next = b;
    b->next = c;

    Node *prev = NULL;
    Node *cur = head;
    while (cur) {
        Node *nxt = cur->next;
        cur->next = prev;
        prev = cur;
        cur = nxt;
    }
    head = prev;
    return 0;
}
