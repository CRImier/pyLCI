.. _logging_config:

Logging configuration
#####################

Changing log levels
===================

In case of problems with ZPUI, logs can help you understand it - especially when
the problem is not easily repeatable. To enable verbose logging for a particular
system/app/driver, go to ``"Settings"->"Logging settings"`` menu, then click on
the part of ZPUI that you're interested in and pick "Debug". From now on, that part
of ZPUI will log a lot more in ``zpui.log`` files - which you can then read through,
or send to the developers.

Alternatively, you can change the log_conf.ini file directly. In it, add a new
section for the app you want to learn, like this:

.. code-block:: ini

    [path.to.code.file]
    level = debug

``path.to.code.file`` would be the Python-style path to the module you want to debug,
for example, ``input.input``, ``context_manager`` or ``apps.network_apps.wpa_cli``.

