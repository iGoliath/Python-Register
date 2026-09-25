from .base_frame import BaseFrame
import tkinter as tk

class AddCategoryFrame(BaseFrame):

    def build_widgets(self):

        self.config(padx=50)

        tk.Label(self, text="Please enter item's category:", 
                font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')
        
        self.add_category_listbox = tk.Listbox(
            self,
            height=4, font=("Arial", 45))
        add_category_scrollbar = tk.Scrollbar(
            self,
            orient=tk.VERTICAL, width=80
        )

        self.add_category_listbox.grid(column = 1, row = 1, sticky='nwe')
        add_category_scrollbar.grid(column = 1, row = 1, sticky='nse')

        self.add_category_listbox.config(yscrollcommand= add_category_scrollbar.set)
        add_category_scrollbar.config(command = self.add_category_listbox.yview)

        categories = self.controller.state_mgr.get_primary_categories()
        list_categories = sorted([categories[i]['category_name'] for i in range(0, len(categories))])

        for category in list_categories:
            self.add_category_listbox.insert(tk.END, category)

        tk.Button(
            self, text="Next", font=("Arial", 50),
            command = lambda: self.on_add_category_listbox_next()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        self.add_category_back_button = tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back())
        self.add_category_back_button.grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.wm.show_frame("main_menu")).grid(
                column = 1, row = 0, sticky='ew'
            )

    def on_show(self, reentering = False):

        if reentering:
            self.add_category_back_button.config(command = lambda: self.controller.reenter_back_button())


    def on_add_category_listbox_next(self, event=None):
            """Places entry in listbox user selected for on_add_item_enter() to pick up."""
            selected_index = self.add_category_listbox.curselection()
            if selected_index == ():
                return
            selected_item = self.add_category_listbox.get(selected_index)
            self.wm.category_var.set(selected_item)
            self.controller.on_add_item_enter()