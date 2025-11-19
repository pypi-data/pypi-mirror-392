import xmlrpc.client
p = xmlrpc.client.ServerProxy("http://localhost:9300/")
print(p.add(5,7), p.sub(10,3), p.mul(4,6))
