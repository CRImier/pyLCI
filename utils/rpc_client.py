from jsonrpclib import Server
import threading
import socket

class RPCCommError(Exception):
    pass

class RPCClient(Server):

    functions = None

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._server = Server("http://{}:{}".format(self.host, self.port))
        #self.retrieve_function_list()
        
    def wrapper(self, func):
        return RPCFunction(func)

    def retrieve_function_list(self):
        try:
            self.functions = self.__getattr__("list_functions")()
        except RPCCommError:
            self.functions = None

    def __getattr__(self, attr_name):
        #print("Getting attribute {}".format(attr_name))
        try:
            attr = self._server.__getattr__(attr_name)
        except socket.error as e:
            if e.errno == 111:
                error = RPCCommError("Connection refused")
                error.errno = e.errno
                raise error
        return self.wrapper(attr)

class RPCFunction():
    def __init__(self, func):
        self.func = func

    def __eq__(self, other):
        return False

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except socket.error as e:
            if e.errno == 111:
                error = RPCCommError("Connection refused")
                error.errno = e.errno
                raise error
