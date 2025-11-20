# ------------------------
# Simple Distributed Banking
# Bully Election + Transactions
# ------------------------

class Node:
    def __init__(self, id):
        self.id = id
        self.alive = True
        self.is_leader = False
        self.leader_id = None
        self.balance = 100
        self.clock = 0  # Lamport clock

    def crash(self):
        self.alive = False
        self.is_leader = False
        print(f"\nNode {self.id} crashed")

    def recover(self):
        self.alive = True
        print(f"\nNode {self.id} recovered")

    # Increment Lamport clock
    def tick(self):
        self.clock += 1
        return self.clock

    # Deposit transaction
    def deposit(self, amount, nodes):
        if not self.alive:
            print(f"Node {self.id} is down!")
            return
        if self.is_leader:
            self.tick()
            self.balance += amount
            print(f"[Leader Node {self.id}] Deposit {amount} → Balance: {self.balance} | Clock: {self.clock}")
        else:
            leader = next((n for n in nodes if n.id == self.leader_id), None)
            if leader and leader.alive:
                print(f"Node {self.id} forwards deposit {amount} to Leader Node {leader.id}")
                leader.deposit(amount, nodes)

    # Withdraw transaction
    def withdraw(self, amount, nodes):
        if not self.alive:
            print(f"Node {self.id} is down!")
            return
        if self.is_leader:
            self.tick()
            self.balance -= amount
            print(f"[Leader Node {self.id}] Withdraw {amount} → Balance: {self.balance} | Clock: {self.clock}")
        else:
            leader = next((n for n in nodes if n.id == self.leader_id), None)
            if leader and leader.alive:
                print(f"Node {self.id} forwards withdraw {amount} to Leader Node {leader.id}")
                leader.withdraw(amount, nodes)


# ------------------------
# Election Functions
# ------------------------
def set_leader(nodes, leader):
    print(f"\nNode {leader.id} is elected as the LEADER")
    leader.is_leader = True
    leader.leader_id = leader.id
    for n in nodes:
        if n.alive and n.id != leader.id:
            n.is_leader = False
            n.leader_id = leader.id
            print(f"Leader Node {leader.id} -> Node {n.id} : I am the new leader")


def start_election(nodes, starter):
    print(f"\nElection started by Node {starter.id}")
    higher = [n for n in nodes if n.id > starter.id and n.alive]
    if not higher:
        set_leader(nodes, starter)
    else:
        winner = max(higher, key=lambda n: n.id)
        set_leader(nodes, winner)


# ------------------------
# Simulation
# ------------------------
nodes = [Node(i) for i in range(1, 6)]

# Initial leader
set_leader(nodes, nodes[-1])  # Node 5

# Transactions
nodes[1].deposit(50, nodes)
nodes[2].withdraw(20, nodes)

# Crash leader
nodes[-1].crash()

# Election after crash
start_election(nodes, nodes[2])  # Node 3 starts election

# Transactions after new leader
nodes[1].deposit(30, nodes)
nodes[2].withdraw(10, nodes)

# Recover old leader
nodes[-1].recover()
start_election(nodes, nodes[-1])  # Old leader triggers election

# Final balances
print("\n--- Final Balances ---")
for n in nodes:
    status = "Leader" if n.is_leader else "Follower"
    print(f"Node {n.id} [{status}] → Balance: {n.balance} | Clock: {n.clock}")
