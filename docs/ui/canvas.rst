.. _ui_canvas:

#####################
Canvas
#####################

.. code-block:: python
                      
    from ui import Canvas
    ...
    c = Canvas(o)
    c.text((0, 0), "Text you want to draw", fill="white")
    c.display()

.. automodule:: ui
 
.. autoclass:: Canvas
    :show-inheritance:
    :members: point,line,text,rectangle,display,load_font,get_image,get_center,invert,width,height,size,image,background_color,default_color,invert_rect_colors,check_coordinates,clear
