import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 8000))

while True:
    data = input("Enter a string: ")
    client.send(data.encode())
    response = client.recv(1024).decode()
    print(f"Response received: {response}")

client.close()


