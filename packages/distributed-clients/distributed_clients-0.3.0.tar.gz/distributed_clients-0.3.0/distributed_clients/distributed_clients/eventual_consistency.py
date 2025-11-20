# EXP 9
import threading
import time
import requests
from flask import Flask, request, jsonify
import logging

# --- Configuration & Global State ---
logging.getLogger("werkzeug").setLevel(logging.ERROR)
NUM_REPLICAS = 3
REPLICAS = {}  # Holds the Node instances


class ReplicaNode:
    def __init__(self, node_id, port):
        self.id = node_id
        self.port = port
        self.key_value_store = {}  # Each node has its own data store
        self.app = Flask(f"Node_{node_id}")
        self._setup_routes()

    def _setup_routes(self):
        # Endpoint to set a value (client interaction)
        @self.app.route("/set", methods=["POST"])
        def set_value():
            data = request.json
            key, value = data["key"], data["value"]
            print(f"[Node {self.id}] Received WRITE: key='{key}', value='{value}'")
            self.key_value_store[key] = value
            # Propagate the update to other nodes after a delay
            threading.Thread(target=self.propagate_update, args=(key, value)).start()
            return jsonify({"status": "ok"})

        # Endpoint to get a value (client interaction)
        @self.app.route("/get/<key>", methods=["GET"])
        def get_value(key):
            value = self.key_value_store.get(key, "not_found")
            return jsonify({"key": key, "value": value, "node_id": self.id})

        # Endpoint for internal replication
        @self.app.route("/replicate", methods=["POST"])
        def replicate_value():
            data = request.json
            key, value = data["key"], data["value"]
            print(
                f"[Node {self.id}] Received REPLICATION: key='{key}', value='{value}'"
            )
            self.key_value_store[key] = value
            return jsonify({"status": "replicated"})

    def propagate_update(self, key, value):
        """Sends the update to all other replicas with a delay."""
        # The delay is what causes the temporary inconsistency
        time.sleep(2)
        print(f"[Node {self.id}] Propagating update for key '{key}'...")
        for node_id, node_instance in REPLICAS.items():
            if node_id != self.id:
                try:
                    url = f"http://127.0.0.1:{node_instance.port}/replicate"
                    requests.post(url, json={"key": key, "value": value}, timeout=1)
                except requests.exceptions.RequestException:
                    pass  # Ignore if a node is down

    def run(self):
        threading.Thread(
            target=lambda: self.app.run(port=self.port), daemon=True
        ).start()


# --- Main Simulation ---
if __name__ == "__main__":
    # 1. Create 3 replica nodes
    for i in range(NUM_REPLICAS):
        node_id = i + 1
        REPLICAS[node_id] = ReplicaNode(node_id, port=5000 + node_id)
        REPLICAS[node_id].run()
        print(f"Replica Node {node_id} started on port {5000 + node_id}")

    time.sleep(1)
    print("\n--- Simulating Eventual Consistency ---")
    print(
        "Difference: A strongly consistent system would block the write until all replicas confirm. An eventually consistent system responds immediately and replicates in the background.\n"
    )

    # 2. Write a value to ONE replica
    print("STEP 1: Writing 'my_key' = 'initial_value' to Node 1...")
    requests.post(
        "http://127.0.0.1:5001/set", json={"key": "my_key", "value": "initial_value"}
    )

    # 3. Immediately read from ALL replicas
    print("\nSTEP 2: Immediately reading 'my_key' from all nodes...")
    for i in range(1, NUM_REPLICAS + 1):
        res = requests.get(f"http://127.0.0.1:500{i}/get/my_key")
        print(f"  -> Read from Node {i}: {res.json()}")
    print("   (Note the inconsistency: Node 1 has the new value, others don't yet)")

    # 4. Wait for propagation delay
    print("\nSTEP 3: Waiting 3 seconds for replication to complete...")
    time.sleep(3)

    # 5. Read from ALL replicas again
    print("\nSTEP 4: Reading 'my_key' from all nodes again...")
    for i in range(1, NUM_REPLICAS + 1):
        res = requests.get(f"http://127.0.0.1:500{i}/get/my_key")
        print(f"  -> Read from Node {i}: {res.json()}")
    print("   (Note: The system is now consistent)")
