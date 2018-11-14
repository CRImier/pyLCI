from time import sleep
from PIL import ImageOps
import PIL

def splash(i, o):
    image = PIL.Image.open("splash.png").convert('L')
    # image = PIL.Image.open("splash_128x128.png").convert('L')
    image = ImageOps.invert(image)
    image = image.convert(o.device_mode)
    o.display_image(image)
