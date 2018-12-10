from helpers import ProHelper

class MTKDownloadProcess(object):
    def __init__(self, path="mtkdownload", parameters=None, base_path=None):
        self.mtkdownload_path = path

    def mtkdownload_is_available(self):
        try:
            p = ProHelper([self.mtkdownload_path], use_terminal=True, output_callback=None)
            p.run_in_foreground()
            if p.get_return_code() != 1:
                return False
            return True
        except OSError:
            False

    def write_image(self):
        pass
