from time import sleep
import PIL

def splash(i, o):
    image = PIL.Image.open("splash.png").convert('L')
    image = PIL.ImageOps.invert(image)
    image = image.convert(o.device.mode)
    o.display_image(image)
