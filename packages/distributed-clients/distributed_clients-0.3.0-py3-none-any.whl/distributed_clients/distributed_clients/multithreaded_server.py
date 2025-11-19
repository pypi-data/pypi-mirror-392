# EXP 10
import threading
import time
from flask import Flask, request, jsonify
import requests

# --- Server Setup ---
app = Flask(__name__)


@app.route("/process", methods=["POST"])
def process_text():
    """
    An endpoint that processes a client's text request.
    This function will be run in a new thread for each client by Flask.
    """
    client_id = request.json.get("id", "Unknown")
    text = request.json.get("text", "")

    # Identify the thread handling this request
    thread_name = threading.current_thread().name
    print(f"[Thread: {thread_name}] Started processing request from Client {client_id}")

    # Simulate a time-consuming task
    time.sleep(3)

    # Process the text (e.g., convert to uppercase)
    processed_text = text.upper()

    print(f"[Thread: {thread_name}] Finished processing for Client {client_id}")
    return jsonify({"original": text, "processed": processed_text})


# --- Client Simulation ---
def client_simulation(client_id, text_to_send):
    """A function to simulate a single client making a request."""
    print(f"[Client {client_id}] Sending request...")
    try:
        res = requests.post(
            "http://127.0.0.1:5000/process",
            json={"id": client_id, "text": text_to_send},
        )
        print(f"[Client {client_id}] Got response: {res.json()}")
    except requests.exceptions.RequestException as e:
        print(f"[Client {client_id}] Error: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    # 1. Start the Flask server in a background thread
    # The 'threaded=True' argument is what makes Flask handle each request in a new thread.
    server_thread = threading.Thread(
        target=lambda: app.run(port=5000, threaded=True), daemon=True
    )
    server_thread.start()
    time.sleep(1)

    print("--- Simulating 3 clients connecting concurrently ---")

    # 2. Create and start threads for multiple clients
    client1 = threading.Thread(target=client_simulation, args=(1, "hello server"))
    client2 = threading.Thread(
        target=client_simulation, args=(2, "this is another client")
    )
    client3 = threading.Thread(target=client_simulation, args=(3, "a third request"))

    client1.start()
    client2.start()
    client3.start()

    # 3. Wait for all clients to finish
    client1.join()
    client2.join()
    client3.join()

    print("\n--- Simulation finished ---")
