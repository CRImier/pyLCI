def ellipsize(string, length, ellipsis="..."):
    if len(string) <= length:
        return string
    string = string[:(length-len(ellipsis))]
    return string+ellipsis
