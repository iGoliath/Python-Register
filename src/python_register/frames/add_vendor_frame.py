import tkinter as tk

from .base_frame import BaseFrame


class AddVendorFrame(BaseFrame):

    def build_widgets(self):

        self.config(padx=50)

        tk.Label(
            self, text="Please enter item's vendor:", font=("Arial", 50), width=25
        ).grid(column=1, row=0, sticky="ew")
        self.add_vendor_entry = tk.Entry(self)

        self.add_vendor_listbox = tk.Listbox(self, height=3, font=("Arial", 50))
        add_vendor_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, width=80)

        self.add_vendor_listbox.grid(column=1, row=1, sticky="nwe")
        add_vendor_scrollbar.grid(column=1, row=1, sticky="nse")

        self.add_vendor_listbox.config(yscrollcommand=add_vendor_scrollbar.set)
        add_vendor_scrollbar.config(command=self.add_vendor_listbox.yview)

        vendors = self.controller.state_mgr.get_vendor_names()
        list_vendors = sorted(
            [vendors[i]["vendor_name"] for i in range(0, len(vendors))]
        )

        for vendor in list_vendors:
            self.add_vendor_listbox.insert(tk.END, vendor)

        tk.Button(
            self,
            text="Next",
            font=("Arial", 50),
            command=lambda: self.on_add_vendor_listbox_next(),
        ).grid(column=1, row=2, sticky="ew")
        back_quit_frame = tk.Frame(self)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column=1, row=3, sticky="ew", pady=(15, 0))
        self.add_vendor_back_button = tk.Button(
            back_quit_frame,
            text="Back",
            font=("Arial", 50),
            command=lambda: self.controller.go_back(),
        )
        self.add_vendor_back_button.grid(column=0, row=0, sticky="ew", padx=(0, 15))
        tk.Button(
            back_quit_frame,
            text="Quit",
            font=("Arial", 50),
            command=lambda: self.wm.show_frame("main_menu"),
        ).grid(column=1, row=0, sticky="ew")

        self.add_vendor_skip_button = tk.Button(
            self,
            text="Skip",
            font=("Arial", 50),
            command=lambda: self.controller.skip_vendor_step(),
        )
        self.add_vendor_skip_button.grid(column=1, row=4, sticky="ew")

    def on_show(self, reentering=False):

        if reentering:
            self.add_vendor_back_button.config(
                command=lambda: self.controller.reenter_back_button()
            )
            self.add_vendor_skip_button.grid_forget()

    def on_add_vendor_listbox_next(self, event=None):
        """Places entry in listbox user selected for on_add_item_enter() to pick up."""
        selected_index = self.add_vendor_listbox.curselection()
        if selected_index == ():
            return
        selected_item = self.add_vendor_listbox.get(selected_index)
        self.wm.vendor_var.set(selected_item)
        self.controller.on_add_item_enter()
