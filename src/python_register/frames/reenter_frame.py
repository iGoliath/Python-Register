import tkinter as tk

from .base_frame import BaseFrame


class ReenterFrame(BaseFrame):

    def build_widgets(self):

        buttons_frame = tk.Frame(self)
        buttons_frame.grid(column=1, row=0, sticky="nsew")
        buttons_frame.columnconfigure(0, weight=1, uniform="equal")
        buttons_frame.columnconfigure(1, weight=1, uniform="equal")

        self.add_name_button = tk.Button(
            buttons_frame,
            text="Name",
            font=("Arial", 50),
            command=lambda: self.controller.reenter_button_pressed("name"),
        )
        self.add_name_button.grid(row=0, column=0, sticky="nsew")

        self.add_price_button = tk.Button(
            buttons_frame,
            text="Price",
            font=("Arial", 50),
            command=lambda: self.controller.reenter_button_pressed("price"),
        )
        self.add_price_button.grid(row=0, column=1, sticky="nsew")

        self.add_barcode_button = tk.Button(
            buttons_frame,
            text="Barcode",
            font=("Arial", 50),
            command=lambda: self.controller.reenter_button_pressed("barcode"),
        )
        self.add_barcode_button.grid(row=1, column=0, sticky="nsew")

        self.add_taxable_button = tk.Button(
            buttons_frame,
            text="Taxable",
            font=("Arial", 50),
            command=lambda: self.controller.reenter_button_pressed("taxable"),
        )
        self.add_taxable_button.grid(row=1, column=1, sticky="nsew")

        self.add_quantity_button = tk.Button(
            buttons_frame,
            text="Quantity",
            font=("Arial", 50),
            command=lambda: self.controller.reenter_button_pressed("quantity"),
        )
        self.add_quantity_button.grid(row=2, column=0, sticky="nsew")

        self.add_category_button = tk.Button(
            buttons_frame,
            text="Category",
            font=("Arial", 50),
            command=lambda: self.controller.reenter_button_pressed("category"),
        )
        self.add_category_button.grid(row=2, column=1, sticky="nsew")

        self.add_subcategory_button = tk.Button(
            buttons_frame,
            text="Subcategory",
            font=("Arial", 50),
            command=lambda: self.controller.reenter_button_pressed("subcategory"),
        )
        self.add_subcategory_button.grid(row=3, column=0, sticky="nsew")

        self.add_vendor_button = tk.Button(
            buttons_frame,
            text="Vendor",
            font=("Arial", 50),
            command=lambda: self.controller.reenter_button_pressed("vendor"),
        )
        self.add_vendor_button.grid(row=3, column=1, sticky="nsew")

        tk.Button(
            buttons_frame,
            text="Back",
            font=("Arial", 50),
            command=lambda: self.controller.on_add_item_enter(None, None, True),
        ).grid(row=4, column=0, sticky="nsew", pady=20)

        tk.Button(
            buttons_frame,
            text="Quit",
            font=("Arial", 50),
            command=lambda: self.wm.show_frame("main_menu"),
        ).grid(row=4, column=1, sticky="nsew", pady=20)
