from evdev import InputDevice, list_devices

devices = [InputDevice(fn) for fn in list_devices()]
for dev in devices:
    print(dev.fn, dev.name, dev.phys)
