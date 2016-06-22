from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import threading

class RPCApi():

    functions = []

    def __init__(self, config):
        self.config = config
        self.server = SimpleJSONRPCServer((self.config['rpc_host'], self.config['rpc_port']))
        self.server.timeout = self.config['rpc_timeout'] if "rpc_timeout" in config else 1
        self.register_function(self.list_functions, "list_functions")
        
    def register_functions(self, **kwargs):
        """Registers functions with the server."""
        for function_name in kwargs:
            function = kwargs[function_name]
            self.register_function(function, function_name)

    def register_function(self, function, function_name):
        """Registers a single function with the server."""
        self.server.register_function(function, function_name)
        self.functions.append(function_name)

    def list_functions(self):
        """An externally accessible function returning all the registered function names"""
        return list(set(self.functions))

    def poll(self):
        """Serves one request from the waiting requests and returns"""
        self.server.handle_request()

    def run(self):
        """Blocks execution and runs the server till the program shutdown"""
        self.server.serve_forever()

    def start_thread(self):
        """Starts self.run() in a separate thread"""
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
