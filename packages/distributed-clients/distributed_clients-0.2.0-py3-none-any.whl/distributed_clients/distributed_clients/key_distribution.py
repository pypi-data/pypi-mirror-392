# EXP 3
from flask import Flask, request, jsonify
import threading
import time
import uuid
import requests  # The Python equivalent of curl

# --- SERVER CODE (Identical to before) ---

API_KEYS = {}
keys_lock = threading.Lock()
KEY_LIFESPAN_SECONDS = 300
BLOCKED_TIMEOUT_SECONDS = 60
app = Flask(__name__)


@app.route("/keys/create", methods=["POST"])
def create_key():
    new_key = str(uuid.uuid4())
    with keys_lock:
        API_KEYS[new_key] = {
            "status": "available",
            "expires_at": time.time() + KEY_LIFESPAN_SECONDS,
            "blocked_until": 0,
        }
    print(f"[Server] Created Key: {new_key}")
    return jsonify({"api_key": new_key}), 201


@app.route("/keys/available", methods=["GET"])
def get_available_key():
    with keys_lock:
        for key, info in API_KEYS.items():
            if info["status"] == "available":
                info["status"] = "blocked"
                info["blocked_until"] = time.time() + BLOCKED_TIMEOUT_SECONDS
                print(f"[Server] Assigned Key: {key}")
                return jsonify({"api_key": key})
    return jsonify({"error": "No available keys"}), 404


# ... (other server endpoints like /unblock and /keep-alive are the same) ...


def cleanup_worker():
    while True:
        time.sleep(5)
        current_time = time.time()
        keys_to_delete = []
        with keys_lock:
            for key, info in API_KEYS.items():
                if current_time > info["expires_at"]:
                    keys_to_delete.append(key)
                elif (
                    info["status"] == "blocked" and current_time > info["blocked_until"]
                ):
                    info["status"] = "available"
                    print(f"[Cleanup] Auto-unblocked Key: {key}")
            for key in keys_to_delete:
                del API_KEYS[key]
                print(f"[Cleanup] Deleted Expired Key: {key}")


# --- NEW: Python Client Simulation Code ---


def run_client_simulation():
    """Uses the 'requests' library to act as a client."""
    base_url = "http://127.0.0.1:5000"

    print("\n--- Starting Client Simulation ---")

    # A) Create a key
    print("\n[Client] 1. Creating a new key...")
    response = requests.post(f"{base_url}/keys/create")
    data = response.json()
    my_key = data["api_key"]
    print(f"[Client]    ...Success! Got key: {my_key}")
    time.sleep(1)

    # B) Get an available key
    print("\n[Client] 2. Getting an available key...")
    response = requests.get(f"{base_url}/keys/available")
    print(
        f"[Client]    ...Success! The server assigned us key: {response.json()['api_key']}"
    )
    time.sleep(1)

    # C) Try to get another one (should fail)
    print("\n[Client] 3. Trying to get another key (this should fail)...")
    response = requests.get(f"{base_url}/keys/available")
    if response.status_code == 404:
        print(
            f"[Client]    ...Success! Server correctly said: {response.json()['error']}"
        )
    else:
        print("[Client]    ...Error! This should have failed.")
    time.sleep(1)

    print("\n--- Simulation Complete ---")


# --- MODIFIED: Main Execution Block ---

if __name__ == "__main__":
    # 1. Start the Flask server in a background daemon thread
    server_thread = threading.Thread(
        target=lambda: app.run(port=5000, threaded=True), daemon=True
    )
    server_thread.start()

    # 2. Start the cleanup worker in its own thread
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()

    # 3. Give the server a moment to start up
    time.sleep(1)

    # 4. Run the client simulation from the main thread
    run_client_simulation()
