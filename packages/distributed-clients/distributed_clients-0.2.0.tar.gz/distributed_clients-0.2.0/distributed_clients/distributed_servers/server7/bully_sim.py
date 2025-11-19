# bully_sim.py
nodes=[1,2,3,4,5]; failed=[5]  # failing highest
def bully(start):
    print(f"{start} starts election")
    higher=[p for p in nodes if p>start and p not in failed]
    if not higher:
        print(f"{start} wins")
        return start
    for h in higher: print(f"{start} -> probe {h}")
    winner=max([p for p in nodes if p not in failed])
    print("Coordinator chosen:", winner); return winner

print("Simulate: node 3 triggers")
bully(3)
