# EXP 4
# uses Lamport logical clocks
import threading
import time
import random

# --- Global State & Configuration ---
NUM_SERVERS = 3
SIMULATION_TIME_SECONDS = 5
LOG_MANAGER = []
run_simulation = True

# A lock to safely append to the global log manager from multiple threads
log_lock = threading.Lock()

# --- Server Class with Lamport Clock Logic ---


class Server:
    def __init__(self, server_id, all_servers):
        self.id = server_id
        self.clock = 0
        self.all_servers = (
            all_servers  # A reference to all other servers for communication
        )

    def _increment_clock(self):
        """Rule 1: Increment clock before any event."""
        self.clock += 1

    def _log_event(self, event_description):
        """Helper to create and store a log entry."""
        log_entry = {
            "server_id": self.id,
            "clock": self.clock,
            "event": event_description,
        }
        with log_lock:
            LOG_MANAGER.append(log_entry)
        print(f"Server {self.id} | Clock: {self.clock} | {event_description}")

    def local_event(self):
        """Rule 1 (continued): An internal event occurs."""
        self._increment_clock()
        self._log_event("Generated a local log event.")

    def send_message(self, target_server_id):
        """Rule 2: Sending a message."""
        self._increment_clock()
        message = {"sender_id": self.id, "clock": self.clock}
        self._log_event(f"Sent message to Server {target_server_id}.")

        # Directly call the receive method of the target server to simulate sending
        self.all_servers[target_server_id].receive_message(message)

    def receive_message(self, message):
        """Rule 3: Receiving a message."""
        # Update local clock to be the max of local and received, then increment
        self.clock = max(self.clock, message["clock"]) + 1
        self._log_event(f"Received message from Server {message['sender_id']}.")

    def run(self):
        """The main loop for the server thread."""
        while run_simulation:
            # Randomly choose an action: either a local event or sending a message
            if random.random() > 0.4:
                self.local_event()
            else:
                # Choose a random server to send a message to (but not itself)
                possible_targets = [sid for sid in self.all_servers if sid != self.id]
                if possible_targets:
                    target_id = random.choice(possible_targets)
                    self.send_message(target_id)

            # Wait for a random time to make the event order unpredictable
            time.sleep(random.uniform(0.5, 1.5))


# --- Main Execution ---

if __name__ == "__main__":
    # 1. Create all server instances
    servers = {}
    for i in range(1, NUM_SERVERS + 1):
        # We pass the 'servers' dict to each server so they know about each other
        servers[i] = Server(server_id=i, all_servers=servers)

    # 2. Start all the Server threads
    threads = []
    for server_id, server_instance in servers.items():
        thread = threading.Thread(target=server_instance.run)
        threads.append(thread)
        thread.start()
        print(f"Started Server {server_id}...")

    # 3. Let the simulation run for a configured duration
    time.sleep(SIMULATION_TIME_SECONDS)
    run_simulation = False  # Signal all threads to stop

    # 4. Wait for all threads to complete
    print("\n--- Stopping simulation, waiting for threads to finish... ---")
    for t in threads:
        t.join()

    print("\n" + "=" * 50)
    print("--- SIMULATION FINISHED ---")
    print("=" * 50 + "\n")

    # 5. Show the globally ordered log timeline
    print("--- Final Log Timeline (sorted by Lamport Clock & Server ID) ---")

    # Sort by the Lamport clock value first, then use server_id as a tie-breaker.
    # This ensures a deterministic, causally consistent order.
    sorted_log = sorted(LOG_MANAGER, key=lambda x: (x["clock"], x["server_id"]))

    for log in sorted_log:
        print(
            f"Clock: {log['clock']:<3} | Server ID: {log['server_id']} | Event: {log['event']}"
        )
