import tkinter as tk
from decimal import Decimal, InvalidOperation

from .base_frame import BaseFrame


class LookupItemsFrame(BaseFrame):

    def build_widgets(self):

        self.item_lookup_var = tk.StringVar(self)
        self.item_lookup_var.trace_add("write", self.on_item_lookup)

        self.vcmd = self.register(self.listbox_input_validation)

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.grid(column=1, row=4, sticky="ew")
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)

        self.lookup_items_label = tk.Label(self, text="Item Lookup", font=("Arial", 50))
        self.lookup_items_label.grid(column=1, row=0, sticky="ew")

        self.lookup_items_listbox = tk.Listbox(
            self, font=("Courier New", 40), height=4, bg="black", fg="white", width=31
        )
        self.lookup_items_listbox.grid(column=1, row=1, sticky="nsw")

        self.lookup_items_scrollbar = tk.Scrollbar(
            self, bg="white", orient=tk.VERTICAL, width=40
        )
        self.lookup_items_scrollbar.grid(column=1, row=1, stick="nse")

        self.lookup_items_entry = tk.Entry(
            self, width=28, font=("Arial", 48), textvariable=self.item_lookup_var
        )
        self.lookup_items_entry.grid(column=1, row=2, sticky="w")

        self.lookup_items_quantity_spinbox = tk.Spinbox(
            self,
            font=("Arial", 50),
            from_=0.0,
            to=10000.0,
            increment=1,
            format="%.4f",
            width=3,
            validate="key",
            vcmd=(self.vcmd, "%P"),
        )
        self.lookup_items_quantity_spinbox.grid(column=1, row=3, sticky="ew")

        self.lookup_items_back_button = tk.Button(
            self.buttons_frame,
            text="Back",
            font=("Arial", 50),
            command=lambda: self.wm.return_to_register(),
        )
        self.lookup_items_back_button.grid(column=0, row=0, sticky="ew")

        self.lookup_items_confirm_button = tk.Button(
            self.buttons_frame,
            text="Confirm",
            font=("Arial", 50),
            command=lambda: self.confirm_lookup_items(),
        )
        self.lookup_items_confirm_button.grid(column=1, row=0, sticky="ew")

        self.lookup_items_listbox.config(yscrollcommand=self.lookup_items_scrollbar.set)
        self.lookup_items_scrollbar.config(command=self.lookup_items_listbox.yview)

    def on_show(self, mode="register"):
        if mode == "additem":
            self.controller.state_mgr.looking_up_add_item = True
        self.lookup_items_quantity_spinbox.delete(0, "end")
        self.lookup_items_quantity_spinbox.insert(0, "1")
        self.lookup_items_listbox.delete(0, tk.END)
        self.lookup_items_entry.delete(0, tk.END)
        self.lookup_items_entry.focus_force()

    def on_item_lookup(self, *args):

        names = self.controller.state_mgr.grab_names_like(self.lookup_items_entry.get())
        self.lookup_items_listbox.delete(0, tk.END)

        for name in names:
            self.lookup_items_listbox.insert(tk.END, f"{name[0]}")

    def confirm_lookup_items(self):
        index = self.lookup_items_listbox.curselection()
        if index == ():
            self.wm.popup_description_label_var.set(
                "Please select an item in the listbox"
            )
            self.wm.popup_frame.tkraise()
            return
        name = self.lookup_items_listbox.get(index).strip()
        print(f"Name: {name}")
        if name in ("", " "):
            self.wm.popup_description_label_var.set("Cannot enter blank item!")
            self.wm.popup_frame.tkraise()
            return
        barcode = self.controller.state_mgr.grab_barcode_given_name(name)
        try:
            quantity = Decimal(self.lookup_items_quantity_spinbox.get())
        except InvalidOperation as e:
            print(f"ERROR while looking up item: decimal.InvalidOperation ({e})")
            self.wm.popup_description_label_var.set("Invalid quantity")
            self.wm.popup_frame.tkraise()
            return
        if quantity <= Decimal("0"):
            self.wm.popup_description_label_var.set("Cannot enter a quantity <= 0!")
            self.wm.popup_frame.tkraise()
            return
        self.controller.handle_lookup_confirmed(
            barcode, Decimal(self.lookup_items_quantity_spinbox.get())
        )

    def listbox_input_validation(self, P):

        if P == "." or P == "":
            return True

        try:
            float(P)
            return True
        except ValueError:
            return False
