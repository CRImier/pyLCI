import os

from PIL import Image, ImageDraw, ImageOps, ImageFont

from ui.utils import is_sequence_not_string as issequence, Rect

fonts_dir = "ui/fonts/"
font_cache = {}

default_font = None
def get_default_font():
    global default_font
    if not default_font:
        default_font = ImageFont.load_default()
    return default_font

from helpers import setup_logger
logger = setup_logger(__name__, "warning")

class Canvas(object):
    """
    This object allows you to work with graphics on the display quicker and easier.
    You can draw text, graphical primitives, insert bitmaps and do other things
    that the ``PIL`` library allows, with a bunch of useful helper functions.

    Args:

        * ``o``: output device
        * ``base_image``: a `PIL.Image` to use as a base, if needed
        * ``name``: a name, for internal usage
        * ``interactive``: whether the canvas updates the display after each drawing
    """

    height = 0 #: height of canvas in pixels.
    width = 0 #: width of canvas in pixels.
    image = None #: ``PIL.Image`` object the ``Canvas`` is currently operating on.
    size = (0, 0) #: a tuple of (width, height).
    background_color = "black" #: default background color to use for drawing
    default_color = "white" #: default color to use for drawing
    default_font = None #: default font, referenced here to avoid loading it every time
    fonts_dir = fonts_dir

    def __init__(self, o, base_image=None, name="", interactive=False):
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
        if not self.default_font:
            self.default_font = get_default_font()
        self.interactive = interactive

    def load_font(self, path, size, alias=None, type="truetype"):
        """
        Loads a font by its path for the given size, then returns it.
        Also, stores the font in the ``canvas.py`` ``font_cache``
        dictionary, so that it doesn't have to be re-loaded later on.

        Supports both absolute paths, paths relative to root ZPUI
        directory and paths to fonts in the ZPUI font directory
        (``ui/fonts`` by default).
        """
        # For fonts in the font directory, can use the filename as a shorthand
        if path in os.listdir(self.fonts_dir):
            logger.debug("Loading font from the font storage directory")
            path = os.path.join(self.fonts_dir, path)
        # If an alias was not specified, using font filename as the alias (for caching)
        if alias is None:
            alias = os.path.basename(path)
        # Adding size to the alias and using it for caching
        font_name = "{}:{}".format(alias, size)
        logger.debug("Font alias: {}".format(font_name))
        # Font already loaded, returning the instance we have
        if font_name in font_cache:
            logger.debug("Font {} already loaded, returning".format(font_name))
            return font_cache[font_name]
        # We don't have it cached - let's see the type requested
        # We only support loading TrueType fonts, though
        elif type == "truetype":
            logger.debug("Loading a TT font from {}".format(font_name))
            font = ImageFont.truetype(path, size)
        else:
            raise ValueError("Font type not yet supported: {}".format(type))
        # We loaded a font, now let's cache it and return
        logger.debug("Caching and returning")
        font_cache[font_name] = font
        return font

    def decypher_font_reference(self, reference):
        """
        Is designed to detect the various ways that a ``font`` argument
        can be passed into a function, then return an ``ImageFont`` instance.
        """
        if reference is None:
            return self.default_font
        if reference in font_cache:
            # Got a font alias
            font = font_cache[reference]
        elif isinstance(reference, (tuple, list)):
            # Got a font path with the size parameter
            font = self.load_font(*reference)
        elif isinstance(reference, (ImageFont.ImageFont, ImageFont.FreeTypeFont)):
            font = reference
        else:
            return ValueError("Unknown font reference/object, type: {}".format(type(reference)))
        return font

    def point(self, coord_pairs, **kwargs):
        """
        Draw a point, or multiple points on the canvas. Coordinates are expected in
        ``((x1, y1), (x2, y2), ...)`` format, where ``x*`` & ``y*`` are coordinates
        of each point you want to draw.

        Keyword arguments:

          * ``fill``: point color (default: white, as default canvas color)
        """
        if not all([issequence(c) for c in coord_pairs]):
            # Didn't get pairs of coordinates - converting into pairs
            # But first, sanity checks
            assert (len(coord_pairs) % 2 == 0), "Odd number of coordinates supplied! ({})".format(coord_pairs)
            assert all([isinstance(c, (int, basestring)) for i in coord_pairs]), "Coordinates are non-uniform! ({})".format(coord_pairs)
            coord_pairs = convert_flat_list_into_pairs(coord_pairs)
        coord_pairs = list(coord_pairs)
        for i, coord_pair in enumerate(coord_pairs):
            coord_pairs[i] = self.check_coordinates(coord_pair)
        coord_pairs = tuple(coord_pairs)
        fill = kwargs.pop("fill", self.default_color)
        self.draw.point(coord_pairs, fill=fill, **kwargs)
        if self.interactive: self.display()

    def line(self, coords, **kwargs):
        """
        Draw a line on the canvas. Coordinates are expected in
        ``(x1, y1, x2, y2)`` format, where ``x1`` & ``y1`` are coordinates
        of the start, and ``x2`` & ``y2`` are coordinates of the end.

        Keyword arguments:

          * ``fill``: line color (default: white, as default canvas color)
        """
        fill = kwargs.pop("fill", self.default_color)
        coords = self.check_coordinates(coords)
        self.draw.line(coords, fill=fill, **kwargs)
        if self.interactive: self.display()

    def text(self, text, coords, **kwargs):
        """
        Draw text on the canvas. Coordinates are expected in (x, y)
        format, where ``x`` & ``y`` are coordinates of the top left corner.

        You can pass a ``font`` keyword argument to it - it accepts either a
        ``PIL.ImageFont`` object or a tuple of ``(path, size)``, which are
        then supplied to ``Canvas.load_font()``.

        Do notice that order of first two arguments is reversed compared
        to the corresponding ``PIL.ImageDraw`` method.

        Keyword arguments:

          * ``fill``: text color (default: white, as default canvas color)
        """
        assert(isinstance(text, basestring))
        fill = kwargs.pop("fill", self.default_color)
        font = kwargs.pop("font", self.default_font)
        font = self.decypher_font_reference(font)
        coords = self.check_coordinates(coords)
        self.draw.text(coords, text, fill=fill, font=font, **kwargs)
        if self.interactive: self.display()

    def rectangle(self, coords, **kwargs):
        """
        Draw a rectangle on the canvas. Coordinates are expected in
        ``(x1, y1, x2, y2)`` format, where ``x1`` & ``y1`` are coordinates
        of the top left corner, and ``x2`` & ``y2`` are coordinates
        of the bottom right corner.

        Keyword arguments:

          * ``outline``: outline color (default: white, as default canvas color)
          * ``fill``: fill color (default: None, as in, transparent)
        """
        coords = self.check_coordinates(coords)
        outline = kwargs.pop("outline", self.default_color)
        fill = kwargs.pop("fill", None)
        self.draw.rectangle(coords, outline=outline, fill=fill, **kwargs)
        if self.interactive: self.display()

    def circle(self, coords, **kwargs):
        """
        Draw a circle on the canvas. Coordinates are expected in
        ``(xc, yx, r)`` format, where ``xc`` & ``yc`` are coordinates
        of the circle center and ``r`` is the radius.

        Keyword arguments:

          * ``outline``: outline color (default: white, as default canvas color)
          * ``fill``: fill color (default: None, as in, transparent)
        """
        assert(len(coords) == 3), "Expects three arguments - x center, y center and radius!"
        radius = coords[2]
        coords = coords[:2]
        coords = self.check_coordinates(coords)
        outline = kwargs.pop("outline", self.default_color)
        fill = kwargs.pop("fill", None)
        ellipse_coords = (coords[0]-radius, coords[1]-radius, coords[0]+radius, coords[1]+radius)
        self.draw.ellipse(ellipse_coords, outline=outline, fill=fill, **kwargs)
        if self.interactive: self.display()

    def ellipse(self, coords, **kwargs):
        """
        Draw a ellipse on the canvas. Coordinates are expected in
        ``(x1, y1, x2, y2)`` format, where ``x1`` & ``y1`` are coordinates
        of the top left corner, and ``x2`` & ``y2`` are coordinates
        of the bottom right corner.

        Keyword arguments:

          * ``outline``: outline color (default: white, as default canvas color)
          * ``fill``: fill color (default: None, as in, transparent)
        """
        coords = self.check_coordinates(coords)
        outline = kwargs.pop("outline", self.default_color)
        fill = kwargs.pop("fill", None)
        self.draw.ellipse(coords, outline=outline, fill=fill, **kwargs)
        if self.interactive: self.display()

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
        if self.interactive: self.display()

    def display(self):
        """
        Display the current image on the ``o`` object that was supplied to
        ``Canvas``.
        """
        self.o.display_image(self.image)

    def clear(self, coords=None, fill=None):
        # type: tuple -> None
        """
        Fill an area of the image with default background color. If coordinates are
        not supplied, fills the whole canvas, effectively clearing it. Uses the
        background color by default.
        """
        if coords is None:
            coords = (0, 0, self.width, self.height)
        if fill is None:
            fill = self.background_color
        coords = self.check_coordinates(coords)
        self.rectangle(coords, fill=fill)  # paint the background black first
        if self.interactive: self.display()

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

    def centered_text(self, text, font=None):
        # type: str -> None
        """
        Draws centered text on the canvas. This is mostly a convenience function,
        used in some UI elements.
        """
        font = self.decypher_font_reference(font)
        coords = self.get_centered_text_bounds(text, font=font)
        self.text(text, (coords.left, coords.top), font=font)

    def get_text_bounds(self, text, font=None):
        # type: str -> Rect
        """
        Returns the dimensions for a given text. If you use a
        non-default font, pass it as ``font``.
        """
        font = self.decypher_font_reference(font)
        w, h = self.draw.textsize(text, font=font)
        return w, h

    def get_centered_text_bounds(self, text, font=None):
        # type: str -> Rect
        """
        Returns the coordinates for the text to be centered on the screen.
        The coordinates come wrapped in a ``Rect`` object. If you use a
        non-default font, pass it as ``font``.
        """
        w, h = self.get_text_bounds(text, font=font)
        tcw = w / 2
        tch = h / 2
        cw, ch = self.get_center()
        return Rect(cw - tcw, ch - tch, cw + tcw, ch + tch)

    def invert_rect(self, coords):
        # type: tuple -> tuple
        """
        Inverts the image in the given rectangle region. Is useful for
        highlighting a part of the image, for example.
        """

        coords = self.check_coordinates(coords)
        image_subset = self.image.crop(coords)

        if image_subset.mode != "L": # PIL can only invert "L" and "RGBA" images
            # We only support "L" for now
            image_subset = image_subset.convert("L")
        image_subset = ImageOps.invert(image_subset)
        image_subset = image_subset.convert(self.o.device_mode)

        self.clear(coords)
        self.draw.bitmap((coords[0], coords[1]), image_subset, fill=self.default_color)
        if self.interactive: self.display()

    def __getattr__(self, name):
        if hasattr(self.draw, name):
            return getattr(self.draw, name)
        raise AttributeError


def convert_flat_list_into_pairs(l):
    pl = []
    for i in range(len(l)/2):
        pl.append((l[i*2], l[i*2+1]))
    return pl
