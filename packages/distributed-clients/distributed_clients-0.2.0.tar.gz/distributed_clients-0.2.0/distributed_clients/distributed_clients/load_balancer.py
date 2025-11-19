# EXP 11
import threading
import time
from flask import Flask, request, jsonify
import requests


# --- Backend Server Simulation ---
# We simulate them as simple functions instead of full threads for simplicity.
def backend_server_1(request_data):
    """Simulates processing by backend server 1."""
    print(f"[Backend 1] Processing request: {request_data}")
    time.sleep(2)  # Simulate work
    return "Response from Backend Server 1"


def backend_server_2(request_data):
    """Simulates processing by backend server 2."""
    print(f"[Backend 2] Processing request: {request_data}")
    time.sleep(2)
    return "Response from Backend Server 2"


def backend_server_3(request_data):
    """Simulates processing by backend server 3."""
    print(f"[Backend 3] Processing request: {request_data}")
    time.sleep(2)
    return "Response from Backend Server 3"


BACKEND_SERVERS = [backend_server_1, backend_server_2, backend_server_3]
current_server_index = 0
lock = threading.Lock()  # To safely update the index in a threaded environment

# --- Load Balancer Module ---
app = Flask(__name__)


@app.route("/request", methods=["POST"])
def load_balancer():
    """
    Implements a Round Robin load balancer.
    It forwards the request to the next available backend server.
    """
    global current_server_index

    # Use a lock to prevent a race condition on the index
    with lock:
        # Select the next server in the list
        target_server = BACKEND_SERVERS[current_server_index]

        # Update the index for the next request, wrapping around if necessary
        current_server_index = (current_server_index + 1) % len(BACKEND_SERVERS)

    print(f"[Load Balancer] Forwarding request to {target_server.__name__}")

    # Forward the request and get the response
    response_from_backend = target_server(request.json)

    return jsonify({"response": response_from_backend})


# --- Client Simulation ---
def run_client(client_id):
    """Simulates a client sending a request to the load balancer."""
    print(f"[Client {client_id}] Sending request to load balancer...")
    try:
        res = requests.post(
            "http://127.0.0.1:5000/request",
            json={"data": f"Hello from client {client_id}"},
        )
        print(f"[Client {client_id}] Received response: {res.json()}")
    except requests.exceptions.RequestException:
        pass


# --- Main Execution ---
if __name__ == "__main__":
    # Start the load balancer server in a background thread
    server_thread = threading.Thread(
        target=lambda: app.run(port=5000, threaded=True), daemon=True
    )
    server_thread.start()
    time.sleep(1)

    print("--- Simulating 5 client requests to the load balancer ---\n")

    client_threads = []
    for i in range(5):
        # We start clients in quick succession
        client_thread = threading.Thread(target=run_client, args=(i + 1,))
        client_threads.append(client_thread)
        client_thread.start()
        time.sleep(0.2)

    for t in client_threads:
        t.join()

    print("\n--- Load distribution printed above. Simulation finished. ---")
