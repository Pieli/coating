%{
#include <stdlib.h>
#include "y.tab.h"
#include <err.h>

void yyerror(char*);
char *yylvals;
#include <string.h>

char buf[100];
char *s;

%}

%x CONTENT_STRING

%%

[^<]                            { BEGIN CONTENT_STRING; s = buf; }
<CONTENT_STRING>\\n             { *s++ = '\n'; }
<CONTENT_STRING>\\t             { *s++ = '\t'; }
<CONTENT_STRING>>               {
                                  *s = 0;
                                  BEGIN 0;
                                  printf("found '%s'\n", buf);
                                }
<CONTENT_STRING>\n              { printf("invalid string"); exit(1); }
<CONTENT_STRING>.               { *s++ = *yytext; }


"<>"            return TAG_START;
"</>"           return TAG_END;


[ \t\n]+        ; // ignore whitespace

.               {
                        return *yytext;
                }

%%

int yywrap(void){
    return 1;
}

int main(int argc, char* argv[]) {
    yyin = fopen(argv[1], "r");
    yylex();
    fclose(yyin);
}
