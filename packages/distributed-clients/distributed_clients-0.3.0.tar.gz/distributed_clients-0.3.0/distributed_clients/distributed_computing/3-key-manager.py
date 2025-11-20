import threading
import time
import uuid

class KeyManager:
    def __init__(self):
        self.keys = {}  # key → {"status": "free/block", "last_alive": timestamp}
        self.lock = threading.Lock()

        # Start cleanup thread
        threading.Thread(target=self.cleanup_loop, daemon=True).start()

    # -------------------------------
    # 1. Generate a new API key
    # -------------------------------
    def create_key(self):
        key = str(uuid.uuid4())
        with self.lock:
            self.keys[key] = {
                "status": "free",
                "last_alive": time.time()
            }
        print(f"[CREATE] Key created → {key}")
        return key

    # -------------------------------
    # 2. Get an available key
    # -------------------------------
    def get_key(self):
        with self.lock:
            for key, info in self.keys.items():
                if info["status"] == "free":
                    info["status"] = "blocked"
                    info["blocked_time"] = time.time()
                    print(f"[ASSIGN] Key assigned → {key}")
                    return key

        print("[ASSIGN] No keys available")
        return None

    # -------------------------------
    # 3. Unblock a key manually
    # -------------------------------
    def unblock_key(self, key):
        with self.lock:
            if key in self.keys and self.keys[key]["status"] == "blocked":
                self.keys[key]["status"] = "free"
                print(f"[UNBLOCK] Key unblocked → {key}")

    # -------------------------------
    # 4. Keep Alive - extend life
    # -------------------------------
    def keep_alive(self, key):
        with self.lock:
            if key in self.keys:
                self.keys[key]["last_alive"] = time.time()
                print(f"[ALIVE] Keep-alive → {key}")

    # -----------------------------------------
    # 5. Background cleanup: delete expired keys
    #    delete if no keep-alive for 5 minutes
    #    auto-unblock after 60 seconds
    # -----------------------------------------
    def cleanup_loop(self):
        while True:
            now = time.time()
            with self.lock:
                to_delete = []
                for key, info in list(self.keys.items()):

                    # Delete keys older than 5 minutes (300 seconds)
                    if now - info["last_alive"] > 300:
                        print(f"[DELETE] Key expired → {key}")
                        to_delete.append(key)

                    # Auto-unblock after 60 seconds
                    if info["status"] == "blocked" and now - info["blocked_time"] > 60:
                        info["status"] = "free"
                        print(f"[AUTO-UNBLOCK] Key auto-released → {key}")

                # Remove expired keys
                for key in to_delete:
                    del self.keys[key]

            time.sleep(5)  # cleanup every 5 sec


# -------------------------------
# SIMULATION / TESTING
# -------------------------------

km = KeyManager()

print("\n=== Key Manager Demo ===")

k1 = km.create_key()
k2 = km.create_key()
k3 = km.create_key()

# Assign key
assigned = km.get_key()

# Keep alive
km.keep_alive(assigned)

# Unblock manually
time.sleep(2)
km.unblock_key(assigned)

# Auto cleanup demonstration
print("\nWait for auto-cleanup...")
time.sleep(10)
