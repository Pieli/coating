%{
#include <stdio.h>
#include <string.h>
#include "types.h"

extern int yylex();
void yyerror(char *s);

tag_info tags[100];
int tag_count = 0;

%}

%token TAG
%token INNER_TEXT

%type <text> tag_info
%type <text> text_info

%%

document:
  | tag_info text_info

tag_info:
  TAG {
    if (yytext[1] == '/') {
      // closing tag
      char *name = strdup(yytext + 2);
      name[strlen(name) - 1] = '\0';
      int i;
      for (i = tag_count - 1; i >= 0; i--) {
        if (strcmp(tags[i].name, name) == 0) {
          tags[i].end_pos = yylloc.first_column;
          break;
        }
      }
    } else {
      // opening tag
      char *name = strdup(yytext + 1);
      name[strlen(name) - 1] = '\0';
      tags[tag_count].name = name;
      tags[tag_count].start_pos = yylloc.first_column;
      tag_count++;
    }
  }

text_info:
  INNER_TEXT { /* do nothing */ }

%%

int main(int argc, char *argv[]) {
  yyparse();
  int i;
  for (i = 0; i < tag_count; i++) {
    printf("TAG: %s, start_pos: %d, end_pos: %d\n", tags[i].name, tags[i].start_pos, tags[i].end_pos);
  }
  return 0;
}
