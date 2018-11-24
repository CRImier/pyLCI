from functools import wraps

from canvas import Canvas

from PIL import Image
Image = Image.Image

class HelpOverlay(object):
    """
    A screen overlay that hooks onto an UI element, allowing you to show a help
    overlay when a button (by default, F5) is pressed.
    """
    do_draw = False
    counter = 0
    top_offset = 0
    right_offset = 20
    t_top_offset = -2
    t_right_offset = -1

    def __init__(self, callback, key = "KEY_F5", duration = 20):
        self.callbacks = [callback]
        self.key = key
        self.duration = duration

    def apply_to(self, ui_el):
        self.wrap_configure_input(ui_el)
        self.wrap_before_foreground(ui_el)
        self.wrap_idle_loop(ui_el)
        self.wrap_view(ui_el)

    def wrap_configure_input(self, ui_el):
        configure_input = ui_el.configure_input
        @wraps(configure_input)
        def wrapper(*args, **kwargs):
            return_value = configure_input(*args, **kwargs)
            key, callback = self.get_key_and_callback()
            ui_el.i.set_callback(key, ui_el.process_callback(callback))
            return return_value
        ui_el.configure_input = wrapper

    def wrap_before_foreground(self, ui_el):
        before_foreground = ui_el.before_foreground
        @wraps(before_foreground)
        def wrapper(*args, **kwargs):
            return_value = before_foreground(*args, **kwargs)
            self.do_draw = True
            self.counter = 0
            return return_value
        ui_el.before_foreground = wrapper

    def wrap_idle_loop(self, ui_el):
        idle_loop = ui_el.idle_loop
        @wraps(idle_loop)
        def wrapper(*args, **kwargs):
            return_value = idle_loop(*args, **kwargs)
            self.update_state(ui_el)
            return return_value
        ui_el.idle_loop = wrapper

    def wrap_view(self, ui_el):
        def wrapper_wrapper(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                image = func(*args, **kwargs)
                if isinstance(image, Image):
                    image = self.modify_image_if_needed(ui_el, image)
                return image
            return wrapper
        ui_el.add_view_wrapper(wrapper_wrapper)

    def push_callback(self, callback):
        self.callbacks.append(callback)

    def pop_callback(self):
        self.callbacks = self.callbacks[:-1]

    def update_state(self, ui_el):
        if self.do_draw:
            self.counter += 1
            if self.counter == self.duration:
                self.do_draw = False
                ui_el.refresh()

    def get_key_and_callback(self):
        return self.key, self.callbacks[-1]

    def modify_image_if_needed(self, ui_el, image):
        if self.do_draw:
            c = Canvas(ui_el.o, base_image=image)
            self.draw_icon(c)
            image = c.get_image()
        return image

    def draw_icon(self, c):
        c.clear((str(-(self.right_offset+c.o.char_width)), self.top_offset, str(-self.right_offset), self.top_offset+c.o.char_height))
        c.text("H", ( str(-(self.right_offset+c.o.char_width+self.t_right_offset)), self.top_offset+self.t_top_offset ))
