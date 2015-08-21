from time import sleep

import wcs

application = wcs.wm.create_new_application("Counter app")
window = application.get_window("Counter window")

input = window.input_interface
output = window.output_interface


class Counter():
    running = False

    prompt = "Counter value is:"
    counter = 0

    def __init__(self, input, output):
        self.input = input
        self.output = output

    def run(self):
        self.running = True
        input.set_callback('KEY_KPPLUS', 'increment', self)
        input.set_callback('KEY_KPMINUS', 'decrement', self)
        input.set_callback('KEY_BACKSPACE', 'reset', self)
        input.set_callback('KEY_ENTER', 'stop', self)
        input.set_callback('KEY_KPENTER', 'stop', self)
        self.refresh()
        while self.running:
            sleep(1)

    def increment(self):
        self.counter += 1
        self.refresh()

    def decrement(self):
        self.counter -= 1
        self.refresh()

    def reset(self):
        self.counter = 0
        self.refresh()

    def refresh(self):
        self.output.display_data(self.prompt, str(self.counter))

    def stop(self):
        self.running = False


counter = Counter(input, output)

wcs.register_object(counter)
wcs.start_daemon_thread()

wcs.wm.activate_app(application.number) #WM-side - to remove

wcs.run(counter.run, application.shutdown) 
