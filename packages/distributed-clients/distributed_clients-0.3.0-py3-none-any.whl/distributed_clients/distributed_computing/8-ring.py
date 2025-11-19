class Node:
    def __init__(self, id):
        self.id = id
        self.alive = True
    
    def crash(self):
        self.alive = False
        print(f"Node {self.id} crashed")

    def recover(self):
        self.alive = True
        print(f"Node {self.id} recovered")


def ring_election(nodes, starter):
    print(f"\nElection started by Node {starter.id}")

    n = len(nodes)
    start_index = nodes.index(starter)

    # Step 2: Start message as LIST
    message_list = [starter.id]
    print(f"Node {starter.id} sends election message: {message_list}")

    index = (start_index + 1) % n

    # Pass the list around the ring
    while index != start_index:

        node = nodes[index]

        if node.alive:
            print(f"Node {node.id} received message: {message_list}")
            # Node adds its ID to the list
            if node.id not in message_list:
                message_list.append(node.id)
                print(f"Node {node.id} adds its ID -> {message_list}")
        else:
            print(f"Node {node.id} is dead. Message skipped.")

        index = (index + 1) % n

    # Message has returned to starter → determine leader
    print(f"\nMessage returned to starter Node {starter.id}")
    print(f"Collected IDs: {message_list}")

    leader_id = max(message_list)
    print(f"\nNode {leader_id} is the NEW LEADER!\n")

    # Announce leader
    for node in nodes:
        if node.alive:
            print(f"Leader Node {leader_id} -> Node {node.id}: I am the new leader")

nodes = [Node(1), Node(2), Node(3), Node(4), Node(5)]

print("Initial Leader: Node 5")

# Leader crashes
nodes[-1].crash()

# Start election from Node 2
ring_election(nodes, nodes[1])
