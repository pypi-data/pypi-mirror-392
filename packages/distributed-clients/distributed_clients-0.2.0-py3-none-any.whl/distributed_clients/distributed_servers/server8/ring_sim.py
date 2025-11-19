# ring_sim.py
nodes=[1,2,3,4]
def ring(start):
    print("Start at",start)
    msg=[start]
    i=nodes.index(start)
    for k in range(len(nodes)-1):
        nxt=nodes[(i+1)%len(nodes)]; i=(i+1)%len(nodes)
        msg.append(nodes[i])
        print("pass ->",nodes[i])
    leader=max(msg); print("Leader:",leader)
ring(2)
