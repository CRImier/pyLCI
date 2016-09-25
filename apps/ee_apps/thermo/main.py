menu_name = "MLX90614" 

from mlx90614 import MLX90614

from ui import Refresher

sensor = MLX90614()

def show_temp():
    try:
        amb_temp = sensor.read_amb_temp()
        obj_temp = sensor.read_obj_temp()
    except IOError:
        amb_temp = None
        obj_temp = None
    data = [
    "Ambient:"+str(amb_temp).rjust(o.cols-len("Ambient:")),
    "Object:"+str(obj_temp).rjust(o.cols-len("Object:"))]
    return data

#Callback global for pyLCI. It gets called when application is activated in the main menu

#Some globals for us
i = None #Input device
o = None #Output device

def init_app(input, output):
    global callback, i, o
    i = input; o = output
    temp_monitor = Refresher(show_temp, i, o, 0.1, name="Temperature monitor")
    callback = temp_monitor.activate

