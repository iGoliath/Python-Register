from makeTransaction import * 
from enteritem import *
import tkinter as tk
import sqlite3
from pathlib import Path

class StateManager:
    def __init__(self, root_window):
        self.add_item_index = self.coupon = 0
        self.coupon_reason = ''
        self.reentering = self.coming_from_register = self.updating_existing_item = False
        self.reentering_quantity = self.browsing_seasonals = self.used_coupon = False 
        self.yes_no_var = tk.StringVar(root_window)
        self.seasonal_id_var = tk.StringVar(root_window)
        self.return_var = tk.StringVar(root_window)
        self.add_price_var = tk.StringVar(root_window)
        self.void_var = tk.StringVar(root_window)
        self.item_lookup_var = tk.StringVar(root_window)
        self.browse_index = tk.IntVar(root_window)
        self.error_var = tk.StringVar(root_window)
        self.binding_manager = None
        self.current_dir = Path(__file__).parent
        self.conn = sqlite3.connect(self.current_dir / 'RegisterDatabase')
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.trans = Transaction(self.conn, self.cursor)
        self.add_item_object = AddToInventory(self.conn, self.cursor)
        self.ADD_ITEM_LAST_STEP = 7
        

    def new_transaction(self):
        del self.trans
        self.trans = Transaction(self.conn, self.cursor)

    def new_add_item_object(self):
        del self.add_item_object
        self.add_item_object = AddToInventory(self.conn, self.cursor)


   

