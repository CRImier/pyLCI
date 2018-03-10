from PIL import Image, ImageDraw, ImageOps, ImageFont

from ui.utils import is_sequence_not_string as issequence

default_font = ImageFont.load_default()

from helpers import setup_logger
logger = setup_logger(__name__, "warning")

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
    default_font = default_font #: default font, referenced here to avoid loading it every time

    def __init__(self, o, base_image=None, name=""):
        """
        Args:

            * ``o``: output device
            * ``base_image``: an image to use as a base
            * ``name``: a name, for internal usage
        """
        self.o = o
        if "b&w-pixel" not in o.type:
            raise ValueError("The output device supplied doesn't support pixel graphics!")
        self.width = o.width
        self.height = o.height
        self.name = name
        self.size = (self.width, self.height)
        if base_image:
            assert(base_image.size == self.size)
            self.image = base_image.copy()
        else:
            self.image = Image.new(o.device_mode, self.size)
        self.draw = ImageDraw.Draw(self.image)

    def load_font(self, path, size, type="truetype"):
        """
        Loads a font by its path for the given size, then returns it.
        """
        if type == "truetype":
            return ImageFont.truetype(path, size)
        else:
            return ValueError("Font type not yet supported: {}".format(type))

    def point(self, coord_pairs, **kwargs):
        """
        Draw a point, or multiple points on the canvas. Coordinates are expected in
        ``((x1, y1), (x2, y2), ...)`` format, where ``x*``&``y*`` are coordinates
        of each point you want to draw.
        """
        fill = kwargs.pop("fill", self.default_color)
        assert all([issequence(c) for c in coord_pairs]), "Expecting a tuple of tuples!"
        coord_pairs = list(coord_pairs)
        for i, coord_pair in enumerate(coord_pairs):
            coord_pairs[i] = self.check_coordinates(coord_pair)
        coord_pairs = tuple(coord_pairs)
        self.draw.point(coord_pairs, fill=fill, **kwargs)

    def line(self, coords, **kwargs):
        """
        Draw a line on the canvas. Coordinates are expected in
        ``(x1, y1, x2, y2)`` format, where ``x1``&``y1`` are coordinates
        of the start, and ``x2``&``y2`` are coordinates of the end.
        """
        fill = kwargs.pop("fill", self.default_color)
        coords = self.check_coordinates(coords)
        self.draw.line(coords, fill=fill, **kwargs)

    def text(self, text, coords, **kwargs):
        """
        Draw text on the canvas. Coordinates are expected in (x, y)
        format, where ``x``&``y`` are coordinates of the top left corner.

        Do notice that order of first two arguments is reversed compared
        to the corresponding ``PIL.ImageDraw`` method.
        """
        assert(isinstance(text, basestring))
        fill = kwargs.pop("fill", self.default_color)
        font = kwargs.pop("font", self.default_font)
        coords = self.check_coordinates(coords)
        self.draw.text(coords, text, fill=fill, font=font, **kwargs)

    def rectangle(self, coords, **kwargs):
        """
        Draw a rectangle on the canvas. Coordinates are expected in
        ``(x1, y1, x2, y2)`` format, where ``x1``&``y1`` are coordinates
        of the top left corner, and ``x2``&``y2`` are coordinates
        of the bottom right corner.
        """
        coords = self.check_coordinates(coords)
        outline = kwargs.pop("outline", self.default_color)
        fill = kwargs.pop("fill", None)
        self.draw.rectangle(coords, outline=outline, fill=fill, **kwargs)

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
        A helper function to check and reformat coordinates supplied to
        functions. Currently, accepts integer coordinates, as well as strings
        - denoting offsets from opposite sides of the screen.
        """
        # Checking for string offset coordinates
        # First, we need to make coords into a mutable sequence - thus, a list
        coords = list(coords)
        for i, c in enumerate(coords):
            sign = "+"
            if isinstance(c, basestring):
                if c.startswith("-"):
                    sign = "-"
                    c = c[1:]
                assert c.isdigit(), "A numeric string expected, received: {}".format(coords[i])
                offset = int(c)
                dim = self.size[i % 2]
                if sign == "+":
                    coords[i] = dim + offset
                elif sign == "-":
                    coords[i] = dim - offset
            elif isinstance(c, float):
                logger.warning("Received {} as a coordinate - pixel offsets can't be float, converting to int".format(c))
                coords[i] = int(c)
        # Restoring the status-quo
        coords = tuple(coords)
        # Now checking whether the coords are right
        for c in coords:
            assert isinstance(c, int), "{} not an integer or 'x' string!".format(c)
        if len(coords) == 2:
            return coords
        elif len(coords) == 4:
            x1, y1, x2, y2 = coords
            # Not sure those checks make sense
            #assert (x2 >= x1), "x2 ({}) is smaller than x1 ({}), rearrange?".format(x2, x1)
            #assert (y2 >= y1), "y2 ({}) is smaller than y1 ({}), rearrange?".format(y2, y1)
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
        self.rectangle(coords)
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
