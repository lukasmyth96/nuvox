import tkinter as tk
from tkinter import messagebox


class YesNoPopup():

    def __init__(self, master, message):
        self.popup = tk.Toplevel(master)
        self.popup.withdraw()
        self.popup.attributes("-topmost", True)
        self.popup.geometry()
        self.message = message

    def get_response(self):
        answered_yes = messagebox.askyesno(message=self.message, parent=self.popup)
        return answered_yes


