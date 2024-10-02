import math
from imaplib import Debug
from random import random

from pyray import *
import raylib
from enum import Enum
from abc import abstractmethod

SCROLL_SPEED = 20

focus = None

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
        self.parent = None

    def set_bounds(self, **kwargs):
        self.__dict__.update(**kwargs)
        print(self.x)

    def update_bounds(self):
        self.set_bounds(x=self.x, y=self.y, w=self.w, h=self.h)

    def draw(self):
        pass

    def mouse_input(self, event: MouseEvent):
        return EventResult.PASS

class VBox(SizedElement):

    def __init__(self, *children: tuple[SizedElement, Fit]):
        super().__init__()
        self.children = children
        for (child, _) in children:
            child.parent = self

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

    def __init__(self, *children: tuple[SizedElement, Fit]):
        super().__init__()
        self.children = children
        for (child, _) in children:
            child.parent = self

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

class VStretch(SizedElement):
    def __init__(self, *children: tuple[SizedElement, Static]):
        super().__init__()
        self.children = children
        for (child, _) in children:
            child.parent = self

    def set_bounds(self, **kwargs):
        super().set_bounds(**kwargs)
        print(kwargs)
        y = self.y
        for (child, size) in self.children:
            child.set_bounds(y=y, x=self.x, h=size.size, w=self.w)
            y += size.size
            print(child.__dict__)
        self.h = y - self.y
        print(self.__dict__)

    def mouse_input(self, event: MouseEvent):
        print(self, "mouse_input", event)
        for (child, _) in self.children:
            if event.y < child.y + child.h:
                res = child.mouse_input(event)
                if res:
                    return res
                continue
        return EventResult.PASS

    def draw(self):
        for (child, _) in self.children:
            child.draw()

class HStretch(SizedElement):
    def __init__(self, *children: tuple[SizedElement, Static]):
        super().__init__()
        self.children = children
        for (child, _) in children:
            child.parent = self

    def set_bounds(self, **kwargs):
        super().set_bounds(**kwargs)
        print(kwargs)
        x = self.x
        for (child, size) in self.children:
            child.set_bounds(x=x, y=self.y, w=size.size, h=self.h)
            x += size.size
            print(child.__dict__)
        self.w = x - self.x
        print(self.__dict__)

    def mouse_input(self, event: MouseEvent):
        print(self, "mouse_input", event)
        for (child, _) in self.children:
            if event.x < child.x + child.w:
                res = child.mouse_input(event)
                if res:
                    return res
                continue
        return EventResult.PASS

    def draw(self):
        for (child, _) in self.children:
            child.draw()

class ScrollContainer(SizedElement):
    def __init__(self, child):
        super().__init__()
        self.child = child
        child.parent = self

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
            return self.scroll(event.h, event.v)

    def scroll(self, v, h):
        oldx, oldy = self.child.x, self.child.y
        x, y = oldx, oldy
        x = clamp(x + h * SCROLL_SPEED, self.x + self.w - self.child.w, self.x)
        y = clamp(y + v * SCROLL_SPEED, self.y + self.h - self.child.h, self.y)
        if x != oldx or y != oldy:
            self.child.set_bounds(x=x, y=y)
            return EventResult.SUCCESS


class VScrollContainer(ScrollContainer):
    def set_bounds(self, **kwargs):
        super().set_bounds(**kwargs)
        self.child.set_bounds(x=self.x, w=self.w)

    def scroll(self, v, h):
        super().scroll(v + h, 0)

class HScrollContainer(ScrollContainer):
    def set_bounds(self, **kwargs):
        super().set_bounds(**kwargs)
        self.child.set_bounds(y=self.y, h=self.h)

    def scroll(self, v, h):
        super().scroll(0, v + h)

class DebugBox(SizedElement):
    def __init__(self, color: Color):
        super().__init__()
        self.color = color

    def draw(self):
        x, y, w, h = int(self.x), int(self.y), int(self.w), int(self.h)
        if self == focus:
            print("focus")
            x += 10
            y += 10
            w -= 20
            h -= 20
        draw_rectangle(x, y, w, h, self.color)

    def mouse_input(self, event: MouseEvent):
        global focus
        if isinstance(event, MouseButtonEvent) and event.b == 0 and event.s == 1:
            print(self.__dict__, "clicked")
            focus = self
            print("get focus")
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

class ScalingTest(DebugBox):
    def __init__(self, color):
        super().__init__(color)
        self.scale = Static(500)

    def draw(self):
        self.scale.size = math.sin(get_time()) * 100 + 300
        self.parent.update_bounds()
        super().draw()

    def to_pair(self):
        return self, self.scale

class TextBox(SizedElement):
    def __

if __name__ == "__main__":
    init_window(1600, 900, "rayui test")
    set_window_state(raylib.FLAG_WINDOW_RESIZABLE)

    root = HBox(
        (VBox(
            (DebugBox(RED), Static(50)),
            (VScrollContainer(
                VStretch(
                    (DebugBox(RED), Static(300)),
                    (DebugBox(YELLOW), Static(300)),
                    (HBox(
                        (DebugBox(RED), Fill(1)),
                        ScalingTest(BLACK).to_pair(),
                        (DebugBox(GREEN), Static(300)),
                    ), Static(300)),
                    (DebugBox(BLUE), Static(300)),
                    (DebugBox(MAGENTA), Static(300)),
                )
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
        #clear_background(WHITE)
        root.draw()
        end_drawing()

    close_window()


