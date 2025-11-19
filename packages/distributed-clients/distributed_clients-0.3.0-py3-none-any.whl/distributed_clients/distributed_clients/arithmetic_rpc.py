# EXP 5
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


def add(numbers):
    """Takes a list of numbers and returns their sum."""
    print(f"[Server] Executing 'add' with {numbers}")
    return sum(numbers)


def subtract(numbers):
    """Takes a list of two numbers [a, b] and returns a - b."""
    print(f"[Server] Executing 'subtract' with {numbers}")
    return numbers[0] - numbers[1]


def multiply(numbers):
    """Takes a list of numbers and returns their product."""
    print(f"[Server] Executing 'multiply' with {numbers}")
    result = 1
    for num in numbers:
        result *= num
    return result


# --- 2. The Server Setup ---


def run_server():
    """Initializes and runs the multithreaded RPC server."""
    server_address = ("localhost", 8000)
    server = ThreadingXMLRPCServer(server_address)

    # Register the arithmetic functions for clients to call
    server.register_function(add, "add")
    server.register_function(subtract, "subtract")
    server.register_function(multiply, "multiply")

    print("Arithmetic RPC Server is running on http://localhost:8000...")
    server.serve_forever()


# --- 3. The Client Simulation ---


def run_client_simulation():
    """Simulates a client making several arithmetic calls."""
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

    try:
        print("\n--- Client starting RPC calls ---")

        # Call 'add'
        add_result = proxy.add([10, 20, 30])
        print(f"[Client] Result of add([10, 20, 30]): {add_result}")

        # Call 'subtract'
        sub_result = proxy.subtract([100, 33])
        print(f"[Client] Result of subtract([100, 33]): {sub_result}")

        # Call 'multiply'
        mul_result = proxy.multiply([5, 2, 10])
        print(f"[Client] Result of multiply([5, 2, 10]): {mul_result}")

        print("--- Client calls finished ---")

    except Exception as e:
        print(f"[Client] An error occurred: {e}")


# --- 4. Main Execution ---

if __name__ == "__main__":
    # Start the server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give server time to start

    # Run the client simulation
    run_client_simulation()
