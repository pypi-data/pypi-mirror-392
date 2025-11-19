# EXP 1
import threading
import time
import requests
from flask import Flask, request, jsonify
import logging
import random

# --- Global State & Configuration ---
# Disable Flask's default logging to keep the output clean
logging.getLogger("werkzeug").setLevel(logging.ERROR)

SERVERS = {}  # A dictionary to hold our server objects
TRANSACTION_LOG = []
LEADER_ID = None


# --- Server Class Definition ---
class Server:
    def __init__(self, server_id, port):
        self.id = server_id
        self.port = port
        self.is_leader = False
        self.is_active = True
        self.lamport_clock = 0
        self.accounts = {"A": 1000, "B": 500}  # Shared account balances for simplicity

        # Each server runs its own web server (Flask app)
        self.app = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        """Defines the API endpoints for this server."""

        # Endpoint for an election message
        @self.app.route("/election", methods=["POST"])
        def handle_election():
            # If my ID is higher, I'll take over the election process.
            if self.id > request.json["id"]:
                # Start my own election in a new thread
                threading.Thread(target=self.start_election).start()
                return jsonify({"response": "OK, I am taking over"})
            # Otherwise, I yield to the sender who has a higher ID.
            return jsonify({"response": "yield"})

        # Endpoint for announcing the new leader
        @self.app.route("/announce", methods=["POST"])
        def handle_announcement():
            global LEADER_ID
            LEADER_ID = request.json["leader_id"]
            self.is_leader = self.id == LEADER_ID
            self.lamport_clock = max(self.lamport_clock, request.json["clock"]) + 1
            if self.is_leader:
                print(f"[Server {self.id}] --- I am now the LEADER ---")
            return jsonify({"response": "acknowledged"})

        # Endpoint for processing client transactions
        @self.app.route("/transaction", methods=["POST"])
        def handle_transaction():
            if not self.is_leader:
                return jsonify({"error": "I am not the leader"}), 400

            self.lamport_clock += 1  # Increment clock for local event
            trans = request.json
            trans["timestamp"] = self.lamport_clock  # Attach Lamport timestamp

            # Simple transaction logic
            if trans["type"] == "deposit":
                self.accounts[trans["account"]] += trans["amount"]
            elif trans["type"] == "withdraw":
                self.accounts[trans["account"]] -= trans["amount"]

            TRANSACTION_LOG.append(trans)
            print(
                f"[Leader {self.id}] Processed TX (Clock={self.lamport_clock}): {trans['type']} {trans['amount']} on {trans['account']}. Balances: {self.accounts}"
            )
            return jsonify({"status": "success", "balances": self.accounts})

    def start_election(self):
        """Initiates a leader election using the Bully Algorithm."""
        print(f"[Server {self.id}] Starting an election.")
        self.lamport_clock += 1

        # Check if any server with a higher ID is active
        higher_servers = [s_id for s_id in SERVERS if s_id > self.id]
        if not higher_servers:
            self.announce_as_leader()
            return

        got_response = False
        for s_id in higher_servers:
            try:
                url = f"http://127.0.0.1:{SERVERS[s_id].port}/election"
                res = requests.post(url, json={"id": self.id}, timeout=0.5)
                if res.status_code == 200:
                    got_response = True  # A higher server is alive and will take over
            except requests.exceptions.RequestException:
                pass  # This server is down, which is fine

        # If no higher server responded, I am the leader.
        if not got_response:
            self.announce_as_leader()

    def announce_as_leader(self):
        """Announce to all other servers that this server is the new leader."""
        global LEADER_ID
        LEADER_ID = self.id
        self.is_leader = True
        print(f"[Server {self.id}] --- Elected as the new LEADER ---")

        self.lamport_clock += 1
        for s_id, server_node in SERVERS.items():
            if s_id != self.id and server_node.is_active:
                try:
                    url = f"http://127.0.0.1:{server_node.port}/announce"
                    requests.post(
                        url,
                        json={"leader_id": self.id, "clock": self.lamport_clock},
                        timeout=0.5,
                    )
                except requests.exceptions.RequestException:
                    pass  # Ignore if a server is unreachable

    def run(self):
        """Run the Flask server in a separate daemon thread."""
        thread = threading.Thread(
            target=lambda: self.app.run(port=self.port), daemon=True
        )
        thread.start()


# --- Leader Monitoring and Client Simulation ---


def monitor_leader():
    """A simple function to periodically check if the leader is alive."""
    while True:
        time.sleep(5)  # Check every 5 seconds
        if LEADER_ID is None or not SERVERS[LEADER_ID].is_active:
            continue

        try:
            # Simple ping to the leader's port
            url = f"http://127.0.0.1:{SERVERS[LEADER_ID].port}/transaction"
            requests.post(url, json={}, timeout=0.5)
        except requests.exceptions.RequestException:
            print(f"\n[Monitor] Leader {LEADER_ID} seems to be down!")
            SERVERS[LEADER_ID].is_active = False  # Mark as crashed

            # Pick a random alive server to start a new election
            alive_servers = [s for s in SERVERS.values() if s.is_active]
            if alive_servers:
                random_server = random.choice(alive_servers)
                print(
                    f"[Monitor] Telling Server {random_server.id} to start a new election."
                )
                threading.Thread(target=random_server.start_election).start()


def client_simulation(server_to_crash):
    """Simulates a client sending transactions, and a leader crash happening."""
    print("\n--- Client starting transactions ---")
    time.sleep(2)  # Wait for initial election

    for i in range(2):
        if LEADER_ID:
            try:
                url = f"http://127.0.0.1:{SERVERS[LEADER_ID].port}/transaction"
                requests.post(
                    url, json={"type": "deposit", "account": "A", "amount": 100}
                )
                time.sleep(1)
            except requests.exceptions.RequestException:
                print("[Client] Could not connect to leader. Waiting...")

    print(f"\n--- SIMULATING CRASH of Leader Server {server_to_crash} ---")
    SERVERS[server_to_crash].is_active = False  # The monitor will detect this

    print("\n--- Client waiting for new leader... ---")
    time.sleep(8)  # Wait for a new election to complete

    print("\n--- Client resuming transactions with NEW leader ---")
    for i in range(2):
        if LEADER_ID:
            try:
                url = f"http://127.0.0.1:{SERVERS[LEADER_ID].port}/transaction"
                requests.post(
                    url, json={"type": "withdraw", "account": "B", "amount": 50}
                )
                time.sleep(1)
            except requests.exceptions.RequestException:
                print("[Client] Could not connect to new leader. Waiting...")


# --- Main Execution ---
if __name__ == "__main__":
    # 1. Create and run 4 servers
    num_servers = 4
    for i in range(num_servers):
        server_id = i + 1
        port = 5000 + server_id
        SERVERS[server_id] = Server(server_id, port)
        SERVERS[server_id].run()
        print(f"Server {server_id} started on port {port}")

    # 2. Start the initial election
    print("\n--- Starting initial leader election ---")
    # The server with the highest ID should win, let's have it start.
    SERVERS[num_servers].start_election()

    # 3. Start the client simulation which will also trigger a crash
    client_simulation(server_to_crash=num_servers)  # Crash the initial leader

    time.sleep(2)
    print("\n--- Simulation finished ---")

    # 4. Show the final transaction log, ordered by the Lamport timestamps
    print("\nFinal Global Transaction Log (ordered by Lamport clock):")
    sorted_log = sorted(TRANSACTION_LOG, key=lambda x: x["timestamp"])
    for entry in sorted_log:
        print(f"  Timestamp: {entry['timestamp']}, Transaction: {entry}")
