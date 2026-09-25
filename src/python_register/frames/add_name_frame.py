from .base_frame import BaseFrame
import tkinter as tk

class AddNameFrame(BaseFrame):

    def build_widgets(self):

        self.config(padx=50)

        tk.Label(self, text="Please enter item's name:", 
        font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')
        self.add_name_entry = tk.Entry(
            self, font=("Arial", 50), justify="right", textvariable=self.wm.name_var)
        self.add_name_entry.grid(column = 1, row = 1, sticky='ew', pady=15)
        self.add_name_entry.bind("<Return>", lambda event: self.controller.on_add_item_enter())
        tk.Button(
            self, text="Next", font=("Arial", 50),
            command = lambda: self.controller.on_add_item_enter()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        self.add_name_back_button = tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back())
        self.add_name_back_button.grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.wm.show_frame("main_menu")).grid(
                column = 1, row = 0, sticky='ew'
            )

    def on_show(self, reentering = False):

        self.add_name_entry.focus_set()
        if reentering:
            self.add_name_back_button.config(command = lambda: self.controller.reenter_back_button())