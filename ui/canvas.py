from PIL import Image, ImageDraw, ImageOps

class Canvas(object):
    """
    This object allows you to work with graphics on the display quicker and easier.
    You can draw text, graphical primitives, insert bitmaps and do other things
    that the ``PIL`` library allows, with a bunch of useful helper functions.
    """

    height = 0 #: height of canvas in pixels.
    width = 0 #: width of canvas in pixels.
    image = None #: ``PIL.Image`` object the ``Canvas`` is currently operating on.
    size = (0, 0) #: a tuple of (width, height).

    def __init__(self, o, base_image=None):
        """
        Args:

            * ``o``: output device
            * ``base_image``: an image to use as a base
        """
        self.o = o
        if "b&w-pixel" not in o.type:
            raise ValueError("The output device supplied doesn't support pixel graphics!")
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
        """
        Get the current ``PIL.Image`` object.
        """
        return self.image

    def get_center(self):
        """
        Get center coordinates. Will not represent the physical center -
        especially with those displays having even numbers as width and height
        in pixels (that is, the absolute majority of them).
        """
        return self.width / 2, self.height / 2

    def invert(self):
        """
        Inverts the image that ``Canvas`` is currently operating on.
        """
        self.image = ImageOps.invert(self.image).convert(o.device_mode)

    def display(self):
        """
        Display the current image on the ``o`` object that was supplied to ``Canvas``.
        """
        self.o.display_image(self.image)

    def __getattr__(self, name):
        if hasattr(self.draw, name):
            return getattr(self.draw, name)
        raise AttributeError
