%{
#include <stdio.h>
#include <stdlib.h>
extern int yylineno;
%}

%option noyywrap

DIGIT   [0-9]+
ID      [A-Za-z_][A-Za-z0-9_]*
WS      [ \t]+

%%

"def"       { printf("LINE %d: KEYWORD(def)\t%s\n", yylineno, yytext); }
"return"    { printf("LINE %d: KEYWORD(return)\t%s\n", yylineno, yytext); }
"if"        { printf("LINE %d: KEYWORD(if)\t%s\n", yylineno, yytext); }
"else"      { printf("LINE %d: KEYWORD(else)\t%s\n", yylineno, yytext); }
"print"     { printf("LINE %d: KEYWORD(print)\t%s\n", yylineno, yytext); }
"end"       { printf("LINE %d: KEYWORD(end)\t%s\n", yylineno, yytext); }

"=="        { printf("LINE %d: EQ\t%s\n", yylineno, yytext); }
"!="        { printf("LINE %d: NEQ\t%s\n", yylineno, yytext); }
">="        { printf("LINE %d: GE\t%s\n", yylineno, yytext); }
"<="        { printf("LINE %d: LE\t%s\n", yylineno, yytext); }

":"         { printf("LINE %d: COLON\t%s\n", yylineno, yytext); }
","         { printf("LINE %d: COMMA\t%s\n", yylineno, yytext); }
"("         { printf("LINE %d: LPAREN\t%s\n", yylineno, yytext); }
")"         { printf("LINE %d: RPAREN\t%s\n", yylineno, yytext); }

"="         { printf("LINE %d: ASSIGN\t%s\n", yylineno, yytext); }
"+"|"-"|"*"|"/"  { printf("LINE %d: ARITH\t%s\n", yylineno, yytext); }

{DIGIT}     { printf("LINE %d: NUMBER\t%s\n", yylineno, yytext); }
{ID}        { printf("LINE %d: ID\t%s\n", yylineno, yytext); }

"\n"        { yylineno++; }
[ \t]+      { /* skip */ }
"//".*      { /* skip comment */ }
.           { printf("LINE %d: UNKNOWN\t%s\n", yylineno, yytext); }

%%
int main(int argc, char **argv) {
    if (argc>1) {
        FILE *f=fopen(argv[1],"r");
        if(!f){ perror("open"); return 1;}
        yyin=f;
    }
    yylex();
    return 0;
}
