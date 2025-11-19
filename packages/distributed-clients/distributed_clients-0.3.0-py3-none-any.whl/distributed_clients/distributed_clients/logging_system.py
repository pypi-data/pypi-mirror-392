# EXP 4
# uses Berkeley's Algorithm
import threading
import time
import random
from datetime import datetime, timedelta

# --- Global State & Configuration ---
NUM_SERVERS = 3
SIMULATION_TIME_SECONDS = 8
LOG_MANAGER = []
SERVER_OFFSETS = {i + 1: timedelta(0) for i in range(NUM_SERVERS)}
run_simulation = True

# A lock to safely append to the global log manager from multiple threads
log_lock = threading.Lock()

# --- Server Simulation ---


def server_node(server_id):
    """
    Simulates a server with its own drifting clock that generates logs.
    """
    # Simulate an inaccurate clock with a random drift
    # The drift makes this server's clock run faster or slower than real time.
    drift = random.uniform(-0.1, 0.1)
    current_time = datetime.now()

    print(
        f"[Server {server_id}] Started with a clock drift of {drift:.2f}s per second."
    )

    while run_simulation:
        # Simulate time passing and apply drift
        time.sleep(1)
        current_time += timedelta(seconds=1 + drift)

        # Generate a log event periodically
        if random.random() > 0.5:
            log_entry = {
                "server_id": server_id,
                "raw_timestamp": current_time,
                "event": f"Generated event on Server {server_id}",
            }
            with log_lock:
                LOG_MANAGER.append(log_entry)
            print(
                f"[Server {server_id}] Logged event at raw time {current_time.strftime('%H:%M:%S.%f')}"
            )


# --- Berkeley Algorithm Time Daemon ---


def time_daemon():
    """
    Acts as the master node for Berkeley's Algorithm. Periodically polls servers,
    calculates the average time, and computes the offsets for synchronization.

    Note: In a real system, this would poll over a network. Here we just read
    the simulated times from the server threads (which is a simplification).
    For this simulation, we will just use the system time of the daemon as the
    source of truth to calculate offsets against the servers' drifting clocks.
    This demonstrates the principle of calculating and applying offsets.
    """
    print("[Daemon] Time Daemon started. Will synchronize every 3 seconds.")

    while run_simulation:
        time.sleep(3)
        print("\n[Daemon] --- Starting synchronization round ---")

        # In a real system, the daemon would ask each server for its time.
        # Here, we simulate this by calculating the difference between the 'true'
        # time (the daemon's clock) and what the server's clock *would* be.
        # Since we can't directly access the 'current_time' variable of the
        # server threads, we will just pre-calculate the expected drift.
        # For a more realistic simulation, servers would need an API endpoint to expose their time.

        # A simplified model for this simulation:
        # We will assume the log manager has recent entries and use them to
        # estimate the current clock offset of each server.

        with log_lock:
            if not LOG_MANAGER:
                continue

            latest_logs = {sid: None for sid in range(1, NUM_SERVERS + 1)}
            for log in reversed(LOG_MANAGER):
                if latest_logs[log["server_id"]] is None:
                    latest_logs[log["server_id"]] = log["raw_timestamp"]
                if all(latest_logs.values()):
                    break

            # Calculate offsets based on the daemon's current time
            master_time = datetime.now()
            time_diffs = []
            for server_id, server_time in latest_logs.items():
                if server_time:
                    diff = master_time - server_time
                    SERVER_OFFSETS[server_id] = diff
                    time_diffs.append(diff)
                    print(
                        f"[Daemon] Server {server_id} clock is off by {diff.total_seconds():.2f}s"
                    )

        print("[Daemon] --- Synchronization round finished ---\n")


# --- Main Execution ---

if __name__ == "__main__":
    # 1. Start the Time Daemon thread
    daemon_thread = threading.Thread(target=time_daemon)
    daemon_thread.start()

    # 2. Start all the Server Node threads
    server_threads = []
    for i in range(NUM_SERVERS):
        server_id = i + 1
        thread = threading.Thread(target=server_node, args=(server_id,))
        server_threads.append(thread)
        thread.start()

    # 3. Let the simulation run for a configured duration
    time.sleep(SIMULATION_TIME_SECONDS)
    run_simulation = False  # Signal all threads to stop

    # 4. Wait for all threads to complete
    for t in server_threads:
        t.join()
    daemon_thread.join()

    print("\n" + "=" * 50)
    print("--- SIMULATION FINISHED ---")
    print("=" * 50 + "\n")

    # 5. Show the logs ordered by their original, unsynchronized timestamps
    print("--- 1. Logs ordered by RAW (unsynchronized) timestamp ---")
    print("--- (This shows how events can appear out of order) ---\n")
    sorted_by_raw = sorted(LOG_MANAGER, key=lambda x: x["raw_timestamp"])
    for log in sorted_by_raw:
        print(
            f"RAW Time: {log['raw_timestamp'].strftime('%H:%M:%S.%f')} | Server ID: {log['server_id']} | Event: {log['event']}"
        )

    # 6. Show the logs ordered by the synchronized timestamps
    print("\n\n--- 2. Logs ordered by SYNCHRONIZED timestamp ---")
    print("--- (This shows the globally ordered timeline) ---\n")

    # Add the synchronized timestamp to each log entry before sorting
    for log in LOG_MANAGER:
        log["sync_timestamp"] = log["raw_timestamp"] + SERVER_OFFSETS[log["server_id"]]

    # Sort by the new synchronized timestamp, using server_id as a tie-breaker
    sorted_by_sync = sorted(
        LOG_MANAGER, key=lambda x: (x["sync_timestamp"], x["server_id"])
    )
    for log in sorted_by_sync:
        print(
            f"SYNC Time: {log['sync_timestamp'].strftime('%H:%M:%S.%f')} | (Raw: {log['raw_timestamp'].strftime('%H:%M:%S.%f')}) | Server ID: {log['server_id']}"
        )
