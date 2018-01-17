from PIL import Image, ImageDraw

class Canvas(object):
    def __init__(self, o, base_image=None):
        self.o = o
        self.width = o.width
        self.height = o.height
        self.size = (self.width, self.height)
        if base_image:
            assert(base_image.size == self.size)
            self.image = base_image.copy()
        else:
            self.image = Image.new(o.device_mode, self.size)
        self.draw = ImageDraw.Draw(self.image)
        
    def get_image(self):
        return self.image

    def get_center(self):
        return self.width / 2, self.height / 2

    def __getattr__(self, name):
        if hasattr(self.draw, name):
            return getattr(self.draw, name)
        raise AttributeError
