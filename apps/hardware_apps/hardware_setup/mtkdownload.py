from helpers import ProHelper

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
