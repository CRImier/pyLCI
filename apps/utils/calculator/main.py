# Serge Spraiter 20190124
import operator
import math
from decimal import *

from ui import Canvas, DialogBox

menu_name = "Calculator"

i = None # Input device
o = None # Output device

def init_app(input, output):
    global i, o
    i = input; o = output

# decimal
def add(num1, num2):
    return num1 + num2

def sub(num1, num2):
    return num1 - num2

def mul(num1, num2):
    return num1 * num2

def div(num1, num2):
    return num1 / num2

def pow(num1, num2):
    return num1 ** num2

def percent(num1, num2):
    return num1 * num2 / 100

def one_x(num1):
    return Decimal(1) / num1

def square(num1):
    return num1 * num1

def mod(num1, num2):
    return num1 % num2

def rem(num1, num2):
    return num1 // num2

# float
def sin(num1):
    return math.sin(float(num1))

def cos(num1):
    return math.cos(float(num1))

def tan(num1):
    return math.tan(float(num1))

def asin(num1):
    return math.asin(float(num1))

def acos(num1):
    return math.acos(float(num1))

def atan(num1):
    return math.atan(float(num1))

def hsin(num1):
    return math.sinh(float(num1))

def hcos(num1):
    return math.cosh(float(num1))

def htan(num1):
    return math.tanh(float(num1))

def pi():
    return math.pi

def e():
    return math.e

# def factorial(num1):
#     return math.factorial(float(num1))

class Oper:
    def __init__(self, short, full, func, parm=1):
        self.short = short
        self.full = full
        self.func = func
        self.parm = parm
        pass

# page1
oper1 = [Oper("1+ ", "+", add, 2),          # 1, +
         Oper("2- ", "-", sub, 2),          # 2, -
         Oper("3% ", "%", percent, 2),      # 3, %
         Oper("4* ", "*", mul, 2),          # 4, *
         Oper("5/ ", "/", div, 2),          # 5, /
         Oper("6/x", "1/x", one_x),         # 6, 1/x
         Oper("7^2", "^2", square),         # 7, ^2
         Oper("8sq", "sqrt", Decimal.sqrt), # 8, sqr
         Oper("9^y", "x^y", pow, 2),        # 9, x^y
         Oper("*ln", "ln", Decimal.ln),     # #, ln
         Oper("0ex", "exp", Decimal.exp),   # 0, exp
         Oper("#pi", "pi",  pi, 0),         # *, pi
         ]
# page2
oper2 = [Oper("1si", "sin", sin),           # 1, sin
         Oper("2co", "cos", cos),           # 2, cos
         Oper("3ta", "tan", tan),           # 3, tan
         Oper("4as", "asin", asin),         # 4, asin
         Oper("5ac", "acos", acos),         # 5, acos
         Oper("6at", "atan", atan),         # 6, atan
         Oper("7hs", "sinh", hsin),         # 7, sinh
         Oper("8hc", "cosh", hcos),         # 8, cosh
         Oper("9ht", "tanh", htan),         # 9, tanh
         Oper("*mo", "mod", mod, 2),        # #, mod
         Oper("0re", "rem", rem, 2),        # 0, rem
         Oper("#e ", "e", e, 0),            # *, e
         ]

# globals
mode = None
todo = None
values = None
add = None

columns = None
char_height = None
font1 = None

class Values:
    def __init__(self):
        self.clear()

    def clear(self):
        self.number = ["", "", None] # number1, number2, memory
        self.oper = 0
        self.page = oper1

    def get_index(self):
        if mode == 0:  # number1
            return 0
        elif mode == 2:  # number2
            return 1
        else: # operation
            return -1

    def clear_number(self):
        global todo
        index = self.get_index()
        if index >= 0: # number1,2
            self.number[index] = ""
        else: # operation
            self.page = oper2
        todo = 1  # update

    def delete_digit(self):
        global todo
        index = self.get_index()
        if index >= 0: # number1,2
            s = str(self.number[index])
            if len(s) == 1:
                self.number[index] = ""
            else:
                self.number[index] = s[0:-1]
        else: # operation
            self.page = oper1
        todo = 1  # update

    def add_digit(self, index, key):
        s = str(self.number[index])
        if len(s) < columns:
            self.number[index] = s + key

    def add_sign(self, index):
        s = str(self.number[index])
        if not s.startswith('-'):
            if s != "":
                if len(s) < columns:
                    self.number[index] = '-' + s
                else:
                    self.number[index] = '-' + s[0:-1]
        else:
            self.number[index] = s[1:]

    def add_dot(self, index):
        s = str(self.number[index])
        if s.find('.') < 0:
            if s != "":
                if len(s) < columns:
                    self.number[index] = s + '.'

    def save(self):
        global todo
        index = self.get_index()
        if index >= 0: # number1,2
            self.number[2] = self.number[index]  # memory
            todo = 1 # update

    def load(self):
        global todo
        index = self.get_index()
        if index >= 0: # number1,2
            if self.number[2] != None:
                self.number[index] = self.number[2]  # memory
                todo = 1 # update

    def clear_memory(self):
        global todo
        self.number[2] = None
        todo = 1 # update

def help():
    #      0123456789abcdef
    show(["*=sign 0-9 #=dot",
          "<=C1 OK=exit >=C",
          "v,^=next F1=help",
          "Pg^=S Pgv=L F2=C"])

def exit():
    global todo
    choice = DialogBox("yn", i, o, message="Exit?").activate()
    if choice:
        todo = -1  # exit
    else:
        todo = 1 # update
        set_keymap()

def next_mode(where):
    global mode, todo, add
    add = where
    mode += add # 0=number1, 1=operation, 2=number2
    if mode > 2:
        mode = 0
    elif mode < 0:
        mode = 2
    todo = 1 # update

def process_key(key):
    global todo
    index = values.get_index()
    if index >= 0:  # number1,2
        if key >= '0' and key <= '9':
            values.add_digit(index, key)
        elif key == '-':
            values.add_sign(index)
        elif key == '.':
            values.add_dot(index)
    else:  # operation
        if key == '-':
            values.oper = 9
        elif key == '0':
            values.oper = 10
        elif key == '.':
            values.oper = 11
        else: # 1-9
            values.oper = ord(key) - ord('1')
        if values.page[values.oper].parm == 2:
            next_mode(add) # continue
        else:
            next_mode(-add)  # return to previous
    todo = 1  # update

def set_keymap():
    keymap = {"KEY_ENTER": lambda: exit(), # exit
              "KEY_LEFT": lambda: values.delete_digit(),  # delete last digit/prev page
              "KEY_RIGHT": lambda: values.clear_number(),  # clear number/next page
              "KEY_UP": lambda: next_mode(-1),  # prev
              "KEY_DOWN": lambda: next_mode(+1),  # next
              "KEY_PGUP": lambda: values.save(),  # save to memory
              "KEY_PGDOWN": lambda: values.load(),  # load from memory
              "KEY_F2": lambda: values.clear_memory(),  # clear memory
              "KEY_F1": lambda: help(),  # help
              "KEY_1": lambda: process_key('1'),
              "KEY_2": lambda: process_key('2'),
              "KEY_3": lambda: process_key('3'),
              "KEY_4": lambda: process_key('4'),
              "KEY_5": lambda: process_key('5'),
              "KEY_6": lambda: process_key('6'),
              "KEY_7": lambda: process_key('7'),
              "KEY_8": lambda: process_key('8'),
              "KEY_9": lambda: process_key('9'),
              "KEY_*": lambda: process_key('-'),
              "KEY_0": lambda: process_key('0'),
              "KEY_#": lambda: process_key('.'),
              }
    i.stop_listen()
    i.set_keymap(keymap)
    i.listen()

def show(lines):
    o.clear()
    if len(lines) < 4:
        return
    c = Canvas(o)
    for y in range(4):
        c.text(lines[y], (0, y * char_height), font=font1)
    c.display()

def fit_result(result, max):
    if len(result) < max: # fit?
        return result
    start = result.find('.')
    if start < 0 or start > max: # more than 15 digits: xx, xx.yy, xx.yyE+zz
        return 'E'
    end = result.find('E')
    if end < 0:  # xx.yy
        return result[0:max]  # cut after .
    exp = result[end:len(result)]  # E+zz
    ln = len(exp)
    if start + ln >= max: # unable to fit E+zz
        return 'E'
    return result[0:max - ln] + exp

def get_lines():
    index = values.get_index()
    if index >= 0:  # number1,2
        if values.page[values.oper].parm == 0: # set pi, e first
            values.number[index] = values.page[values.oper].func()
        if index == 0: # number1 is current
            l1 = "*{:>15}".format(str(values.number[0]))  # number1
        else:
            if values.page[values.oper].parm == 1:
                l1 = ""  # clear for 1 operand
            else:
                l1 = " {:>15}".format(str(values.number[0]))  # number1
        if values.number[2] != None:  # memory
            mem = 'M'
        else:
            mem = ' '
        if values.page[values.oper] == None:
            l2 = ""
        else:
            l2 = "{}{:>15}".format(mem, values.page[values.oper].full) # operation
        if index == 1: # number2 is current
            l3 = "*{:>15}".format(str(values.number[1]))  # number1
        else:
            if values.page[values.oper].parm == 1:
                l3 = ""  # clear for 1 operand
            else:
                l3 = " {:>15}".format(str(values.number[1]))  # number1
        try:
            if values.number[index] == "":
                num1 = Decimal("0")
            else:
                num1 = Decimal(values.number[index])
            ind = index ^ 1 # second, pow has order
            if values.number[ind] == "":
                num2 = Decimal("0")
            else:
                num2 = Decimal(values.number[ind])
            result = ""
            if values.page[values.oper] != None:
                if values.page[values.oper].parm == 2:
                    result = str(values.page[values.oper].func(num1, num2))
                elif values.page[values.oper].parm == 1:
                    result = str(values.page[values.oper].func(num1))
        except:
            result = 'E'
        res = fit_result(result, 16) # not more than 16 chars
        l4 = "{:>16}".format(res) # result
        return [l1, l2, l3, l4, ]
    # operation
    return ["< {} {} {} >".format(values.page[0].short, values.page[1].short, values.page[2].short),
            "  {} {} {}".format(values.page[3].short, values.page[4].short, values.page[5].short),
            "  {} {} {}".format(values.page[6].short, values.page[7].short, values.page[8].short),
            "  {} {} {}".format(values.page[9].short, values.page[10].short, values.page[11].short),]

def init():
    global columns, char_height, font1, mode, add, todo, values
    getcontext().prec =  16 - len('0.1E+zz') # results has all 16 digits: xx.yyE+zz
    columns = 15  # display width in chars without * - current line
    char_height = int(o.height / 4)
    c1 = Canvas(o)
    font1 = c1.load_font("Fixedsys62.ttf", char_height)
    mode = 0  # number1
    add = +1 # move down
    todo = 0  # run
    values = Values()

def callback():
    global todo
    init()
    help()
    set_keymap()
    while todo != -1: # exit
        if todo == 1: # update
            todo = 0 # run
            lines = get_lines()
            show(lines)
