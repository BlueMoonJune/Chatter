from random import random

from pyray import *
import raylib
from enum import Enum
from abc import abstractmethod

SCROLL_SPEED = 20

class MouseEvent:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class ScrollEvent(MouseEvent):
    def __init__(self, x, y, v, h):
        super().__init__(x, y)
        self.v = v
        self.h = h

class MouseButtonEvent(MouseEvent):
    def __init__(self, x, y, b, s):
        super().__init__(x, y)
        self.b = b
        self.s = s

class EventResult:
    PASS = 0
    SUCCESS = 1

class Fit:
    pass

class Fill(Fit):
    def __init__(self, weight):
        self.weight = weight

class Static(Fit):
    def __init__(self, size):
        self.size = size

class SizedElement:

    def __init__(self):
        self.w = 0
        self.h = 0
        self.y = 0
        self.x = 0
        self.parent = 0

    def set_bounds(self, **kwargs):
        self.__dict__.update(**kwargs)
        print(self.x)

    def draw(self):
        pass

    def mouse_input(self, event: MouseEvent):
        return EventResult.PASS

class VBox(SizedElement):

    def __init__(self, *args: tuple[SizedElement, Fit]):
        super().__init__()
        self.children = args

    def set_bounds(self, **kwargs):
        super().set_bounds(**kwargs)
        print("bounds")
        space = self.h
        weights = 0
        for (child, fit) in self.children:
            if isinstance(fit, Static):
                space -= fit.size
            elif isinstance(fit, Fill):
                weights += fit.weight
            else:
                raise Exception(f"Invalid Fit {fit}")
        y = self.y
        for (child, fit) in self.children:
            if isinstance(fit, Static):
                child.set_bounds(x=self.x, y=y, w=self.w, h=fit.size)
                y += fit.size
            elif isinstance(fit, Fill):
                height = fit.weight/weights*space
                child.set_bounds(x=self.x, y=y, w=self.w, h=height)
                y += height
            else:
                raise Exception(f"Invalid Fit {fit}")

    def draw(self):
        for (child, _) in self.children:
            child.draw()

    def mouse_input(self, event: MouseEvent):
        print(self, "mouse_input", event)
        for (child, _) in self.children:
            if event.y < child.y + child.h:
                res = child.mouse_input(event)
                if res:
                    return res
        return EventResult.PASS

class HBox(SizedElement):

    def __init__(self, *args: tuple[SizedElement, Fit]):
        super().__init__()
        self.children = args

    def set_bounds(self, **kwargs):
        super().set_bounds(**kwargs)
        space = self.w
        weights = 0
        for (child, fit) in self.children:
            if isinstance(fit, Static):
                space -= fit.size
            elif isinstance(fit, Fill):
                weights += fit.weight
            else:
                raise Exception(f"Invalid Fit {fit}")
        x = self.x
        for (child, fit) in self.children:
            if isinstance(fit, Static):
                child.set_bounds(y=self.y, x=x, h=self.h, w=fit.size)
                x += fit.size
            elif isinstance(fit, Fill):
                height = fit.weight/weights*space
                child.set_bounds(y=self.y, x=x, h=self.h, w=height)
                x += height
            else:
                raise Exception(f"Invalid Fit {fit}")

    def draw(self):
        for (child, _) in self.children:
            child.draw()

    def mouse_input(self, event: MouseEvent):
        print(self, "mouse_input", event)
        for (child, _) in self.children:
            if event.x < child.x + child.w:
                res = child.mouse_input(event)
                if res:
                    return res
                continue
        return EventResult.PASS

class ScrollContainer(SizedElement):
    def __init__(self, child):
        super().__init__()
        self.child = child

    def set_bounds(self, **kwargs):
        oldx, oldy = self.x, self.y
        super().set_bounds(**kwargs)
        self.child.set_bounds(
            x=self.child.x + self.x - oldx,
            y=self.child.y + self.y - oldy
        )

    def draw(self):
        begin_scissor_mode(int(self.x), int(self.y), int(self.w), int(self.h))
        self.child.draw()
        end_scissor_mode()

    def mouse_input(self, event: MouseEvent):
        print(event.__dict__)
        res = self.child.mouse_input(event)
        if res: return res
        if isinstance(event, ScrollEvent):
            oldx, oldy = self.child.x, self.child.y
            x, y = oldx, oldy
            x = clamp(x + event.h * SCROLL_SPEED, self.x + self.w - self.child.w, self.x)
            y = clamp(y + event.v * SCROLL_SPEED, self.y + self.h - self.child.h, self.y)
            if x != oldx or y != oldy:
                self.child.set_bounds(x=x, y=y)
                return EventResult.SUCCESS

class VScrollContainer(ScrollContainer):
    def set_bounds(self, **kwargs):
        super().set_bounds(**kwargs)
        self.child.set_bounds(x=self.x, w=self.w)

    def mouse_input(self, event: MouseEvent):
        event.v += event.h
        event.h = 0
        super().mouse_input(event)

class HScrollContainer(ScrollContainer):
    def set_bounds(self, **kwargs):
        super().set_bounds(**kwargs)
        self.child.set_bounds(y=self.y, h=self.h)

    def mouse_input(self, event: MouseEvent):
        event.h += event.v
        event.v = 0
        super().mouse_input(event)

class DebugBox(SizedElement):
    def __init__(self, color: Color):
        super().__init__()
        self.color = color

    def draw(self):
        draw_rectangle(int(self.x), int(self.y), int(self.w), int(self.h), self.color)

    def mouse_input(self, event: MouseEvent):
        if isinstance(event, MouseButtonEvent) and event.b == 0 and event.s == 1:
            print(self.__dict__, "clicked")
            self.color = Color(255, 255, 255, 255)
            return EventResult.SUCCESS
        return EventResult.PASS

class Image(SizedElement):
    def __init__(self, image: Texture):
        super().__init__()
        self.image = image,
        self.w = image.width
        self.h = image.height

    def draw(self):
        draw_texture(self.image[0], int(self.x), int(self.y), WHITE)



if __name__ == "__main__":
    init_window(1600, 900, "rayui test")
    set_window_state(raylib.FLAG_WINDOW_RESIZABLE)

    root = HBox(
        (VBox(
            (DebugBox(RED), Static(50)),
            (HScrollContainer(
                Image(load_texture("image.png"))
            ), Fill(1)),
            (DebugBox(PURPLE), Static(100)),
        ), Fill(1)),
        (DebugBox(GRAY), Static(300))
    )
    root.set_bounds(w=1600, h=900)

    win_size = (get_screen_width(), get_screen_height())
    while not window_should_close():
        new_size = (get_screen_width(), get_screen_height())
        if win_size != new_size:
            win_size = new_size
            root.set_bounds(w=win_size[0], h=win_size[1])

        x = get_mouse_x()
        y = get_mouse_y()
        for i in range(3):
            if is_mouse_button_pressed(i):
                root.mouse_input(MouseButtonEvent(x, y, i, 1))
            if is_mouse_button_released(i):
                root.mouse_input(MouseButtonEvent(x, y, i, 0))
        scroll = get_mouse_wheel_move_v()
        if not scroll.x == scroll.y == 0:
            root.mouse_input(ScrollEvent(x, y, scroll.y, scroll.x))


        begin_drawing()
        root.draw()
        end_drawing()

    close_window()


