%{
#include<stdio.h>
#include <string.h>
#include "y.tab.h"
#include "types.h"

void yyerror(char*);

#define YYSTYPE char*
char *text;

%}


%token TAG
%token INNER_TEXT


%%

"<[^>]*>"       {
                  yylval = strdup(yytext);
                  return TAG;
                }

[^<]+           {
                  yylval = strdup(yytext);
                  return INNER_TEXT;
                }

%%

int yywrap(){}

/* Driver code */
// int main()
// {
//
//     yylex();
//     return 0;
// }
