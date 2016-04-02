.. _apps_wpa_cli:

#############################
Wireless (wpa_supplicant) app
#############################

This application lets you connect to wireless networks and manage connections. Under the hood, it uses ``wpa_cli`` to connect to a running ``wpa_supplicant`` instance. 

.. note:: Seriously, wpa_supplicant as wireless management daemon is awesome. Minimalistic and really easy to interface. Also, it's included and running in latest Raspbian versions (from 02.16). 

It uses a 'wpa_cli.py' wrapper library to provide a layer between command-line calls and UI (library is included in the application and resides in the application folder).

It's capable of:

* Scanning wireless networks and displaying scan results
* Connecting to known and open wireless networks
* Viewing wireless connection status
* Managing multiple wireless interfaces
* Saving configuration changes to wpa_supplicant.conf file


If you're not running wpa_supplicant as a daemon and you want to do it, you should follow this guide for adjusting your /etc/network/interfaces and this guide for contents of your /etc/wpa_supplicant/wpa_supplicant.conf.

