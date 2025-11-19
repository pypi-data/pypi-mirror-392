# vector_clock.py
def vc_inc(vc, i): vc[i]+=1
def vc_merge(a,b): return [max(a[i],b[i]) for i in range(len(a))]

A=[0,0,0]; B=[0,0,0]
vc_inc(A,0)            # A local event
msg=A.copy()
vc_merge(B,msg); vc_inc(B,1)  # B receives then local event
print("A:",A,"B:",B)
# Compare
def cmp(a,b):
    less=all(a[i]<=b[i] for i in range(len(a))) and any(a[i]<b[i] for i in range(len(a)))
    greater=all(a[i]>=b[i] for i in range(len(a))) and any(a[i]>b[i] for i in range(len(a)))
    if less: return "happens-before"
    if greater: return "happens-after"
    return "concurrent"
print("Relation A vs B:", cmp(A,B))
