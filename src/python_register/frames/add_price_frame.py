import tkinter as tk
from pathlib import Path

import pygame

from .base_frame import BaseFrame


class AddPriceFrame(BaseFrame):

    def build_widgets(self):

        self.config(padx=50)
        pygame.mixer.init()

        self.wm.price_var.trace_add("write", self.number_pressed)
        self.price_entry_var = tk.StringVar()

        tk.Label(
            self, text="Please enter item's price:", font=("Arial", 50), width=25
        ).grid(column=1, row=0, sticky="ew")
        self.add_price_entry = tk.Entry(
            self, font=("Arial", 50), justify="right", textvariable=self.price_entry_var
        )
        self.add_price_entry.grid(column=1, row=1, sticky="ew", pady=15)

        self.add_price_invisible_entry = tk.Entry(
            self, validate="key", vcmd=self.wm.vcmd, textvariable=self.wm.price_var
        )
        self.add_price_invisible_entry.place(x=-100, y=-100)
        self.add_price_invisible_entry.bind(
            "<Return>", lambda event: self.controller.on_add_item_enter()
        )
        for key in ("Left", "Right", "Up", "Down"):
            self.add_price_invisible_entry.bind(f"<{key}>", self.disable_arrow_keys)
        self.add_price_entry.bind(
            "<FocusIn>", lambda e: self.return_invisible_entry_focus()
        )
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
        self.add_price_back_button = tk.Button(
            back_quit_frame,
            text="Back",
            font=("Arial", 50),
            command=lambda: self.controller.go_back(),
        )
        self.add_price_back_button.grid(column=0, row=0, sticky="ew", padx=(0, 15))
        tk.Button(
            back_quit_frame,
            text="Quit",
            font=("Arial", 50),
            command=lambda: self.wm.show_frame("main_menu"),
        ).grid(column=1, row=0, sticky="ew")

    def disable_arrow_keys(self, event):
        return "break"

    def return_invisible_entry_focus(self):
        self.add_price_invisible_entry.focus_set()
        return "break"

    def on_show(self, reentering=False):

        self.price_entry_var.set("$0.00")

        self.add_price_invisible_entry.delete(0, tk.END)
        self.add_price_invisible_entry.focus_set()

        if reentering:
            self.add_price_back_button.config(
                command=lambda: self.controller.reenter_back_button()
            )

    def number_pressed(self, *args):
        """NEED TO PASS PYGAME MIXER SO BEEPS WORK"""

        pygame.mixer.music.load(Path(__file__).parent / "../short-beep.mp3")
        pygame.mixer.music.play()

        string = self.add_price_invisible_entry.get().strip()

        while len(string) < 3:
            string = "0" + string

        self.price_entry_var.set(f"${string[0:-2]}.{string[-2:]}")
