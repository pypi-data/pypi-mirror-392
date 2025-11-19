import socket
import threading

def handle_client(client_socket, addr):
    while True:
        data = client_socket.recv(1024).decode()
        print(f"Request received: {data}")

        response = data.upper()
        client_socket.send(response.encode())
        print(f"Response sent: {response}")
    
    client_socket.close()
    print(f"Client disconnected: {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 8000))
    server.listen(5)
    print("Server started. Listening on port 8000...")

    while True:
        client_socket, addr = server.accept()
        print(f"Client connected: {addr}")

        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()
        print(f"Thread started for client: {addr}")
        print(f"Active threads: {threading.active_count()-1}")

start_server()