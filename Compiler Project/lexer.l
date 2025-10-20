%{
#include "definitions.h"
#include "parser.tab.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern int yylineno;
extern FILE *yyin;
%}

%option noyywrap yylineno

DIGIT   [0-9]+
ID      [A-Za-z_][A-Za-z0-9_]*

%%
"def"       { printf("[Task 1] Line %d: %s → keyword\n", yylineno, yytext); return DEF; }
"return"    { printf("[Task 1] Line %d: %s → keyword\n", yylineno, yytext); return RETURN; }
"if"        { printf("[Task 1] Line %d: %s → keyword\n", yylineno, yytext); return IF; }
"else"      { printf("[Task 1] Line %d: %s → keyword\n", yylineno, yytext); return ELSE; }
"print"     { printf("[Task 1] Line %d: %s → keyword\n", yylineno, yytext); return PRINT; }
"end"       { printf("[Task 1] Line %d: %s → keyword\n", yylineno, yytext); return END; }

"=="        return EQ;
"!="        return NEQ;
">="        return GE;
"<="        return LE;

":"         return ':';
"("         return '(';
")"         return ')';
"="         return '=';
">"         return '>';
"<"         return '<';
"+"         return '+';
"-"         return '-';
"*"         return '*';
"/"         return '/';

{DIGIT}     { printf("[Task 1] Line %d: %s → number\n", yylineno, yytext);
               yylval.num = atoi(yytext); return NUMBER; }

{ID}        { printf("[Task 1] Line %d: %s → identifier\n", yylineno, yytext);
               yylval.s = strdup(yytext); return ID; }

[ \t\r\n]+  ;
"//".*      ;
.           { printf("Unknown symbol %s at line %d\n", yytext, yylineno); }

%%

