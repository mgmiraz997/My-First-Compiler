import re
print("\n========== [Task 7] Assembly Code Generation ==========")

tac=[l.strip()for l in open("out_opt.tac")if l.strip()]
asm=[];regs={}
def reg(x):
  if x not in regs:regs[x]=f"R{len(regs)+1}"
  return regs[x]
asm.append(".text")
for line in tac:
  if "=" in line and any(op in line for op in ["+","-","*","/"]):
    lhs,expr=line.split(" = ");parts=re.split(r' [+\-*/] ',expr)
    if len(parts)==2:
      a,b=parts;op=[o for o in "+-*/" if o in expr][0]
      ra,rb,rc=reg(a.strip()),reg(b.strip()),reg(lhs.strip())
      asm.append(f"{'ADD'if op=='+'else'SUB'if op=='-'else'MUL'if op=='*'else'DIV'} {rc}, {ra}, {rb}")
  elif re.match(r'\w+ = \d+',line):
    var,val=line.split(' = ');asm.append(f"MOV {reg(var.strip())}, #{val.strip()}")
  elif line.startswith("print"):
    v=line.split()[1];asm.append(f"OUT {reg(v)}")
  elif line.startswith("ifFalse"):
    v=line.split()[1];L=line.split()[-1]
    asm.append(f"CMP {reg(v)}, #0");asm.append(f"BEQ {L}")
  elif line.endswith(":"):asm.append(line)
  elif line.startswith("goto"):asm.append(f"B {line.split()[-1]}")
  elif line.startswith("ret"):
    v=line.split()[-1];asm.append(f"MOV R0, {reg(v)}");asm.append("SWI 0x011")
open("out.asm","w").write("\n".join(asm))
print("Assembly code written to out.asm ✅")

