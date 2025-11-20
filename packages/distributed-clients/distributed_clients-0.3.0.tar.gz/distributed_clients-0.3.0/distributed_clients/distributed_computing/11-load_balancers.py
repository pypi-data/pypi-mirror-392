import time
import random
import threading

# -----------------------------
# Backend Server (Threaded)
# -----------------------------
class BackendServer:
    def __init__(self, id):
        self.id = id
        self.active_connections = 0
        self.lock = threading.Lock()

    def handle_request(self, request):
        thread = threading.Thread(target=self.process_request, args=(request,))
        thread.start()

    def process_request(self, request):
        with self.lock:
            self.active_connections += 1
            active = self.active_connections

        print(f"[START] Server {self.id} handling {request} | Active={active}")

        # Simulate work
        time.sleep(random.uniform(0.5, 1.5))

        with self.lock:
            self.active_connections -= 1
            active = self.active_connections

        print(f"[END]   Server {self.id} completed {request} | Active={active}")


# -----------------------------
# Load Balancer
# -----------------------------
class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.rr_index = 0  # Round Robin pointer

    # Round Robin
    def round_robin(self, request):
        server = self.servers[self.rr_index]
        self.rr_index = (self.rr_index + 1) % len(self.servers)
        print(f"LB → (RR) Sending {request} to Server {server.id}")
        server.handle_request(request)

    # Least Connections
    def least_connections(self, request):
        server = min(self.servers, key=lambda s: s.active_connections)
        print(f"LB → (LC) Sending {request} to Server {server.id}")
        server.handle_request(request)


# -----------------------------
# Simulation
# -----------------------------
servers = [BackendServer(1), BackendServer(2), BackendServer(3)]
lb = LoadBalancer(servers)

requests = [f"REQ-{i}" for i in range(1, 11)]

print("\n=== ROUND ROBIN MODE ===\n")
for req in requests:
    lb.round_robin(req)
    time.sleep(0.3)  # clients arrive at intervals

# Wait for all threads to finish
time.sleep(5)

print("\n=== LEAST CONNECTIONS MODE ===\n")
for req in requests:
    lb.least_connections(req)
    time.sleep(0.3)

# Wait for remaining threads
time.sleep(5)
