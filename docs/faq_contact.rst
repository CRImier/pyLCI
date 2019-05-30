############
FAQ&contacts
############

Here are some answers to questions that arise. Don't forget to look through the "Future plans"!
Got a question that isn't answered here? Try to look through `GitHub issues`_. If not found, create a new one!
If you have another questions, `e-mail me`_ .

.. _GitHub issues: https://github.com/ZeroPhone/ZPUI/issues
.. _e-mail me: mailto:crimier@yandex.ru

.. contents::
    :local:
    :depth: 2


FAQ
===

.. _interfaces_supported:

Does ZPUI support screen connected via 595/this particular Pi shield/some other input/output device I have?
------------------------------------------------------------------------------------------------------------

Short answer - it may not, but it's likely easy to add support for it. 

First of all, look through the drivers supported. If you don't understand something, feel free to ask (GitHub issue/e-mail)! I'll be happy to help you, as well as update the docs.

Second thing is - drivers for input/output devices are hella easy to implement. HD44780 screens use a common library, so that only the "sending actual commands/characters" to the character screen has to be implemented, and input devices just have to send "KEY_something" strings to ``InputListener`` when there's a keypress, optionally, do their best to shutdown cleanly (bane of the HID driver for now). You have a shield with a Python library available? Chances are, it's easy to write a driver for it by hooking it up to ZPUI driver structure - look at ``pfcad`` driver, that's exactly the approach used. Or look at the ``output/driver/pi_gpio`` driver, it's a nice example of leveraging the HD44780 abstraction. In short - you can do it yourself, and if you can't, then open an issue on GitHub and you can help develop and test the driver to whatever input device you have so that you can enjoy all the benefits of ZPUI.

.. note:: Well, I have to admit things are still better not using some additional libraries, but they work, and that's the main thing. You need a driver, quick? Great, just take a look at current version of ``output/drivers/pfcad``, it's an example of both how to connect an external library and on various workarounds you might need to use. 


.. _screens_supported:

Does ZPUI support graphical/color OLEDs/TFTs, or other non-character non-HD44780 displays?
-------------------------------------------------------------------------------------------

Short answer - it yet doesn't, but I'm developing everything so that it will.

There's a significant amount of work to be put into it. You need to make fonts for applications/UI elements relying on character output, facilitate display re-draws so that it's not painfully slow because it's redrawing the whole display every time, provide abstraction layers for fallback & other screen types, oh, and document it well enough so that it's usable. And yet, this is something to be included. 

The reasons it's not included now is to be able to focus on applications that need to be developed, and because HD44780 screens are the most popular ones - excluding, maybe, the HDMI-, VGA- and RCA-connected ones, but they're partly the reason ZPUI is developed =) If you lack on-screen place, 20x4 screens are popular and cheap.


.. _multiple_screens:

Does ZPUI support multiple output devices, such as 2 or more screens?
----------------------------------------------------------------------

Short answer - it yet doesn't, but I'll be happy to work on it once there's a user for it and there's a use case.

It's not hard to include this, but there are multiple ways to do it, and each one seems right. For now, many users say they'd just pass different screens to different applications, or use a separate screen for monitoring. This is possible, but would require close collaboration with end users of such a setup so that it's spot on for their applications and adjustable for others - in other words, not a dirty hack for the sake of adding a feature. So - contact me, we can work on it if you need it!

Also, I'd like to remind about ``LCDproc`` project, which is all about displaying relatively static information, such as music player/CPU load info and similar things. It's a well-developed project and ZPUI is not yet claiming its place because they have different use cases, each has their own strengths and weaknesses. It's not hard to imagine using one screen for ZPUI and another - for LCDproc. That said, it's also not hard to use full ZPUI configuration on one screen and ZPUI in single-app mode in another ;-)


.. _root_necessary:

Does the system need to run as root?
------------------------------------

It does not *need* to, but it doesn't make much sense otherwise. ZPUI drivers&apps need all kinds of different privileges for various tasks, and it's run as a single application, so it either needs to be run as root or to be run as a user with enough privileges to do management tasks, which is not that far away from root in terms of danger.

However, from some point there will be a split between ZPUI core and applications, where only core will need to run as a user privileged enough to access input/output devices, and applications will be able to run under separate users. 
.. _openwrt_possible:

Is it possible to run ZPUI under OpenWRT?
------------------------------------------

Yes, as OpenWRT is a Linux distribution. It doesn't even really need ``pip`` if you take care of all dependencies. However, it's not tested. Also, you're likely to need extroot because Python takes a lot of space.

.. note:: UCI interface for now is lacking, but shouldn't be difficult to implement.


.. _hid_grab:

Why does it grab all the HID events from a device given to the HID driver?
--------------------------------------------------------------------------

Unfortunately, now there's no 'passthrough' driver that'd take only part of all the keypresses and pass all the other further. This driver is to appear soon.


.. _x86_hardware:

Which hardware can you use for running ZPUI on desktop computer/server/HTPC?
-----------------------------------------------------------------------------

* First of all, there are plans for making a firmware&driver for Arduino devices with commonly encountered button&16x2 LCD shields. The result will be connectable over USB as a USB-Serial device. 
* Second thing is that most video cards have I2C lines on video ports accessible from Linux, and there's no problem with connecting I2C GPIO expanders to it, except that there's no GPIO to take advantage of button interrupt function.
* Third thing is that you can easily use HID keyboards and numpads as input devices.
