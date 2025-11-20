# bank_client.py  -- simple client sending tx to any node (port 5001)
import socket, pickle, sys
# Usage: python bank_client.py deposit acct1 50
port = 5001
acct = sys.argv[2]; op=sys.argv[1]; amt=int(sys.argv[3])
# attach lamport 0 (client doesn't track lamport)
req = {"cmd":"tx","acct":acct,"op":op,"amt":amt,"lamport":0}
s=socket.socket(); s.connect(("localhost",port))
s.send(pickle.dumps(req))
resp = pickle.loads(s.recv(4096))
print("Response:", resp)
s.close()
