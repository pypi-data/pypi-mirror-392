# rce_server.py
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import math, threading

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer): pass

# Allowed operations mapping (avoid exec for safety). Add functions here.
def run_task(task_name, args):
    if task_name=="fib":
        n=int(args[0]); a,b=0,1
        for _ in range(n): a,b=b,a+b
        return a
    if task_name=="sort":
        arr=list(args[0])
        return sorted(arr)
    if task_name=="sum":
        return sum(args)
    if task_name=="reverse":
        return args[0][::-1]
    return "unknown task"

server = ThreadedXMLRPCServer(("localhost", 9100), allow_none=True)
server.register_function(run_task, "run_task")
print("RCE server threaded running on 9100")
server.serve_forever()
