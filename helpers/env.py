import psutil
import os

def zpui_running_as_service():
    if psutil.Process(os.getpid()).ppid() == 1:
        return True;
    else:
        return False;
