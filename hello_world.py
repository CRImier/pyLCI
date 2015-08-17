from time import sleep

import wcs

application = wcs.wm.create_new_application("Hello world")
window = application.get_window("Hello window")

input = window.input_interface
output = window.output_interface


class HelloWorld():
    running = False

    def __init__(self, input, output):
        self.input = input
        self.output = output

    def run(self):
        self.running = True
        output.display_data("Hello world!", "ENTER to exit")
        input.set_callback('KEY_ENTER', 'stop', self)
        input.set_callback('KEY_KPENTER', 'stop', self)
        while self.running:
            sleep(1)

    def stop(self):
        self.running = False



helloworld = HelloWorld(input, output)

wcs.register_object(helloworld)
wcs.start_daemon_thread()

wcs.wm.activate_app(0) #WM-side - to remove

wcs.run(helloworld.run, application.shutdown) 
