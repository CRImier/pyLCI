def get_model_str(model_file = "/sys/firmware/devicetree/base/model"):
    with open(model_file, 'r') as f:
        return f.read().strip()

def is_pi_zero(f_c = None):
    """Returns True if hw is Zero or Zero W.
    You can pass file contents to this function instead"""
    if not f_c:
        try:
            f_c = get_model_str()
        except:
            return False
    return f_c.startswith("Raspberry Pi Zero")

def is_pi_zero_w(f_c = None):
    """Returns True if hw is Zero W.
    You can pass file contents to this function instead"""
    if not f_c:
        try:
            f_c = get_model_str()
        except:
            return False
    return f_c.startswith("Raspberry Pi Zero W")


if __name__ == "__main__":
    print(get_model_str())
    print(is_pi_zero())
    print(is_pi_zero_w())
