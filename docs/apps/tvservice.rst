.. _apps_tvservice:

#####################################
TVService (Raspberry Pi-specific) app
#####################################

This application lets you change the HDMI/TV display parameters on your Raspberry Pi. Useful when you, for example, want to hot-plug it to a monitor and make RPi recognise it.

It uses a 'tvservice.py' wrapper library to provide a layer between command-line calls and UI (library is included in the application and resides in the application folder).

It's capable of:

* Turning HDMI display on (with preferred settings, see ``tvservice -p``) and off, as well as calling appropriate ``fbset`` triggers afterwards.
* Choosing resolution from those the display supports
* Viewing TVService status
* Parsing and showing TVService flags

TVService is installed by default on Raspbian.
