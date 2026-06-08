from makeTransaction import * 
from enteritem import *
import tkinter as tk
import sqlite3
from pathlib import Path
from decimal import Decimal

sqlite3.register_adapter(Decimal, lambda d: int(d.quantize(Decimal("0.01")) * Decimal("100")))
sqlite3.register_converter("TWODECINT", lambda b: Decimal(b.decode()) / Decimal("100"))

sqlite3.register_adapter(Dec4, lambda d: int(d.quantize(Decimal("0.0001")) * Decimal("10000")))
sqlite3.register_converter("FOURDECINT", lambda b: Dec4(b.decode()) / Dec4("10000"))


class StateManager:
    def __init__(self, root_window):
        self.add_item_index = self.coupon = 0
        self.sale_items_listbox_index = -1
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
        self.popup_var = tk.StringVar(root_window)
        self.sale_items_listbox_var = tk.IntVar(root_window, -1)
        self.binding_manager = None
        self.current_dir = Path(__file__).parent
        self.conn = sqlite3.connect(self.current_dir / 'RegisterDatabase', detect_types=sqlite3.PARSE_DECLTYPES)
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


   

