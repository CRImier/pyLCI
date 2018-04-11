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

Draw on the screen
==================

Display an image
----------------

You can easily draw an image on the screen with ZPUI. The easiest way is
by using the ``GraphicsPrinter`` UI element, which accepts either a path
to an image you want to display, or a ``PIL.Image`` instance:

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

Draw text on the screen
-----------------------

You can draw text on the screen, and you can use different fonts. By default, a 8pt font
is used:

.. code-block:: python

    c = Canvas(o)
    c.text("Hello world", (0, 0)) # Draws "Hello world", starting from the top left corner
    c.display()

You can also use a non-default font - for example, the Fixedsys62 font in
the ZPUI font storage:

.. code-block:: python

    c.text("Hello world", (0, 0), font=("Fixedsys62.ttf", 16)) # Same, but in a 16pt Fixedsys62 font
    c.text("Hello world", (0, 0), font=(local_path("my_font.ttf"), 16) ) # Using a custom font from your app directory

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

Read JSON from a ``config.json`` file located in the app directory
------------------------------------------------------------------

.. code-block:: python

    from helpers import read_config, local_path_gen
    config_filename = "config.json"
    
    local_path = local_path_gen(__name__)
    config = read_config(local_path(config_filename))

------------

Read a ``config.json`` file, and restore it to defaults if it can't be read
---------------------------------------------------------------------------

.. code-block:: python

    from helpers import read_or_create_config, local_path_gen
    default_config = '{"your":"default", "config":"to_use"}' #has to be a string
    config_filename = "config.json"
    
    local_path = local_path_gen(__name__)
    config = read_or_create_config(local_path(config_filename), default_config, menu_name+" app")

.. note:: The faulty ``config.json`` file will be copied into a ``config.json.faulty`` 
          file before being overwritten

Run tasks on app startup
=====================================

Run a short task only once when your app is called
--------------------------------------------------

This is suitable for short tasks that you only call once, and that won't conflict
with other apps.

.. code-block:: python

    def init_app(i, o):
        ...
        init_hardware() #Your task - short enough to run while app is being loaded

.. warning:: If there's a chance that the task will take a long time, use one
             of the following methods instead

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
to use ZPUI until your app has finished loading (pretty egoistic, if you think about it).

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
