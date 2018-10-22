

from helpers import setup_logger
from ui import IntegerAdjustInput
from decimal import Decimal, ROUND_HALF_UP

menu_name = "Calculator"

from subprocess import call
from time import sleep

from ui import Menu, Printer

logger = setup_logger(__name__, "info")

def get_numbers():
  inputA = IntegerAdjustInput(0, i, o, message="Pick first number", name="CalculatorAInput").activate()
  if inputA is None:
    Printer("Operation canceled.", i, o, 2)
    return;

  inputB = IntegerAdjustInput(0, i, o, message="Pick second number", name="CalculatorBInput").activate()
  if inputB is None:
    Printer("Operation canceled.", i, o, 2)
    return;
  
  return [Decimal(inputA), Decimal(inputB)]


def do_operation(operation):
    values = get_numbers()
    if operation == '+':
        result = ( values[0] + values[1] )
    elif operation == '-':
        result = ( values[0] - values[1] )
    elif operation == '*':
        result = ( values[0] * values[1] )
    elif operation == '/':
        if values[0] == 0:
            result = 0
        elif values[1] == 0:
            result = "DNE"
        else:
            #TODO make decimal places a config item along with rounding options
            result = ( values[0] / values[1] ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    if result == -0:
        result = 0

    Printer((str(values[0]) + ' ' + operation + ' ' + str(values[1]) + ' = ' + str(result)), i, o, 15)


def callback():
    main_menu_contents = [
    ["Add", lambda: do_operation('+')],
    ["Subtract", lambda: do_operation('-')],
    ["Multiply", lambda: do_operation('*')],
    ["Divide", lambda: do_operation('/')]]
    Menu(main_menu_contents, i, o, "Calculator app menu").activate()

i = None #Input device
o = None #Output device

def init_app(input, output):
    global i, o
    i = input
    o = output
