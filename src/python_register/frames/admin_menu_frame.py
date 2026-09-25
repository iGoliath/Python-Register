import tkinter as tk

from .base_frame import BaseFrame


class AdminMenuFrame(BaseFrame):

    def build_widgets(self):

        buttons_frame = tk.Frame(self)
        buttons_frame.grid(column=1, row=0, sticky="nsew")
        buttons_frame.columnconfigure(0, weight=1, uniform="equal")
        buttons_frame.columnconfigure(1, weight=1, uniform="equal")

        self.run_x_button = tk.Button(
            buttons_frame,
            text="Run X",
            font=("Arial", 58),
            height=1,
            command=lambda: self.wm.show_frame("print_summaries"),
        )

        self.new_item_button = tk.Button(
            buttons_frame,
            text="Manage Inv",
            font=("Arial", 58),
            height=1,
            command=lambda: self.controller.enter_add_item_frame(),
        )

        self.browse_transactions_button = tk.Button(
            buttons_frame,
            text="Browse Trans",
            font=("Arial", 58),
            command=lambda: self.wm.show_frame(
                "browse_transactions", browse_mode="browse"
            ),
        )

        self.quit_program_button = tk.Button(
            buttons_frame,
            text="Quit Program",
            font=("Arial", 58),
            command=lambda: self.wm.quit_program(),
        )

        self.run_reports_button = tk.Button(
            buttons_frame,
            text="Run Reports",
            font=("Arial", 58),
            command=lambda: self.wm.show_frame("run_reports"),
        )

        self.settings_menu_button = tk.Button(
            buttons_frame,
            text="Settings",
            font=("Arial", 58),
            command=lambda: self.wm.show_frame("settings"),
        )

        self.admin_menu_back_button = tk.Button(
            buttons_frame,
            text="Back",
            font=("Arial", 58),
            command=lambda: self.wm.show_frame("main_menu"),
        )

        self.run_x_button.grid(column=0, row=0, sticky="nsew", pady=2)
        self.new_item_button.grid(column=1, row=0, sticky="nsew", pady=2)
        self.browse_transactions_button.grid(column=1, row=1, sticky="nsew", pady=2)
        self.quit_program_button.grid(column=0, row=1, sticky="nsew", pady=2)
        self.admin_menu_back_button.grid(column=0, row=2, sticky="nsew", pady=2)
        self.run_reports_button.grid(column=1, row=2, sticky="nsew", pady=2)
        self.settings_menu_button.grid(column=0, row=3, sticky="nsew")

    def on_show(self):
        pass
