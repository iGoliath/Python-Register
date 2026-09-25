from .base_frame import BaseFrame
import tkinter as tk

class AddTaxFrame(BaseFrame):

    def build_widgets(self):

        self.config(padx=50)

        tk.Label(self, text="Is the item taxable?:", 
            font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')
    
        yes_no_frame = tk.Frame(self)
        yes_no_frame.columnconfigure(0, weight=1)
        yes_no_frame.columnconfigure(1, weight=1)
        yes_no_frame.grid(column = 1, row = 1, sticky='ew')
        
        tk.Button(
            yes_no_frame, text="Yes", font=("Arial", 100),
            command= lambda: self.wm.tax_var.set("1")).grid(
                column = 0, row = 0, sticky='ew'
            )
        tk.Button(
            yes_no_frame, text="No", font=("Arial", 100),
            command= lambda: self.wm.tax_var.set("0")).grid(
                column = 1, row = 0, sticky='ew'
            )

        self.add_tax_entry = tk.Entry(self)

        back_quit_frame = tk.Frame(self)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        self.add_tax_back_button = tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back())
        self.add_tax_back_button.grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.wm.show_frame("main_menu")).grid(
                column = 1, row = 0, sticky='ew'
            )

    def on_show(self, reentering = True):

        self.add_tax_entry.focus_set()

        if reentering:
            self.add_tax_back_button.config(command = lambda: self.controller.reenter_back_button())