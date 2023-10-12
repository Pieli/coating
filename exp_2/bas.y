%{
#include <stdio.h>
#include <string.h>

extern int yylex();
void yyerror(char *s);

typedef struct tag_info {
  char *name;
  int start_pos;
  int end_pos;
} tag_info;

tag_info tags[100];
int tag_count = 0;

%}
