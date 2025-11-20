import socket
import threading
import sys
import time

ports = {1: 9001, 2: 9002, 3: 9003, 4: 9004, 5: 9005}

pid = int(sys.argv[1])
alive = True

def send(to, message):
    try:
        s = socket.socket()
        s.connect(("localhost", ports[to]))
        s.send(message.encode())
        s.close()
    except:
        pass

def start_election():
    print(f"\nNode {pid} starting election...")
    higher = [p for p in ports if p > pid]

    replied = False
    for h in higher:
        try:
            send(h, "ELECTION")
        except:
            pass

    # Wait for any OK replies
    time.sleep(2)

    if not replied:
        announce_coordinator()

def announce_coordinator():
    global coordinator
    coordinator = pid
    print(f"*** Node {pid} is the NEW COORDINATOR ***")

    for p in ports:
        if p != pid:
            send(p, f"COORDINATOR:{pid}")

def listener():
    global coordinator

    s = socket.socket()
    s.bind(("localhost", ports[pid]))
    s.listen(5)
    print(f"Node {pid} listening on port {ports[pid]}")

    while True:
        conn, _ = s.accept()
        data = conn.recv(1024).decode().strip()
        conn.close()

        if data == "ELECTION":
            print(f"Node {pid} received ELECTION. Sending OK.")
            send(int(_.split(":")[1]) if False else pid, "OK")  # dummy return
            start_election()

        elif data == "OK":
            pass

        elif "COORDINATOR" in data:
            leader = int(data.split(":")[1])
            print(f"Node {pid} recognizes Leader = {leader}")

threading.Thread(target=listener, daemon=True).start()

time.sleep(1)

print(f"Node {pid} ready.")

while True:
    cmd = input("Enter 'E' to start election: ").strip().upper()
    if cmd == "E":
        start_election()
