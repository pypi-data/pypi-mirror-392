import time
import random

# -----------------------------
# Server with Lamport + Unsynced Clock
# -----------------------------
class Server:
    def __init__(self, server_id):
        self.server_id = server_id
        self.lamport = 0

    def generate_log(self, message):
        # Increment Lamport clock
        self.lamport += 1

        # Unsynchronized physical timestamp (simulate drift)
        raw_ts = time.time() + random.uniform(-5, 5)

        log = {
            "server": self.server_id,
            "message": message,
            "raw_timestamp": raw_ts,      # UNSYNCHRONIZED CLOCK
            "lamport": self.lamport       # SYNCHRONIZED ORDER CLOCK
        }

        print(f"[Server {self.server_id}] Generated log → {log}")
        return log


# -----------------------------
# Central Log Manager
# -----------------------------
class LogManager:
    def __init__(self):
        self.logs = []

    def collect(self, log):
        self.logs.append(log)

    def merge_logs(self):
        # Sorting by Lamport clock + tie-break by server ID
        self.logs.sort(key=lambda x: (x["lamport"], x["server"]))

    def show(self):
        print("\n========= CENTRALIZED ORDERED LOGS (Lamport Ordered) =========\n")
        for log in self.logs:
            print(
                f"Server-{log['server']} | "
                f"LC={log['lamport']} | "
                f"raw={log['raw_timestamp']} | "
                f"event='{log['message']}'"
            )


# -----------------------------
# Simulation
# -----------------------------
s1 = Server(1)
s2 = Server(2)
s3 = Server(3)

manager = LogManager()

print("\n=== Distributed Logging Simulation (Unsynced Clocks + Lamport Clock) ===\n")

# Simulated logs from each server
log1 = s1.generate_log("User logged in")
time.sleep(0.2)

log2 = s2.generate_log("File uploaded")
time.sleep(0.1)

log3 = s3.generate_log("Access granted")

log4 = s2.generate_log("Warning: High CPU usage")
log5 = s1.generate_log("User logged out")

# Collect logs at central system
manager.collect(log1)
manager.collect(log2)
manager.collect(log3)
manager.collect(log4)
manager.collect(log5)

# Merge logs into correct order using Lamport clock
manager.merge_logs()

# Show final ordered logs
manager.show()
