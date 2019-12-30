
import random
import time
from tkinter import *

import pyautogui


class Display:

    def __init__(self, keyboard, display_width, display_height):

        """
        Encapsulates the Keyboard display
        Parameters
        ----------
        keyboard: nuvox.keyboard.Keyboard
            keyboard object containing information about the keyboard layout and contents of each key
        display_width: int
            width of display in pixels
        display_height: int
            height of display in pixels
        """

        self.keyboard = keyboard
        self.display_width = display_width
        self.display_height = display_height

        self.gui = Tk()
        self.gui.configure(background="light green")
        self.gui.title("nuvox keyboard")
        self.gui.geometry("{}x{}".format(self.display_width, self.display_height))
        self.gui.resizable(width=False, height=False)
        self.gui.bind('<Motion>', self.record_mouse_position)

        self.display_text = ""
        self.display_variable = StringVar()

        # dict mapping key_id to TK object
        self.key_list = []

        self.pointer = None
        self.build_display()

    def build_display(self):
        """ Build gui from information in keyboard object"""
        for key in self.keyboard.keys:

            if key.type == 'button':
                text = ' '.join(key.contents).upper()
                callback = lambda id: lambda: self.press_key(id)
                obj = Button(self.gui, text=text, fg='black', bg='steel blue', command=callback(key.key_id), font=("Calibri 18"))

            elif key.type == 'clear_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg='black', bg='steel blue', command=lambda: self.clear_display(), font=("Calibri 14"))

            elif key.type == 'exit_button':
                text = ' '.join(key.contents).upper()
                obj = Button(self.gui, text=text, fg='black', bg='steel blue', command=lambda: self.exit(), font=("Calibri 14"))

            elif key.type == 'display':
                obj = Entry(self.gui, textvariable=self.display_variable, font=("Calibri 18"))

            else:
                raise ValueError('Key type: {} not handled yet in build_display method'.format(key.type))

            obj.place(relx=key.x1, rely=key.y1, relwidth=key.w, relheigh=key.h)
            self.key_list.append(obj)

        self.pointer = Label(self.gui, text='', bg='red', font=("Calibri 18"))
        self.pointer.place(relx=0.5, rely=0.5, relwidth=0.05, relheight=0.05)

    def start_display(self):
        """ Start display"""
        self.gui.mainloop()

    def press_key(self, key_id):
        """ method for updating display text when key is pressed"""

        # TODO currently just selects character randomly from the keys contents

        key_contents = self.keyboard.key_id_to_contents[key_id]
        random_choice = random.choice(key_contents)

        self.display_text = self.display_text + str(random_choice)

        self.display_variable.set(self.display_text)

    # of text entry box
    def clear_display(self):
        self.display_text = ""
        self.display_variable.set("")

    def exit(self):
        self.gui.destroy()

    def record_mouse_position(self, event):

        relx = (self.gui.winfo_pointerx() - self.gui.winfo_x()) / self.gui.winfo_width()
        rely = (self.gui.winfo_pointery() - self.gui.winfo_y()) / self.gui.winfo_height()

        print('{:.2f}, {:.2f}'.format(relx, rely))
        print('\n\n')
        self.move_pointer(relx, rely)

    def move_pointer(self, x, y):
        """move mouse pointer to position x, y"""
        self.pointer.place(relx=x, rely=y)


if __name__ == "__main__":
    """ Testing"""
    from nuvox.config.keyboard_config import nuvox_standard_keyboard
    from nuvox.keyboard import Keyboard

    _keyboard = Keyboard()
    _keyboard.build_keyboard(nuvox_standard_keyboard)
    _display = Display(_keyboard, display_width=900, display_height=1200)
    _display.start_display()


