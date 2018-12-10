import os
from helpers import ProHelper, setup_logger

logger = setup_logger(__name__, "debug")

class MTKDownloadProcess(object):
    state = "not_started"
    output = ""

    def __init__(self, port, fw_dir, path="mtkdownload", callback=None):
        self.mtkdownload_path = path
        self.port = port
        self.callback = callback
        self.fw_dir = fw_dir
        self.output = []

    def mtkdownload_is_available(self):
        try:
            p = ProHelper([self.mtkdownload_path], use_terminal=True, output_callback=None)
            p.run_in_foreground()
            if p.get_return_code() != 1:
                return False
            return True
        except OSError:
            False

    def gen_commandline(self, format_fat="Y"):
        return [self.mtkdownload_path, self.port, "ROM_VIVA", format_fat]

    def write_image(self):
        self.state = "not_started"
        self.output = ""
        commandline = self.gen_commandline()
        p = ProHelper(commandline, cwd=self.fw_dir, use_terminal=True, output_callback=self.process_output)
        p.run()
        self.state = "started"
        while p.is_ongoing():
            p.poll()
            if not p.is_ongoing():
                rc = p.get_return_code()
                if rc != 0:
                    self.state = "failed"
                else:
                    self.state = "finished"
            if callable(self.callback):
                self.callback(self.get_state)

    def process_output(self, output):
        print(repr(output))
        self.output += output

    def get_state(self):
        s_d = {"state":self.state, "output":self.output}
        if self.state in ["started", "finished", "not_started"]:
            return s_d
        elif self.state == "failed":
            s_d["returncode"] = self.p.get_return_code()
            return s_d

def collect_fw_folders(base_path, key="SIM800", check_cfg=True, requirements=["ROM", "ROM_VIVA", "VIVA"]):
    unsorted_paths = []
    for path in os.listdir(base_path):
        full_path = os.path.join(base_path, path)
        if os.path.isdir(full_path):
            if key not in path:
                logger.debug("{} doesn't have \"{}\" key in it, continuing".format(path, key))
                continue
            fw_files = os.listdir(full_path)
            version = None
            if "sim_fw_zp_version" in fw_files:
                with open(os.path.join(full_path, "sim_fw_zp_version")) as f:
                    version = f.read().strip()
            if check_cfg and not "{}.cfg".format(path) in fw_files:
                logger.debug("{} doesn't have CFG, continuing".format(path))
                continue
            if not all([req in fw_files for req in requirements]):
                logger.debug("{} doesn't have one of the requirements, continuing".format(path))
                continue
            unsorted_paths.append([version, full_path])
    logger.debug(unsorted_paths)
    paths = [path for v, path in reversed(sorted(unsorted_paths))]
    return paths
