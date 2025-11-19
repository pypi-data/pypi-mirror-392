import socket
s=socket.socket(); s.connect(("localhost",9400))
s.send(b"hello server"); print(s.recv(1024)); s.close()
