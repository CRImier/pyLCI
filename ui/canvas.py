from PIL import Image, ImageDraw

class Canvas(object):
    def __init__(self, o, base_image=None):
        self.o = o
        if base_image:
            assert(base_image.size == (o.width, o.height))
            self.image = base_image.copy()
        else:
            self.image = Image.new(o.device_mode, (o.width, o.height))
        self.draw = ImageDraw.Draw(self.image)
        
    def get_image(self):
        return self.image

    def __getattr__(self, name):
        if hasattr(self.draw, name):
            return getattr(self.draw, name)
        raise AttributeError
