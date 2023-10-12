%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define YYSTYPE char *

extern int yylex();
extern int yylineno;
extern char *yytext;

void yyerror(char const *s) {
    fprintf(stderr, "line %d: %s\n", yylineno, s);
}

struct tag {
    char *name;
    char *text;
};

struct tag_stack {
    struct tag *tag;
    struct tag_stack *next;
};

struct tag_stack *stack = NULL;

void push_tag(struct tag *t) {
    struct tag_stack *node = malloc(sizeof(struct tag_stack));
    node->tag = t;
    node->next = stack;
    stack = node;
}

struct tag *pop_tag() {
    struct tag_stack *node = stack;
    stack = node->next;
    struct tag *tag = node->tag;
    free(node);
    return tag;
}

%}

%token TAG_START
%token TAG_END
%token TEXT

%%

input:
    | input tag
    ;

tag:
    | TAG_START expr TAG_END    { puts("Hello");}
    | expr
    ;

%%

int main() {
}

int yywrap() {
    return 1;
}

int yylex() {
}
