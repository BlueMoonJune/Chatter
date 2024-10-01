from pyray import *
from math import *
import raylib
from random import randint

#FONT = load_font("Roboto-Regular.ttf")
FONT_SIZE = 20
FONT_SPACING = 2
INDENT = 10
SCROLL_SPEED = 20

class Message():
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content

def measure_text_ex(font: Font, text: str, size: float, spacing: float):
    width = 0
    for c in text:
        #index = raylib.GetGlyphInfo(font, 33)
        #glyph: GlyphInfo = font.glyphs[index]
        #rec = font.recs[index]
        #width += (rec.width if glyph.advanceX == 0 else glyph.advanceX) * size
        pass
    return width

'''
def word_wrap(text: str, width, size):
    ret = ""
    buffer = ""
    for c in text:
        if c in " \n\t":
            if measure_text(ret + buffer, size) > width:

    return ret
'''
def main():

    scroll = -100
    realscroll = 0
    bottom = 0

    messages = [
        Message("John", "Lorem ipsum dolor sit amet"),
        Message("John", "Lorem ipsum dolor sit amet"),
        Message("John", "Lorem ipsum dolor sit amet"),
        Message("Jane", "Lorem ipsum dolor sit amet"),
        Message("Jane", "Lorem ipsum dolor sit amet"),
    ]

    for i in range(1, 100):
        if randint(0, 1) == 1:
            messages.append(Message("aaa", "Lorem ipsum"))
        else:
            messages.append(Message("Wowowow", "Lorem ipsum"))

    init_window(1600, 900, "chat.py")
    set_window_state(raylib.FLAG_WINDOW_RESIZABLE)

    win_size = (800, 600)

    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\nUt enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\nExcepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

    while not window_should_close():

        new_size = (get_screen_width(), get_screen_height())
        if new_size != win_size:
            win_size = new_size

        scroll -= get_mouse_wheel_move_v().y * SCROLL_SPEED
        if scroll != -100:
            scroll = clamp(scroll, 0, bottom)
        print(scroll)
        realscroll = (scroll-realscroll)*0.1+realscroll

        begin_drawing()
        clear_background(WHITE)
        y = 0
        last_sender = None
        for message in messages:
            if last_sender != message.sender:
                y += int(FONT_SIZE / 2)
                last_sender = message.sender
                draw_text(last_sender, 0, y - int(realscroll), FONT_SIZE, BLACK)
                y += FONT_SIZE
            draw_text(message.content, INDENT, y - int(realscroll), FONT_SIZE, BLACK)
            y += FONT_SIZE
        end_drawing()

        bottom = y - win_size[1] + 100
        if scroll == -100:
            scroll = bottom

    close_window()


if __name__ == '__main__':
    main()
