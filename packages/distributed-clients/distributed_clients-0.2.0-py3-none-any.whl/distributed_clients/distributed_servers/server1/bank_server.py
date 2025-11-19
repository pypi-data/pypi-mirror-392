# bank_server.py  -- run as: python bank_server.py
import threading, socket, pickle, time

# Configuration: list of nodes (ports) and ids
NODES = [(5001,1),(5002,2),(5003,3)]
HEARTBEAT_INTERVAL = 1.0

# Each server as a thread-based node
class Node(threading.Thread):
    def __init__(self, port, nid, nodes):
        super().__init__(daemon=True)
        self.port = port; self.id = nid; self.nodes = nodes
        self.balances = {"acct1":100}
        self.coordinator = max(n for _,n in nodes)
        self.lamport = 0
        self.alive = True
        self.leader_alive = True

    def run(self):
        threading.Thread(target=self.heartbeat_listener, daemon=True).start()
        threading.Thread(target=self.monitor_leader, daemon=True).start()
        s = socket.socket(); s.bind(("localhost", self.port)); s.listen(5)
        while self.alive:
            conn, _ = s.accept()
            msg = pickle.loads(conn.recv(4096))
            cmd = msg["cmd"]
            if cmd=="tx":         # transaction request (from client)
                # increment lamport on receive
                self.lamport = max(self.lamport, msg["lamport"]) + 1
                if self.coordinator == self.id:
                    # leader performs and replicates
                    self.apply_and_replicate(msg, conn)
                else:
                    # forward to coordinator
                    self.forward_to_leader(msg, conn)
            elif cmd=="replicate":
                # replicate state (lamport included)
                self.lamport = max(self.lamport, msg["lamport"]) + 1
                self.balances = msg["balances"]
                conn.send(pickle.dumps({"status":"ok"}))
            elif cmd=="election":
                # bully: reply if higher id exists
                conn.send(pickle.dumps({"id":self.id}))
            conn.close()

    def apply_and_replicate(self, msg, conn):
        # apply transaction deterministically: deposit/withdraw
        acct, op, amt = msg["acct"], msg["op"], msg["amt"]
        if op=="deposit": self.balances[acct] = self.balances.get(acct,0)+amt
        elif op=="withdraw": self.balances[acct] = self.balances.get(acct,0)-amt
        # increase lamport and replicate
        self.lamport += 1
        for (p,n) in self.nodes:
            if n!=self.id:
                try:
                    s=socket.socket(); s.connect(("localhost",p))
                    s.send(pickle.dumps({"cmd":"replicate","balances":self.balances,"lamport":self.lamport}))
                    s.close()
                except: pass
        conn.send(pickle.dumps({"status":"applied","lamport":self.lamport,"leader":self.id}))

    def forward_to_leader(self, msg, conn):
        # forward request to leader and return leader response to client
        leader_port = [p for p,n in self.nodes if n==self.coordinator][0]
        try:
            s=socket.socket(); s.connect(("localhost", leader_port))
            s.send(pickle.dumps(msg))
            resp = pickle.loads(s.recv(4096))
            conn.send(pickle.dumps(resp))
            s.close()
        except Exception as e:
            conn.send(pickle.dumps({"status":"leader_unreachable"}))

    def heartbeat_listener(self):
        # very simple: accept heartbeat pings (we don't implement explicit pings for brevity)
        pass

    def monitor_leader(self):
        while self.alive:
            if self.coordinator==self.id:
                # I'm leader: send heartbeats (not implemented as messages to save space)
                self.leader_alive = True
            else:
                # check leader by attempting connection
                leader_port = [p for p,n in self.nodes if n==self.coordinator][0]
                try:
                    s=socket.socket(); s.settimeout(0.5)
                    s.connect(("localhost", leader_port)); s.close()
                    self.leader_alive = True
                except:
                    self.leader_alive = False
                    # start Bully election
                    self.start_bully()
            time.sleep(HEARTBEAT_INTERVAL)

    def start_bully(self):
        # Bully algorithm: ask higher-id nodes; if none respond, become leader
        higher = [ (p,n) for p,n in self.nodes if n>self.id ]
        got_reply=False
        for p,n in higher:
            try:
                s=socket.socket(); s.settimeout(0.5)
                s.connect(("localhost", p)); s.send(pickle.dumps({"cmd":"election"}))
                reply=pickle.loads(s.recv(4096)); s.close()
                if reply: got_reply=True
            except: pass
        if not got_reply:
            self.coordinator = self.id
            # announce leader by setting coordinator locally (others will detect liveness or learn)
            print(f"Node {self.id} becomes coordinator")

# start nodes (3) in this process for exam convenience
nodes = NODES
threads=[]
for port,nid in nodes:
    t=Node(port,nid,nodes); t.start(); threads.append(t)

print("Bank nodes started. Start clients via bank_client.py")
while True:
    time.sleep(1)
