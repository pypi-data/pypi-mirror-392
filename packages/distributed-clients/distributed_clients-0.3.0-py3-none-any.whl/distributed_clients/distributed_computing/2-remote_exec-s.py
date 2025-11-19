from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import traceback

# Multithreaded RPC server
class ThreadedRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

# --- Sandbox execution function ---
def execute_code(code):
    try:
        # Very light sandbox: restricted globals
        allowed_globals = {"__builtins__": {"print": print, "len": len}}
        local_vars = {}

        exec(code, allowed_globals, local_vars)

        # return local variables as output
        return {"status": "success", "output": local_vars}

    except Exception as e:
        return {"status": "error", "output": traceback.format_exc()}


def main():
    server = ThreadedRPCServer(("localhost", 8000), allow_none=True)
    server.register_function(execute_code, 'execute')

    print("RPC Execution Server running on port 8000...")
    server.serve_forever()

if __name__ == "__main__":
    main()
