import psutil
import os

def is_running_under_systemd():
    if psutil.Process(os.getpid()).ppid() == 1:
        return true;
    else:
        return false;
