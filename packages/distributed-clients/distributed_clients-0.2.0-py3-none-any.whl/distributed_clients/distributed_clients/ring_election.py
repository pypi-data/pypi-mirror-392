# EXP 8
import threading
import time
import random

# --- Global State & Configuration ---
NUM_PROCESSES = 5
ALL_PROCESSES = {}  # Global dict to hold process instances and their state
LEADER_ID = -1


class Process:
    def __init__(self, process_id):
        self.id = process_id
        self.is_active = True
        self.is_participant = False  # Flag to see if it's already in an election

    def get_successor(self):
        """Finds the next active process in the ring."""
        next_id = (self.id + 1) % NUM_PROCESSES
        while next_id != self.id:
            if ALL_PROCESSES[next_id]["instance"].is_active:
                return ALL_PROCESSES[next_id]["instance"]
            next_id = (next_id + 1) % NUM_PROCESSES
        return self  # Should not happen in a ring with >1 active nodes

    def start_election(self):
        """Initiates an election by sending a message to its successor."""
        if not self.is_active:
            return

        print(f"[Process {self.id}] Detects leader failure. Starting an election.")
        self.is_participant = True

        # Create the initial election message with its own ID
        election_message = [self.id]

        successor = self.get_successor()
        print(
            f"[Process {self.id}] Passing ELECTION message {election_message} to Process {successor.id}"
        )
        successor.handle_election_message(election_message)

    def handle_election_message(self, message):
        """Processes a received election message."""
        if not self.is_active:
            return

        # If this process's ID is in the message, the message has completed a full circle.
        if self.id in message:
            # The election is over. Determine the new leader and announce it.
            new_leader_id = max(message)
            self.announce_leader(new_leader_id)
            return

        # Add my ID to the list
        message.append(self.id)

        # Pass the updated message clockwise
        successor = self.get_successor()
        print(
            f"[Process {self.id}] Adding my ID. Passing ELECTION message {message} to Process {successor.id}"
        )
        successor.handle_election_message(message)

    def announce_leader(self, new_leader_id):
        """Handles the announcement of the new leader."""
        global LEADER_ID

        # If this announcement has already been seen, stop forwarding it.
        if LEADER_ID == new_leader_id:
            return

        LEADER_ID = new_leader_id

        if self.id == new_leader_id:
            print(f"\n[Process {self.id}] --- I AM THE NEW LEADER ---")
        else:
            print(
                f"[Process {self.id}] Acknowledged new leader: Process {new_leader_id}"
            )

        # Forward the announcement message around the ring
        self.get_successor().announce_leader(new_leader_id)


# --- Main Simulation ---


def monitor_leader():
    """A simple external monitor to detect leader failure and trigger an election."""
    global LEADER_ID
    time.sleep(3)  # Give time for initial state

    # Requirement: On failure of leader -> initiate election.
    if LEADER_ID != -1 and not ALL_PROCESSES[LEADER_ID]["instance"].is_active:
        print(f"\n[Monitor] Detected that Leader {LEADER_ID} has failed.")

        # Pick a random, non-leader process to start the election
        initiator_id = random.choice(
            [i for i in range(NUM_PROCESSES) if i != LEADER_ID]
        )
        print(f"[Monitor] Telling Process {initiator_id} to start a new election.\n")
        ALL_PROCESSES[initiator_id]["instance"].start_election()


if __name__ == "__main__":
    # 1. Create N processes arranged in a ring.
    for i in range(NUM_PROCESSES):
        ALL_PROCESSES[i] = {"instance": Process(process_id=i)}

    # 2. Assume the process with the highest ID is the initial leader.
    initial_leader_id = NUM_PROCESSES - 1
    LEADER_ID = initial_leader_id
    print(
        f"--- Initial State: {NUM_PROCESSES} processes in a ring. Process {LEADER_ID} is the leader. ---\n"
    )

    # 3. Simulate failure of the leader.
    time.sleep(2)
    print(f"--- Simulating CRASH of Leader Process {initial_leader_id} ---")
    ALL_PROCESSES[initial_leader_id]["instance"].is_active = False

    # 4. Use a monitor to detect the failure and start the election process.
    monitor_thread = threading.Thread(target=monitor_leader)
    monitor_thread.start()
    monitor_thread.join()

    time.sleep(2)  # Allow time for announcement to circulate
    print("\n--- Simulation Finished ---")
    print(f"Final determined leader: Process {LEADER_ID}")
