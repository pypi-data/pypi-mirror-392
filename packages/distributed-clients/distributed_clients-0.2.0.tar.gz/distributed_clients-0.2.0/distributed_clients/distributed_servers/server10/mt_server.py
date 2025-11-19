# mt_server.py
import socket, threading
def handle(conn):
    data=conn.recv(1024).decode()
    # simple processing: uppercase
    conn.send(data.upper().encode()); conn.close()
s=socket.socket(); s.bind(("localhost",9400)); s.listen(5)
print("Multithreaded server on 9400")
while True:
    conn,_=s.accept()
    threading.Thread(target=handle,args=(conn,),daemon=True).start()
