from time import sleep
from copy import copy
from collections import OrderedDict

from ui import Canvas, Listbox, PrettyPrinter, FunctionOverlay
from ui.base_ui import BaseUIElement
from ui.utils import to_be_foreground
from helpers import flatten, Singleton
from apps import ZeroApp


class ToolBucket(Singleton):
    tools = OrderedDict()

    @classmethod
    def register_tool(self, name, obj):
        print("Registering tool {}".format(name))
        self.tools[name] = obj

    @classmethod
    def get_tools(self):
        return list(self.tools.items())


class ToolHandler(type):
    def __init__(cls, name, bases, clsdict):
        if hasattr(cls, "menu_name"):
            ToolBucket().register_tool(cls.menu_name, cls)
        super(ToolHandler, cls).__init__(name, bases, clsdict)


class DrawingTool(object):
    __metaclass__ = ToolHandler

    def __init__(self, board):
        self.board = board
        self.tool_is_up = False
        self.blink_on = True
        self.c = Canvas(self.board.o)
        self.init_vars()
        #ToolBucket().register_tool(self.menu_name, self)

    def init_vars(self):
        pass

    def on_enter(self):
        if hasattr(self, 'tool_up'):
            if self.tool_is_up:
                self.tool_up()
                self.tool_is_up = False
            else:
                self.tool_down()
                self.tool_is_up = True
        else:
            self.tool_down()

    def get_current_image(self):
        image = self.board.field.get_image()
        return self.modify_image(image)

    def modify_image(self, image):
        if self.blink_on:
            self.blink_on = False
            image = self.draw_tool_position(image)
            return image
        else:
            self.blink_on = True
            return image

    # A tool needs to implement at least these two, at the very least

    def tool_down(self):
        raise NotImplementedError

    def draw_tool_position(self, image):
        raise NotImplementedError


class PointTool(DrawingTool):
    menu_name = "Point"

    def tool_down(self):
        self.board.update_image(self.draw_tool_position(self.board.field.get_image()))

    def draw_tool_position(self, image):
        self.c.load_image(image)
        self.c.point(self.board.coords)
        return self.c.get_image()


class LineTool(DrawingTool):
    menu_name = "Line"

    def init_vars(self):
        self.start = None

    def tool_down(self):
        self.start = copy(self.board.coords)

    def tool_up(self):
        self.board.update_image(self.draw_tool_position(self.board.field.get_image()))
        self.start = None

    def draw_tool_position(self, image):
        self.c.load_image(image)
        if self.start:
            coords = self.start + self.board.coords
            self.c.line( coords )
        else:
            self.c.point(self.board.coords)
        return self.c.get_image()


class RectangleTool(LineTool):
    menu_name = "Rectangle"

    def draw_tool_position(self, image):
        self.c.load_image(image)
        if self.start:
            coords = self.start + self.board.coords
            self.c.rectangle( coords )
        else:
            self.c.point(self.board.coords)
        return self.c.get_image()


class EllipseTool(LineTool):
    menu_name = "Ellipse"

    def draw_tool_position(self, image):
        self.c.load_image(image)
        if self.start:
            coords = self.start + self.board.coords
            self.c.ellipse( coords )
        else:
            self.c.point(self.board.coords)
        return self.c.get_image()


class CircleTool(LineTool):
    menu_name = "Circle"

    def draw_tool_position(self, image):
        self.c.load_image(image)
        if self.start:
            radius = max( [ abs(self.start[0]-self.board.coords[0]),
                            abs(self.start[1]-self.board.coords[1])] )
            if radius > 0:
                coords = self.start + [radius]
                self.c.circle( coords )
            else:
                self.c.point(self.board.coords)
        else:
            self.c.point(self.board.coords)
        return self.c.get_image()


class PolygonTool(DrawingTool):
    menu_name = "Polygon"

    def init_vars(self):
        self.polygon_coords = []

    def tool_down(self):
        if self.board.coords in self.polygon_coords:
            self.polygon_coords.append(copy(self.board.coords))
            self.board.update_image(self.draw_tool_position(self.board.field.get_image(), final=True))
            self.polygon_coords = []
        else:
            self.polygon_coords.append(copy(self.board.coords))

    def draw_tool_position(self, image, final=False):
        pc = copy(self.polygon_coords)
        if not final: pc.append(copy(self.board.coords))
        self.c.load_image(image)
        if len(pc) > 2:
            self.c.polygon( pc )
        elif len(pc) == 2:
            self.c.line( flatten(pc) )
        elif len(pc) == 1:
            self.c.point( pc[0] )
        self.c.point(self.board.coords)
        return self.c.get_image()


class DrawingBoard(BaseUIElement):
    def __init__(self, i, o):
        BaseUIElement.__init__(self, i, o, "Drawing app's drawing board", override_left=False)
        self.reset()
        self.sleep_time = 0.01
        self.view_wrappers = []

    def idle_loop(self):
        self.display_tool_image()
        sleep(self.sleep_time)

    @to_be_foreground
    def display_tool_image(self):
        image = self.tool.get_current_image()
        for wrapper in self.view_wrappers:
            image = wrapper(image)
        self.o.display_image(image)

    def add_view_wrapper(self, wrapper):
        self.view_wrappers.append(wrapper)

    def reset(self):
        self.coords = [0, 0]
        self.field = Canvas(self.o)
        self.tool = PointTool(self)

    def on_enter(self):
        self.tool.on_enter()

    def load_image(self, image):
        self.field.load_image(image)

    def update_image(self, image):
        self.field.load_image(image)
        self.refresh()

    def move_up(self):
        y = self.coords[1]
        if y > 1:
            self.coords[1] = y - 1
            self.refresh()

    def move_down(self):
        y = self.coords[1]
        if y < self.field.height-1:
            self.coords[1] = y + 1
            self.refresh()

    def move_left(self):
        x = self.coords[0]
        if x > 1:
            self.coords[0] = x - 1
            self.refresh()

    def move_right(self):
        x = self.coords[0]
        if x < self.field.width-1:
            self.coords[0] = x + 1
            self.refresh()

    def tool_settings(self):
        pass

    def back(self):
        self.deactivate()

    def pick_tools(self):
        lb_contents = ToolBucket().get_tools()
        choice = Listbox(lb_contents, self.i, self.o, "Drawing app tool picker listbox").activate()
        if choice:
            self.tool = choice(self)

    def generate_keymap(self):
        return {
            "KEY_UP": "move_up",
            "KEY_DOWN": "move_down",
            "KEY_LEFT": "move_left",
            "KEY_RIGHT": "move_right",
            "KEY_ENTER": "on_enter",
            "KEY_F3": self.tool_settings,
            "KEY_F1": "back",
            "KEY_F2": self.pick_tools}

    @to_be_foreground
    def refresh(self):
        self.field.display()


class DrawingApp(ZeroApp):
    menu_name = "Draw"

    def on_start(self):
        PrettyPrinter("No image saving implemented yet!", self.i, self.o, 3)
        board = DrawingBoard(self.i, self.o)
        FunctionOverlay(["back", board.pick_tools], labels=["Exit", "Tools"]).apply_to(board)
        board.activate()
