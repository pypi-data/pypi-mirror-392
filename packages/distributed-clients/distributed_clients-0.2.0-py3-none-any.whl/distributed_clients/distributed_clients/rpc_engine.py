# EXP 2
import xmlrpc.server
import xmlrpc.client
import threading
import time
from socketserver import ThreadingMixIn


# --- 1. The Server's Defined Remote Functions ---
# --- CHANGE 2: Manually create the ThreadingXMLRPCServer class ---
class ThreadingXMLRPCServer(ThreadingMixIn, xmlrpc.server.SimpleXMLRPCServer):
    """
    This class is a combination of a Threading Server and an XML-RPC Server.
    This is the standard way to create a multithreaded XML-RPC server.
    """

    pass


# --- 1. The Server's Defined Remote Functions ---


def add_numbers(numbers):
    """
    A specific, safe function exposed by the server.
    It takes a list of numbers and returns their sum.
    """
    thread_name = threading.current_thread().name
    print(f"[Server - {thread_name}] Executing 'add_numbers' with {numbers}")
    time.sleep(1)  # Simulate work
    return sum(numbers)


def concatenate_strings(strings):
    """
    Another specific, safe function.
    It takes a list of strings and joins them together.
    """
    thread_name = threading.current_thread().name
    print(f"[Server - {thread_name}] Executing 'concatenate_strings' with {strings}")
    time.sleep(1)  # Simulate work
    return "".join(strings)


# --- 2. The Server Setup ---


def run_server():
    """Initializes and runs the multithreaded RPC server."""
    server_address = ("localhost", 8000)
    # Threading server handles each request in a new thread
    server = ThreadingXMLRPCServer(server_address)

    # Register the functions with the server, giving them names clients will use.
    # The client will call 'add', which will map to our 'add_numbers' function.
    server.register_function(add_numbers, "add")
    server.register_function(concatenate_strings, "concat")

    print(
        f"RPC Server with defined methods is running on http://{server_address[0]}:{server_address[1]}..."
    )
    print("Available methods: add, concat")
    server.serve_forever()


# --- 3. The Client Simulation ---


def run_client(method_to_call, arguments, client_id):
    """
    Simulates a client calling a specific remote method.
    """
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

    try:
        print(f"[Client {client_id}] Calling remote method '{method_to_call}'...")

        # Get the function from the proxy object and call it with arguments
        # For example, if method_to_call is 'add', this becomes proxy.add(arguments)
        remote_function = getattr(proxy, method_to_call)
        result = remote_function(arguments)

        print(f"[Client {client_id}] Received result: {result}")
    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")


# --- 4. Main Simulation Execution ---

if __name__ == "__main__":
    # Start the server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    print("--- Simulating two clients calling different methods concurrently ---\n")

    # Define the tasks for two different clients
    task1_method = "add"
    task1_args = [10, 25, 100, -5]

    task2_method = "concat"
    task2_args = ["Learning ", "about ", "RPC ", "is ", "fun!"]

    # Create and start threads for the clients
    client1 = threading.Thread(target=run_client, args=(task1_method, task1_args, 1))
    client2 = threading.Thread(target=run_client, args=(task2_method, task2_args, 2))

    client1.start()
    client2.start()

    # Wait for both client threads to complete
    client1.join()
    client2.join()

    print("\n--- Simulation finished ---")
