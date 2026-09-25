import tkinter as tk

from ..widget_functions import disable_arrow_keys
from .base_frame import BaseFrame


class AddQuantityFrame(BaseFrame):

    def build_widgets(self):

        self.config(padx=50)

        self.add_quantity_label_var = tk.StringVar()
        self.add_quantity_label = tk.Label(
            self,
            textvariable=self.add_quantity_label_var,
            font=("Arial", 50),
            width=25,
        )
        self.add_quantity_label.grid(column=1, row=0, sticky="ew")
        self.add_quantity_label_var.set("Please enter item's quantity:")

        self.add_quantity_entry = tk.Entry(
            self,
            font=("Arial", 50),
            justify="right",
            validate="key",
            textvariable=self.wm.quantity_var,
        )
        self.add_quantity_entry.grid(column=1, row=1, sticky="ew", pady=15)
        self.add_quantity_entry.bind(
            "<Return>", lambda e: self.controller.on_add_item_enter()
        )

        for key in ("Left", "Right", "Up", "Down"):
            self.add_quantity_entry.bind(f"<{key}>", disable_arrow_keys)

        tk.Button(
            self,
            text="Next",
            font=("Arial", 50),
            command=lambda: self.controller.on_add_item_enter(),
        ).grid(column=1, row=2, sticky="ew")
        back_quit_frame = tk.Frame(self)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column=1, row=3, sticky="ew", pady=(15, 0))
        self.add_quantity_back_button = tk.Button(
            back_quit_frame,
            text="Back",
            font=("Arial", 50),
            command=lambda: self.controller.go_back(),
        )
        self.add_quantity_back_button.grid(column=0, row=0, sticky="ew", padx=(0, 15))
        tk.Button(
            back_quit_frame,
            text="Quit",
            font=("Arial", 50),
            command=lambda: self.wm.show_frame("main_menu"),
        ).grid(column=1, row=0, sticky="ew")

    def on_show(self, reentering=False):

        if reentering:
            self.add_quantity_back_button.config(
                command=lambda: self.controller.reenter_back_button()
            )
            self.add_quantity_label_var.set(
                f"Current quantity is: {self.controller.state_mgr.add_item_dictionary.quantity}\nNew quantity will be:"
            )
        else:
            self.add_quantity_label_var.set("Please enter item's quantity:")

        self.add_quantity_entry.focus_set()
