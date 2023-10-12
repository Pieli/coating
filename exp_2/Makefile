all:
	yacc -d bas.y # creates y.tab.h, y.tab.c
	lex bas.l     # creates lex.yy.c
	cc lex.yy.c y.tab.c -o bas
	# cc lex.yy.c

lex:
	lex bas.l
	cc lex.yy.c -o bas
