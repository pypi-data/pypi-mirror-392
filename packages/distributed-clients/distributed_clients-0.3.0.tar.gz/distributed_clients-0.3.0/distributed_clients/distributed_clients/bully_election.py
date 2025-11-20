# EXP 7
import threading
import time
import requests
from flask import Flask, request, jsonify
import logging

# --- Configuration & Global State ---
logging.getLogger("werkzeug").setLevel(logging.ERROR)
NODES = {}
LEADER_ID = None


class Node:
    def __init__(self, node_id, port):
        self.id = (
            node_id  # Requirement: Assign priorities to nodes (ID acts as priority)
        )
        self.port = port
        self.is_leader = False
        self.is_active = True
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/election", methods=["POST"])
        def handle_election():
            # A lower ID node started an election. I am "bullying" it.
            print(
                f"[Node {self.id}] Received election message from a lower ID node. Sending OK and starting my own election."
            )
            threading.Thread(target=self.start_election).start()
            return jsonify({"response": "OK"})

        @self.app.route("/announce", methods=["POST"])
        def handle_announcement():
            global LEADER_ID
            LEADER_ID = request.json["leader_id"]
            self.is_leader = self.id == LEADER_ID
            if self.is_leader:
                print(f"[Node {self.id}] Acknowledged new leader: ME!")
            else:
                print(f"[Node {self.id}] Acknowledged new leader: Node {LEADER_ID}")
            return jsonify({"response": "acknowledged"})

    def start_election(self):
        """Triggers an election and determines the new coordinator."""
        print(f"\n[Node {self.id}] --- Starting an election ---")
        higher_nodes = [n_id for n_id in NODES if n_id > self.id]

        if not higher_nodes:
            # If no nodes have a higher ID, I am the leader.
            self.announce_as_leader()
            return

        got_response = False
        for n_id in higher_nodes:
            try:
                url = f"http://127.0.0.1:{NODES[n_id].port}/election"
                res = requests.post(url, timeout=0.5)
                if res.status_code == 200:
                    print(
                        f"[Node {self.id}] Got OK from Node {n_id}. I will not be the leader."
                    )
                    got_response = True
            except requests.exceptions.RequestException:
                print(f"[Node {self.id}] Node {n_id} is down.")

        if not got_response:
            # If no higher node responded, I am the leader.
            self.announce_as_leader()

    def announce_as_leader(self):
        """Announces to all other nodes that this node is the new leader."""
        global LEADER_ID
        LEADER_ID = self.id
        self.is_leader = True
        print(
            f"[Node {self.id}] --- Elected as the new LEADER. Announcing to others. ---"
        )

        for n_id, node_instance in NODES.items():
            if n_id != self.id and node_instance.is_active:
                try:
                    url = f"http://127.0.0.1:{node_instance.port}/announce"
                    requests.post(url, json={"leader_id": self.id}, timeout=0.5)
                except requests.exceptions.RequestException:
                    pass

    def run(self):
        threading.Thread(
            target=lambda: self.app.run(port=self.port), daemon=True
        ).start()


# --- Main Simulation ---

if __name__ == "__main__":
    num_nodes = 4
    for i in range(num_nodes):
        node_id = i + 1
        NODES[node_id] = Node(node_id, port=5000 + node_id)
        NODES[node_id].run()
        print(f"Node {node_id} started.")

    # Let's assume Node 4 (highest ID) is the initial leader.
    LEADER_ID = 4
    NODES[4].is_leader = True
    print(f"\nInitial State: Node {LEADER_ID} is the leader.\n")
    time.sleep(2)

    # Requirement: Simulate node failure.
    print(f"--- Simulating CRASH of Leader Node {LEADER_ID} ---")
    NODES[LEADER_ID].is_active = False

    # Requirement: Trigger election.
    # In a real system, any node could detect this. Here, we'll have Node 2 detect it.
    print("Node 2 detects the leader is down and starts an election.\n")
    time.sleep(1)
    NODES[2].start_election()

    # The simulation will run and display the election steps in the console.
    time.sleep(5)
    print("\n--- Simulation finished. ---")
    print(f"Final Leader: Node {LEADER_ID}")
