def ellipsize(string, length, ellipsis="..."):
    if len(string) <= length:
        return string
    string = string[:(length-len(ellipsis))]
    return string+ellipsis

def format_for_screen(data, screen_width, break_words=True, linebreak=None):
    strings = data.split('\n')
    #Filter \n's
    data = ' \n '.join(strings) #Making sure linebreaks are surrounded by space characters so that when splitting by space you don't have to scan for linebreaks and just can compare
    words = data.split(' ')
    screen_data = []
    current_data = ""
    for word in words:
        #Five cases:
        if not word: #An empty line encountered somehow
            pass
        elif word == '\n': #A linebreak, need to indent them in a way
            screen_data.append(current_data)
            current_data = ""
            if linebreak is not None:
                screen_data.append(linebreak) 
        elif len(word) <= screen_width-len(current_data): #Word fits on current line
            current_data += word+" "
        elif not break_words and len(word) <= screen_width:
            screen_data.append(current_data)
            current_data = word+" "
        else:
            space_on_current_line = screen_width-len(current_data)
            screen_data.append(current_data+word[:space_on_current_line])
            word = word[space_on_current_line:]
            current_line = ""
            while word:
                data = word[:screen_width]
                if len(data) == screen_width: #Full line taken
                    screen_data.append(data)
                else:
                    current_data = data+" "
                word = word[screen_width:]
    screen_data.append(current_data)
    return screen_data

ffs = format_for_screen
