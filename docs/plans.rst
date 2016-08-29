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

.. rubric:: Supporting graphical displays

* Get/make fonts
* Include compatibility layers

============
Applications
============

* Bluetooth app (delayed, involves a lot of DBus work)
* "Quick reading" app (word-by-word)
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
* Simple number input
* Character input using keypads and keyboards

============
Development
============

* More example apps & examples for UI elements
* An app development course

.. rubric:: Integration into projects

* Examples for RPC API wrapper (for integration in any projects running in separate threads)
