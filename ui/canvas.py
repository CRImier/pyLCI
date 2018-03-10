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
    background_color = "black" #: default background color to use for drawing
    default_color = "white" #: default color to use for drawing

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

    def text(self, text, coords, **kwargs):
        """
        Draw text on the canvas. Coordinates are expected in (x, y)
        format, where ``x``&``y`` are coordinates of the top left corner.

        Do notice that order of first two arguments is reversed compared
        to the corresponding ``PIL.ImageDraw`` method.
        """
        assert(isinstance(text, basestring))
        fill = kwargs.pop("fill", self.default_color)
        coords = self.check_coordinates(coords)
        self.draw.text(coords, text, fill=fill, **kwargs)

    def rectangle(self, coords, **kwargs):
        """
        Draw a rectangle on the canvas. Coordinates are expected in
        ``(x1, y1, x2, y2)`` format, where ``x1``&``y1`` are coordinates
        of the top left corner, and ``x2``&``y2`` are coordinates
        of the bottom right corner.
        """
        coords = self.check_coordinates(coords)
        outline = kwargs.pop("outline", self.default_color)
        self.draw.rectangle(coords, outline=outline, **kwargs)

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
        Display the current image on the ``o`` object that was supplied to
        ``Canvas``.
        """
        self.o.display_image(self.image)

    def clear(self, coords):
        # type: tuple -> None
        """
        Fill an area of the image with default background color.
        """
        coords = self.check_coordinates(coords)
        self.rectangle(coords, fill=self.background_color)  # paint the background black first

    def check_coordinates(self, coords):
        # type: tuple -> tuple
        """
        A helper function to check (later, also reformat) coordinates supplied to
        functions. Currently, only accepts integer coordinates.
        """
        for i in coords:
            assert isinstance(i, int), "{} not an integer!".format(i)
        if len(coords) == 2:
            return coords
        elif len(coords) == 4:
            x1, y1, x2, y2 = coords
            assert (x2 >= x1), "x2 ({}) is smaller than x1 ({}), rearrange?".format(x2, x1)
            assert (y2 >= y1), "y2 ({}) is smaller than y1 ({}), rearrange?".format(y2, y1)
            return coords
        else:
            raise ValueError("Invalid number of coordinates!")

    def invert_rect_colors(self, coords):
        # type: tuple -> tuple
        """
        Inverts colors of the image in the given rectangle. Is useful for
        highlighting a part of the image, for example.
        """

        coords = self.check_coordinates(coords)
        #self.rectangle(coords)
        image_subset = self.image.crop(coords)

        if image_subset.mode != "L": # PIL can only invert "L" and "RGBA" images
            # We only support "L" for now
            image_subset = image_subset.convert("L")
        image_subset = ImageOps.invert(image_subset)
        image_subset = image_subset.convert(self.o.device_mode)

        self.clear(coords)
        self.draw.bitmap((coords[0], coords[1]), image_subset, fill=self.default_color)

    def __getattr__(self, name):
        if hasattr(self.draw, name):
            return getattr(self.draw, name)
        raise AttributeError
