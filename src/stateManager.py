from makeTransaction import * 
from enteritem import *
import tkinter as tk
import sqlite3

class StateManager:
    def __init__(self, root_window):
        self.add_item_index = 0
        self.reentering = self.coming_from_register = self.updating_existing_item = self.reentering_quantity = False 
        self.yes_no_var = tk.StringVar(root_window)
        self.reference_number_var = tk.StringVar(root_window)
        self.update_inventory_var = tk.StringVar(root_window)
        self.return_var = tk.StringVar(root_window)
        self.add_item_var = tk.StringVar(root_window)
        self.void_var = tk.StringVar(root_window)
        self.browse_index = tk.IntVar(root_window)
        self.binding_manager = None
        self.conn = sqlite3.connect("/tmp/RegisterDatabase")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.trans = Transaction(self.conn, self.cursor)
        self.add_item_object = AddToInventory(self.conn, self.cursor)

    def new_transaction(self):
        del self.trans
        self.trans = Transaction(self.conn, self.cursor)

    def new_add_item_object(self):
        del self.add_item_object
        self.add_item_object = AddToInventory(self.conn, self.cursor)


   

