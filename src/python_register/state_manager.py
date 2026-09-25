from .make_transaction import Transaction
from .enter_item import Dec4, AddToInventory
import tkinter as tk
import sqlite3
from pathlib import Path
from decimal import Decimal

sqlite3.register_adapter(Decimal, lambda d: int(d.quantize(Decimal("0.01")) * Decimal("100")))
sqlite3.register_converter("TWODECINT", lambda b: Decimal(b.decode()) / Decimal("100"))

sqlite3.register_adapter(Dec4, lambda d: int(d.quantize(Decimal("0.0001")) * Decimal("10000")))
sqlite3.register_converter("FOURDECINT", lambda b: Dec4(b.decode()) / Dec4("10000"))


class StateManager:
    def __init__(self, root_window, database_name, db_connection, tax_rate = Decimal("1")):
        self.tax_rate = Decimal(tax_rate)
        self.add_item_index = self.coupon = 0
        self.sale_items_listbox_index = -1
        self.coupon_reason = ''
        self.reentering = self.coming_from_register = self.updating_existing_item = False
        self.reentering_quantity = self.browsing_seasonals = self.used_coupon = False 
        self.looking_up_add_item = False
        self.yes_no_var = tk.StringVar(root_window)
        self.register_yes_no_var = tk.StringVar(root_window)
        self.seasonal_id_var = tk.StringVar(root_window)
        self.return_var = tk.StringVar(root_window)
        self.browse_index = tk.IntVar(root_window)
        self.browse_mode = tk.StringVar(root_window)
        self.popup_var = tk.StringVar(root_window)
        self.sale_items_listbox_var = tk.IntVar(root_window, -1)
        self.binding_manager = None
        self.current_dir = Path(__file__).parent
        if db_connection == None:
            self.conn = sqlite3.connect(self.current_dir / database_name, detect_types=sqlite3.PARSE_DECLTYPES)
        else:
            self.conn = db_connection
        
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.trans = Transaction(self.conn, self.cursor, self.tax_rate)
        self.add_item_object = AddToInventory(self.conn, self.cursor)
        self.ADD_ITEM_LAST_STEP = 7
        
    def new_transaction(self):
        del self.trans
        self.trans = Transaction(self.conn, self.cursor, self.tax_rate)

    def new_add_item_object(self):
        del self.add_item_object
        self.add_item_object = AddToInventory(self.conn, self.cursor)

    def grab_names_like(self, name):
        return self.cursor.execute("SELECT item_name FROM inventory WHERE item_name LIKE ?", (f'%{name}%', )).fetchall()

    def grab_barcode_given_name(self, name):
        return self.cursor.execute('''SELECT item_barcode FROM inventory WHERE item_name = ?''', (name,)).fetchone()['item_barcode']

    def check_voided(self, sale_id):
        return self.cursor.execute('''SELECT is_voided FROM sales WHERE sale_id = ?''', (sale_id, )).fetchone()['is_voided']

    def set_voided(self, sale_id):
        self.cursor.execute('''UPDATE sales SET is_voided = ? WHERE sale_id = ?''', (1, sale_id))

    def get_sale_info(self, sale_id):
        return self.cursor.execute('''SELECT * FROM sales WHERE sale_id = ?''', (sale_id, )).fetchall()

    def get_sale_items(self, sale_id):
        return self.cursor.execute('''SELECT * from sale_items WHERE sale_id = ?''', (sale_id, )).fetchall()

    def get_item_quantity_id(self, id):
        return self.cursor.execute('''SELECT item_quantity FROM inventory WHERE item_id = ?''', (id, )).fetchone()['item_quantity']

    def update_quantity(self, quantity, id):
        self.cursor.execute('''UPDATE inventory SET item_quantity = ? WHERE item_id = ?''', (Dec4(quantity), id))

    def get_primary_categories(self):
        return self.cursor.execute('''SELECT category_name FROM categories WHERE parent_id IS NULL''').fetchall()

    def get_category_id(self, category_name):
        return self.cursor.execute('''SELECT category_id FROM categories WHERE category_name = ?''', (category_name, )).fetchone()['category_id']

    def get_secondary_categories(self, primary_category_id):
        return self.cursor.execute('''SELECT category_name FROM categories WHERE parent_id = ?''', (primary_category_id, )).fetchall()

    def get_vendor_names(self):
        return self.cursor.execute('''SELECT vendor_name from vendors''').fetchall()

    def get_drink_quantities(self):
        return self.cursor.execute('''
            SELECT i.item_id,
            i.item_name,
            i.item_price,
            i.item_quantity,
            COALESCE(s.total_sold, 0)        AS total_sold,
            COALESCE(d.total_decremented, 0) AS total_decremented
        FROM inventory i
        LEFT JOIN (
            SELECT item_id, SUM(quantity) / 10000 AS total_sold
            FROM sale_items
            GROUP BY item_id
        ) s ON s.item_id = i.item_id
        LEFT JOIN (
            SELECT item_id, SUM(decrement_quantity) / 10000 AS total_decremented
            FROM inventory_decrements_items
            GROUP BY item_id
        ) d ON d.item_id = i.item_id
        WHERE subcategory_id = 141''').fetchall()


   

