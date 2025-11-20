import socket
import threading
import sys
import time

N = 3  # number of processes

ports = {1: 8001, 2: 8002, 3: 8003}

pid = int(sys.argv[1])
vector = [0] * N

def update_on_receive(data):
    global vector
    recv_vec = list(map(int, data.split(",")))

    for i in range(N):
        vector[i] = max(vector[i], recv_vec[i])

    vector[pid - 1] += 1  # increment own clock
    print(f"\n[P{pid}] Received message. Updated VC = {vector}")

def listener():
    s = socket.socket()
    s.bind(("localhost", ports[pid]))
    s.listen(5)
    print(f"Process {pid} listening on port {ports[pid]}")

    while True:
        conn, _ = s.accept()
        data = conn.recv(1024).decode()
        update_on_receive(data)
        conn.close()

def send_message(to_pid):
    global vector
    vector[pid - 1] += 1  # increment own clock before send

    msg = ",".join(map(str, vector))
    s = socket.socket()
    s.connect(("localhost", ports[to_pid]))
    s.send(msg.encode())
    s.close()

    print(f"[P{pid}] Sent message to P{to_pid}. VC = {vector}")

threading.Thread(target=listener, daemon=True).start()

time.sleep(1)

while True:
    to = int(input(f"[P{pid}] Send message to (1/2/3 except {pid}): "))
    if to in ports and to != pid:
        send_message(to)
