import tkinter as tk

from .base_frame import BaseFrame


class AddItemFrame(BaseFrame):

    def build_widgets(self) -> None:

        back_quit_frame = tk.Frame(self)

        back_quit_frame.columnconfigure(1, weight=1, uniform="equal")
        back_quit_frame.columnconfigure(0, weight=1, uniform="equal")

        self.add_item_label = tk.Label(
            self,
            text="Please confirm item's info:",
            font=("Arial", 50),
            width=27,
        )

        self.add_item_label.grid(column=1, row=0, sticky="ew")

        self.add_item_quit_button = tk.Button(
            back_quit_frame,
            text="Quit",
            font=("Arial", 50),
            command=lambda: self.wm.show_frame("main_menu"),
        )

        self.add_item_quit_button.grid(column=0, row=0, sticky="ew")

        self.item_info_confirmation = tk.Text(
            self, font=("Ubuntu Mono", 35), width=6, height=5
        )
        self.item_info_confirmation.tag_configure("justify_right", justify="right")

        self.item_info_confirmation.grid(column=1, row=1, sticky="ew")

        self.item_info_scrollbar = tk.Scrollbar(
            self, bg="white", orient=tk.VERTICAL, width=40
        )

        self.item_info_scrollbar.grid(column=1, row=1, sticky="nse")
        self.item_info_confirmation.config(yscrollcommand=self.item_info_scrollbar.set)
        self.item_info_scrollbar.config(command=self.item_info_confirmation.yview)

        back_quit_frame.grid(column=1, row=4, sticky="ew")

        self.yes_button = tk.Button(
            back_quit_frame,
            text="Yes",
            font=("Arial", 60),
            command=lambda: self.controller.on_yes_no("yes"),
        )

        self.no_button = tk.Button(
            back_quit_frame,
            text="No",
            font=("Arial", 60),
            command=lambda: self.controller.on_yes_no("no"),
        )

        self.yes_button.grid(column=0, row=1, sticky="nsew", padx=10)
        self.no_button.grid(column=1, row=1, sticky="nsew", padx=10)

    def on_show(self):

        self.print_confirmation_info()

    def print_confirmation_info(self) -> None:
        """Print the current information of the item the user has entered
        to the confirmation box."""

        self.item_info_confirmation.delete("1.0", "end")
        self.item_info_confirmation.insert(
            tk.END, f"Name: {self.state_mgr.add_item_object.name}"
        )
        self.item_info_confirmation.insert(
            tk.END,
            f"\nPrice : ${self.state_mgr.add_item_object.price:.2f}",
        )
        self.item_info_confirmation.insert(
            tk.END,
            (
                " | Tax?: Yes"
                if self.state_mgr.add_item_object.taxable == 1
                else " | Tax?: No"
            ),
        )
        self.item_info_confirmation.insert(
            tk.END, f"\nCat.: {self.state_mgr.add_item_object.category}"
        )
        if self.state_mgr.add_item_object.subcategory != None:
            if len(self.state_mgr.add_item_object.subcategory) <= 30:
                self.item_info_confirmation.insert(
                    tk.END,
                    f"\nSub Cat.: {self.state_mgr.add_item_object.subcategory}",
                )
            else:
                self.item_info_confirmation.insert(
                    tk.END,
                    f"\nSub Cat.: {self.state_mgr.add_item_object.subcategory[0:30]}-\n{self.state_mgr.add_item_object.subcategory[30:]}",
                )
        else:
            self.item_info_confirmation.insert(
                tk.END, f"\nSub Cat.: {self.state_mgr.add_item_object.subcategory}"
            )
        self.item_info_confirmation.insert(
            tk.END, "\nBarcode: " + str(self.state_mgr.add_item_object.barcode)
        )
        self.item_info_confirmation.insert(
            tk.END,
            f" | Qty: {self.state_mgr.add_item_object.quantity:.4f}",
            "justify_right",
        )
        self.item_info_confirmation.insert(
            tk.END, f"\nVendor: {self.state_mgr.add_item_object.vendor}"
        )
