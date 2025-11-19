from xmlrpc.server import SimpleXMLRPCServer
def add(a,b): return a+b
def sub(a,b): return a-b
def mul(a,b): return a*b
server=SimpleXMLRPCServer(("localhost",9300))
server.register_function(add,"add")
server.register_function(sub,"sub")
server.register_function(mul,"mul")
print("Arithmetic RPC server on 9300"); server.serve_forever()
