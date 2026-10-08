import tkinter as tk

from .base_frame import BaseFrame


class RegisterAddItemPromptFrame(BaseFrame):

    def build_widgets(self):

        self.add_item_yes_no_frame = tk.Frame(self)
        self.add_item_yes_no_frame.grid(row=1, column=1, sticky="nsew")
        self.add_item_yes_no_frame.columnconfigure(0, weight=1)
        self.add_item_yes_no_frame.columnconfigure(1, weight=1)

        self.register_add_item_prompt_label = tk.Label(
            self,
            text="Item not found\nAdd it?",
            font=("Arial", 50),
        )
        self.register_add_item_prompt_label.grid(row=0, column=1, sticky="ew")

        self.register_add_item_yes_button = tk.Button(
            self.add_item_yes_no_frame,
            text="Yes",
            font=("Arial", 150),
            command=lambda: self.controller.state_mgr.register_yes_no_var.set("yes"),
        )
        self.register_add_item_yes_button.grid(row=0, column=0, sticky="nsew")

        self.register_add_item_no_button = tk.Button(
            self.add_item_yes_no_frame,
            text="No",
            font=("Arial", 150),
            command=lambda: self.controller.state_mgr.register_yes_no_var.set("no"),
        )
        self.register_add_item_no_button.grid(row=0, column=1, sticky="nsew")
