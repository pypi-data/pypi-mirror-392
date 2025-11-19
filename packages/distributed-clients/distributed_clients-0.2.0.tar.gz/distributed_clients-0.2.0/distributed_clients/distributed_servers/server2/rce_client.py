# rce_client.py
import xmlrpc.client
proxy = xmlrpc.client.ServerProxy("http://localhost:9100/")
print(proxy.run_task("sum", (1,2,3,4)))
print(proxy.run_task("fib", (10,)))
print(proxy.run_task("sort", ([5,2,3,1],)))
