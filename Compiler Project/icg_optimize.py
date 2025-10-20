#!/usr/bin/env python3
import sys, re

# Simple optimizer: constant folding for binary ops where operands are numbers or known constants,
# and propagate constants.

def read_tac(fn):
    with open(fn) as f:
        return [l.rstrip() for l in f if l.strip()]

def is_assign_num(line):
    # e.g. x = 3
    m = re.match(r'^\s*([A-Za-z_]\w*)\s*=\s*(-?\d+)\s*$', line)
    return m.groups() if m else None

def fold_line(line, consts):
    # patterns: t1 = a + b  or t1 = 3 + 4
    m = re.match(r'^\s*([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*|-?\d+)\s*([\+\-\*\/<>!=]{1,2})\s*([A-Za-z_]\w*|-?\d+)\s*$', line)
    if not m:
        return line, consts
    dest,a,op,b = m.group(1),m.group(2),m.group(3),m.group(4)
    av = None; bv = None
    if re.match(r'^-?\d+$', a): av=int(a)
    elif a in consts: av=consts[a]
    if re.match(r'^-?\d+$', b): bv=int(b)
    elif b in consts: bv=consts[b]
    if av is not None and bv is not None:
        if op == '+': val = av + bv
        elif op == '-': val = av - bv
        elif op == '*': val = av * bv
        elif op == '/': val = av // bv if bv!=0 else 0
        elif op == '>': val = 1 if av > bv else 0
        elif op == '<': val = 1 if av < bv else 0
        elif op == '==': val = 1 if av == bv else 0
        elif op == '!=': val = 1 if av != bv else 0
        elif op == '>=': val = 1 if av >= bv else 0
        elif op == '<=': val = 1 if av <= bv else 0
        else: return line, consts
        consts[dest] = val
        return f"{dest} = {val}", consts
    # propagate known constants into expression
    if a in consts: a = str(consts[a])
    if b in consts: b = str(consts[b])
    return f"{dest} = {a} {op} {b}", consts

def optimize(lines):
    consts = {}
    out=[]
    for l in lines:
        # if assign number
        m = is_assign_num(l)
        if m:
            var,num = m
            consts[var]=int(num)
            out.append(f"{var} = {num}")
            continue
        newl, consts = fold_line(l, consts)
        out.append(newl)
    return out

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("Usage: icg_optimize.py out.tac > out_opt.tac")
        sys.exit(1)
    lines = read_tac(sys.argv[1])
    opt = optimize(lines)
    for l in opt:
        print(l)
