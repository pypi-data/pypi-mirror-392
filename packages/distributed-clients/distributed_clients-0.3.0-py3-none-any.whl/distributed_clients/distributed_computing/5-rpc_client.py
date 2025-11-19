import xmlrpc.client

server = xmlrpc.client.ServerProxy("http://localhost:8000")

print(f"5 + 3 = {server.add(5, 3)}")
print(f"5 - 3 = {server.subtract(5, 3)}")   
print(f"5 * 3 = {server.multiply(5, 3)}")