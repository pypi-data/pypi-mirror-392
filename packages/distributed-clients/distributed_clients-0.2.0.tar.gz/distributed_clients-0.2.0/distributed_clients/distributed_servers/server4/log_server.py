# log_server.py  (single process simulation of multiple servers)
import threading, time, queue

NUM=3
logq = queue.Queue()
class Server(threading.Thread):
    def __init__(self, sid):
        super().__init__(daemon=True)
        self.sid=sid; self.lamport=0
    def produce(self,msg):
        self.lamport+=1
        logq.put((self.lamport,self.sid,msg))
    def run(self):
        for i in range(3):
            self.produce(f"event-{i}-from-{self.sid}")
            time.sleep(0.2)

# central manager
def manager():
    collected=[]
    time.sleep(1)
    while not logq.empty(): collected.append(logq.get())
    # sort by (lamport, server id)
    collected.sort(key=lambda x:(x[0], x[1]))
    print("Merged logs (lamport, sid, msg):")
    for e in collected: print(e)

# run
servers=[Server(i+1) for i in range(NUM)]
for s in servers: s.start()
threading.Thread(target=manager,daemon=True).start()
time.sleep(2)
