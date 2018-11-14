from time import sleep
from PIL import ImageOps
import PIL

def splash(i, o):
    if o.size == (128, 64):
	image = PIL.Image.open("splash.png").convert('L')
    elif (o.width, o.height) == (128, 128):
	image = PIL.Image.open("splash_128x128.png").convert('L')
    else:
	o.display_data("Welcome to", "ZPUI")
    image = ImageOps.invert(image)
    image = image.convert(o.device_mode)
    o.display_image(image)
