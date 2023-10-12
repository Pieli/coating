nodeType*
con(int value)
{
  nodeType* p;
  /* allocate node */
  if ((p = malloc(sizeof(conNodeType))) == NULL)
    yyerror("out of memory");
  /* copy information */
  p->type = typeCon;
  p->con.value = value;
  return p;
}

nodeType*
id(int i)
{
  nodeType* p;
  /* allocate node */
  if ((p = malloc(sizeof(idNodeType))) == NULL)
    yyerror("out of memory");
  /* copy information */
  p->type = typeId;
  p->id.i = i;
  return p;
}

nodeType*
opr(int oper, int nops, ...)
{
  va_list ap;
  nodeType* p;
  size_t size;
  int i;
  /* allocate node */
  size = sizeof(oprNodeType) + (nops - 1) * sizeof(nodeType*);
  if ((p = malloc(size)) == NULL)
    yyerror("out of memory");
  /* copy information */
  p->type = typeOpr;
  p->opr.oper = oper;
  p->opr.nops = nops;
  va_start(ap, nops);
  for (i = 0; i < nops; i++)
    p->opr.op[i] = va_arg(ap, nodeType*);
  va_end(ap);
  return p;
}

void
freeNode(nodeType* p)
{
  int i;
  if (!p)
    return;
  if (p->type == typeOpr) {
    for (i = 0; i < p->opr.nops; i++)
      freeNode(p->opr.op[i]);
  }
  free(p);
}
void
yyerror(char* s)
{
  fprintf(stdout, "%s\n", s);
}
int
main(void)
{
  yyparse();
  return 0;
}
