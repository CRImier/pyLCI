#########################
Future plans
#########################

A TODO document, if you will

.. note:: This list is not by any means complete. What's listed here is bound to appear sooner or later. What's not listed is either not yet considered or not going to be implemented - feel free to ask me at GitHub!

=====================
Global system changes
=====================

* Make hotplug of input/output devices possible
* Include a notification system

.. rubric:: Hardware

* Make a simple Arduino setup with screen&buttons and firmware+drivers for it to act as pyLCI I/O device over serial
* Make a wireless (ESP8266-based) setup
* Make a fully working PiFaceCAD driver

==============
Input devices
==============

* Make global non-overridable and global overridable callbacks (that could be used by apps to process buttons even while being inactive)
* Make a "passthrough" driver for HID so that a single keyboard can both be used for X and pyLCI
* Make an input emulator for development tasks
* Add key remapping to HID driver
* Pressed/released/held button states
* Input streaming mode (pass all keycodes received to one callback)

==============
Output devices
==============

* Make an output emulator for development tasks
* Add backlight control layer to all displays


.. rubric:: Supporting graphical displays

* Get/make fonts
* Include compatibility layers

============
Applications
============

* Bluetooth app (delayed, involves a lot of DBus work)
* MPD/Mopidy app
* Camera app
* Stopwatch/timer app
* UCI management app
* Counter app
* Calculator app
* Mount partitions app
* OpenHAB console
* Twitter reader
* NMap app
* SMS and call app - interfacing to mobile phones and GSM/3G modems

============
UI elements
============

* Dialog box
* File choice dialog (possibly, assisted by character input)

.. rubric:: Adding input UI elements

* Date/time picker
* "Quick reading" UI element (word-by-word)
* Simple number input
* Character input using keypads and keyboards
* Wraparound for Menu UI element
* Page up/down for Menu UI element

============
Development
============

* More example apps & examples for UI elements
* Guide about input callbacks and 5 main keys
* An app development course
* Make a release system
* More links to UI element usage examples in existing apps

.. rubric:: Integration into projects

* Examples for RPC API wrapper (for integration in any projects running in separate threads)

============
Maintenance
============

* Refactor UI elements to use common classes
* Refactor main.py launcher
* Clean up comments in UI elements, decide what functions to expose in the docs
* Make an app for configuring pyLCI on the fly

=========
Publicity
=========

* Some videos
* A website
* Collection of projects developed with pyLCI
