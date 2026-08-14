/* 链表头插法示例：复制到可视化器，点击各行查看内存变化 */
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int val;
    struct Node *next;
} Node;

int main() {
    Node *head = NULL;

    Node *n1 = malloc(sizeof(Node));
    n1->val = 1;
    n1->next = NULL;
    head = n1;

    Node *n2 = malloc(sizeof(Node));
    n2->val = 2;
    n2->next = head;
    head = n2;

    Node *n3 = malloc(sizeof(Node));
    n3->val = 3;
    n3->next = head;
    head = n3;

    return 0;
}
