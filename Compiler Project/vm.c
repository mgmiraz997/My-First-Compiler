// vm.c - very small interpreter for our pseudo-assembly (not full ARM)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_LINES 2000
#define MAX_VARS 1024

char *lines[MAX_LINES];
int nlines=0;

typedef struct Var { char name[64]; int val; } Var;
Var vars[MAX_VARS];
int nvars=0;

int find_var(const char *name){
    for(int i=0;i<nvars;i++) if(!strcmp(vars[i].name,name)) return i;
    return -1;
}
int add_var(const char *name){
    int idx = find_var(name);
    if(idx>=0) return idx;
    strcpy(vars[nvars].name,name);
    vars[nvars].val = 0;
    return nvars++;
}

int is_label_line(const char *s){
    const char *p = strchr(s,':');
    if(!p) return 0;
    // label at start
    return (p == s + strlen(s) - strlen(p));
}

int main(int argc, char **argv){
    if(argc<2){ printf("Usage: vm out.s\n"); return 1; }
    FILE *f = fopen(argv[1],"r");
    if(!f){ perror("open"); return 1; }
    char buf[512];
    while(fgets(buf,sizeof(buf),f)){
        lines[nlines++]=strdup(buf);
    }
    fclose(f);

    // read data section to collect variables
    int data_start = -1;
    for(int i=0;i<nlines;i++){
        if(strstr(lines[i],".data")) data_start = i;
        if(data_start!=-1 && strstr(lines[i],".word")){
            char name[64]; int val;
            if(sscanf(lines[i], " %63s : .word %d", name, &val)==2){
                int id = add_var(name);
                vars[id].val = val;
            } else {
                // try alternative parse
                char *colon = strchr(lines[i],':');
                if(colon){
                    char nm[64];
                    strncpy(nm, lines[i], colon - lines[i]);
                    nm[colon-lines[i]] = 0;
                    // no value provided
                    add_var(nm);
                }
            }
        }
    }

    // build label map
    int label_pos = 0;
    typedef struct Lab { char name[64]; int idx; } Lab;
    Lab labs[1024]; int nlabs=0;
    for(int i=0;i<nlines;i++){
        char name[64];
        if(sscanf(lines[i], " %63[^:]:", name)==1){
            strcpy(labs[nlabs].name, name);
            labs[nlabs].idx = i;
            nlabs++;
        }
    }

    // small stack of registers R0..R12
    int R[16] = {0};

    // interpreter loop (very small subset)
    int ip = 0;
    while(ip < nlines){
        char op[64], a[128], b[128], c[128];
        op[0]=a[0]=b[0]=c[0]=0;
        int res = sscanf(lines[ip], " %63s %127s %127s %127s", op,a,b,c);

        if(op[0]==';' || strchr(lines[ip],'.')){ ip++; continue; } // comments or directives
        if(op[strlen(op)-1]==':'){ ip++; continue; } // label

        if(strcmp(op,"MOV")==0){
            // MOV Rn, #imm  or MOV Rn, Rm
            if(a[0]=='R' && b[0]=='#'){
                int rn = atoi(a+1);
                int imm = atoi(b+1);
                R[rn] = imm;
            } else if(a[0]=='R' && b[0]=='R'){
                int rn=atoi(a+1), rm=atoi(b+1);
                R[rn] = R[rm];
            } else if(a[0]=='R' && b[0]=='='){ // LDR Rn, =var handled as next lines LDR and STR in conversion are simple and we skip
                // ignore
            }
            ip++;
            continue;
        } else if(strcmp(op,"LDR")==0){
            // LDR Rn, =name OR LDR Rn, [Rk] -> we handle only LDR Rn, =name (load address)
            if(a[0]=='R' && b[0]=='='){
                // LDR Rn, =name -> store index of variable name into Rn as address index
                int rn = atoi(a+1);
                char varname[64];
                strcpy(varname, b+1);
                // remove potential newline or trailing
                char *p = varname;
                while(*p && !isspace((unsigned char)*p) && *p!='\n' && *p!='\r') p++;
                *p = 0;
                int id = find_var(varname);
                if(id<0) id = add_var(varname);
                R[rn] = id; // store index as "address"
            } else if(a[0]=='R' && b[0]=='['){
                // LDR Rn, [Rk] we implement as Rn = vars[ Rk ]
                // pattern "[Rk]"
                char *p = strchr(b,'R');
                if(p){
                    int rk = atoi(p+1);
                    int id = R[rk];
                    R[atoi(a+1)] = vars[id].val;
                }
            }
            ip++;
            continue;
        } else if(strcmp(op,"STR")==0){
            // STR Rn, [Rk] -> store Rn value into vars[ Rk ]
            if(a[0]=='R' && b[0]=='['){
                char *p = strchr(b,'R');
                if(p){
                    int rk = atoi(p+1);
                    int id = R[rk];
                    int rn = atoi(a+1);
                    vars[id].val = R[rn];
                }
            }
            ip++;
            continue;
        } else if(strcmp(op,"ADD")==0 || strcmp(op,"SUB")==0 || strcmp(op,"MUL")==0 || strcmp(op,"SDIV")==0){
            // ADD R3, R1, R2  etc.
            int rd = atoi(op[3]) ; // naive, not used
            // fallback parse to use R[1] and R[2]
            if(strcmp(op,"ADD")==0) R[3] = R[1] + R[2];
            if(strcmp(op,"SUB")==0) R[3] = R[1] - R[2];
            if(strcmp(op,"MUL")==0) R[3] = R[1] * R[2];
            if(strcmp(op,"SDIV")==0) R[3] = R[1] / (R[2]?R[2]:1);
            ip++;
            continue;
        } else if(strcmp(op,"CMP")==0){
            // CMP R1, #10 -> set R15 as flag storing R1 - imm
            int r1 = atoi(a+1);
            int imm = atoi(b+1);
            R[15] = R[r1] - imm;
            ip++;
            continue;
        } else if(strcmp(op,"BGT")==0 || strcmp(op,"BGE")==0 || strcmp(op,"BLT")==0 || strcmp(op,"BLE")==0 || strcmp(op,"BEQ")==0 || strcmp(op,"BNE")==0 || strcmp(op,"B")==0){
            char *label = a;
            int jump=0;
            if(strcmp(op,"B")==0) jump=1;
            else if(strcmp(op,"BEQ")==0 && R[15]==0) jump=1;
            else if(strcmp(op,"BNE")==0 && R[15]!=0) jump=1;
            else if(strcmp(op,"BGT")==0 && R[15]>0) jump=1;
            else if(strcmp(op,"BLT")==0 && R[15]<0) jump=1;
            else if(strcmp(op,"BGE")==0 && R[15]>=0) jump=1;
            else if(strcmp(op,"BLE")==0 && R[15]<=0) jump=1;
            if(jump){
                // find label
                int found = -1;
                for(int i=0;i<nlabs;i++) if(!strcmp(labs[i].name,label)) { found = labs[i].idx; break; }
                if(found>=0) { ip = found + 1; continue; }
            }
            ip++;
            continue;
        } else if(strcmp(op,";")==0){
            ip++; continue;
        } else {
            ip++;
        }
    }

    // print vars to show runtime values
    printf("\n--- VM variable values ---\n");
    for(int i=0;i<nvars;i++){
        printf("%s = %d\n", vars[i].name, vars[i].val);
    }
    return 0;
}
