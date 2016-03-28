Welcome to pyLCI's documentation!
=================================

pyLCI stands for Python-based Linux Control Interface. It's an external interface for configuration of your Linux devices in an easy and quick way. 

It can be used on:

* Embedded devices (where dependency on Python isn't problematic to satisfy), such as OpenWRT-powered routers
* Single-board computers, including, but not limited to Raspberry Pi, BeagleBone and many others 
* Tablets and laptops
* Servers
* Desktop PCs and HTPCs

Guides:
=================================

* Setup and configuration guide
* Debugging issues
* Managing applications
* Developing applications

It has two parts - the software part (pyLCI daemon) and the hardware part - typically consisting of a character LCD and a keypad of some sort. 

The pyLCI framework consists of 5 parts:

#. Input modules
#. Output modules
#. :doc:`UI elements <ui>`
#. Applications
#. Glue logic (mostly main.py)


.. toctree::
   :maxdepth: 1

   ui.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


