import socket
def send(cmd):
    s=socket.socket(); s.connect(("localhost",9200)); s.send(cmd.encode()); r=s.recv(1024).decode(); s.close(); return r

print(send("CREATE"))
k=send("CREATE"); print("created",k)
print("retrieve:", send("RETRIEVE"))
# keepalive: send("KEEP <key>")
# unblock: send("UNBLOCK <key>")
