class Process:
    def __init__(self, id, total):
        self.id = id
        self.clock = [0] * total

    def internal_event(self):
        self.clock[self.id] += 1
        print(f"\nProcess {self.id} INTERNAL EVENT | VC={self.clock}")

    def send(self, receiver):
        self.clock[self.id] += 1
        print(f"\nProcess {self.id} SEND -> Process {receiver.id} | VC={self.clock}")
        receiver.receive(self.clock)

    def receive(self, incoming_clock):
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], incoming_clock[i])

        self.clock[self.id] += 1
        print(f"Process {self.id} RECEIVE | Updated VC={self.clock}")


# ---- Simulation ----
n0 = Process(0, 3)
n1 = Process(1, 3)
n2 = Process(2, 3)

print("\n--- Vector Clock---")

n0.send(n1)    # event 1
n1.send(n2)    # event 2
n2.send(n0)    # event 3

print("\n--- Final Vector Clocks ---")
print("Process 0:", n0.clock)
print("Process 1:", n1.clock)
print("Process 2:", n2.clock)
