from xmlrpc.server import SimpleXMLRPCServer

server = SimpleXMLRPCServer(("localhost", 8000))
print("Server started. Listening on port 8000")

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

server.register_function(add, "add")
server.register_function(subtract, "subtract")
server.register_function(multiply, "multiply")

server.serve_forever()