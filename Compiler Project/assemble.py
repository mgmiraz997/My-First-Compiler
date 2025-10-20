#!/usr/bin/env python3
import sys, re
from collections import OrderedDict

def is_num(s): return re.match(r'^-?\d+$', s) is not None

def read_tac(fn):
    with open(fn) as f:
        return [l.strip() for l in f if l.strip()]

def gather_vars(tac):
    vars = OrderedDict()
    for l in tac:
        # match var names (left of '=' or args)
        m = re.match(r'^([A-Za-z_]\w*)\s*=', l)
        if m:
            vars[m.group(1)] = 0
        for tok in re.findall(r'\b([A-Za-z_]\w*)\b', l):
            if not tok.startswith('t') and not tok in ('ifFalse','goto','print','ret'):
                vars[tok] = 0
    return list(vars.keys())

def to_asm(tac_lines, outname):
    vars = gather_vars(tac_lines)
    asm=[]
    regmap = {}  # map temps and vars to pseudo registers when needed
    nextr = 0

    def load_operand(op):
        if is_num(op):
            asm.append(f"    MOV R12, #{op}")
            return "R12"
        if op.startswith('t'):
            reg = f"R{10 + int(op[1:])%6}"  # quick mapping for temps
            asm.append(f"    LDR {reg}, ={op}") # temps stored as labels
            return reg
        # variable
        reg = f"R0"
        asm.append(f"    LDR R0, ={op}")
        asm.append(f"    LDR R0, [R0]")
        return "R0"

    label_count=0
    # prologue
    asm.append("\t.text")
    asm.append("\t.global _start")
    asm.append("_start:")

    for l in tac_lines:
        # comment original TAC
        asm.append(f"\t; {l}")
        # patterns
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*|-?\d+)\s*([\+\-\*\/<>!=]{1,2})\s*([A-Za-z_]\w*|-?\d+)$', l)
        if m:
            dest,a,op,b = m.group(1),m.group(2),m.group(3),m.group(4)
            # load a into R1, b into R2
            if is_num(a):
                asm.append(f"    MOV R1, #{a}")
            else:
                asm.append(f"    LDR R1, ={a}")
                asm.append(f"    LDR R1, [R1]")
            if is_num(b):
                asm.append(f"    MOV R2, #{b}")
            else:
                asm.append(f"    LDR R2, ={b}")
                asm.append(f"    LDR R2, [R2]")
            # map op to instruction or CMP+Bxx
            if op == '+':
                asm.append("    ADD R3, R1, R2")
                asm.append(f"    LDR R4, ={dest}")
                asm.append("    STR R3, [R4]")
            elif op == '-':
                asm.append("    SUB R3, R1, R2")
                asm.append(f"    LDR R4, ={dest}")
                asm.append("    STR R3, [R4]")
            elif op == '*':
                asm.append("    MUL R3, R1, R2")
                asm.append(f"    LDR R4, ={dest}")
                asm.append("    STR R3, [R4]")
            elif op == '/':
                asm.append("    SDIV R3, R1, R2")
                asm.append(f"    LDR R4, ={dest}")
                asm.append("    STR R3, [R4]")
            elif op in ('>','<','==','!=','>=','<='):
                # compute comparison to R3 = (a op b) as 1/0
                asm.append("    CMP R1, R2")
                lab_true = f"LBL_true_{label_count}"
                lab_end = f"LBL_end_{label_count}"
                label_count += 1
                if op == '>':
                    asm.append(f"    BGT {lab_true}")
                elif op == '<':
                    asm.append(f"    BLT {lab_true}")
                elif op == '==':
                    asm.append(f"    BEQ {lab_true}")
                elif op == '!=':
                    asm.append(f"    BNE {lab_true}")
                elif op == '>=':
                    asm.append(f"    BGE {lab_true}")
                elif op == '<=':
                    asm.append(f"    BLE {lab_true}")
                asm.append("    MOV R3, #0")
                asm.append(f"    B {lab_end}")
                asm.append(f"{lab_true}:")
                asm.append("    MOV R3, #1")
                asm.append(f"{lab_end}:")
                asm.append(f"    LDR R4, ={dest}")
                asm.append("    STR R3, [R4]")
            else:
                asm.append(f"    ; unknown op {op}")
            continue

        # direct assign: x = 3 or x = t1
        m = re.match(r'^([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*|-?\d+)\s*$', l)
        if m:
            dest,src = m.group(1),m.group(2)
            if is_num(src):
                asm.append(f"    MOV R1, #{src}")
            else:
                asm.append(f"    LDR R1, ={src}")
                asm.append(f"    LDR R1, [R1]")
            asm.append(f"    LDR R2, ={dest}")
            asm.append("    STR R1, [R2]")
            continue

        # print
        m = re.match(r'^print\s+([A-Za-z_]\w*|-?\d+)$', l)
        if m:
            v=m.group(1)
            if is_num(v):
                asm.append(f"    MOV R0, #{v}")
            else:
                asm.append(f"    LDR R0, ={v}")
                asm.append("    LDR R0, [R0]")
            asm.append("    BL _print_int")
            continue

        # ifFalse x goto L
        m = re.match(r'^ifFalse\s+([A-Za-z_]\w*|-?\d+)\s+goto\s+([A-Za-z_]\w*)$', l)
        if m:
            cond, lab = m.group(1), m.group(2)
            if is_num(cond):
                asm.append(f"    MOV R1, #{cond}")
            else:
                asm.append(f"    LDR R1, ={cond}")
                asm.append("    LDR R1, [R1]")
            asm.append("    CMP R1, #0")
            asm.append(f"    BEQ {lab}")
            continue

        # goto label
        m = re.match(r'^goto\s+([A-Za-z_]\w*)$', l)
        if m:
            asm.append(f"    B {m.group(1)}")
            continue

        # label
        m = re.match(r'^([A-Za-z_]\w*):$', l)
        if m:
            asm.append(f"{m.group(1)}:")
            continue

        # ret value
        m = re.match(r'^ret\s+([A-Za-z_]\w*|-?\d+)$', l)
        if m:
            v = m.group(1)
            if is_num(v):
                asm.append(f"    MOV R0, #{v}")
            else:
                asm.append(f"    LDR R0, ={v}")
                asm.append("    LDR R0, [R0]")
            asm.append("    B _exit")
            continue

        asm.append(f"    ; unrecognized: {l}")

    # runtime helpers and .data
    asm.append("\t/* runtime helpers */")
    asm.append("_print_int:")
    asm.append("    ; stub print (in VM we may implement this)")
    asm.append("    BX LR")
    asm.append("_exit:")
    asm.append("    BX LR")

    asm.append("\n\t.data")
    # declare variables
    vars = gather_vars(tac_lines)
    for v in vars:
        asm.append(f"{v}: .word 0")

    with open(outname, "w") as f:
        f.write("\n".join(asm))
    print("Wrote", outname)

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Usage: assemble.py out_opt.tac")
        sys.exit(1)
    tac_lines = read_tac(sys.argv[1])
    outname = sys.argv[1].rsplit('.',1)[0] + ".s"
    to_asm(tac_lines, outname)
