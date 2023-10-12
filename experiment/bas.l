%{
#include <stdlib.h>
#include <err.h>
#include "calc3.h"
#include "y.tab.h"

void yyerror(char*);
char *yylvals;
#include <string.h>

char buf[100];
char *s;

%}

%x STRING
%%

\"                  { BEGIN STRING; s = buf; }
<STRING>\\n         { *s++ = '\n'; }
<STRING>\\t         { *s++ = '\t'; }
<STRING>\\\"        { *s++ = '\"'; }
<STRING>\"          {
                    *s = 0;
                    BEGIN 0;
                    printf("found '%s'\n", buf);
                    }
<STRING>\n          { printf("invalid string"); exit(1); }
<STRING>.           { *s++ = *yytext; }

[a-z]           {
                    yylval.sIndex = *yytext - 'a';
                    return VARIABLE;
                }
[0-9]+          {
                    yylval.iValue = atoi(yytext);
                    return INTEGER;
                }

[-()<>=+*/;{}.] {
                    return *yytext;
                }

">="            return GE;
"<="            return LE;
"=="            return EQ;
"!="            return NE;
"while"         return WHILE;
"if"            return IF;
"else"          return ELSE;
"print"         return PRINT;


[ \t\n]+           ; // ignore whitespace

.               yyerror("Unknown character");

%%

int yywrap(void){
    return 1;
}

// int main(int argc, char* argv[]) {
//     yyin = fopen(argv[1], "r");
//     yylex();
//     fclose(yyin);
// }