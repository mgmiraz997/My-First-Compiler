#ifndef DEFINITIONS_H
#define DEFINITIONS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---------- AST Node ---------- */
typedef struct Node {
    char *kind;
    char *val;
    struct Node *left, *right;
} Node;

/* ---------- Node Constructor ---------- */
static inline Node* newnode(const char *kind, const char *val, Node *left, Node *right) {
    Node *n = malloc(sizeof(Node));
    n->kind = strdup(kind);
    n->val = val ? strdup(val) : NULL;
    n->left = left;
    n->right = right;
    return n;
}

#endif

