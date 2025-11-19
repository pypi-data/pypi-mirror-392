# berkeley_clock.py (coordinator polls and averages)
nodes = {"A":100.0,"B":98.7,"C":101.2}
master="A"
diffs=[t-nodes[master] for t in nodes.values()]
avg=sum(diffs)/len(diffs)
for n in nodes: nodes[n]-=avg
print("Synchronized clocks:", nodes)
