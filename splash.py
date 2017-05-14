import PIL
from PIL.ImageOps import invert
from luma.core.render import canvas
from time import sleep

def splash(i, o):
    image = PIL.Image.open("splash.png").convert('L')
    image = invert(image)
    image = image.convert(o.device.mode)
    with canvas(o.device) as draw:
        o.device.display(image)
        sleep(2)

