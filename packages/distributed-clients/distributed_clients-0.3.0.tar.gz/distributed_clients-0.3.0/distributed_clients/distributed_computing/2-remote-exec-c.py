import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

# Example code snippet to execute remotely
code = """
result = 0
for i in range(1, 11):
    result += i
"""

print("Sending code to server...")
response = proxy.execute(code)
print("Server Response:", response)
