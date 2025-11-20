# EXP 6
import threading
import time
import random

# --- Global State & Configuration ---
NUM_PROCESSES = 3
run_simulation = True
ALL_PROCESSES = {}  # Global dict to hold process instances


class Process:
    def __init__(self, process_id):
        self.id = process_id
        # Initialize a vector clock for all processes, starting at 0.
        self.vector_clock = [0] * NUM_PROCESSES

    def local_event(self):
        """Rule 1: An internal event occurs."""
        # Increment the clock for this process's own index.
        self.vector_clock[self.id] += 1
        print(f"Process {self.id} | Local Event | Clock: {self.vector_clock}")

    def send_message(self, target_process_id):
        """Rule 2: Sending a message."""
        # First, increment own clock for the 'send' event.
        self.vector_clock[self.id] += 1
        print(
            f"Process {self.id} | Send to P{target_process_id} | Clock: {self.vector_clock}"
        )

        # Send a copy of the vector clock with the message.
        message = {"sender_id": self.id, "vector": list(self.vector_clock)}

        # Directly call the receive method of the target process.
        ALL_PROCESSES[target_process_id].receive_message(message)

    def receive_message(self, message):
        """Rule 3: Receiving a message."""
        received_vector = message["vector"]

        # Update local vector by taking the element-wise maximum.
        for i in range(NUM_PROCESSES):
            self.vector_clock[i] = max(self.vector_clock[i], received_vector[i])

        # Finally, increment own clock for the 'receive' event.
        self.vector_clock[self.id] += 1
        print(
            f"Process {self.id} | Recv from P{message['sender_id']} | Clock: {self.vector_clock}"
        )

    def run(self):
        """Main loop for the process thread."""
        while run_simulation:
            time.sleep(random.uniform(1, 2))
            # Randomly choose an action
            if random.random() > 0.5:
                self.local_event()
            else:
                possible_targets = [i for i in range(NUM_PROCESSES) if i != self.id]
                if possible_targets:
                    target_id = random.choice(possible_targets)
                    self.send_message(target_id)


if __name__ == "__main__":
    # 1. Create all process instances
    for i in range(NUM_PROCESSES):
        ALL_PROCESSES[i] = Process(process_id=i)

    # 2. Start all process threads
    threads = []
    for i in range(NUM_PROCESSES):
        thread = threading.Thread(target=ALL_PROCESSES[i].run)
        threads.append(thread)
        thread.start()

    # 3. Let the simulation run for a bit
    time.sleep(10)
    run_simulation = False
    print("\n--- Stopping simulation... ---")
    for t in threads:
        t.join()
