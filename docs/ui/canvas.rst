.. _ui_canvas:

#####################
Canvas
#####################

.. code-block:: python
                      
    from ui import Canvas
    ...
    c = Canvas(o)
    c.text("Hello world", (10, 20))
    c.display()

.. automodule:: ui.canvas

.. autoclass:: Canvas
    :show-inheritance:
    :members: point,line,text,rectangle,circle,ellipse,display,clear,get_image,get_center,invert,invert_rect,width,height,size,image,background_color,default_color,get_text_bounds,get_centered_text_bounds,check_coordinates,load_font
