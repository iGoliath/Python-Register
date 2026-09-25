from .base_frame import BaseFrame
import tkinter as tk

class AddSubcategoryFrame(BaseFrame):

    def build_widgets(self):

        self.config(padx=50)

        tk.Label(self, text="Please enter item's subcategory:", 
        font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')

        self.add_subcategory_listbox = tk.Listbox(
            self, height=4, font=("Arial", 45))
        add_subcategory_scrollbar = tk.Scrollbar(
            self,
            orient=tk.VERTICAL, width=80
        )

        self.add_subcategory_listbox.grid(column = 1, row = 1, sticky='nwe')
        add_subcategory_scrollbar.grid(column = 1, row = 1, sticky='nse')

        self.add_subcategory_listbox.config(yscrollcommand= add_subcategory_scrollbar.set)
        add_subcategory_scrollbar.config(command = self.add_subcategory_listbox.yview)

        tk.Button(
            self, text="Next", font=("Arial", 50),
            command = lambda: self.on_add_subcategory_listbox_next()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        self.add_subcategory_back_button = tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back())
        self.add_subcategory_back_button.grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.wm.show_frame("main_menu")).grid(
                column = 1, row = 0, sticky='ew'
            )

    def on_show(self, reentering = False):

        if self.controller.state_mgr.add_item_object.category != '':
            self.populate_listbox()

        if reentering:
            self.add_subcategory_back_button.config(command = lambda: self.controller.reenter_back_button())


    def on_add_subcategory_listbox_next(self, event=None):
        """Places entry in listbox user selected for on_add_item_enter() to pick up."""
        selected_index = self.add_subcategory_listbox.curselection()
        if selected_index == ():
            return
        selected_item = self.add_subcategory_listbox.get(selected_index)
        self.wm.subcategory_var.set(selected_item)
        self.controller.on_add_item_enter()

    def populate_listbox(self):
        self.add_subcategory_listbox.delete(0, tk.END)


        category_id = self.controller.state_mgr.get_category_id(self.controller.state_mgr.add_item_object.category)
        subcategories = self.controller.state_mgr.get_secondary_categories(category_id)
        if subcategories == []:
            self.add_subcategory_listbox.insert(tk.END, 'None')            
        else:
            list_subcategories = sorted([subcategories[i]['category_name'] for i in range(0, len(subcategories))])
            
            for subcategory in list_subcategories:
                self.add_subcategory_listbox.insert(tk.END, subcategory)


