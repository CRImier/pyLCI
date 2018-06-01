.. _howto:

How to...
#########

Do you want to improve your ZPUI app or solve your problem by copy-pasting
a snippet in your app code? This page is for you =)

.. contents::
    :local:
    :depth: 2

Basics
======

What's the minimal ZPUI app?
----------------------------

In ``app/main.py``:

.. code-block:: python

    menu_name = "Skeleton app"
    
    i = None #Input device
    o = None #Output device
    
    def init_app(input, output):
        #Gets called when app is loaded
        global i, o
        i = input; o = output
    
    def callback():
        #Gets called when app is selected from menu
        pass

``app/__init__.py`` has to be an empty file:

.. code-block:: python


------------

What's the minimal class-based app?
-----------------------------------

In ``app/main.py``:

.. code-block:: python

    from apps import ZeroApp

    class YourGreatApp(ZeroApp):
        menu_name = "Skeleton app"

        def on_start():
            #Gets called when app is selected from menu
            pass

``app/__init__.py`` has to be an empty file, as with the previous example.
     
------------

Draw on the screen
==================

Display an image
----------------

You can easily draw an image on the screen with ZPUI. The easiest way is
by using the ``display_image`` method of ``OutputProxy`` object:

.. code-block:: python

    o.display_image(image) #A PIL.Image object

However, you might want a user-friendly wrapper around it that would allow
you to easily load images by filename, invert, add a delay/exit-on-key etc.
In this case, you'll want to use the ``GraphicsPrinter`` UI element, which
accepts either a path to an image you want to display, or a ``PIL.Image``
instance and supports some additional arguments:

.. code-block:: python

    from ui import GraphicsPrinter
    ...
    # Will display the ZPUI splash image for 1 second
    # By default, it's inverted
    GraphicsPrinter("splash.png", i, o, 1)
    # Same, but the image is not inverted
    GraphicsPrinter("splash.png", i, o, 1, invert=False)
    # Display an image from the app folder - using the local_path helper
    GraphicsPrinter(local_path("image.png"), i, o, 1)
    # Display an image you drew on a Canvas
    GraphicsPrinter(c.get_image(), i, o, 1)

In case you have a Canvas object and you just want to display it, there's
a shorthand:

.. code-block:: python

    c.display()

------------

Draw things on the screen - basics
----------------------------------

Uou can use the Canvas objects to draw on the screen.

.. code-block:: python

    from ui import Canvas
    ...
    c = Canvas(o) # Create a canvas
    c.point((1, 2)) # Draw a point at x=1, y=2
    c.point( ( (2, 1), (2, 3), (3, 4) ) ) # Draw some more points
    ... # Draw other stuff here
    c.display() # Display the canvas on the screen

.. image:: _static/canvas_test_1.png

------------

Draw text
---------

You can draw text on the screen, and you can use different fonts. By default, a 8pt font
is used:

.. code-block:: python

    c = Canvas(o)
    c.text("Hello world", (0, 0)) # Draws "Hello world", starting from the top left corner
    c.display()

.. image:: _static/canvas_test_2.png

You can also use a non-default font - for example, the Fixedsys62 font in
the ZPUI font storage:

.. code-block:: python

    c.text("Hello world", (0, 0), font=("Fixedsys62.ttf", 16)) # Same, but in a 16pt Fixedsys62 font
    c.text("Hello world", (0, 0), font=(local_path("my_font.ttf"), 16) ) # Using a custom font from your app directory

------------

Draw centered text
------------------

You can draw centered text, too!

.. code-block:: python

    c = Canvas(o)
    c.centered_text("Hello world") # Draws "Hello world" in the center of the screen
    c.display()

.. image:: _static/canvas_test_7.png

You can also draw text that's centered on one of the dimensions:

.. code-block:: python

    c = Canvas(o)
    ctc = c.get_centered_text_bounds("a") # Centered Text Coords
    # ctc == Rect(left=61, top=27, right=67, bottom=37)
    c.text("a", (ctc.left, 0)) 
    c.text("b", (str(ctc.left-ctc.right), ctc.top)) # ('-6', 27)
    c.text("c", (ctc.left, str(ctc.top-ctc.bottom))) # (61, '-10')
    c.text("d", (0, ctc.top))
    c.display()

.. image:: _static/canvas_test_8.png

------------

Draw a line
-----------

.. code-block:: python

    c = Canvas(o)
    c.line((10, 4, "-8", "-4")) # Draws a line from top left to bottom right corner
    c.display()

.. image:: _static/canvas_test_3.png

------------

Draw a rectangle
----------------

.. code-block:: python

    c = Canvas(o)
    c.rectangle((10, 4, 20, "-10")) # Draws a rectangle in the left of the screen
    c.display()

.. image:: _static/canvas_test_4.png

------------

Draw a circle
-------------

.. code-block:: python

    c = Canvas(o)
    c.circle(("-8", 8, 4)) # Draws a circle in the top left corner - with radius 4
    c.display()

.. image:: _static/canvas_test_5.png

.. note:: There's also a ``Canvas.ellipse()`` method, which takes four coordinates
          instead of two + radius.

------------

Invert a region of the screen
-----------------------------

If you want to highlight a region of the screen, you might want to invert it:

.. code-block:: python

    c = Canvas(o)
    c.text("Hello world", (5, 5))
    c.invert_rect((35, 5, 80, 17)) # Inverts, roughly, the right half of the text
    c.display()

.. image:: _static/canvas_test_6.png

.. note:: To invert the whole screen, you can use the ``invert`` method.

------------

Make your app easier to support
===============================

Add logging to your app
-----------------------

In case your application does something more complicated than printing a sentence
on the display and exiting, you might need to add logging - so that users can then
look through the ZPUI history, figure out what was it that went wrong, and maybe
submit a bugreport to you!

.. code-block:: python

    from helpers import setup_logger # Importing the needed function
    logger = setup_logger(__name__, "warning") # Getting a logger for your app, 
    # default level is "warning" - this level controls logging statements that
    # will be displayed (and saved in the logfile) by default.
    
    ...
    
    try:
        command = "my_awesome_script"
        logger.info("Calling the '{}' command".format(command))
        output = call(command)
        logger.debug("Finished executing the command")
        for value in output.split():
            if value not in expected_values:
                logger.warning("Unexpected value {} found when parsing command output; proceeding".format(value))
    except:
        logger.exception("Exception while calling the command!")
        # .exception will also log the details of the exception after your message

Config (and other) files
========================

Read JSON from a config file located in the app directory
---------------------------------------------------------

.. code-block:: python

    from helpers import read_config, local_path_gen
    config_filename = "config.json"
    
    local_path = local_path_gen(__name__)
    config = read_config(local_path(config_filename))

------------

Read a config file with an easy "save" function and "restore to defaults on error" check
----------------------------------------------------------------------------------------

.. code-block:: python

    from helpers import read_or_create_config, local_path_gen, save_config_gen
    default_config = '{"your":"default", "config":"to_use"}' #has to be a string
    config_filename = "config.json"
    
    local_path = local_path_gen(__name__)
    config = read_or_create_config(local_path(config_filename), default_config, menu_name+" app")
    save_config = save_config_gen(local_path(config_filename))

To save the config, use ``save_config(config)`` from anywhere in your app.

.. note:: The faulty ``config.json`` file will be copied into a ``config.json.faulty`` 
          file before being overwritten

.. warning:: If you're reassigning contents of the ``config`` variable from inside a
             function, you will likely want to use Python ``global`` keyword in order
             to make sure your reassignment will actually work.

------------

"Read", "save" and "restore" - in a class-based app
---------------------------------------------------

.. code-block:: python

    from helpers import read_or_create_config, local_path_gen, save_config_method_gen
    local_path = local_path_gen(__name__)

    class YourApp(ZeroApp):

        menu_name = "My greatest app"
        default_config = '{"your":"default", "config":"to_use"}' #has to be a string
        config_filename = "config.json"
        
        def __init__(self, *args, **kwargs):
            ZeroApp.__init__(self, *args, **kwargs)
            self.config = read_or_create_config(local_path(self.config_filename), self.default_config, self.menu_name+" app")
            self.save_config = save_config_method_gen(local_path(self.config_filename))

To save the config, use ``self.save_config()`` from anywhere in your app class.

------------

Get path to a file in the app directory
---------------------------------------

Say, you have a ``my_song.mp3`` file shipped with your app. However, in order to use
that file from your code, you have to refer to that file using a path relative to the
ZPUI root directory, such as ``apps/personal/my_app/my_song.mp3``.

Here's how to get that path automatically, without hardcoding which folder your app is put in:

.. code-block:: python

    from helpers import local_path_gen
    local_path = local_path_gen(__name__)
    mp3_file_path = local_path("my_song.mp3")

In case of your app having nested folders, you can also give multiple arguments to
``local_path()``:

.. code-block:: python

    song_folder = "songs/"
    mp3_file_path = local_path(song_folder, "my_song.mp3")

------------

Run tasks on app startup
=====================================

How to do things on app startup in a class-based app?
-----------------------------------------------------

.. code-block:: python

    def __init__(self, *args, **kwargs):
        ZeroApp.__init__(self, *args, **kwargs)
        # do your thing
     
------------

Run a short task only once when your app is called
--------------------------------------------------

This is suitable for short tasks that you only call once, and that won't conflict
with other apps.

.. code-block:: python

    def init_app(i, o):
        ...
        init_hardware() #Your task - short enough to run while app is being loaded

.. warning:: If there's a chance that the task will take a long time, use one
             of the following methods instead.

------------

Run a task only once, first time when the app is called
-------------------------------------------------------

This is suitable for tasks that you can only call once, and you'd only need to
call once the user activates the app (maybe grabbing some resource that could
conflict with other apps, such as setting up GPIO or other interfaces).

.. code-block:: python

    from helpers import Oneshot
    ...
    def init_hardware():
        #can only be run once

    #since oneshot is only defined once, init_hardware function will only be run once,
    #unless oneshot is reset.
    oneshot = Oneshot(init_hardware)
    
    def callback():
        oneshot.run() #something that you can't or don't want to init in init_app
        ... #do whatever you want to do

Run a task in background after the app was loaded
-------------------------------------------------

This is suitable for tasks that take a long time. You wouldn't want to execute that task
directly in ``init_app()``, since it'd stall loading of all ZPUI apps, not allowing the user
to use ZPUI until your app has finished loading (which is pretty inconvenient for the user).

.. code-block:: python

    from helpers import BackgroundRunner
    ...
    def init_hardware():
        #takes a long time

    init = BackgroundRunner(init_hardware)
    
    def init_app(i, o):
        ...
        init.run() #something too long that just has to run in the background,
        #so that app is loaded quickly, but still can be initialized.

    def callback():
        if init.running: #still hasn't finished
            PrettyPrinter("Still initializing...", i, o)
            return
        elif init.failed: #finished but threw an exception
            PrettyPrinter("Hardware initialization failed!", i, o)
            return
        ... #everything initialized, can proceed safely

Control flow and user-friendliness
==================================

Allow exiting a loop on a keypress
-----------------------------------

Say, you have a loop that doesn't have an UI element in it - you're just doing something
repeatedly. You'll want to let the user exit that loop, and the reasonable way is to
interrupt the loop when the user presses a key (by default, ``KEY_LEFT``).
Here's how to allow that:

.. code-block:: python

    from helpers import ExitHelper
    ...
    eh = ExitHelper(i).start()
    while eh.do_run():
        ... #do something repeatedly until the user presses KEY_LEFT

Stopping a foreground task on a keypress
----------------------------------------

If you have some kind of task that's running in foreground (say, a HTTP server), you will
want to let the user exit the UI, at least - maybe even stop the task. If a task can be
stopped from another thread, you can use ``ExitHelper``, too - it can call a custom function
that would signal the task to stop.

.. code-block:: python

    from helpers import ExitHelper
    ...
    task = ... # Can be run in foreground with ``task.run()``
    # Can also be stopped from another thread with ``task.stop()``
    eh = ExitHelper(i, cb=task.stop).start()
    task.run() # Will run until the task is not stopped

Context management
==================

Contexts are the core of ZPUI multitasking. They allow you to switch between apps
dynamically, have notifications, global hotkeys and menus that appear on a button press.

Get the context object
----------------------

In order to interact with your app's context object, you first need to get it. If your
app is a simple one (function-based), you need to add a ``set_context()`` method that
needs to accept a context object as its first argument. This function will be called
after ``init_app`` is called. In case of a class-based app, you need to have a
``set_context()`` method in the app's class. Once you get the context object, you
can do whatever you want with it and, optionally, save it internally. Here's an example
for the function-based apps:

.. code-block:: python

    def set_context(received_context):
        global context
        context = received_context
        # Do things with the context

Here's an example for the class-based apps:

.. code-block:: python

    def set_context(self, received_context):
        self.context = received_context
        # Do things with the context

Check and request focus for your app
------------------------------------

User can switch from your app at any time, leaving it in the background. You won't receive
any key input in the meantime - the screen interactions will work as intended regardless 
of whether your app is the one active, but the actual screen won't be updated with your 
images until the user switches back to your app. Here's how to check whether your app
is the one active, and request the context manager to switch to your app:

.. code-block:: python

    if not context.is_active():
        has_switched = context.request.switch()
        if has_switched:
            ... # Request to switch has been granted, your app is now the one active

.. warning:: Don't overuse this capability - only use it when it's absolutely necessary.
             The user will be annoyed. Also, keep in mind that your request might be denied.

Set a global key callback for your app
--------------------------------------

You can define a hotkey for your app to request focus - or do something else. This way,
you can have a function from your app be called when a certain key is pressed from any
place in the interface.

.. code-block:: python

    # Call a function from your app without switching to it
    context.request_global_keymap({"KEY_F6":function_you_want_to_call})
    # Request switch to your app
    context.request_global_keymap({"KEY_F6":self.context.request_switch})

The ``request_global_keymap`` call returns a dictionary with a keyname as a key for each
requested callback, with ``True`` as the value if the key was set or, if an exception was
raised while setting the , an exception object.
