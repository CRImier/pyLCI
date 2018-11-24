#############################
Working on this documentation
#############################

If you want to help the project by working on documentation, this is the tutorial on how to start!

==============
Pre-requisites
==============

* Fork the `ZPUI repository`_ on GitHub
* Create a separate branch for your documentation needs
* Install the necessary Python packages for testing the documentation locally:

    ``pip install sphinx sphinx-autobuild sphinx-rtd-theme``

.. _ZPUI repository: https://github.com/ZeroPhone/ZPUI/

======================
Find a task to work on
======================

* Look into `ZPUI GitHub issues`_ and see if there are issues concerning documentation
* Unleash your inner perfectionist
* If you're not intimately familiar with reStructuredText markup, feel free to look through the existing documentation to see syntax and solutions that are already used.

.. _ZPUI GitHub issues: https://github.com/ZeroPhone/ZPUI/issues

============================
Testing your changes locally
============================

You can build the documentation using ``make html`` from the ``docs/`` folder. Then,
you can run ``./run_server.py`` to run a HTTP server on localhost, serving the
documentation on port 8000. If you make changes to the documentation, just run
``make html`` again to rebuild the documentation - webserver will serve the updated
documentation once it finishes building. In addition to that, you can test the code
blocks for errors using ``docs/test.sh`` - you need to have ``rstcheck`` installed
from pip for that to work.

=========================
Contributing your changes
=========================

Send us `a pull request`_!

.. _a pull request: https://github.com/ZeroPhone/ZPUI/compare

============
Useful links
============

* `ReadTheDocs "Getting started" guide`_

.. _ReadTheDocs "Getting started" guide: http://docs.readthedocs.io/en/latest/getting_started.html
