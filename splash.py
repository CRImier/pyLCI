import PIL
from PIL.ImageOps import invert
from luma.core.render import canvas
from time import sleep

def splash(i, o):
    image = PIL.Image.open("splash.png").convert('L')
    image = invert(image)

    #FIXME:
    # need a first-class API call on the display to do this properly
    # Moving the emulator out of proc broke this feature (can't access
    # the 'device' property anymore)
    if hasattr(o, "device"):
        image = image.convert(o.device.mode)
        o.device.display(image)
