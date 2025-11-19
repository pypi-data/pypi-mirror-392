# apikey_server.py
import threading, socket, pickle, time, uuid
PORT=9200

class KeyManager:
    def __init__(self):
        self.lock=threading.Lock()
        self.keys={}  # key -> {"expiry":ts, "blocked":False, "last_keep":ts}
        threading.Thread(target=self.gc,daemon=True).start()

    def create(self):
        k=str(uuid.uuid4())[:8]
        with self.lock:
            self.keys[k]={"expiry":time.time()+300,"blocked":False,"last_keep":time.time(),"assigned":False}
        return k

    def retrieve(self):
        with self.lock:
            for k,v in self.keys.items():
                if not v["blocked"] and not v["assigned"] and v["expiry"]>time.time():
                    v["blocked"]=True; v["assigned"]=True; v["last_keep"]=time.time()
                    # auto-unblock in 60s if not unblocked explicitly
                    threading.Timer(60, self.auto_unblock, args=(k,)).start()
                    return k
        return None

    def unblock(self,k):
        with self.lock:
            if k in self.keys:
                self.keys[k]["blocked"]=False; self.keys[k]["assigned"]=False
                return True
        return False

    def keepalive(self,k):
        with self.lock:
            if k in self.keys:
                self.keys[k]["expiry"]=time.time()+300; self.keys[k]["last_keep"]=time.time(); return True
        return False

    def auto_unblock(self,k):
        with self.lock:
            if k in self.keys and self.keys[k]["assigned"] and time.time()-self.keys[k]["last_keep"]>60:
                self.keys[k]["blocked"]=False; self.keys[k]["assigned"]=False

    def gc(self):
        while True:
            with self.lock:
                todel=[k for k,v in self.keys.items() if v["expiry"]<time.time()]
                for k in todel: del self.keys[k]
            time.sleep(5)

km=KeyManager()

# Simple TCP command server
s=socket.socket(); s.bind(("localhost", PORT)); s.listen(5)
print("API key server on", PORT)
while True:
    conn, _ = s.accept()
    cmd = conn.recv(1024).decode().split()
    if cmd[0]=="CREATE":
        conn.send(km.create().encode())
    elif cmd[0]=="RETRIEVE":
        k=km.retrieve(); conn.send((k or "NONE").encode())
    elif cmd[0]=="UNBLOCK":
        conn.send(str(km.unblock(cmd[1])).encode())
    elif cmd[0]=="KEEP":
        conn.send(str(km.keepalive(cmd[1])).encode())
    conn.close()
