import tkinter as tk

from .base_frame import BaseFrame


class RegisterMenuFrame(BaseFrame):

    def build_widgets(self):

        buttons_frame = tk.Frame(self)
        buttons_frame.grid(column=1, row=0, sticky="nsew")
        buttons_frame.columnconfigure(0, weight=1, uniform="equal")
        buttons_frame.columnconfigure(1, weight=1, uniform="equal")

        self.void_button = tk.Button(
            buttons_frame,
            text="Void Trans",
            font=("Arial", 58),
            command=lambda: self.wm.show_frame(
                "browse_transactions", browse_mode="void"
            ),
        )

        self.print_receipt_button = tk.Button(
            buttons_frame,
            text="Print Receipt",
            font=("Arial", 58),
            command=lambda: self.wm.show_frame(
                "browse_transactions", browse_mode="browse"
            ),
        )

        self.make_return_button = tk.Button(
            buttons_frame,
            text="Make Return",
            font=("Arial", 58),
            command=lambda: self.controller.process_return(),
        )

        self.back_to_register_button = tk.Button(
            buttons_frame,
            text="Back",
            font=("Arial", 58),
            command=lambda: self.wm.show_frame("main_menu"),
        )

        self.seasonal_button = tk.Button(
            buttons_frame,
            text="Seasonal Sale",
            font=("Arial", 58),
            command=lambda: self.setup_seasonal_sale(),
        )

        self.coupon_button = tk.Button(
            buttons_frame,
            text="Apply coupon",
            font=("Arial", 58),
            command=lambda: self.coupon_frame.tkraise(),
        )

        self.lookup_item_button = tk.Button(
            buttons_frame,
            text="Lookup Item",
            font=("Arial", 58),
            command=lambda: self.wm.show_frame("lookup_items"),
        )

        self.void_button.grid(column=0, row=0, sticky="nsew", pady=2)
        self.print_receipt_button.grid(column=1, row=0, sticky="nsew", pady=2)
        self.make_return_button.grid(column=0, row=1, sticky="nsew", pady=2)
        self.back_to_register_button.grid(column=1, row=1, sticky="nsew", pady=2)
        # self.seasonal_button.grid(column = 0, row = 2, sticky='nsew', pady=2)
        # self.coupon_button.grid(column = 1, row = 2, sticky='nsew', pady=2)
        self.lookup_item_button.grid(column=0, row=3, sticky="nsew", pady=2)
