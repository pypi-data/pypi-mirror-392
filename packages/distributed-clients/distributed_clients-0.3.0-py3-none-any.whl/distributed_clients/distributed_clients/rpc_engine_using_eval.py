# EXP 2
# dont use mostly
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


# ########################################################################## #
# # --- EXTREME WARNING: EVEN MORE DANGEROUS ---                           # #
# # Using exec() is the most dangerous way to handle remote code. It allows # #
# # a client to run ANY code on the server, including defining functions,   # #
# # infinite loops, deleting files, etc. This is for simulation ONLY.      # #
# ########################################################################## #

# --- 1. The Server's Code Executor Function ---


def execute_multiline_code(code_snippet):
    """
    Executes a multiline block of Python code using exec().
    It looks for a variable named 'result' to return to the client.
    """
    thread_name = threading.current_thread().name
    print(f"[Server - {thread_name}] --- Executing multiline snippet ---")
    print(code_snippet)
    print("--------------------------------------------------")

    try:
        # Create a dictionary to hold the local variables for the executed code.
        local_scope = {}

        # Use exec() to run the block of statements. The results (variables)
        # will be stored in the local_scope dictionary.
        exec(code_snippet, {}, local_scope)

        # The convention is that the client's code should assign its output
        # to a variable named 'result'.
        if "result" in local_scope:
            result_value = local_scope["result"]
            print(
                f"[Server - {thread_name}] Execution complete. Found 'result': {result_value}"
            )
            return result_value
        else:
            print(
                f"[Server - {thread_name}] Execution complete. No 'result' variable found."
            )
            return "Execution successful, but no 'result' variable was set."

    except Exception as e:
        error_message = f"Error during execution: {e}"
        print(f"[Server - {thread_name}] {error_message}")
        return error_message


# --- 2. The Server Setup ---


def run_server():
    """Initializes and runs the multiline-capable RPC server."""
    server_address = ("localhost", 8000)
    server = ThreadingXMLRPCServer(server_address)
    server.register_function(execute_multiline_code, "execute")
    print(
        f"Multiline Server ready on http://{server_address[0]}:{server_address[1]}..."
    )
    server.serve_forever()


# --- 3. The Client Simulation ---


def run_client(snippet_to_send, client_id):
    """Simulates a client sending a multiline code snippet."""
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
    try:
        print(f"\n[Client {client_id}] Sending multiline snippet...")
        result = proxy.execute(snippet_to_send)
        print(f"[Client {client_id}] Received result: {result}")
    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")


# --- 4. Main Simulation Execution ---

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    print("--- Simulating two clients with multiline snippets ---\n")

    # Client 1: A snippet with intermediate variables
    snippet1 = """
x = 10
y = 20
# The final answer must be in a variable named 'result'
result = f"The sum of {x} and {y} is {x + y}"
"""

    # Client 2: A snippet with a loop to find prime numbers
    snippet2 = """
primes = []
for num in range(2, 50):
    is_prime = True
    for i in range(2, num):
        if (num % i) == 0:
            is_prime = False
            break
    if is_prime:
        primes.append(num)
# Assign the final list to the 'result' variable
result = primes
"""

    # Run the clients concurrently
    client1 = threading.Thread(target=run_client, args=(snippet1, 1))
    client2 = threading.Thread(target=run_client, args=(snippet2, 2))

    client1.start()
    client2.start()

    client1.join()
    client2.join()

    print("\n--- Simulation finished ---")
