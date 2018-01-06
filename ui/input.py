from numpad_input import NumpadCharInput
from char_input import CharArrowKeysInput

def UniversalInput(i, o, *args, **kwargs):
    """
    Returns the most appropriate input UI element, based on available keys
    of input devices present. For now, always returns UI elements configured
    for character input.
    """
    # First, checking if any of the drivers with None as available_keys is present
    if None in i.available_keys.values():
        # HID driver (or other driver with "any key is possible" is likely used
        # Let's use the most fully-functional input available at the moment
        return NumpadCharInput(i, o, *args, **kwargs)
    all_available_keys = sum(i.available_keys.values(), [])
    number_keys = ["KEY_{}".format(x) for x in range(10)]
    number_keys_available = all([number_key in all_available_keys for number_key in number_keys ])
    if number_keys_available:
        # All number keys are supported
        return NumpadCharInput(i, o, *args, **kwargs)
    #fallback - only needs five primary keys
    return CharArrowKeysInput(i, o, *args, **kwargs)
    
