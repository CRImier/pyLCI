############
FAQ&contacts
############

Here are some answers to questions that arise.
Got a question that isn't answered here? Try  to look through `GitHub issues`_. If not found, create a new one!
If you have another questions, `e-mail me`_ .

.. _GitHub issues: https://github.com/CRImier/pyLCI/issues
.. _e-mail me: mailto:crimier@yandex.ru

.. contents::
    :local:
    :depth: 2


FAQ
===


.. _root_necessary:

Does the system need to run as root?
------------------------------------

It does not *need* to, but it doesn't make much sense. System needs all kinds of different privileges for various tasks, and it's run as a single application, so it either needs to be run as root or to be run as a user with enough privileges to do management tasks, which is not that far away from root in terms of danger.

However, from some point there will be a split between pyLCI core and applications, where only core will need to run as a user privileged enough to access input/output devices, and applications will be able to run under separate users. 

.. _openwrt_possible:

Is it possible to run pyLCI under OpenWRT?
------------------------------------------

Yes, as OpenWRT is a Linux distribution. It doesn't even really need ``pip`` if you take care of all dependencies. However, it's not tested. Also, you're likely to need extroot because Python takes a lot of space.

.. note:: UCI interface for now is lacking, but shouldn't be difficult to implement.


.. _hid_grab:

Why does it grab all the HID events from a specified device?
------------------------------------------------------------

Unfortunately, now there's no 'passthrough' driver that'd take only part of all the keypresses and pass all the other further. This driver is to appear soon.


.. _x86_hardware:

Which hardware can you use for running pyLCI on desktop computer/server/HTPC?
-----------------------------------------------------------------------------

* First of all, there are plans for making a firmware&driver for Arduino devices with commonly encountered button&16x2 LCD shields. The result will be connectable over USB as a USB-Serial device. 
* Second thing is that most video cards have I2C lines on video ports accessible from Linux, and there's no problem with connecting I2C GPIO expanders to it, except that there's no GPIO to take advantage of button interrupt function.
* Third thing is that you can easily use HID keyboards and numpads as input devices.
