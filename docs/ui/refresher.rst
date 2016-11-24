.. _ui_refresher:

#####################
Refresher UI element
#####################

``from ui import Refresher
counter = 0
def get_data():
    counter += 1
    return [str(counter), str(1000-counter)] #Return value will be sent directly to output.display_data
Refresher(get_data, i, o, 1, name="Counter view").activate()

``

Contents:

.. toctree::
   :maxdepth: 2

.. automodule:: ui.refresher

.. autoclass:: Refresher
    :members: __init__,activate,deactivate,print_name

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

