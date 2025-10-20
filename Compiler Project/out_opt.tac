a = 3
t1 = a * 2
t2 = t1 + 5
b = t2
print b
t3 = b > 8
print b
print a
ifFalse t3 goto L1
goto L2
L1:
L2:
a = 3
t1 = a * 2
t2 = t1 + 5
b = t2
print b
t3 = b > 8
ifFalse t3 goto L1
goto L2
L1:
L2:
ret b