class Node:
    def __init__(self, id):
        self.id = id
        self.alive = True

    def crash(self):
        self.alive = False
        print(f"\nNode {self.id} crashed")

    def recover(self):
        self.alive = True
        print(f"Node {self.id} recovered")


def set_leader(nodes, leader):
    print(f"\nNode {leader.id} is elected as the LEADER")
    for n in nodes:
        if n.alive and n.id != leader.id:
            print(f"Leader Node {leader.id} -> Node {n.id} : I am the new leader")


def start_election(nodes, starter):
    print(f"\nElection started by Node {starter.id}")

    for n in nodes:
        if n.id > starter.id:
            print(f"Node {starter.id} -> Node {n.id} : Election Message")
            if n.alive:
                print(f"Node {n.id} -> Node {starter.id} : Response OK")
            else:
                print(f"Node {n.id} -> Node {starter.id} : No Response (Node dead)")

    higher = [n for n in nodes if n.id > starter.id and n.alive]

    if not higher:
        set_leader(nodes, starter)
        return
    else:
        winner = max(higher, key=lambda n: n.id)
        set_leader(nodes, winner)
        return


nodes = [Node(1), Node(2), Node(3), Node(4), Node(5)]

# Set initial leader
set_leader(nodes, nodes[-1])   # Node 5

# Crash the leader
nodes[-1].crash()              # Node 5

# Start election from Node 3
start_election(nodes, nodes[2])
