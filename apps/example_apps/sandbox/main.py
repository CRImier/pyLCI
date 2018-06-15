menu_name = "Python sandbox"

i = None
o = None
context = None

def init_app(input, output):
    global i, o
    i = input; o = output

def set_context(new_context):
    global context
    context = new_context

def callback():
    import code as __code__
    __code__.interact(local=dict(globals(), **locals()))
