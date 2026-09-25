from .base_frame import BaseFrame
import tkinter as tk

class MainMenuFrame(BaseFrame):

    def build_widgets(self):

        self.config(padx=500)

     
        self.menu_label = tk.Label(
            self, text="Menu", font=("Arial", 50))
        self.menu_label.grid(column = 1, row = 0, sticky='ew')

        self.menu_buttons_frame = tk.Frame(self)
        self.menu_buttons_frame.columnconfigure(0, weight=1)
        self.menu_buttons_frame.grid(row=1, column=1, sticky='nsew')

        self.register_functions_button = tk.Button(
            self.menu_buttons_frame, text="Register\nFunctions", font=("Arial", 60),
            command = lambda: self.wm.show_frame("register_menu")
        )
        self.register_functions_button.grid(column = 0, row = 0, sticky='nsew',pady=5)

        self.admin_functions_button = tk.Button(
            self.menu_buttons_frame, text="Administrator\nFunctions", font=("Arial", 60),
            command = lambda: self.wm.show_frame("admin_menu")
        )
        self.admin_functions_button.grid(column = 0, row = 1, sticky='nsew', pady=5)

        self.main_menu_back_button = tk.Button(
            self.menu_buttons_frame, text="Back", font=("Arial", 60),
            command = lambda: self.wm.return_to_register()
        )
        self.main_menu_back_button.grid(column = 0, row = 2, sticky='nsew', pady=5)
        