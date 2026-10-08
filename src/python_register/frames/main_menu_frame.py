import tkinter as tk

from .base_frame import BaseFrame


class MainMenuFrame(BaseFrame):

    def build_widgets(self):

        self.menu_label = tk.Label(self, text="Menu", font=("Arial", 50))
        self.menu_label.grid(column=1, row=0, sticky="nsew")

        self.register_functions_button = tk.Button(
            self,
            text="Register\nFunctions",
            font=("Arial", 60),
            command=lambda: self.wm.show_frame("register_menu"),
        )
        self.register_functions_button.grid(column=1, row=1, sticky="nsew", pady=5)

        self.admin_functions_button = tk.Button(
            self,
            text="Administrator\nFunctions",
            font=("Arial", 60),
            command=lambda: self.wm.show_frame("admin_menu"),
        )
        self.admin_functions_button.grid(column=1, row=2, sticky="nsew", pady=5)

        self.main_menu_back_button = tk.Button(
            self,
            text="Back",
            font=("Arial", 60),
            command=lambda: self.wm.show_frame("register"),
        )
        self.main_menu_back_button.grid(column=1, row=3, sticky="nsew", pady=5)
