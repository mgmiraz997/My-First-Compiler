import re
print("\n========== [Task 6] Code Optimization ==========")
lines=[l.strip()for l in open("out.tac")if l.strip()]
optimized=[];consts={}
for line in lines:
  if re.match(r'^[A-Za-z_]\w* = \d+$',line):
    var,val=line.split(' = ');consts[var.strip()]=int(val)
    optimized.append(line)
  elif any(op in line for op in ['+','-','*','/','>','<']):
    m=re.match(r'(t\d+) = (\w+) ([+\-*/><=]+) (\w+)',line)
    if m:
      res,a,op,b=m.groups()
      if a in consts and b in consts:
        val=eval(f"{consts[a]}{op}{consts[b]}")
        consts[res]=val
        optimized.append(f"{res} = {val} # const fold")
      else:optimized.append(line)
    else:optimized.append(line)
  else:optimized.append(line)
open("out_opt.tac","w").write("\n".join(optimized))
print("Optimized TAC written to out_opt.tac ✅")

