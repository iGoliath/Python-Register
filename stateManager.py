from makeTransaction import * 
from enteritem import *
import tkinter as tk

class StateManager:
    def __init__(self, root_window):
        self.add_item_index = 0
        self.reentering = self.coming_from_register = self.updating_existing_item = False 
        self.trans = Transaction()
        self.add_item_object = AddToInventory()
        self.yes_no_var = tk.StringVar(root_window)
        self.reference_number_var = tk.StringVar(root_window)
        self.update_inventory_var = tk.StringVar(root_window)
        self.return_var = tk.StringVar(root_window)

    def new_transaction(self):
        del self.trans
        self.trans = Transaction()

    def new_add_item_object(self):
        del self.add_item_object
        self.add_item_object = AddToInventory()


   

