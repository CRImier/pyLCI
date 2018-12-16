from functools import wraps

from canvas import Canvas

from PIL import Image
Image = Image.Image

class BaseOverlayWithTimeout(object):

    active = False
    counter = 0

    def __init__(self, duration = 20):
        self.duration = duration

    def apply_to(self, ui_el):
        self.wrap_before_foreground(ui_el)
        self.wrap_idle_loop(ui_el)

    def update_state(self, ui_el):
        raise NotImplementedException

    def wrap_idle_loop(self, ui_el):
        idle_loop = ui_el.idle_loop
        @wraps(idle_loop)
        def wrapper(*args, **kwargs):
            return_value = idle_loop(*args, **kwargs)
            self.update_state(ui_el)
            return return_value
        ui_el.idle_loop = wrapper

    def wrap_before_foreground(self, ui_el):
        before_foreground = ui_el.before_foreground
        @wraps(before_foreground)
        def wrapper(*args, **kwargs):
            return_value = before_foreground(*args, **kwargs)
            self.active = True
            self.counter = 0
            return return_value
        ui_el.before_foreground = wrapper


class HelpOverlay(BaseOverlayWithTimeout):
    """
    A screen overlay that hooks onto an UI element, allowing you to show a help
    overlay when a button (by default, F5) is pressed.
    """
    top_offset = 0
    right_offset = 20
    t_top_offset = -2
    t_right_offset = -1

    def __init__(self, callback, key = "KEY_F5", **kwargs):
        self.callbacks = [callback]
        self.key = key
        BaseOverlayWithTimeout.__init__(self, **kwargs)

    def apply_to(self, ui_el):
        self.wrap_generate_keymap(ui_el)
        self.wrap_view(ui_el)
        BaseOverlayWithTimeout.apply_to(self, ui_el)

    def wrap_generate_keymap(self, ui_el):
        generate_keymap = ui_el.generate_keymap
        @wraps(generate_keymap)
        def wrapper(*args, **kwargs):
            keymap = generate_keymap(*args, **kwargs)
            key, callback = self.get_key_and_callback()
            keymap[key] = ui_el.process_callback(callback)
            return keymap
        ui_el.generate_keymap = wrapper
        ui_el.set_default_keymap()

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
        if self.active:
            self.counter += 1
            if self.counter == self.duration:
                self.active = False
                ui_el.refresh()

    def get_key_and_callback(self):
        return self.key, self.callbacks[-1]

    def modify_image_if_needed(self, ui_el, image):
        if self.active:
            c = Canvas(ui_el.o, base_image=image)
            self.draw_icon(c)
            image = c.get_image()
        return image

    def draw_icon(self, c):
        c.clear((str(-(self.right_offset+c.o.char_width)), self.top_offset, str(-self.right_offset), self.top_offset+c.o.char_height))
        c.text("H", ( str(-(self.right_offset+c.o.char_width+self.t_right_offset)), self.top_offset+self.t_top_offset ))

class FunctionOverlay(HelpOverlay):
    """
    A screen overlay that hooks onto an UI element, allowing you to execute actions
    when buttons (by default, "F1" and "F2") are pressed.
    """
    font = None
    bottom_offset = 10
    right_offset = 0
    t_top_offset = -2
    t_right_offset = -1
    default_keys = ["KEY_F1", "KEY_F2"]
    num_keys = len(default_keys)

    def __init__(self, keymap, labels=["Exit", "Options"], **kwargs):
        if isinstance(keymap, (list, tuple)):
            # Can also pass a list of functions instead of a keymap dict
            # The list will then be mapped to the default keys
            if len(keymap) > len(self.default_keys):
                raise ValueError("Can't use a shorthand - passed {} callback with {} default keys!".format(len(keymap), len(self.default_keys)))
            self.keymap = {}
            for i, cb in enumerate(keymap):
                self.keymap[self.default_keys[i]] = cb
        else:
            self.keymap = keymap
        self.labels = labels
        BaseOverlayWithTimeout.__init__(self, **kwargs)

    def wrap_generate_keymap(self, ui_el):
        generate_keymap = ui_el.generate_keymap
        @wraps(generate_keymap)
        def wrapper(*args, **kwargs):
            keymap = generate_keymap(*args, **kwargs)
            keymap.update(self.keymap)
            return keymap
        ui_el.generate_keymap = wrapper
        ui_el.set_default_keymap()

    def draw_icon(self, c):
        half_line_length = c.o.cols/self.num_keys
        last_line = "".join([label.center(half_line_length) for label in self.labels])
        c.clear((self.right_offset, str(-self.bottom_offset), c.width-self.right_offset, c.height))
        c.text(last_line, (self.right_offset, str(-self.bottom_offset)), font=self.font)
