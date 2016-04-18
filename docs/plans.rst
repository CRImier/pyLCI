#########################
Future plans
#########################

.. note:: This list is not by any means complete. What's listed here is bound to appear sooner or later. What's not listed is either not yet considered or not going to be implemented.

=====================
Global system changes
=====================

* Make hotplug of input/output devices possible
* Make nested folders for applications
* Include a notification system

.. rubric:: Hardware

* Make a simple Arduino setup with screen&buttons and a firmware+drivers for it to act as pyLCI I/O device over serial
* Make a wireless (ESP8266?) setup

==============
Input devices
==============

* Make a "passthrough" driver for HID so that a single keyboard can both be used for X and pyLCI
* Make an input emulator for development tasks

==============
Output devices
==============

* Make an output emulator for development tasks
* Add a way to automatically turn off the backlight after a set interval
* Eliminate unnecessary redraws of the screen

.. rubric:: Supporting graphical displays

* Get/make fonts
* Include compatibility layers

============
Applications
============

* Bluetooth app (involves a lot of DBus work)
* "Quick reading" app (word-by-word)
* Camera app
* lsusb app
* Stopwatch/timer app
* UCI management app
* Counter app
* Calculator app
* Mount/unmount partitions app
* OpenHAB console
* Systemctl menu
* Tvservice menu (configuring Raspberry Pi video output modes)
* Twitter reader
* NMap app
* Gammu app - sending SMS and receiving making calls using moble phones

============
UI elements
============

* Dialog box
* File choice dialog (possibly, assisted by character input)

.. rubric:: Adding input UI elements

* Date/time picker
* Simple number input
* Character input using left/down/up/right
* Character input using keypads and keyboards
